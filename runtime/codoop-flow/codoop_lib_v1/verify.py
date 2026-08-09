"""Verify stage: UI screenshot gate.

These checks are deterministic conveyor-belt work — no AI involved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .ticket import Ticket

# Image extensions counted as captured screenshots for the UI gate.
_SCREENSHOT_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


@dataclass
class VerifyResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


def captured_screenshots(ticket: Ticket) -> list[Path]:
    d = ticket.screenshot_dir
    if not d.exists():
        return []
    return [p for p in d.rglob("*") if p.suffix.lower() in _SCREENSHOT_EXTS]


def verify(ticket: Ticket, worktree: Path) -> VerifyResult:
    reasons: list[str] = []

    # UI tickets must produce screenshots for the review personas.
    if ticket.ui_capture and not captured_screenshots(ticket):
        reasons.append(
            "ui_capture ticket produced no screenshots in "
            f"{ticket.screenshot_dir}; add the delivery screenshots there"
        )

    return VerifyResult(ok=not reasons, reasons=reasons)
