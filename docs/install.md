# Installing the codoop-flow skills in each coding agent

**English** · [简体中文](./install.zh-CN.md)

codoop-flow includes **twelve public skills**, each addressing a different stage of AI-driven development:

**Core Loop Skills:**

| Skill | Purpose | Stage |
|-------|---------|-------|
| **codoop-init** | Inspect existing custom paths or create selected empty standard project directories | Setup |
| **grilling** | Resolve product decisions one plain-language question at a time | Discovery / ticket intake |
| **codoop-discover** | Product design & architecture (0→1 planning) | Loop 1 |
| **codoop-ticket** | Orchestrate ticket design (PRD → Spec → Plan) | Loop 2 |
| **spec-driven-development** | Design technical specs before coding | Loop 2 / standalone |
| **planning-and-task-breakdown** | Break specs into ordered tasks | Loop 2 / standalone |
| **definition-of-done** | Project-level completion standards | Reference |
| **codoop-execute** | Code implementation in isolated worktree | Loop 3 |
| **codoop-ux-walkthrough** | Persona-based experience report; advisory only | Standalone / Loop 3 after approval |

**Loop 3 Engineering Disciplines:**

| Skill | Purpose | Usage |
|-------|---------|-------|
| **incremental-implementation** | Split large changes into verifiable slices | Loop 3 Build phase / standalone |
| **debugging-and-error-recovery** | Systematic root-cause analysis & self-healing | Loop 3 Debug phase / standalone |
| **test-driven-development** | Red-Green-Refactor cycle with high coverage | Loop 3 Verify phase / standalone |

Each skill is independently invokable inside the complete codoop-flow plugin.
Deterministic CLIs, shared Python modules, and review personas live once under
`runtime/codoop-flow/`; skills do not copy or own those files.

> Prerequisites: the machine has `python3` (standard library only, zero third-party deps); the target project is a git repo with `docs/tickets/{pending,in_progress,done,failed}/`. Prepare a `codoop_flow.toml` pointing at the target project (see `codoop_flow.toml.example`).

During setup, `codoop-init` asks for an output language and stores it as
`output_language` in `codoop_flow.toml`. It accepts any BCP 47 language tag,
such as `zh-CN`, `en`, `ko`, `es`, `pt-BR`, or `ar`; `auto` follows the user's
current language. Manual setup can pass `--output-language <language>`.

---

## One-shot install (all 12 skills)

Clone the repo once, then run:

```bash
git clone https://github.com/Codoop/codoop-flow.git
bash codoop-flow/scripts/install-skills.sh
```

This copies all 12 skills plus one shared Runtime to each agent. Codex uses
`~/.codex/runtime/codoop-flow/`; Claude uses `~/.claude/runtime/codoop-flow/`;
Cursor uses `~/.cursor/runtime/codoop-flow/`. Re-running updates them in place.
Use `--agent codex`, `--agent claude`, or `--agent cursor` to target one agent.
Use `--dry-run` to preview.

> For Cursor, installing the plugin (see the Cursor section below) is preferred
> over this copy; the script's `--agent cursor` mode is a fallback.

---

## Codex

Install codoop-flow as a Codex plugin from the GitHub marketplace repo:

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

Then restart/open Codex. The normal workflow is just:

```text
Use $codoop-init to inspect this repo and set up codoop-flow.
Use the codoop-execute skill to run the next ticket against /path/to/codoop_flow.toml.
```

For local development without plugin installation, clone and use the install script:

```bash
git clone https://github.com/Codoop/codoop-flow.git
bash codoop-flow/scripts/install-skills.sh --agent codex
```

## Claude Code

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

Install the complete `codoop-flow` plugin entry. Individual codoop-flow skills
share its Runtime and are not published as separate Claude plugins.

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

Once installed, you can invoke the core skills and engineering disciplines:

**1. codoop-discover** (Phase 1: Product Design) — invoke in-session:
```
/skill codoop-discover I want to build a SaaS project management tool for remote teams
```

**2. codoop-ticket** (Phase 2: Ticket Design Orchestration) — invoke in-session:
```
/skill codoop-ticket Design the user search feature for our e-commerce platform
```

**3. spec-driven-development** (Phase 2: Technical Spec Design) — standalone or called by codoop-ticket:
```
/skill spec-driven-development Based on the ticket PRD, design the technical spec
```

**4. planning-and-task-breakdown** (Phase 2: Task Decomposition) — standalone or called by codoop-ticket:
```
/skill planning-and-task-breakdown Break down the spec into implementation tasks
```

**5. definition-of-done** (Reference: Completion Standards) — reference during development:
```
/skill definition-of-done Check if my completed task meets our quality standards
```

**6. codoop-execute** (Phase 3: Code Implementation) — invoke in-session:
```
Use the codoop-execute skill to run a ticket against /path/to/codoop_flow.toml
```

Or schedule continuously with:
```
/loop 5m run the codoop-execute skill against /path/to/codoop_flow.toml
```

**7. codoop-ux-walkthrough** (Standalone / post-approval insight) — simulate a task as a chosen persona and write a non-blocking report:
```
/skill codoop-ux-walkthrough Experience this feature as a first-time operations manager and write experience_report.md.
```

**8. incremental-implementation** (Loop 3 Engineering Discipline) — standalone or Loop 3 build:
```
/skill incremental-implementation How do I break down this large refactoring into verifiable slices?
```

**9. debugging-and-error-recovery** (Loop 3 Engineering Discipline) — standalone or Loop 3 debug:
```
/skill debugging-and-error-recovery The test failed with an obscure stack trace. Help me find the root cause.
```

**10. test-driven-development** (Loop 3 Engineering Discipline) — standalone or Loop 3 verify:
```
/skill test-driven-development How should I write tests for this feature to ensure high coverage?
```

---

## Cursor

Cursor reads the same `SKILL.md` format as Claude and Codex and ships a plugin
system, so codoop-flow installs as one plugin — skills and their shared Runtime
stay adjacent, exactly as on the other agents. The manifest lives at
`.cursor-plugin/plugin.json`.

**Local / development** — symlink the repo into Cursor's local plugin dir, then
reload:

```bash
git clone https://github.com/Codoop/codoop-flow.git
ln -s "$(pwd)/codoop-flow" ~/.cursor/plugins/local/codoop-flow
# In Cursor: run "Developer: Reload Window" (or restart)
```

After reload, open the **Customize** panel to confirm the plugin loaded, then
invoke skills by typing `/` and searching by name (e.g. `/codoop-init`,
`/codoop-execute`), or just describe the task — Cursor discovers skills from
their `description` like the other agents:

```
/codoop-init inspect this repo and set up codoop-flow
Use codoop-execute to run the next ticket against /path/to/codoop_flow.toml
```

Cursor supports parallel **subagents**, so `codoop-execute` can run the review
personas concurrently just like Codex/Claude.

**Fallback (no plugin system):** copy skills + Runtime into the Cursor home,
keeping them adjacent:

```bash
bash codoop-flow/scripts/install-skills.sh --agent cursor
```

This writes `~/.cursor/skills/` and `~/.cursor/runtime/codoop-flow/`.

---

## Generic copy (Gemini / other agents)

Keep the plugin layout together. Copy the public skills and the Runtime to
matching `skills/` and `runtime/` directories under the same agent home:

```bash
git clone https://github.com/Codoop/codoop-flow.git
# Copy all 12 public skills — each brings its own SKILL.md
for skill in codoop-init grilling codoop-discover codoop-ticket spec-driven-development \
             planning-and-task-breakdown definition-of-done codoop-execute \
             codoop-ux-walkthrough incremental-implementation \
             debugging-and-error-recovery test-driven-development; do
  cp -R "codoop-flow/skills/$skill"  <the agent's skills directory>/
done
mkdir -p <agent-home>/runtime
cp -R codoop-flow/runtime/codoop-flow <agent-home>/runtime/
```

Where each agent expects it (check their own docs, may change across versions):

| Agent | Where | How to trigger |
|---|---|---|
| Gemini CLI | Put them in its skills directory | Auto-discovered |
| Other agents | The skills are plain Markdown; feed each `SKILL.md`'s content as system prompt / instructions | Just talk to it |

**Key point**: keep `<agent-home>/skills/` and `<agent-home>/runtime/codoop-flow/`
at the same level. Every codoop-flow skill resolves the Runtime relative to its
own `SKILL.md`; moving only a skill folder breaks its CLI and review personas.

---

## Verify the install

```bash
codex plugin list
python3 <agent-home>/runtime/codoop-flow/codoop_tools.py --config <toml> status
```

If it prints ticket counts per stage (JSON), the guardrail CLI is in place and the config is correct.

> Note: if the host agent lacks a subagent tool, run the review personas serially in the same session.
