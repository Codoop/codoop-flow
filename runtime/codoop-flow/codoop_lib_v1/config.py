"""Configuration loading for codoop-flow.

codoop-flow is a portable tool: it drives the ticket pipeline of a *target*
project that lives elsewhere. All project-specific paths come from a TOML
config file so the tool itself carries no business-project state.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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
    # The user's usual professional context for conversation style.
    user_role: str = "general"

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
DEFAULT_CONFIG_PATH = Path(".codoop-flow") / DEFAULT_CONFIG_NAME
VALID_TICKET_DESIGN_MODES = ("strict", "one_pass")
VALID_PROJECT_TYPES = ("backend", "web", "desktop", "mobile")
VALID_USER_ROLES = (
    "developer",
    "product_manager",
    "designer",
    "operations",
    "founder",
    "general",
)

# Ticket pipeline stages the target repo needs under docs/tickets/.
TICKET_STAGES = ("pending", "in_progress", "done", "failed")


def setup_target(
    target_repo: str | Path,
    worktree_root: str | Path = "~/codoop_tickets/worktrees",
    config_path: str | Path | None = None,
    project_paths: dict[str, str] | None = None,
    create_project_dirs: bool = False,
    output_language: str | None = None,
    user_role: str | None = None,
) -> tuple[Config, Path]:
    """One-shot onboarding: create the ticket pipeline dirs in the target repo
    and write out a codoop_flow.toml. Returns (config, config_path).

    Idempotent: re-running fills in missing dirs and refreshes project_paths,
    but refuses a config that points at another target.
    """
    repo = Path(target_repo).expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"target_repo is not a git repository: {repo}")

    wt_root = (repo / Path(worktree_root).expanduser()).resolve()
    cfg_path = Path(config_path).expanduser() if config_path \
        else repo / DEFAULT_CONFIG_PATH
    legacy = repo / DEFAULT_CONFIG_NAME
    migration = not config_path and not cfg_path.exists() and legacy.is_file()
    existing_path = legacy if migration else cfg_path
    existing = load_config(existing_path) if existing_path.exists() else None
    if existing and existing.target_repo != repo:
        raise FileExistsError(
            f"{cfg_path} already exists and points at a different "
            f"target_repo ({existing.target_repo}); remove it first"
        )
    language = _validate_output_language(output_language) \
        if output_language is not None else None
    role = _validate_user_role(user_role) if user_role is not None else None

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

    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    if migration:
        # Preserve comments and unknown fields; the old file survives any failure.
        with tempfile.NamedTemporaryFile(dir=cfg_path.parent, suffix=".toml", delete=False) as f:
            temporary = Path(f.name)
            f.write(legacy.read_bytes())
        try:
            if project_paths is not None:
                _write_project_paths(temporary, paths)
            if language is not None:
                _write_setting(temporary, "output_language", language)
            if role is not None:
                _write_setting(temporary, "user_role", role)
            if load_config(temporary).target_repo != repo:
                raise ValueError("migrated config points at a different target_repo")
            _ensure_config_gitignored(repo, cfg_path)
            temporary.replace(cfg_path)
        finally:
            temporary.unlink(missing_ok=True)
        existing = load_config(cfg_path)

    if existing:
        if project_paths is not None and not migration:
            _write_project_paths(cfg_path, paths)
        if language is not None and not migration:
            _write_setting(cfg_path, "output_language", language)
        if role is not None and not migration:
            _write_setting(cfg_path, "user_role", role)
        if project_paths is not None or language is not None or role is not None:
            existing = load_config(cfg_path)
        config = existing
    else:
        language = language or "auto"
        role = role or "general"
        config = Config(
            target_repo=repo,
            worktree_root=wt_root,
            project_paths=paths,
            output_language=language,
            user_role=role,
        )
        cfg_path.write_text(
            f'target_repo = "{repo}"\n'
            f'worktree_root = "{worktree_root}"\n'
            'ticket_design_mode = "strict"\n'
            f'output_language = {json.dumps(language, ensure_ascii=False)}\n'
            f'user_role = {json.dumps(role, ensure_ascii=False)}\n'
            + _format_project_paths(paths),
            encoding="utf-8",
        )

    for stage in TICKET_STAGES:
        (config.tickets_dir / stage).mkdir(parents=True, exist_ok=True)

    # The config captures per-developer choices (output language, project
    # paths). Committing it would clash across teammates, so keep it local.
    _ensure_config_gitignored(repo, cfg_path)
    if migration:
        legacy.unlink()
    return config, cfg_path


def _ensure_config_gitignored(repo: Path, cfg_path: Path) -> None:
    """Add the config file to the target repo's .gitignore.

    The config holds per-developer choices, so teammates sharing the plugin
    must not commit it. Idempotent, and a no-op when the config lives outside
    the repository. The entry is repo-relative with forward slashes so it
    matches regardless of where setup was invoked.
    """
    try:
        relative = cfg_path.resolve().relative_to(repo)
    except ValueError:
        return  # config lives outside the repo; nothing to ignore
    entry = "/" + relative.as_posix()

    gitignore = repo / ".gitignore"
    lines = gitignore.read_text(encoding="utf-8").splitlines() \
        if gitignore.exists() else []
    if any(line.strip() in (entry, relative.as_posix()) for line in lines):
        return

    with gitignore.open("a", encoding="utf-8") as f:
        if lines and lines[-1].strip():
            f.write("\n")
        f.write(f"# codoop-flow local config (per-developer, do not commit)\n")
        f.write(f"{entry}\n")


def resolve_config_path(path: str | Path | None = None) -> Path:
    """Explicit path, then Git-root workspace config, then legacy root config."""
    if path is not None:
        chosen = Path(path).expanduser().resolve()
    else:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if result.returncode:
            raise FileNotFoundError("outside a Git project; supply --config <path>")
        repo = Path(result.stdout.strip())
        preferred, legacy = repo / DEFAULT_CONFIG_PATH, repo / DEFAULT_CONFIG_NAME
        chosen = preferred if preferred.exists() or not legacy.exists() else legacy
        if preferred.exists() and legacy.exists():
            print(f"Using {preferred}; legacy config also exists at {legacy}", file=sys.stderr)
    if not chosen.is_file():
        raise FileNotFoundError(f"config file not found: {chosen}")
    return chosen


def load_config(path: str | Path | None = None) -> Config:
    """Load the explicit config or discover it within the current Git project."""
    cfg_path = resolve_config_path(path)

    with open(cfg_path, "rb") as f:
        raw = tomllib.load(f)

    try:
        target_repo = Path(raw["target_repo"]).expanduser()
        # Both default locations anchor relative targets at the project root.
        base = cfg_path.parent.parent if cfg_path.parent.name == ".codoop-flow" else cfg_path.parent
        target_repo = (base / target_repo).resolve()
    except KeyError as e:
        raise ValueError("config missing required key: target_repo") from e

    worktree_root = (target_repo / Path(
        raw.get("worktree_root", "~/codoop_tickets/worktrees")
    ).expanduser()).resolve()
    ticket_design_mode = raw.get("ticket_design_mode", "strict")
    if ticket_design_mode not in VALID_TICKET_DESIGN_MODES:
        raise ValueError(
            "config ticket_design_mode must be 'strict' or 'one_pass'"
        )
    output_language = _validate_output_language(raw.get("output_language", "auto"))
    user_role = _validate_user_role(raw.get("user_role", "general"))
    project_paths = _validate_project_paths(raw.get("project_paths", {}))

    return Config(
        target_repo=target_repo,
        worktree_root=worktree_root,
        ticket_design_mode=ticket_design_mode,
        output_language=output_language.strip(),
        user_role=user_role,
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


def _validate_user_role(value: object) -> str:
    if value not in VALID_USER_ROLES:
        roles = ", ".join(VALID_USER_ROLES)
        raise ValueError(f"config user_role must be one of: {roles}")
    return value


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


def _write_setting(path: Path, key: str, value: str) -> None:
    """Edit a root setting without touching same-named keys in unknown tables."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    end = next((i for i, line in enumerate(lines) if line.lstrip().startswith("[")), len(lines))
    index = next((i for i, line in enumerate(lines[:end])
                  if line.partition("=")[0].strip().strip('"\'') == key), None)
    assignment = f'{key} = {json.dumps(value, ensure_ascii=False)}\n'
    if index is None:
        if end and not lines[end - 1].endswith("\n"):
            lines[end - 1] += "\n"
        lines.insert(end, assignment)
    else:
        lines[index] = assignment
    path.write_text("".join(lines), encoding="utf-8")
