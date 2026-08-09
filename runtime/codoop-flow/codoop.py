#!/usr/bin/env python3
"""codoop-flow human-facing CLI.

Covers the human-driven ticket lifecycle (design §4.1):

    python codoop.py ticket init <id> --config <toml> [--title "..."]
    python codoop.py ticket validate <id> --config <toml>
    python codoop.py ticket promote <id> --config <toml>   # drafts/ -> pending/

The Venture-Discovery loop (design §2) is now invoked in-session via the
codoop-discover skill. The Agent-Centric loop (build/verify/review/ship) is
driven via the codoop-execute skill (skills/codoop-execute/SKILL.md), which
calls the guardrail CLI codoop_tools.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The shared library lives beside this plugin-level CLI.
sys.path.insert(0, str(Path(__file__).parent))
from codoop_lib_v1.config import load_config, setup_target
from codoop_lib_v1.tickets_cli import init_draft, promote, validate_draft, update_metadata_from_docs, write_metadata


def _parse_project_path(value: str) -> tuple[str, str]:
    project_type, separator, path = value.partition("=")
    if not separator or not project_type or not path:
        raise argparse.ArgumentTypeError("expected TYPE=PATH, for example web=admin-console")
    return project_type, path


def _cmd_setup(args) -> int:
    try:
        project_paths = dict(args.project_path) if args.project_path else None
        if args.project_path and len(project_paths) != len(args.project_path):
            raise ValueError("each project type may be configured only once")
        config, cfg_path = setup_target(
            args.target_repo,
            worktree_root=args.worktree_root,
            config_path=args.config,
            project_paths=project_paths,
            create_project_dirs=args.create_project_dirs,
        )
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}")
        return 1
    print(f"config ready: {cfg_path}")
    print(f"ticket pipeline ready under: {config.tickets_dir}")
    if config.project_paths:
        print("project paths: " + ", ".join(
            f"{kind}={path}" for kind, path in config.project_paths.items()
        ))
    print("Next: add a ticket to pending/, then in Codex or Claude Code say")
    print(f'  "use the codoop-execute skill and run a ticket against {cfg_path}"')
    return 0


def _cmd_ticket_init(args) -> int:
    config = load_config(args.config)
    draft = init_draft(config, args.ticket_id, title=args.title or "", language=args.language or "auto")
    print(f"created draft: {draft}")
    print("Fill module_prd.md + spec.md (+ plan/todo), then: "
          f"python codoop.py ticket promote {args.ticket_id} --config <toml>")
    return 0


def _cmd_ticket_validate(args) -> int:
    config = load_config(args.config)
    result = validate_draft(config, args.ticket_id)
    for w in result.warnings:
        print(f"warning: {w}")
    if result.ok:
        print(f"OK: {args.ticket_id} is ready to promote")
        return 0
    for e in result.errors:
        print(f"error: {e}")
    return 1


def _cmd_ticket_promote(args) -> int:
    config = load_config(args.config)
    try:
        dest = promote(config, args.ticket_id)
    except (ValueError, FileExistsError) as e:
        print(str(e))
        return 1
    print(f"promoted to pending: {dest}")
    print("The codoop-execute skill will pick it up via `codoop_tools.py pick`.")
    return 0


def _cmd_ticket_update_metadata(args) -> int:
    config = load_config(args.config)
    try:
        updated = update_metadata_from_docs(config, args.ticket_id)
        write_metadata(config, args.ticket_id, updated)
    except ValueError as e:
        print(f"error: {e}")
        return 1
    import json
    print("Updated metadata.json:")
    print(json.dumps(updated, indent=2, ensure_ascii=False))
    return 0


def _cmd_install(args) -> int:
    import subprocess
    install_sh = Path(__file__).parents[2] / "scripts" / "install-skills.sh"
    if not install_sh.exists():
        print(f"error: install script not found: {install_sh}", file=sys.stderr)
        return 1
    cmd = ["bash", str(install_sh)]
    if getattr(args, "agent", None):
        cmd += ["--agent", args.agent]
    if getattr(args, "dry_run", False):
        cmd += ["--dry-run"]
    return subprocess.run(cmd).returncode


def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop", description="codoop-flow human CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_setup = sub.add_parser("setup", help="onboard a target repo: make ticket dirs + write config")
    p_setup.add_argument("target_repo", help="path to the target git repo to drive")
    p_setup.add_argument("--config", default=None, help="where to write codoop_flow.toml (default: ./codoop_flow.toml)")
    p_setup.add_argument("--worktree-root", default="~/codoop_tickets/worktrees", help="where per-ticket worktrees are created")
    p_setup.add_argument(
        "--project-path", action="append", type=_parse_project_path,
        metavar="TYPE=PATH",
        help="map backend/web/desktop/mobile to an existing relative directory; repeat as needed",
    )
    p_setup.add_argument(
        "--create-project-dirs", action="store_true",
        help="create selected standard project directories with only .gitkeep",
    )
    p_setup.set_defaults(func=_cmd_setup)

    p_install = sub.add_parser("install", help="copy the core skills to global agent paths")
    p_install.add_argument("--agent", choices=["codex", "claude", "all"],
                          help="target agent (default: auto-detect both)")
    p_install.add_argument("--dry-run", action="store_true",
                          help="preview without copying")
    p_install.set_defaults(func=_cmd_install)

    p_ticket = sub.add_parser("ticket", help="ticket lifecycle (draft -> pending)")
    tsub = p_ticket.add_subparsers(dest="ticket_command", required=True)

    for name, func, extra in (
        ("init", _cmd_ticket_init, True),
        ("validate", _cmd_ticket_validate, False),
        ("update-metadata", _cmd_ticket_update_metadata, False),
        ("promote", _cmd_ticket_promote, False),
    ):
        sp = tsub.add_parser(name, help=f"{name} a draft ticket")
        sp.add_argument("ticket_id", help="e.g. ticket_001")
        sp.add_argument("--config", default=None, help="path to codoop_flow.toml")
        if extra:
            sp.add_argument("--title", default="", help="ticket title")
            sp.add_argument("--language", default="auto", choices=["auto", "zh", "en"],
                          help="template language: auto (detect from title), zh, or en")
        sp.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
