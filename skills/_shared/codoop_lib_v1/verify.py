"""Verify stage: run per-module tests (+ UI screenshot gate).

These checks are deterministic conveyor-belt work — no AI involved.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .ticket import Ticket

# Image extensions counted as captured screenshots for the UI gate.
_SCREENSHOT_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


@dataclass
class VerifyResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    test_output: str = ""


def run_tests(ticket: Ticket, worktree: Path) -> tuple[bool, str]:
    """Run test_command for each module. Returns (all_passed, combined_output).

    For UI tickets the screenshot dir is created and its absolute path exposed
    to the test script via CODOOP_QA_SCREENSHOT_DIR — the script (owned by the
    target repo) is responsible for driving Playwright/simulator and writing
    screenshots + test-results.json there (design §5.2).
    """
    env = os.environ.copy()
    if ticket.ui_capture:
        ticket.screenshot_dir.mkdir(parents=True, exist_ok=True)
        env["CODOOP_QA_SCREENSHOT_DIR"] = str(ticket.screenshot_dir)

    chunks: list[str] = []
    all_ok = True
    for module in ticket.modules:
        cmd = ticket.test_command[module]
        proc = subprocess.run(
            cmd, shell=True, cwd=str(worktree), capture_output=True, text=True,
            env=env,
        )
        chunks.append(
            f"$ [{module}] {cmd}\n(exit {proc.returncode})\n{proc.stdout}{proc.stderr}"
        )
        if proc.returncode != 0:
            all_ok = False
    return all_ok, "\n\n".join(chunks)


def captured_screenshots(ticket: Ticket) -> list[Path]:
    d = ticket.screenshot_dir
    if not d.exists():
        return []
    return [p for p in d.rglob("*") if p.suffix.lower() in _SCREENSHOT_EXTS]


def verify(ticket: Ticket, worktree: Path) -> VerifyResult:
    reasons: list[str] = []

    # Hard gate 1: tests must pass.
    tests_ok, test_output = run_tests(ticket, worktree)
    if not tests_ok:
        reasons.append("one or more module test commands failed")

    # Hard gate 2: UI tickets must produce screenshots for the review personas.
    if ticket.ui_capture and not captured_screenshots(ticket):
        reasons.append(
            "ui_capture ticket produced no screenshots in "
            f"{ticket.screenshot_dir}; the test script must write them to "
            "$CODOOP_QA_SCREENSHOT_DIR"
        )

    return VerifyResult(ok=not reasons, reasons=reasons, test_output=test_output)
