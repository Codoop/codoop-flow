---
name: codoop-flow
description: Drive the codoop-flow Agent-Centric ticket pipeline in-session from Codex, Claude Code, or another coding agent. Use when the user asks to run codoop-flow tickets, process the pending queue, or work a specific ticket through build/verify/review/ship. Orchestrates a deterministic guardrail CLI (scripts/codoop_tools.py) plus the current agent's coding, review, and self-healing work.
---

# codoop-flow orchestration

You are the orchestrator of the codoop-flow Agent-Centric loop (engineering
design §5). You do the intelligent work **in this session**: writing code,
self-healing, review judgment, and living-doc sync. A small guardrail CLI
(`scripts/codoop_tools.py`, inside this skill) handles everything that must be
100% deterministic — claiming tickets, moving folders, managing the isolated git
worktree, running tests, enforcing the edit-scope whitelist, committing.
**Never do the CLI's job by hand** (don't move ticket folders, create worktrees,
or judge whitelist membership yourself) — always call the tool, because those
steps must never be guessed.

## This skill is self-contained

Everything needed lives under **this skill's own directory** (call it `$SKILL`):

```
$SKILL/
├── SKILL.md                       (this file)
├── scripts/
│   ├── codoop_tools.py            guardrail CLI (Agent loop)
│   ├── codoop.py                  human CLI (discover + ticket lifecycle)
│   └── codoop_flow/               deterministic modules the CLIs import
└── references/
    ├── agents/                    review + doc personas
    ├── skills/                    incremental-implementation / debugging / tdd / discovery
    └── discovery-agents/          sub-agents for the discovery loop
```

**First, locate `$SKILL`** — the absolute path of the directory containing this
SKILL.md. Build every path below from it (e.g. `$SKILL/scripts/codoop_tools.py`).
The CLI imports its sibling `codoop_flow/` package automatically, so just invoke
it by absolute path with your launch Python.

## Prerequisites

- A `codoop_flow.toml` pointing at the target repo. All CLI calls take
  `--config <path>`. Ask the user for the path if it isn't obvious; reuse it for
  every call in the run.

## Setup a target repo

If the user asks to onboard, install, set up, or initialize codoop-flow for a
target project, run:

```
python3 $SKILL/scripts/codoop.py setup <target-repo> --config <target-repo>/codoop_flow.toml
```

This creates `docs/tickets/{pending,in_progress,done,failed}/` in the target
repo and writes `codoop_flow.toml`. After setup, tell the user to add or draft a
ticket, then run the normal loop below against that config.

## The loop (one ticket, end to end)

### 1. Pick
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> pick
```
Parse the JSON. If `picked` is false, stop and tell the user why (nothing
pending, or a ticket already in_progress). If a ticket is already in_progress,
that JSON still gives you its `ticket_dir` + `worktree` — resume it rather than
picking a new one. On success you get: `ticket_id`, `ticket_dir` (holds
module_prd.md / spec.md / plan.md / todo.md), `worktree` (the ISOLATED clone you
must edit in), `files_to_edit` (glob whitelist), `ui_capture`, `screenshot_dir`.

### 2. Build (your work)
- Read the ticket's design docs from `ticket_dir`: `module_prd.md` (business),
  `spec.md` (contract), `plan.md` + `todo.md` (steps). Also read the target
  repo's `docs/tech/project-structure.md` and `docs/tech/tech-standards.md` if
  present — respect them as hard architectural boundaries.
- Load `$SKILL/references/skills/incremental-implementation/SKILL.md` discipline
  and implement the ticket **inside the `worktree` directory only**.
- **Edit-scope rule:** only create/modify files matching the `files_to_edit`
  globs. Editing anything outside will fail verify (hard gate) — don't do it.
- Work the `todo.md` items in order; check them off (`- [x]`) as you go.

### 3. Verify (the tool)
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> verify <ticket_id>
```
Exit 0 / `ok:true` = tests passed AND all edits were in-scope AND (for
`ui_capture` tickets) screenshots were produced. Otherwise read `reasons` +
`test_output`.

### 4. Self-heal (your work) — on verify failure
- Apply `$SKILL/references/skills/debugging-and-error-recovery/SKILL.md` triage.
  Denoise `test_output` to the real traceback / assertion / out-of-scope file.
- Fix the **root cause** with a minimal change; stay in scope; don't add
  unrelated features. Re-run verify.
- Budget: retry up to the ticket's `max_healing_attempts` (default 3). If still
  failing, go to **Fail**.

### 5. Review (your reviewers) — after verify passes
Run the review personas from `$SKILL/references/agents/` against `git diff` in
the worktree. Prefer parallel subagents when the host provides them (for example
Codex multi-agent tools or Claude Code Task). If no subagent facility is
available, perform the same reviews serially in this session. Approval must be
**unanimous**; any Critical/Important defect = REJECT.

Always run these three (static group):
- `code-reviewer` → `$SKILL/references/agents/code-reviewer.md`
- `security-auditor` → `$SKILL/references/agents/security-auditor.md`
- `test-engineer` → `$SKILL/references/agents/test-engineer.md`

If `ui_capture` is true, ALSO run these two (dynamic UI/UX group), and give them
the `screenshot_dir` to actually inspect the rendered screens:
- `evidence-collector` → `$SKILL/references/agents/testing-evidence-collector.md`
- `reality-checker` → `$SKILL/references/agents/testing-reality-checker.md`

For each reviewer: read its markdown, use it as the review persona, hand it the
diff (and screenshot dir for the UI two), and require a verdict. If **any**
reviewer rejects, collect the findings and go back to **Self-heal** (still
within the healing budget) to fix them, then re-verify and re-review.

### 6. Ship living docs (your work) — after unanimous approval
Before finishing, sync the target repo's living docs inside the worktree (only
under `docs/prd/` and `docs/tech/`, never source):
- Update `docs/prd/` with changed business logic.
- Update `docs/tech/project-structure.md` for new/moved files.
- Append a concise entry to `docs/tech/changelog.md`.
Adopt the technical-writer discipline
(`$SKILL/references/agents/engineering-technical-writer.md`).

### 7. Finish (the tool)
Draft a Conventional Commit message, then:
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> finish <ticket_id> --message "<conventional commit>"
```
This stages (excluding generated noise), commits on `dev/<ticket_id>`, moves the
ticket to `done/`, and removes the worktree. **Pushing is the human's call** —
tell the user the branch is ready; only push if they ask.

### Fail (the tool) — when the healing budget is exhausted
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> fail <ticket_id> --report "<what failed, denoised>"
```
Writes `healing_report.md` into `failed/<ticket_id>/` and cleans the worktree.
Report back so the human can intervene.

## Human-facing CLI (out of the autonomous loop)

The same package ships a human CLI for the other two loops (design §2 / §4):
```
# One-shot target repo setup:
python3 $SKILL/scripts/codoop.py setup <repo> --config <repo>/codoop_flow.toml
# Venture-Discovery: interactive multi-role design session -> docs/backlog/
python3 $SKILL/scripts/codoop.py discover --config <toml> "an idea"
# Human-Centric ticket lifecycle:
python3 $SKILL/scripts/codoop.py ticket init <id> --config <toml> --title "..."
python3 $SKILL/scripts/codoop.py ticket validate <id> --config <toml>
python3 $SKILL/scripts/codoop.py ticket promote  <id> --config <toml>
```

## Running periodically

To keep working the queue, use the host agent's scheduler/loop facility. In
Claude Code, for example:
```
/loop 5m run the codoop-flow skill against <toml>
```
In Codex, use a recurring automation or explicitly ask Codex to run the skill
again against the same config. The guardrail CLI only lets one `in_progress`
ticket run at a time, so repeated invocations resume the active ticket instead
of double-picking.

## Guardrails recap (why the split)

| Deterministic → `scripts/codoop_tools.py` | Intelligent → you (in-session) |
|---|---|
| pick / move folders / worktree lifecycle | write code, self-heal |
| run tests + edit-scope whitelist gate | review judgment (subagents if available, serial otherwise) |
| commit / archive done\|failed | living-doc sync, commit message |

Trust the tool for the deterministic parts; never re-derive them yourself.
