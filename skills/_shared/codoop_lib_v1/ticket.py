"""Ticket model and metadata.json validation.

A ticket is a directory (e.g. ``ticket_001/``) containing at least
``metadata.json`` plus the human-authored design docs (module_prd.md,
spec.md, plan.md, todo.md).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

METADATA_FILE = "metadata.json"


VALID_TICKET_TYPES = ("feature", "fix")


@dataclass
class Ticket:
    ticket_id: str
    title: str
    modules: list[str]
    # module name -> shell command. Scheduler runs one per module in `modules`.
    test_command: dict[str, str]
    # "feature" (需求单) or "fix" (修复单). Drives which docs Loop 2 requires and
    # which commit prefix Loop 3 uses. Defaults to "feature" for back-compat.
    ticket_type: str = "feature"
    coding_engine: str | None = None
    max_healing_attempts: int = 3
    # When true, this ticket touches UI: tests must emit screenshots into the
    # qa-screenshots dir, and review adds the UI/UX personas.
    ui_capture: bool = False
    # When true, the ticket must include a static HTML preview for human review
    # before it can be promoted.
    visual_preview: bool = False
    # Absolute path to the ticket directory (set at load time).
    path: Path = field(default=None)  # type: ignore[assignment]

    @property
    def screenshot_dir(self) -> Path:
        """Where UI tests must write screenshots + test-results.json (design
        §5.2). Lives under the ticket dir so it travels to done/failed for the
        human to inspect, and is read-only-shared with the UI review personas.
        """
        return self.path / "public" / "qa-screenshots"

    @classmethod
    def load(cls, ticket_dir: Path) -> "Ticket":
        meta_path = ticket_dir / METADATA_FILE
        if not meta_path.exists():
            raise ValueError(f"ticket missing {METADATA_FILE}: {ticket_dir}")

        with open(meta_path, "r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON in {meta_path}: {e}") from e

        _require(raw, "ticket_id", str, meta_path)
        _require(raw, "title", str, meta_path)
        _require(raw, "modules", list, meta_path)
        _require(raw, "test_command", dict, meta_path)
        if "visual_preview" in raw and not isinstance(raw["visual_preview"], bool):
            raise ValueError(f"{meta_path}: field 'visual_preview' must be bool")

        # ticket_type is optional; defaults to "feature". Validate when present.
        ticket_type = raw.get("ticket_type", "feature")
        if ticket_type not in VALID_TICKET_TYPES:
            raise ValueError(
                f"{meta_path}: field 'ticket_type' must be one of "
                f"{VALID_TICKET_TYPES}, got {ticket_type!r}"
            )

        modules = raw["modules"]
        test_command = raw["test_command"]
        # Every module must have a test command mapping.
        missing = [m for m in modules if m not in test_command]
        if missing:
            raise ValueError(
                f"{meta_path}: modules missing test_command entries: {missing}"
            )

        return cls(
            ticket_id=raw["ticket_id"],
            title=raw["title"],
            modules=modules,
            test_command=test_command,
            ticket_type=ticket_type,
            coding_engine=raw.get("coding_engine"),
            max_healing_attempts=int(raw.get("max_healing_attempts", 3)),
            ui_capture=bool(raw.get("ui_capture", False)),
            visual_preview=raw.get("visual_preview", False),
            path=ticket_dir,
        )


def _require(raw: dict, key: str, typ: type, src: Path) -> None:
    if key not in raw:
        raise ValueError(f"{src}: missing required field {key!r}")
    if not isinstance(raw[key], typ):
        raise ValueError(
            f"{src}: field {key!r} must be {typ.__name__}, got {type(raw[key]).__name__}"
        )
