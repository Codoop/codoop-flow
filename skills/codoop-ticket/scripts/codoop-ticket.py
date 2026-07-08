#!/usr/bin/env python3
"""codoop-ticket — Human-Centric ticket design CLI (Loop 2).

Standalone tool for designing work tickets: init draft → fill PRD/Spec/Plan → promote to pending.

    python codoop-ticket.py ticket init <id> --config <toml> [--title "..."]
    python codoop-ticket.py ticket validate <id> --config <toml>
    python codoop-ticket.py ticket promote <id> --config <toml>
    python codoop-ticket.py ticket update-metadata <id> --config <toml>

Completely independent of codoop-flow (Loop 3). No cross-loop code dependencies.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add _shared to path for shared libraries
sys.path.insert(0, str(Path(__file__).parents[2] / "_shared"))
from codoop_lib_v1.config import load_config
from codoop_lib_v1.ticket import Ticket
from codoop_lib_v1.tickets_cli import init_draft, promote, validate_draft, update_metadata_from_docs, write_metadata


def _cmd_ticket_init(args) -> int:
    config = load_config(args.config)
    draft = init_draft(
        config, args.ticket_id,
        title=args.title or "",
        language=args.language or "auto",
        ticket_type=args.type or "feature",
    )
    print(f"created draft: {draft}")
    print("Fill module_prd.md + spec.md (+ plan/todo), then: "
          f"python codoop-ticket.py ticket promote {args.ticket_id} --config <toml>")
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
        result = validate_draft(config, args.ticket_id)
        if not result.ok:
            for e in result.errors:
                print(f"error: {e}")
            return 1

        # Show summary before promoting
        draft_dir = config.tickets_dir / "drafts" / args.ticket_id
        ticket = Ticket.load(draft_dir)
        print("\n📋 Ticket Summary:")
        print(f"  ID: {ticket.ticket_id}")
        print(f"  Title: {ticket.title}")
        print(f"  Modules: {', '.join(ticket.modules)}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for w in result.warnings:
                print(f"  - {w}")

        # Skip confirmation if --force flag is set
        if not args.force:
            print("\n" + "="*50)
            response = input("Confirm promoting to pending? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                print("Promotion cancelled.")
                return 1

        dest = promote(config, args.ticket_id)
    except (ValueError, FileExistsError) as e:
        print(str(e))
        return 1
    print(f"\n✅ Promoted to pending: {dest}")
    print("Ready for Loop 3 execution.")
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


def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop-ticket", description="Loop 2: Human-Centric ticket design")
    sub = parser.add_subparsers(dest="command", required=True)

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
            sp.add_argument("--type", default="feature", choices=["feature", "fix"],
                          help="ticket type: feature (需求单, default) or fix (修复单)")
        if name == "promote":
            sp.add_argument("--force", action="store_true", help="skip confirmation prompt")
        sp.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
