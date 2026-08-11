"""Configuration loading for codoop-flow.

codoop-flow is a portable tool: it drives the ticket pipeline of a *target*
project that lives elsewhere. All project-specific paths come from a TOML
config file so the tool itself carries no business-project state.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
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
    # Ticket-document review behavior in the in-session ticket-design skill.
    ticket_design_mode: str = "strict"
    # System project type -> actual repository-relative directory.
    project_paths: dict[str, str] = field(default_factory=dict)
    # Language for user-facing prose and generated documents; "auto" follows
    # the user's current language.
    output_language: str = "auto"

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
VALID_TICKET_DESIGN_MODES = ("strict", "one_pass")
VALID_PROJECT_TYPES = ("backend", "web", "desktop", "mobile")

# Ticket pipeline stages the target repo needs under docs/tickets/.
TICKET_STAGES = ("pending", "in_progress", "done", "failed")


def setup_target(
    target_repo: str | Path,
    worktree_root: str | Path = "~/codoop_tickets/worktrees",
    config_path: str | Path | None = None,
    project_paths: dict[str, str] | None = None,
    create_project_dirs: bool = False,
    output_language: str | None = None,
) -> tuple[Config, Path]:
    """One-shot onboarding: create the ticket pipeline dirs in the target repo
    and write out a codoop_flow.toml. Returns (config, config_path).

    Idempotent: re-running fills in missing dirs and refreshes project_paths,
    but refuses a config that points at another target.
    """
    repo = Path(target_repo).expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"target_repo is not a git repository: {repo}")

    wt_root = Path(worktree_root).expanduser()
    cfg_path = Path(config_path).expanduser() if config_path \
        else Path.cwd() / DEFAULT_CONFIG_NAME
    existing = load_config(cfg_path) if cfg_path.exists() else None
    if existing and existing.target_repo != repo:
        raise FileExistsError(
            f"{cfg_path} already exists and points at a different "
            f"target_repo ({existing.target_repo}); remove it first"
        )
    language = _validate_output_language(output_language) \
        if output_language is not None else None

    paths = _validate_project_paths(project_paths or {})
    if create_project_dirs and not paths:
        raise ValueError("new project setup requires at least one project path")
    if project_paths is not None and not paths:
        raise ValueError("project_paths must include at least one project")
    if create_project_dirs:
        _validate_new_project_paths(repo, paths)
        for relative in paths.values():
            project_dir = repo / relative
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / ".gitkeep").touch(exist_ok=True)
    elif project_paths is not None:
        missing = [relative for relative in paths.values()
                   if not _project_dir(repo, relative).is_dir()]
        if missing:
            raise ValueError(f"project directories not found: {', '.join(missing)}")

    if existing:
        if project_paths is not None:
            _write_project_paths(cfg_path, paths)
        if language is not None:
            _write_output_language(cfg_path, language)
        if project_paths is not None or language is not None:
            existing = load_config(cfg_path)
        config = existing
    else:
        language = language or "auto"
        config = Config(
            target_repo=repo,
            worktree_root=wt_root,
            project_paths=paths,
            output_language=language,
        )
        cfg_path.write_text(
            f'target_repo = "{repo}"\n'
            f'worktree_root = "{worktree_root}"\n'
            'ticket_design_mode = "strict"\n'
            f'output_language = {json.dumps(language, ensure_ascii=False)}\n'
            + _format_project_paths(paths),
            encoding="utf-8",
        )

    for stage in TICKET_STAGES:
        (config.tickets_dir / stage).mkdir(parents=True, exist_ok=True)
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
    ticket_design_mode = raw.get("ticket_design_mode", "strict")
    if ticket_design_mode not in VALID_TICKET_DESIGN_MODES:
        raise ValueError(
            "config ticket_design_mode must be 'strict' or 'one_pass'"
        )
    output_language = _validate_output_language(raw.get("output_language", "auto"))
    project_paths = _validate_project_paths(raw.get("project_paths", {}))

    return Config(
        target_repo=target_repo,
        worktree_root=worktree_root,
        ticket_design_mode=ticket_design_mode,
        output_language=output_language.strip(),
        project_paths=project_paths,
    )


def _validate_project_paths(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("config project_paths must be a table")
    paths: dict[str, str] = {}
    for project_type, raw_path in value.items():
        if project_type not in VALID_PROJECT_TYPES:
            raise ValueError(
                f"config project_paths has unknown type: {project_type}"
            )
        if not isinstance(raw_path, str) or not raw_path:
            raise ValueError("config project_paths values must be non-empty strings")
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("config project_paths must stay inside target_repo")
        paths[project_type] = raw_path
    return paths


def _validate_output_language(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("config output_language must be a non-empty string")
    return value.strip()


def _validate_new_project_paths(repo: Path, paths: dict[str, str]) -> None:
    for project_type, relative in paths.items():
        if relative != project_type:
            raise ValueError(
                "new projects must use backend, web, desktop, or mobile directory names"
            )
        project_dir = _project_dir(repo, relative)
        if project_dir.exists():
            contents = {child.name for child in project_dir.iterdir()}
            if contents - {".gitkeep"}:
                raise FileExistsError(f"new project directory is not empty: {project_dir}")


def _project_dir(repo: Path, relative: str) -> Path:
    project_dir = (repo / relative).resolve()
    try:
        project_dir.relative_to(repo)
    except ValueError as exc:
        raise ValueError("config project_paths must stay inside target_repo") from exc
    return project_dir


def _format_project_paths(paths: dict[str, str]) -> str:
    if not paths:
        return ""
    lines = ["\n[project_paths]\n"]
    for project_type in VALID_PROJECT_TYPES:
        if project_type in paths:
            lines.append(f"{project_type} = {json.dumps(paths[project_type])}\n")
    return "".join(lines)


def _write_project_paths(path: Path, paths: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(
        (index for index, line in enumerate(lines)
         if line.strip() == "[project_paths]"),
        None,
    )
    block = _format_project_paths(paths).lstrip("\n")
    if start is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append("\n" + block)
    else:
        end = next(
            (index for index in range(start + 1, len(lines))
             if lines[index].lstrip().startswith("[")),
            len(lines),
        )
        lines[start:end] = [block]
    path.write_text("".join(lines), encoding="utf-8")


def _write_output_language(path: Path, language: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    assignment = f'output_language = {json.dumps(language, ensure_ascii=False)}\n'
    index = next(
        (index for index, line in enumerate(lines)
         if line.partition("=")[0].strip() == "output_language"),
        None,
    )
    if index is None:
        index = next(
            (index for index, line in enumerate(lines)
             if line.lstrip().startswith("[")),
            len(lines),
        )
        lines.insert(index, assignment)
    else:
        lines[index] = assignment
    path.write_text("".join(lines), encoding="utf-8")
