# Installing the codoop-flow skills in each coding agent

**English** · [简体中文](./install.zh-CN.md)

codoop-flow includes **three independent skills**, each addressing a different stage of AI-driven development:

| Skill | Purpose | Stage |
|-------|---------|-------|
| **codoop-discover** | Product design & architecture (0→1 planning) | Before coding |
| **codoop-ticket** | Work ticket planning & breakdown | Ticket design (coming soon) |
| **codoop-flow** | Code implementation in isolated worktree | Coding & shipping |

Each skill is **self-contained**: it carries the orchestration guide (`SKILL.md`), any deterministic CLI, and shared sub-agent personas. So no matter which agent you install it into, as long as the directory is readable and `python3` runs, the skills work.

> Prerequisites: the machine has `python3` (standard library only, zero third-party deps); the target project is a git repo with `docs/tickets/{pending,in_progress,done,failed}/`. Prepare a `codoop_flow.toml` pointing at the target project (see `codoop_flow.toml.example`).

---

## Codex

Install codoop-flow as a Codex plugin from the GitHub marketplace repo:

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

Then restart/open Codex. The normal workflow is just:

```text
Use $codoop-flow to set up this repo for codoop-flow.
Use $codoop-flow to run the next ticket against /path/to/codoop_flow.toml.
```

For local development without plugin installation, clone and copy the skill:

```bash
git clone https://github.com/Codoop/codoop-flow.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codoop-flow/skills/codoop-flow "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## Claude Code

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

> SSH error? The marketplace clones over SSH by default. Without an SSH key, use the full HTTPS URL:
> ```
> /plugin marketplace add https://github.com/Codoop/codoop-flow.git
> /plugin install codoop-flow@codoop-flow
> ```

**Local / development:**
```bash
git clone https://github.com/Codoop/codoop-flow.git
claude --plugin-dir /path/to/codoop-flow
```

Once installed, you can invoke the three skills:

**1. codoop-discover** (Product Design) — invoke in-session:
```
/skill codoop-discover I want to build a SaaS project management tool for remote teams
```

**2. codoop-flow** (Code Implementation) — invoke in-session:
```
Use the codoop-flow skill to run a ticket against /path/to/codoop_flow.toml
```

Or schedule continuously with:
```
/loop 5m run the codoop-flow skill against /path/to/codoop_flow.toml
```

---

## Generic copy (Cursor / Gemini / others)

The skill is a self-contained directory; any agent can copy it into its own skills/rules directory:

```bash
git clone https://github.com/Codoop/codoop-flow.git
# copy just this one directory — it brings its own scripts/ and references/
cp -R codoop-flow/skills/codoop-flow  <the agent's skills directory>/
```

Where each agent expects it (check their own docs, may change across versions):

| Agent | Where | How to trigger |
|---|---|---|
| Cursor | Put `SKILL.md` in `.cursor/rules/`, or have the agent reference the whole `skills/codoop-flow/` | Reference the rule in conversation |
| Other agents | The skill is plain Markdown; feed `SKILL.md`'s content as system prompt / instructions | Just talk to it |
| Gemini CLI | Put it in its skills directory | Auto-discovered |

**Key point**: after copying, make sure `skills/codoop-flow/scripts/` and `references/` stay in the same parent directory as `SKILL.md` — all paths in SKILL.md are relative to itself (`$SKILL/scripts/...`, `$SKILL/references/...`), so splitting them apart breaks the CLI and review personas.

---

## Verify the install

```bash
codex plugin list
python3 <skill-path>/scripts/codoop_tools.py --config <toml> status
```

If it prints ticket counts per stage (JSON), the guardrail CLI is in place and the config is correct.

> Note: if the host agent lacks a subagent tool, run the review personas serially in the same session.
