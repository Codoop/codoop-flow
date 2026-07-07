#!/usr/bin/env python3
"""codoop-flow human-facing CLI.

Covers the human-driven ticket lifecycle (design §4.1):

    python codoop.py ticket init <id> --config <toml> [--title "..."]
    python codoop.py ticket validate <id> --config <toml>
    python codoop.py ticket promote <id> --config <toml>   # drafts/ -> pending/

The Venture-Discovery loop (design §2) is now invoked in-session via the
codoop-discover skill. The Agent-Centric loop (build/verify/review/ship) is
driven via the codoop-flow skill (skills/codoop-flow/SKILL.md), which calls
the guardrail CLI codoop_tools.py.
"""

from __future__ import annotations

import argparse
import sys

from codoop_flow.config import load_config, setup_target
from codoop_flow.tickets_cli import init_draft, promote, validate_draft


def _cmd_setup(args) -> int:
    try:
        config, cfg_path = setup_target(
            args.target_repo,
            worktree_root=args.worktree_root,
            config_path=args.config,
        )
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}")
        return 1
    print(f"created config: {cfg_path}")
    print(f"ticket pipeline ready under: {config.tickets_dir}")
    print("Next: add a ticket to pending/, then in Codex or Claude Code say")
    print(f'  "use the codoop-flow skill and run a ticket against {cfg_path}"')
    return 0


def _cmd_ticket_init(args) -> int:
    config = load_config(args.config)
    draft = init_draft(config, args.ticket_id, title=args.title or "")
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
    print("The codoop-flow skill will pick it up via `codoop_tools.py pick`.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop", description="codoop-flow human CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_setup = sub.add_parser("setup", help="onboard a target repo: make ticket dirs + write config")
    p_setup.add_argument("target_repo", help="path to the target git repo to drive")
    p_setup.add_argument("--config", default=None, help="where to write codoop_flow.toml (default: ./codoop_flow.toml)")
    p_setup.add_argument("--worktree-root", default="~/codoop_tickets/worktrees", help="where per-ticket worktrees are created")
    p_setup.set_defaults(func=_cmd_setup)

    p_ticket = sub.add_parser("ticket", help="ticket lifecycle (draft -> pending)")
    tsub = p_ticket.add_subparsers(dest="ticket_command", required=True)

    for name, func, extra in (
        ("init", _cmd_ticket_init, True),
        ("validate", _cmd_ticket_validate, False),
        ("promote", _cmd_ticket_promote, False),
    ):
        sp = tsub.add_parser(name, help=f"{name} a draft ticket")
        sp.add_argument("ticket_id", help="e.g. ticket_001")
        sp.add_argument("--config", default=None, help="path to codoop_flow.toml")
        if extra:
            sp.add_argument("--title", default="", help="ticket title")
        sp.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
