# Installing the codoop-flow skill in each coding agent

**English** · [简体中文](./install.zh-CN.md)

codoop-flow is a **self-contained skill**: under `skills/codoop-flow/` it carries the orchestration guide (`SKILL.md`), the deterministic guardrail CLI (`scripts/`), and the review personas / sub-skills it depends on (`references/`). So no matter which agent you install it into, as long as that directory is readable and `python3` runs, the pipeline works.

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

Once installed, just tell Claude Code: "read the codoop-flow skill and run a ticket against <codoop_flow.toml>", or schedule it with `/loop 5m run the codoop-flow skill against <toml>`.

For the discovery loop, `--agent claude-code` and `--agent claude` both launch
the local `claude` command:

```bash
python3 /path/to/codoop-flow/skills/codoop-flow/scripts/codoop.py \
  discover --agent claude-code --config /path/to/codoop_flow.toml "an idea"
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
