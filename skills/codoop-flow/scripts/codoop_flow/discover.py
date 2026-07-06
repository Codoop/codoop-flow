"""Venture-Discovery loop launcher (design §2).

Discovery is inherently human-in-the-loop: the orchestrator agent runs the
product-discovery-loop skill, halting to ask the human whenever something is
ambiguous (SNAP). So — unlike the headless Agent-loop work — this launches
an interactive coding-agent session in the target repo. Claude Code gets the
discovery skill injected as an appended system prompt; Codex gets a prompt that
points at the same skill file and an added readable references directory.

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


def _agent(agent: str | None) -> str:
    selected = (agent or os.environ.get("CODOOP_AGENT") or "claude").strip().lower()
    aliases = {
        "claude-code": "claude",
        "codex-cli": "codex",
    }
    return aliases.get(selected, selected)


def build_command(config: Config, initial_idea: str = "", agent: str | None = None) -> list[str]:
    """Assemble the interactive command for a discovery session.

    Kept separate from launch() so it can be asserted in tests without
    spawning an agent.
    """
    if not _SKILL_PATH.exists():
        raise FileNotFoundError(f"discovery skill not found: {_SKILL_PATH}")

    selected = _agent(agent)
    if selected == "claude":
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
        if initial_idea:
            cmd.append(initial_idea)
        return cmd

    if selected == "codex":
        prompt = (
            "Use the product-discovery-loop skill at "
            f"{_SKILL_PATH} to run a codoop-flow discovery session. "
            "Read the relevant discovery-agent prompts from the references "
            f"directory at {_SKILLS_LIB}. "
            "Write discovery outputs under docs/backlog/ in this target repo."
        )
        if initial_idea:
            prompt += f"\n\nInitial idea: {initial_idea}"
        cmd = [
            "codex",
            "--cd", str(config.target_repo),
            "--add-dir", str(_SKILLS_LIB),
        ]
        model = os.environ.get("CODOOP_CODEX_MODEL")
        if model:
            cmd += ["--model", model]
        cmd.append(prompt)
        return cmd

    raise ValueError(f"unsupported discovery agent: {selected}")


def launch(config: Config, initial_idea: str = "", agent: str | None = None) -> int:
    """Start the interactive discovery session in the target repo. Blocks until
    the human exits the selected agent. Returns the CLI exit code.
    """
    cmd = build_command(config, initial_idea, agent=agent)
    (config.target_repo / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, cwd=str(config.target_repo))
    return proc.returncode
