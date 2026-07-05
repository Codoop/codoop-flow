"""Configuration loading for codoop-flow.

codoop-flow is a portable tool: it drives the ticket pipeline of a *target*
project that lives elsewhere. All project-specific paths come from a TOML
config file so the tool itself carries no business-project state.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    # Absolute path to the target git repository being driven.
    target_repo: Path
    # Directory where isolated worktrees are created (one per ticket).
    worktree_root: Path

    @property
    def tickets_dir(self) -> Path:
        return self.target_repo / "docs" / "tickets"

    @property
    def pending_dir(self) -> Path:
        return self.tickets_dir / "pending"

    @property
    def in_progress_dir(self) -> Path:
        return self.tickets_dir / "in_progress"

    @property
    def done_dir(self) -> Path:
        return self.tickets_dir / "done"

    @property
    def failed_dir(self) -> Path:
        return self.tickets_dir / "failed"


DEFAULT_CONFIG_NAME = "codoop_flow.toml"


def load_config(path: str | Path | None = None) -> Config:
    """Load config from a TOML file.

    Search order when ``path`` is None: ./codoop_flow.toml
    """
    cfg_path = Path(path) if path else Path.cwd() / DEFAULT_CONFIG_NAME
    if not cfg_path.exists():
        raise FileNotFoundError(f"config file not found: {cfg_path}")

    with open(cfg_path, "rb") as f:
        raw = tomllib.load(f)

    try:
        target_repo = Path(raw["target_repo"]).expanduser().resolve()
    except KeyError as e:
        raise ValueError("config missing required key: target_repo") from e

    worktree_root = Path(
        raw.get("worktree_root", "~/codoop_tickets/worktrees")
    ).expanduser()

    return Config(target_repo=target_repo, worktree_root=worktree_root)
