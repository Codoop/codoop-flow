# Installing the codoop-flow skills in each coding agent

**English** · [简体中文](./install.zh-CN.md)

codoop-flow includes **nine independent skills**, each addressing a different stage of AI-driven development:

**Core Loop Skills:**

| Skill | Purpose | Stage |
|-------|---------|-------|
| **codoop-discover** | Product design & architecture (0→1 planning) | Loop 1 |
| **codoop-ticket** | Orchestrate ticket design (PRD → Spec → Plan) | Loop 2 |
| **spec-driven-development** | Design technical specs before coding | Loop 2 / standalone |
| **planning-and-task-breakdown** | Break specs into ordered tasks | Loop 2 / standalone |
| **definition-of-done** | Project-level completion standards | Reference |
| **codoop-execute** | Code implementation in isolated worktree | Loop 3 |

**Loop 3 Engineering Disciplines:**

| Skill | Purpose | Usage |
|-------|---------|-------|
| **incremental-implementation** | Split large changes into verifiable slices | Loop 3 Build phase / standalone |
| **debugging-and-error-recovery** | Systematic root-cause analysis & self-healing | Loop 3 Debug phase / standalone |
| **test-driven-development** | Red-Green-Refactor cycle with high coverage | Loop 3 Verify phase / standalone |

Each skill is **self-contained**: it carries the orchestration guide (`SKILL.md`), any deterministic CLI, and shared sub-agent personas. So no matter which agent you install it into, as long as the directory is readable and `python3` runs, the skills work.

> Prerequisites: the machine has `python3` (standard library only, zero third-party deps); the target project is a git repo with `docs/tickets/{pending,in_progress,done,failed}/`. Prepare a `codoop_flow.toml` pointing at the target project (see `codoop_flow.toml.example`).

---

## One-shot install (all 6 skills)

Clone the repo once, then run:

```bash
git clone https://github.com/Codoop/codoop-flow.git
bash codoop-flow/scripts/install-skills.sh
```

This copies all 6 skills to `~/.codex/skills/` and `~/.claude/skills/`. Re-running updates skills in-place. Use `--agent codex` or `--agent claude` to target one agent. Use `--dry-run` to preview.

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

Once installed, you can invoke the six skills:

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

**7. incremental-implementation** (Loop 3 Engineering Discipline) — standalone or Loop 3 build:
```
/skill incremental-implementation How do I break down this large refactoring into verifiable slices?
```

**8. debugging-and-error-recovery** (Loop 3 Engineering Discipline) — standalone or Loop 3 debug:
```
/skill debugging-and-error-recovery The test failed with an obscure stack trace. Help me find the root cause.
```

**9. test-driven-development** (Loop 3 Engineering Discipline) — standalone or Loop 3 verify:
```
/skill test-driven-development How should I write tests for this feature to ensure high coverage?
```

---

## Generic copy (Cursor / Gemini / others)

Each skill is a self-contained directory; any agent can copy all nine into its own skills/rules directory:

```bash
git clone https://github.com/Codoop/codoop-flow.git
# Copy all 9 skills — each brings its own SKILL.md
for skill in codoop-discover codoop-ticket spec-driven-development \
             planning-and-task-breakdown definition-of-done codoop-execute \
             incremental-implementation debugging-and-error-recovery test-driven-development; do
  cp -R "codoop-flow/skills/$skill"  <the agent's skills directory>/
done
# _shared is referenced by all skills via relative path
cp -R codoop-flow/skills/_shared <the agent's skills directory>/
```

Where each agent expects it (check their own docs, may change across versions):

| Agent | Where | How to trigger |
|---|---|---|
| Cursor | Put each `SKILL.md` in `.cursor/rules/`, or point the agent at `skills/` | Reference the rule in conversation |
| Other agents | The skills are plain Markdown; feed each `SKILL.md`'s content as system prompt / instructions | Just talk to it |
| Gemini CLI | Put them in its skills directory | Auto-discovered |

**Key point**: after copying, make sure `scripts/` and `references/` etc. stay in the same parent directory as each skill's `SKILL.md` — all paths in SKILL.md are relative to itself (`$SKILL/scripts/...`, `$SKILL/references/...`), so splitting them apart breaks the CLI and review personas.

---

## Verify the install

```bash
codex plugin list
python3 <skill-path>/scripts/codoop_tools.py --config <toml> status
```

If it prints ticket counts per stage (JSON), the guardrail CLI is in place and the config is correct.

> Note: if the host agent lacks a subagent tool, run the review personas serially in the same session.
