#!/usr/bin/env python3
"""codoop-flow guardrail CLI — the deterministic conveyor belt.

In the skill-based architecture, the *intelligent* work (writing code,
self-healing, review judgment, doc sync) is done by the active coding agent
in-session. This CLI is the small set of things that must be 100% deterministic
and never hallucinate:

    pick    — claim the oldest pending ticket: move to in_progress/, create the
              isolated worktree, print the ticket + worktree paths (JSON).
    verify  — run the ticket's tests (+ UI screenshot gate). Print pass/fail +
              output (JSON).
    finish  — stage (excl. generated noise), commit on dev/<id>, move the
              ticket to done/, remove the worktree.
    fail    — move the ticket to failed/, write healing_report.md, remove wt.
    status  — print what's in pending/ and in_progress/ (JSON).

All commands take --config <toml>. Output is JSON so the skill can parse it.
Agent orchestration is driven by the `codoop-flow` skill; see its SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add _shared to path for shared libraries
sys.path.insert(0, str(Path(__file__).parents[2] / "_shared"))
from codoop_lib_v1.config import Config, load_config
from codoop_lib_v1.gitutil import git
from codoop_lib_v1.ignore import GENERATED_PATHSPECS
from codoop_lib_v1.lease import (
    PipelineLock,
    mint_lease,
    read_lease,
    release_lease,
    token_matches,
)
from codoop_lib_v1.ticket import Ticket
from codoop_lib_v1.verify import verify as run_verify
from codoop_lib_v1.worktree import Worktree


def _emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _oldest_pending(config: Config) -> Path | None:
    if not config.pending_dir.exists():
        return None
    dirs = [d for d in config.pending_dir.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return min(dirs, key=lambda d: d.stat().st_mtime)


def _move(src: Path, dst_parent: Path) -> Path:
    import shutil
    dst_parent.mkdir(parents=True, exist_ok=True)
    dst = dst_parent / src.name
    shutil.move(str(src), str(dst))
    return dst


def _todo_progress(ticket_dir: Path) -> str | None:
    """Count checked/total checklist items in todo.md, e.g. "3/8". None if no
    todo.md or it has no checklist items."""
    todo = ticket_dir / "todo.md"
    if not todo.exists():
        return None
    done = total = 0
    for line in todo.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("- [x]") or s.startswith("- [X]"):
            done += 1
            total += 1
        elif s.startswith("- [ ]"):
            total += 1
    return f"{done}/{total}" if total else None


def _in_progress_detail(config: Config, ticket_dir: Path) -> dict:
    """Deterministic facts a human uses to judge 'how far did this room get' —
    ownership + checklist progress + whether the worktree/branch shows activity.
    Never draws a conclusion; just surfaces what's on disk (design §4.5)."""
    ticket_id = ticket_dir.name
    detail: dict = {"ticket_id": ticket_id}

    lease = read_lease(config.worktree_root, ticket_id)
    detail["held_by"] = lease.note if (lease and lease.note) else (
        "unowned" if lease is None else "")
    detail["acquired_at"] = lease.acquired_at if lease else None

    detail["todo"] = _todo_progress(ticket_dir)

    wt = Worktree(config.target_repo, config.worktree_root, ticket_id)
    detail["worktree_exists"] = wt.path.exists()
    if wt.path.exists():
        try:
            status = git("status", "--porcelain", cwd=wt.path)
            detail["worktree_dirty"] = bool(status.strip())
        except Exception:
            detail["worktree_dirty"] = None
    else:
        detail["worktree_dirty"] = None

    try:
        from codoop_lib_v1.gitutil import branch_exists
        if branch_exists(config.target_repo, wt.branch):
            count = git("rev-list", "--count", wt.branch, "^HEAD",
                        cwd=config.target_repo).strip()
            detail["dev_commits"] = int(count) if count.isdigit() else None
        else:
            detail["dev_commits"] = 0
    except Exception:
        detail["dev_commits"] = None

    return detail


def cmd_status(config: Config) -> int:
    def names(d: Path) -> list[str]:
        return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.exists() else []

    in_progress = []
    if config.in_progress_dir.exists():
        for d in sorted(p for p in config.in_progress_dir.iterdir() if p.is_dir()):
            in_progress.append(_in_progress_detail(config, d))

    _emit({
        "pending": names(config.pending_dir),
        "in_progress": in_progress,
        "done": names(config.done_dir),
        "failed": names(config.failed_dir),
    })
    return 0


def cmd_pick(config: Config, lease_token: str | None = None,
             runner_note: str = "") -> int:
    """Claim the oldest pending ticket for work, holding a lease on it.

    Concurrency (design §4): only one runner may own an in_progress ticket. If a
    ticket is already in_progress:
      - caller presents the matching lease token  -> resume (same runner)
      - no lease file exists (legacy / first upgrade) -> adopt + mint a lease
      - caller has no / wrong token, lease is held  -> blocked_by_active_runner
        (exit non-zero, DO NOT touch the worktree)

    The pick bookkeeping runs under a short pipeline lock so two concurrent
    first-picks can't both claim the same pending ticket.
    """
    with PipelineLock(config.worktree_root, config.target_repo):
        in_prog = [d for d in config.in_progress_dir.iterdir() if d.is_dir()] \
            if config.in_progress_dir.exists() else []
        if in_prog:
            existing = in_prog[0]
            ticket = Ticket.load(existing)
            tid = ticket.ticket_id
            lease = read_lease(config.worktree_root, tid)

            # Someone actively owns it and the caller can't prove ownership.
            if lease is not None and not token_matches(config.worktree_root, tid, lease_token):
                _emit({
                    "picked": False,
                    "reason": "blocked_by_active_runner",
                    "ticket_id": tid,
                    "held_by": lease.note or "",
                    "acquired_at": lease.acquired_at,
                    "hint": "another runner owns this ticket; stop cleanly. To "
                            "hand it to a fresh runner, a human runs: takeover "
                            f"{tid}",
                })
                return 1

            # Resume: either caller owns the lease, or it's unowned (legacy) so
            # we adopt it. Rebuild the worktree only now that ownership is ours.
            wt = Worktree(config.target_repo, config.worktree_root, tid)
            if not wt.path.exists():
                wt.create()
            if lease is None:
                lease = mint_lease(config.worktree_root, tid, wt.path, note=runner_note)
            _emit({
                "picked": False,
                "reason": "resumed",
                "ticket_id": tid,
                "ticket_dir": str(existing),
                "worktree": str(wt.path),
                "lease_token": lease.token,
                "ui_capture": ticket.ui_capture,
                "screenshot_dir": str(ticket.screenshot_dir) if ticket.ui_capture else None,
            })
            return 0

        pending = _oldest_pending(config)
        if pending is None:
            _emit({"picked": False, "reason": "no pending tickets"})
            return 0

        in_prog_dir = _move(pending, config.in_progress_dir)
        ticket = Ticket.load(in_prog_dir)
        wt = Worktree(config.target_repo, config.worktree_root, ticket.ticket_id)
        worktree_path = wt.create()
        lease = mint_lease(config.worktree_root, ticket.ticket_id, worktree_path,
                           note=runner_note)

    _emit({
        "picked": True,
        "ticket_id": ticket.ticket_id,
        "title": ticket.title,
        "ticket_dir": str(in_prog_dir),
        "worktree": str(worktree_path),
        "branch": wt.branch,
        "lease_token": lease.token,
        "modules": ticket.modules,
        "ui_capture": ticket.ui_capture,
        "screenshot_dir": str(ticket.screenshot_dir) if ticket.ui_capture else None,
    })
    return 0


def cmd_takeover(config: Config, ticket_id: str, runner_note: str = "") -> int:
    """Human-triggered hand-off: void the old lease, mint a new one, hand the
    worktree to a fresh runner. The only way to seize a ticket whose lease is
    still present — and it is deliberately manual (liveness is a human's call)."""
    tdir = config.in_progress_dir / ticket_id
    if not tdir.exists():
        _emit({"ok": False, "reason": "ticket not in_progress", "ticket_id": ticket_id})
        return 1
    ticket = Ticket.load(tdir)
    wt = Worktree(config.target_repo, config.worktree_root, ticket_id)
    if not wt.path.exists():
        wt.create()
    lease = mint_lease(config.worktree_root, ticket_id, wt.path, note=runner_note)
    _emit({
        "ok": True,
        "ticket_id": ticket_id,
        "ticket_dir": str(tdir),
        "worktree": str(wt.path),
        "lease_token": lease.token,
        "ui_capture": ticket.ui_capture,
        "screenshot_dir": str(ticket.screenshot_dir) if ticket.ui_capture else None,
    })
    return 0


def _load_in_progress(config: Config, ticket_id: str) -> tuple[Ticket, Worktree]:
    tdir = config.in_progress_dir / ticket_id
    if not tdir.exists():
        raise FileNotFoundError(f"ticket not in_progress: {tdir}")
    ticket = Ticket.load(tdir)
    wt = Worktree(config.target_repo, config.worktree_root, ticket_id)
    return ticket, wt


def _lease_guard(config: Config, ticket_id: str, lease_token: str | None) -> int | None:
    """Ownership check for verify/finish/fail. Returns an exit code to abort
    with, or None to proceed.

      - matching token         -> proceed
      - no lease on the ticket  -> proceed (nothing to enforce)
      - token given but wrong   -> reject (someone ran takeover) [exit 1]
      - no token given, lease held -> proceed + warning (back-compat; the real
        concurrency gate is pick)
    """
    lease = read_lease(config.worktree_root, ticket_id)
    if lease is None:
        return None
    if lease_token is None:
        print("warning: no --lease token provided; proceeding for "
              "back-compat, but this ticket is owned by a runner. The real "
              "concurrency gate is `pick`.", file=sys.stderr)
        return None
    if token_matches(config.worktree_root, ticket_id, lease_token):
        return None
    _emit({
        "ticket_id": ticket_id,
        "ok": False,
        "reason": "lease_token_mismatch",
        "hint": "this ticket was taken over by another runner; stop.",
    })
    return 1


def cmd_verify(config: Config, ticket_id: str, lease_token: str | None = None) -> int:
    guard = _lease_guard(config, ticket_id, lease_token)
    if guard is not None:
        return guard
    ticket, wt = _load_in_progress(config, ticket_id)
    result = run_verify(ticket, wt.path)
    _emit({
        "ticket_id": ticket_id,
        "ok": result.ok,
        "reasons": result.reasons,
        "test_output": result.test_output,
    })
    return 0 if result.ok else 1


def cmd_finish(config: Config, ticket_id: str, message: str,
               lease_token: str | None = None) -> int:
    """Commit the verified work and archive the ticket to done/."""
    guard = _lease_guard(config, ticket_id, lease_token)
    if guard is not None:
        return guard
    ticket, wt = _load_in_progress(config, ticket_id)
    worktree = wt.path

    git("add", "-A", "--", ".",
        *(f":(exclude){p}" for p in GENERATED_PATHSPECS), cwd=worktree)
    status = git("status", "--porcelain", cwd=worktree)
    committed = bool(status.strip())
    sha = ""
    if committed:
        # Prefix follows ticket_type: fix tickets get fix(...), else feat(...).
        prefix = "fix" if ticket.ticket_type == "fix" else "feat"
        msg = message or (
            f"{prefix}({ticket.modules[0] if ticket.modules else 'core'}): "
            f"{ticket.title} [{ticket.ticket_id}]"
        )
        git("commit", "-m", msg, cwd=worktree)
        sha = git("rev-parse", "HEAD", cwd=worktree).strip()

    _move(config.in_progress_dir / ticket_id, config.done_dir)
    wt.remove()
    release_lease(config.worktree_root, ticket_id)
    _emit({"ticket_id": ticket_id, "state": "done", "committed": committed, "commit": sha})
    return 0


def cmd_fail(config: Config, ticket_id: str, report: str,
             lease_token: str | None = None) -> int:
    guard = _lease_guard(config, ticket_id, lease_token)
    if guard is not None:
        return guard
    ticket, wt = _load_in_progress(config, ticket_id)
    dest = _move(config.in_progress_dir / ticket_id, config.failed_dir)
    (dest / "healing_report.md").write_text(
        report or f"# Healing report for {ticket_id}\n\n(no detail provided)\n",
        encoding="utf-8",
    )
    wt.remove()
    release_lease(config.worktree_root, ticket_id)
    _emit({"ticket_id": ticket_id, "state": "failed", "report": str(dest / "healing_report.md")})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop_tools", description="codoop-flow guardrail CLI")
    parser.add_argument("--config", default=None, help="path to codoop_flow.toml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show ticket counts + in_progress detail")

    p_pick = sub.add_parser("pick", help="claim oldest pending ticket + create worktree")
    p_pick.add_argument("--lease", default=None, help="lease token to resume an owned ticket")
    p_pick.add_argument("--runner-note", default="", help="optional label for the lease holder (diagnostics)")

    p_takeover = sub.add_parser("takeover", help="human hand-off: void old lease, mint a new one")
    p_takeover.add_argument("ticket_id")
    p_takeover.add_argument("--runner-note", default="", help="optional label for the new lease holder")

    p_verify = sub.add_parser("verify", help="run tests (+ UI screenshot gate)")
    p_verify.add_argument("ticket_id")
    p_verify.add_argument("--lease", default=None, help="lease token (ownership check)")

    p_finish = sub.add_parser("finish", help="commit + archive to done/")
    p_finish.add_argument("ticket_id")
    p_finish.add_argument("--message", default="", help="commit message (else template)")
    p_finish.add_argument("--lease", default=None, help="lease token (ownership check)")

    p_fail = sub.add_parser("fail", help="archive to failed/ + write report")
    p_fail.add_argument("ticket_id")
    p_fail.add_argument("--report", default="", help="healing report body")
    p_fail.add_argument("--lease", default=None, help="lease token (ownership check)")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "status":
        return cmd_status(config)
    if args.command == "pick":
        return cmd_pick(config, lease_token=args.lease, runner_note=args.runner_note)
    if args.command == "takeover":
        return cmd_takeover(config, args.ticket_id, runner_note=args.runner_note)
    if args.command == "verify":
        return cmd_verify(config, args.ticket_id, lease_token=args.lease)
    if args.command == "finish":
        return cmd_finish(config, args.ticket_id, args.message, lease_token=args.lease)
    if args.command == "fail":
        return cmd_fail(config, args.ticket_id, args.report, lease_token=args.lease)
    return 2


if __name__ == "__main__":
    sys.exit(main())
