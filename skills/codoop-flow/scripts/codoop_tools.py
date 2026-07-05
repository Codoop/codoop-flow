#!/usr/bin/env python3
"""codoop-flow guardrail CLI — the deterministic conveyor belt.

In the skill-based architecture, the *intelligent* work (writing code,
self-healing, review judgment, doc sync) is done by Claude in-session. This CLI
is the small set of things that must be 100% deterministic and never hallucinate:

    pick    — claim the oldest pending ticket: move to in_progress/, create the
              isolated worktree, print the ticket + worktree paths (JSON).
    verify  — run the ticket's tests + enforce the files_to_edit whitelist
              (+ UI screenshot gate). Print pass/fail + output (JSON).
    finish  — stage (excl. generated noise), commit on dev/<id>, move the
              ticket to done/, remove the worktree.
    fail    — move the ticket to failed/, write healing_report.md, remove wt.
    status  — print what's in pending/ and in_progress/ (JSON).

All commands take --config <toml>. Output is JSON so the skill can parse it.
The Claude orchestration is driven by the `codoop-flow` skill; see its SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codoop_flow.config import Config, load_config
from codoop_flow.gitutil import git
from codoop_flow.ignore import GENERATED_PATHSPECS
from codoop_flow.ticket import Ticket
from codoop_flow.verify import verify as run_verify
from codoop_flow.worktree import Worktree


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


def cmd_status(config: Config) -> int:
    def names(d: Path) -> list[str]:
        return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.exists() else []
    _emit({
        "pending": names(config.pending_dir),
        "in_progress": names(config.in_progress_dir),
        "done": names(config.done_dir),
        "failed": names(config.failed_dir),
    })
    return 0


def cmd_pick(config: Config) -> int:
    """Claim the oldest pending ticket for work. Idempotent-ish: if something is
    already in_progress, report it instead of picking a new one (the skill runs
    one ticket at a time in-session)."""
    in_prog = [d for d in config.in_progress_dir.iterdir() if d.is_dir()] \
        if config.in_progress_dir.exists() else []
    if in_prog:
        existing = in_prog[0]
        ticket = Ticket.load(existing)
        wt = Worktree(config.target_repo, config.worktree_root, ticket.ticket_id)
        # The worktree may have been removed out-of-band (manual rm, crashed
        # session). Rebuild it so the resumed ticket has a live workspace.
        if not wt.path.exists():
            wt.create()
        _emit({
            "picked": False,
            "reason": "a ticket is already in_progress",
            "ticket_id": ticket.ticket_id,
            "ticket_dir": str(existing),
            "worktree": str(wt.path),
            "files_to_edit": ticket.files_to_edit,
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

    _emit({
        "picked": True,
        "ticket_id": ticket.ticket_id,
        "title": ticket.title,
        "ticket_dir": str(in_prog_dir),
        "worktree": str(worktree_path),
        "branch": wt.branch,
        "modules": ticket.modules,
        "files_to_edit": ticket.files_to_edit,
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


def cmd_verify(config: Config, ticket_id: str) -> int:
    ticket, wt = _load_in_progress(config, ticket_id)
    result = run_verify(ticket, wt.path)
    _emit({
        "ticket_id": ticket_id,
        "ok": result.ok,
        "reasons": result.reasons,
        "test_output": result.test_output,
    })
    return 0 if result.ok else 1


def cmd_finish(config: Config, ticket_id: str, message: str) -> int:
    """Commit the verified work and archive the ticket to done/."""
    ticket, wt = _load_in_progress(config, ticket_id)
    worktree = wt.path

    git("add", "-A", "--", ".",
        *(f":(exclude){p}" for p in GENERATED_PATHSPECS), cwd=worktree)
    status = git("status", "--porcelain", cwd=worktree)
    committed = bool(status.strip())
    sha = ""
    if committed:
        msg = message or (
            f"feat({ticket.modules[0] if ticket.modules else 'core'}): "
            f"{ticket.title} [{ticket.ticket_id}]"
        )
        git("commit", "-m", msg, cwd=worktree)
        sha = git("rev-parse", "HEAD", cwd=worktree).strip()

    _move(config.in_progress_dir / ticket_id, config.done_dir)
    wt.remove()
    _emit({"ticket_id": ticket_id, "state": "done", "committed": committed, "commit": sha})
    return 0


def cmd_fail(config: Config, ticket_id: str, report: str) -> int:
    ticket, wt = _load_in_progress(config, ticket_id)
    dest = _move(config.in_progress_dir / ticket_id, config.failed_dir)
    (dest / "healing_report.md").write_text(
        report or f"# Healing report for {ticket_id}\n\n(no detail provided)\n",
        encoding="utf-8",
    )
    wt.remove()
    _emit({"ticket_id": ticket_id, "state": "failed", "report": str(dest / "healing_report.md")})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop_tools", description="codoop-flow guardrail CLI")
    parser.add_argument("--config", default=None, help="path to codoop_flow.toml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show ticket counts per stage")
    sub.add_parser("pick", help="claim oldest pending ticket + create worktree")

    p_verify = sub.add_parser("verify", help="run tests + edit-scope gate")
    p_verify.add_argument("ticket_id")

    p_finish = sub.add_parser("finish", help="commit + archive to done/")
    p_finish.add_argument("ticket_id")
    p_finish.add_argument("--message", default="", help="commit message (else template)")

    p_fail = sub.add_parser("fail", help="archive to failed/ + write report")
    p_fail.add_argument("ticket_id")
    p_fail.add_argument("--report", default="", help="healing report body")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "status":
        return cmd_status(config)
    if args.command == "pick":
        return cmd_pick(config)
    if args.command == "verify":
        return cmd_verify(config, args.ticket_id)
    if args.command == "finish":
        return cmd_finish(config, args.ticket_id, args.message)
    if args.command == "fail":
        return cmd_fail(config, args.ticket_id, args.report)
    return 2


if __name__ == "__main__":
    sys.exit(main())
