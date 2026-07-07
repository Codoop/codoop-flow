"""Configuration loading for codoop-flow.

codoop-flow is a portable tool: it drives the ticket pipeline of a *target*
project that lives elsewhere. All project-specific paths come from a TOML
config file so the tool itself carries no business-project state.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tomli"])
        import tomli as tomllib  # type: ignore


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

# Ticket pipeline stages the target repo needs under docs/tickets/.
TICKET_STAGES = ("pending", "in_progress", "done", "failed")


def setup_target(
    target_repo: str | Path,
    worktree_root: str | Path = "~/codoop_tickets/worktrees",
    config_path: str | Path | None = None,
) -> tuple[Config, Path]:
    """One-shot onboarding: create the ticket pipeline dirs in the target repo
    and write out a codoop_flow.toml. Returns (config, config_path).

    Idempotent: re-running only fills in missing dirs and refuses to clobber an
    existing config unless it points at the same target.
    """
    repo = Path(target_repo).expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"target_repo is not a git repository: {repo}")

    wt_root = Path(worktree_root).expanduser()
    config = Config(target_repo=repo, worktree_root=wt_root)

    for stage in TICKET_STAGES:
        (config.tickets_dir / stage).mkdir(parents=True, exist_ok=True)

    cfg_path = Path(config_path).expanduser() if config_path \
        else Path.cwd() / DEFAULT_CONFIG_NAME
    if cfg_path.exists():
        existing = load_config(cfg_path)
        if existing.target_repo != repo:
            raise FileExistsError(
                f"{cfg_path} already exists and points at a different "
                f"target_repo ({existing.target_repo}); remove it first"
            )
    else:
        cfg_path.write_text(
            f'target_repo = "{repo}"\n'
            f'worktree_root = "{worktree_root}"\n',
            encoding="utf-8",
        )
    return config, cfg_path


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
