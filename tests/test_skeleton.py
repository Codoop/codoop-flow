"""Skeleton validation for the guardrail CLI + human lifecycle CLI.

Runs without pytest: `python tests/test_skeleton.py`. No AI dependency — the
intelligent work (writing code, review) is the active coding agent's job
in-session, driven by the codoop-execute skill. Here we only exercise the
DETERMINISTIC guardrails (codoop_tools.py) and the human ticket lifecycle, using
a throwaway git repo.

The CLI is invoked as a subprocess (as the skill would), and its JSON output
is parsed and asserted.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# The CLI script is under skills/codoop-execute/scripts/; shared libraries are in skills/_shared/.
_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "skills" / "codoop-execute" / "scripts"
_SHARED = _ROOT / "skills" / "_shared"
sys.path.insert(0, str(_SHARED))

from codoop_lib_v1.config import Config  # noqa: E402

_TOOLS = _SCRIPTS / "codoop_tools.py"


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True)


def _init_target_repo(root: Path) -> None:
    _git("init", cwd=root)
    _git("config", "user.email", "test@codoop.local", cwd=root)
    _git("config", "user.name", "codoop test", cwd=root)
    (root / "backend").mkdir()
    (root / "backend" / ".keep").write_text("", encoding="utf-8")
    (root / "script").mkdir()
    for name in ("pending", "in_progress", "done", "failed"):
        (root / "docs" / "tickets" / name).mkdir(parents=True)
    _git("add", "-A", cwd=root)
    _git("commit", "-m", "init", cwd=root)


def _write_config(root: Path, worktrees: Path) -> Path:
    cfg = root / "codoop_flow.toml"
    cfg.write_text(
        f'target_repo = "{root}"\nworktree_root = "{worktrees}"\n',
        encoding="utf-8",
    )
    return cfg


def _config_obj(root: Path, worktrees: Path) -> Config:
    return Config(target_repo=root, worktree_root=worktrees)


def _make_ticket(
    root: Path, ticket_id: str, *, files_to_edit, test_cmd,
    title="skeleton test", ui_capture=False, ticket_type=None,
) -> Path:
    tdir = root / "docs" / "tickets" / "pending" / ticket_id
    tdir.mkdir(parents=True)
    meta = {
        "ticket_id": ticket_id,
        "title": title,
        "modules": ["backend"],
        "test_command": {"backend": test_cmd},
        "files_to_edit": files_to_edit,
        "max_healing_attempts": 3,
    }
    if ui_capture:
        meta["ui_capture"] = True
    if ticket_type:
        meta["ticket_type"] = ticket_type
    (tdir / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    (tdir / "module_prd.md").write_text("# PRD\nbuild a thing", encoding="utf-8")
    return tdir


def _tool(cfg: Path, *args: str) -> tuple[int, dict]:
    """Run codoop_tools.py and parse its JSON stdout."""
    proc = subprocess.run(
        [sys.executable, str(_TOOLS), "--config", str(cfg), *args],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        data = {"_raw": proc.stdout, "_stderr": proc.stderr}
    return proc.returncode, data


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  ok: {msg}")


# --- guardrail CLI: pick / verify / finish / fail ---------------------------

def test_pick_moves_and_creates_worktree(root: Path, worktrees: Path) -> None:
    print("[test] pick: pending -> in_progress + worktree")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_001", files_to_edit=["backend/**"], test_cmd="true")
    code, data = _tool(cfg, "pick")
    _check(code == 0 and data["picked"], "pick succeeded")
    _check(data["ticket_id"] == "ticket_001", "picked the pending ticket")
    _check(Path(data["ticket_dir"]).exists(), "ticket now in in_progress/")
    _check("in_progress" in data["ticket_dir"], "ticket_dir under in_progress/")
    _check(Path(data["worktree"]).exists(), "worktree created")
    _check(not (root / "docs/tickets/pending/ticket_001").exists(), "gone from pending/")


def test_pick_reports_when_in_progress_busy(root: Path, worktrees: Path) -> None:
    print("[test] pick: reports existing in_progress instead of double-picking")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_a", files_to_edit=["backend/**"], test_cmd="true")
    _tool(cfg, "pick")  # claims ticket_a
    _make_ticket(root, "ticket_b", files_to_edit=["backend/**"], test_cmd="true")
    code, data = _tool(cfg, "pick")
    _check(not data["picked"], "second pick does not claim a new ticket")
    _check(data["ticket_id"] == "ticket_a", "reports the busy in_progress ticket")
    _check((root / "docs/tickets/pending/ticket_b").exists(), "ticket_b untouched in pending/")


def test_verify_passes_in_scope(root: Path, worktrees: Path) -> None:
    print("[test] verify: passing tests + in-scope edit -> ok")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_002", files_to_edit=["backend/**"], test_cmd="true")
    _, picked = _tool(cfg, "pick")
    # Edit in scope inside the worktree.
    (Path(picked["worktree"]) / "backend" / "feature.txt").write_text("x", encoding="utf-8")
    code, data = _tool(cfg, "verify", "ticket_002")
    _check(code == 0 and data["ok"], "verify passed")


def test_verify_ignores_edit_scope(root: Path, worktrees: Path) -> None:
    print("[test] verify: edit scope is advisory, not enforced -> out-of-scope edit passes")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_003", files_to_edit=["backend/**"], test_cmd="true")
    _, picked = _tool(cfg, "pick")
    # Edit OUTSIDE files_to_edit (web/): no longer a hard gate.
    (Path(picked["worktree"]) / "web").mkdir(exist_ok=True)
    (Path(picked["worktree"]) / "web" / "oops.txt").write_text("x", encoding="utf-8")
    code, data = _tool(cfg, "verify", "ticket_003")
    _check(code == 0 and data["ok"], "verify passes despite out-of-scope edit")
    _check(not any("whitelist" in r for r in data["reasons"]), "no whitelist violation reported")


def test_verify_fails_on_failing_tests(root: Path, worktrees: Path) -> None:
    print("[test] verify: failing test command -> fail")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_004", files_to_edit=["backend/**"], test_cmd="false")
    _tool(cfg, "pick")
    code, data = _tool(cfg, "verify", "ticket_004")
    _check(not data["ok"], "verify failed on failing tests")


def test_ui_capture_gate(root: Path, worktrees: Path) -> None:
    print("[test] verify: ui_capture with/without screenshots")
    cfg = _write_config(root, worktrees)
    # No screenshots -> fail.
    _make_ticket(root, "ticket_ui1", files_to_edit=["backend/**"], test_cmd="true", ui_capture=True)
    _tool(cfg, "pick")
    _, data = _tool(cfg, "verify", "ticket_ui1")
    _check(not data["ok"] and any("screenshot" in r.lower() for r in data["reasons"]),
           "ui ticket without screenshots fails")
    _tool(cfg, "fail", "ticket_ui1", "--report", "no shots")

    # Writes a screenshot via the injected env var -> pass.
    _make_ticket(
        root, "ticket_ui2", files_to_edit=["backend/**"], ui_capture=True,
        test_cmd='mkdir -p "$CODOOP_QA_SCREENSHOT_DIR" && printf x > "$CODOOP_QA_SCREENSHOT_DIR/desktop.png"',
    )
    _tool(cfg, "pick")
    _, data2 = _tool(cfg, "verify", "ticket_ui2")
    _check(data2["ok"], "ui ticket with screenshots passes")


def test_finish_commits_and_archives(root: Path, worktrees: Path) -> None:
    print("[test] finish: commit on dev branch + move to done/ + clean worktree")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_005", files_to_edit=["backend/**"], test_cmd="true")
    _, picked = _tool(cfg, "pick")
    (Path(picked["worktree"]) / "backend" / "f.txt").write_text("x", encoding="utf-8")
    code, data = _tool(cfg, "finish", "ticket_005", "--message", "feat(backend): x [ticket_005]")
    _check(code == 0 and data["state"] == "done", "finish returned done")
    _check(data["committed"], "committed changes")
    _check((root / "docs/tickets/done/ticket_005").exists(), "ticket in done/")
    _check(not Path(picked["worktree"]).exists(), "worktree removed")
    log = subprocess.run(
        ["git", "log", "dev/ticket_005", "--oneline"],
        cwd=str(root), capture_output=True, text=True,
    ).stdout
    _check("ticket_005" in log, "commit landed on dev/ticket_005")


def test_finish_fix_uses_fix_prefix(root: Path, worktrees: Path) -> None:
    print("[test] finish (fix): auto commit message uses fix(...) prefix")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_fix2", files_to_edit=["backend/**"], test_cmd="true",
                 ticket_type="fix")
    _, picked = _tool(cfg, "pick")
    (Path(picked["worktree"]) / "backend" / "f.txt").write_text("x", encoding="utf-8")
    # No --message: default template should derive the prefix from ticket_type.
    code, data = _tool(cfg, "finish", "ticket_fix2")
    _check(code == 0 and data["committed"], "fix ticket committed")
    msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%s", "dev/ticket_fix2"],
        cwd=str(root), capture_output=True, text=True,
    ).stdout.strip()
    _check(msg.startswith("fix(backend):"), f"commit prefixed fix(...): {msg!r}")


def test_fail_archives_with_report(root: Path, worktrees: Path) -> None:
    print("[test] fail: move to failed/ + write healing_report")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_006", files_to_edit=["backend/**"], test_cmd="true")
    picked = _tool(cfg, "pick")[1]
    code, data = _tool(cfg, "fail", "ticket_006", "--report", "root cause: boom")
    _check(code == 0 and data["state"] == "failed", "fail returned failed")
    report = (root / "docs/tickets/failed/ticket_006/healing_report.md").read_text()
    _check("boom" in report, "healing_report carries the reason")
    _check(not Path(picked["worktree"]).exists(), "worktree removed on fail")


def test_status_reports_counts(root: Path, worktrees: Path) -> None:
    print("[test] status: reports tickets per stage")
    cfg = _write_config(root, worktrees)
    _make_ticket(root, "ticket_007", files_to_edit=["backend/**"], test_cmd="true")
    code, data = _tool(cfg, "status")
    _check(code == 0, "status ran")
    _check("ticket_007" in data["pending"], "pending count includes the ticket")


# --- human lifecycle CLI (tickets_cli) --------------------------------------

def test_ticket_lifecycle(root: Path, worktrees: Path) -> None:
    print("[test] lifecycle: init -> validate(fail) -> fill -> validate(ok) -> promote")
    from codoop_lib_v1.tickets_cli import init_draft, promote, validate_draft
    cfg = _config_obj(root, worktrees)
    draft = init_draft(cfg, "ticket_010", title="demo")
    _check(draft.exists(), "draft scaffolded")
    _check(not validate_draft(cfg, "ticket_010").ok, "empty scaffold fails validation")
    (draft / "module_prd.md").write_text("# PRD\n用户看到欢迎语。\n", encoding="utf-8")
    (draft / "spec.md").write_text("# Spec\nGET /hello -> hi\n", encoding="utf-8")
    _check(validate_draft(cfg, "ticket_010").ok, "filled draft validates")
    dest = promote(cfg, "ticket_010")
    _check(dest == cfg.pending_dir / "ticket_010" and dest.exists(), "promoted to pending/")
    _check(not draft.exists(), "draft removed after promote")


def test_fix_ticket_lifecycle(root: Path, worktrees: Path) -> None:
    print("[test] lifecycle (fix): init --type fix -> only bug_report.md required")
    from codoop_lib_v1.tickets_cli import init_draft, promote, validate_draft
    from codoop_lib_v1.ticket import Ticket
    cfg = _config_obj(root, worktrees)
    draft = init_draft(cfg, "ticket_fix1", title="修复分页越界", ticket_type="fix")
    _check(draft.exists(), "fix draft scaffolded")
    _check((draft / "bug_report.md").exists(), "bug_report.md scaffolded")
    _check(not (draft / "module_prd.md").exists(), "no module_prd.md for fix")
    _check(not (draft / "spec.md").exists(), "no spec.md for fix")
    _check(Ticket.load(draft).ticket_type == "fix", "metadata records ticket_type=fix")
    # Empty scaffold fails; filling bug_report.md alone is enough (no PRD/spec).
    _check(not validate_draft(cfg, "ticket_fix1").ok, "empty fix scaffold fails validation")
    (draft / "bug_report.md").write_text(
        "# 修复分页越界\n## 现象\n翻到最后一页会 500。\n", encoding="utf-8")
    _check(validate_draft(cfg, "ticket_fix1").ok, "fix draft validates with just bug_report.md")
    dest = promote(cfg, "ticket_fix1")
    _check(dest.exists(), "fix ticket promoted to pending/")


def test_promote_blocks_incomplete(root: Path, worktrees: Path) -> None:
    print("[test] promote refuses incomplete draft")
    from codoop_lib_v1.tickets_cli import init_draft, promote
    cfg = _config_obj(root, worktrees)
    init_draft(cfg, "ticket_011")
    raised = False
    try:
        promote(cfg, "ticket_011")
    except ValueError:
        raised = True
    _check(raised, "promote raised on incomplete draft")
    _check(not (cfg.pending_dir / "ticket_011").exists(), "did not reach pending/")


# TODO: These tests were for the old subprocess launcher (discover.py).
# After refactoring to in-session skill mode (Phase 1), the discovery flow
# is now orchestrated within the SKILL.md and no longer uses subprocess.
# These tests can be removed or replaced with tests for the SKILL validation.
#
# def test_discover_claude_command_build(root: Path, worktrees: Path) -> None:
#     print("[test] discover command assembly for Claude (no spawn)")
#     from codoop_flow import discover
#     cfg = _config_obj(root, worktrees)
#     cmd = discover.build_command(cfg, initial_idea="a todo app", agent="claude")
#     _check(cmd[0] == "claude", "invokes claude")
#     _check("--append-system-prompt" in cmd, "injects discovery skill")
#     _check(cmd[-1] == "a todo app", "initial idea passed")
#     idx = cmd.index("--append-system-prompt")
#     _check("Product Discovery" in cmd[idx + 1], "system prompt is the discovery skill")
#
#
# def test_discover_codex_command_build(root: Path, worktrees: Path) -> None:
#     print("[test] discover command assembly for Codex (no spawn)")
#     from codoop_flow import discover
#     cfg = _config_obj(root, worktrees)
#     cmd = discover.build_command(cfg, initial_idea="a todo app", agent="codex")
#     _check(cmd[0] == "codex", "invokes codex")
#     _check("--cd" in cmd and str(root) in cmd, "sets Codex working root")
#     _check("--add-dir" in cmd, "lets Codex read bundled references")
#     _check("product-discovery-loop" in cmd[-1], "prompt points at discovery skill")
#     _check("a todo app" in cmd[-1], "initial idea passed in prompt")
#
#
# def test_discover_agent_aliases(root: Path, worktrees: Path) -> None:
#     print("[test] discover command aliases")
#     from codoop_flow import discover
#     cfg = _config_obj(root, worktrees)
#     _check(discover.build_command(cfg, agent="claude-code")[0] == "claude",
#            "claude-code aliases to claude CLI")
#     _check(discover.build_command(cfg, agent="codex-cli")[0] == "codex",
#            "codex-cli aliases to codex CLI")


def main() -> int:
    tests = [
        test_pick_moves_and_creates_worktree,
        test_pick_reports_when_in_progress_busy,
        test_verify_passes_in_scope,
        test_verify_ignores_edit_scope,
        test_verify_fails_on_failing_tests,
        test_ui_capture_gate,
        test_finish_commits_and_archives,
        test_finish_fix_uses_fix_prefix,
        test_fail_archives_with_report,
        test_status_reports_counts,
        test_ticket_lifecycle,
        test_fix_ticket_lifecycle,
        test_promote_blocks_incomplete,
        # TODO: discover tests removed after refactoring to in-session skill mode
        # test_discover_claude_command_build,
        # test_discover_codex_command_build,
        # test_discover_agent_aliases,
    ]
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for i, fn in enumerate(tests):
            root = base / f"repo_{i}"
            root.mkdir()
            _init_target_repo(root)
            worktrees = base / f"wt_{i}"
            fn(root, worktrees)
    print("\nALL SKELETON TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
