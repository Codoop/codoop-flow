"""Venture-Discovery loop launcher (design §2).

Discovery is inherently human-in-the-loop: the orchestrator agent runs the
product-discovery-loop skill, halting to ask the human whenever something is
ambiguous (SNAP). So — unlike the headless Agent-loop work — this launches
an *interactive* Claude session in the target repo, with the discovery skill
injected as the system persona and the skills library made readable so the
orchestrator can load the PM / GTM / UI-UX / Architect / Alignment sub-agents.

codoop-flow only wires the launch (deterministic); the actual multi-role
drafting, challenge loop, and consistency audit are the AI's + human's work.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .config import Config

# This file lives at <skill>/scripts/codoop_flow/discover.py, so the skill
# root (which holds references/) is three parents up.
_SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
_DISCOVERY_DIR = _SKILL_ROOT / "references" / "skills" / "product-discovery-loop"
_SKILL_PATH = _DISCOVERY_DIR / "SKILL.md"
# The discovery orchestrator reads its sub-agents from here.
_SKILLS_LIB = _SKILL_ROOT / "references"


def build_command(config: Config, initial_idea: str = "") -> list[str]:
    """Assemble the interactive `claude` command for a discovery session.

    Kept separate from launch() so it can be asserted in tests without
    spawning Claude.
    """
    if not _SKILL_PATH.exists():
        raise FileNotFoundError(f"discovery skill not found: {_SKILL_PATH}")

    system_prompt = _SKILL_PATH.read_text(encoding="utf-8")
    cmd = [
        "claude",
        "--append-system-prompt", system_prompt,
        # Let the orchestrator read the sub-agent markdowns + sibling skills.
        "--add-dir", str(_SKILLS_LIB),
    ]
    model = os.environ.get("CODOOP_CLAUDE_MODEL")
    if model:
        cmd += ["--model", model]
    # An interactive session (no -p): the human directs, the agent asks.
    if initial_idea:
        cmd.append(initial_idea)
    return cmd


def launch(config: Config, initial_idea: str = "") -> int:
    """Start the interactive discovery session in the target repo. Blocks until
    the human exits Claude. Returns the CLI exit code.
    """
    cmd = build_command(config, initial_idea)
    # Discovery writes design docs into the target repo's docs/backlog/.
    (config.target_repo / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, cwd=str(config.target_repo))
    return proc.returncode
