---
name: codoop-execute
description: Drive the codoop-flow Agent-Centric ticket pipeline in-session from Codex, Claude Code, or another coding agent. Use when the user asks to run tickets, process the pending queue, or work a specific ticket through build/verify/review/ship. Orchestrates a deterministic guardrail CLI (scripts/codoop_tools.py) plus the current agent's coding, review, and self-healing work.
---

# codoop-execute orchestration

You are the orchestrator of the codoop-flow Agent-Centric loop (Loop 3, engineering
design §5). You do the intelligent work **in this session**: writing code,
self-healing, review judgment, and living-doc sync. A small guardrail CLI
(`scripts/codoop_tools.py`, inside this skill) handles everything that must be
100% deterministic — claiming tickets, moving folders, managing the isolated git
worktree, running tests, committing.
**Never do the CLI's job by hand** (don't move ticket folders or create worktrees
yourself) — always call the tool, because those steps must never be guessed.

## This skill uses shared libraries

The core CLI logic lives here, but shared modules are in the `_shared/` directory:

```
$SKILL/
├── SKILL.md                       (this file)
└── scripts/
    ├── codoop_tools.py            guardrail CLI (Loop 3)
    └── codoop.py                  human CLI (setup/install global commands)

_SHARED/
└── codoop_lib_v1/                 shared modules (codoop-execute + codoop-ticket)
    ├── config.py
    ├── ticket.py
    ├── verify.py
    ├── worktree.py
    ├── gitutil.py
    └── ignore.py
```

**First, locate `$SKILL`** — the absolute path of the directory containing this
SKILL.md. Build every path below from it (e.g. `$SKILL/scripts/codoop_tools.py`).
The CLI automatically imports `codoop_lib_v1/` from `$SKILL/../../_shared/`, so just
invoke it by absolute path with your launch Python.

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
Parse the JSON, then branch on `reason`:
- `picked:true` — you claimed a fresh ticket. **Record `lease_token`** and pass
  `--lease <token>` on EVERY later CLI call in this run (verify/finish/fail).
- `reason:"resumed"` (`picked:false`, exit 0) — a ticket was already in_progress
  and you own it (or it was unowned and you just adopted it). It also returns a
  `lease_token`; use it for the rest of the run. Resume this ticket rather than
  picking a new one.
- `reason:"blocked_by_active_runner"` (exit **non-zero**) — another runner owns
  this ticket. **Stop cleanly and do NOT enter the worktree.** Tell the user
  who holds it (`held_by`, `acquired_at`) and that a human can hand it over with
  `takeover <ticket_id>` (see below).
- `reason:"no pending tickets"` — nothing to do; stop.

On a claim/resume you get: `ticket_id`, `lease_token`, `ticket_dir` (holds
module_prd.md / spec.md / plan.md / todo.md), `worktree` (the ISOLATED clone you
must edit in), `ui_capture`, `screenshot_dir`.

### 2. Build (your work)
- Read the ticket's design docs from `ticket_dir`: `module_prd.md` (business),
  `spec.md` (contract), `plan.md` + `todo.md` (steps). Also read the target
  repo's `docs/tech/project-structure.md` and `docs/tech/tech-standards.md` if
  present — respect them as hard architectural boundaries.
- Load `$SKILL/../../incremental-implementation/SKILL.md` discipline
  and implement the ticket **inside the `worktree` directory only**.
- **Edit-scope guidance:** prefer to create/modify files within the scope
  described in `spec.md` — stay in scope unless the task genuinely requires
  touching adjacent files.
- Work the `todo.md` items in order; check them off (`- [x]`) as you go.

### 3. Verify (the tool)
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> verify <ticket_id> --lease <token>
```
Exit 0 / `ok:true` = tests passed AND (for `ui_capture` tickets) screenshots
were produced. Otherwise read `reasons` + `test_output`.

### 4. Self-heal (your work) — on verify failure
- Apply `$SKILL/../../debugging-and-error-recovery/SKILL.md` triage.
  Denoise `test_output` to the real traceback / assertion.
- Fix the **root cause** with a minimal change; stay in scope; don't add
  unrelated features. Re-run verify.
- Budget: retry up to the ticket's `max_healing_attempts` (default 3). If still
  failing, go to **Fail**.

### 5. Review (your reviewers) — after verify passes
Run the review personas from `$SKILL/../../_shared/agents/` against `git diff` in
the worktree. Prefer parallel subagents when the host provides them (for example
Codex multi-agent tools or Claude Code Task). If no subagent facility is
available, perform the same reviews serially in this session. Approval must be
**unanimous**; any Critical/Important defect = REJECT.

Always run these three (static group):
- `code-reviewer` → `$SKILL/../../_shared/agents/code-reviewer.md`
- `security-auditor` → `$SKILL/../../_shared/agents/security-auditor.md`
- `test-engineer` → `$SKILL/../../_shared/agents/test-engineer.md`

If `ui_capture` is true, ALSO run these two (dynamic UI/UX group), and give them
the `screenshot_dir` to actually inspect the rendered screens:
- `evidence-collector` → `$SKILL/../../_shared/agents/testing-evidence-collector.md`
- `reality-checker` → `$SKILL/../../_shared/agents/testing-reality-checker.md`

For each reviewer: read its markdown, use it as the review persona, hand it the
diff (and screenshot dir for the UI two), and require a verdict. If **any**
reviewer rejects, collect the findings and go back to **Self-heal** (still
within the healing budget) to fix them, then re-verify and re-review.

### 6. Experience walkthrough (optional, non-blocking)
After unanimous technical approval, decide whether the ticket has a runnable,
user-visible behavior. For such tickets, load
`$SKILL/../codoop-ux-walkthrough/SKILL.md` and follow its Loop 3
integration instructions:

- Read `module_prd.md` and pass its user role, goal, scope, and acceptance
  criteria to the walkthrough as runtime task context.
- Keep the selected persona independent of the PRD role; record whether it is
  a core, adjacent, or stress-test persona.
- Write `experience_report.md` directly in `ticket_dir` so it moves to `done/`
  with the completed ticket.
- The report is advisory only. Its findings never reject the ticket, trigger
  self-healing, modify code, expand scope, or create another ticket.

Skip this step for infrastructure, refactoring, and internal-only tickets, or
when no runnable evidence exists. Record the reason in a short
`experience_report.md` only when the walkthrough was requested for that ticket.

### 7. Ship living docs (your work) — after unanimous approval
Before finishing, sync the target repo's living docs inside the worktree (only
under `docs/prd/` and `docs/tech/`, never source):
- Update `docs/prd/` with changed business logic.
- Update `docs/tech/project-structure.md` for new/moved files.
- Append a concise entry to `docs/tech/changelog.md`.
Adopt the technical-writer discipline
(`$SKILL/../../_shared/agents/engineering-technical-writer.md`).

### 8. Finish (the tool)
Draft a Conventional Commit message, then:
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> finish <ticket_id> --lease <token> --message "<conventional commit>"
```
This stages (excluding generated noise), commits on `dev/<ticket_id>`, moves the
ticket to `done/`, and removes the worktree. **Pushing is the human's call** —
tell the user the branch is ready; only push if they ask.

### Fail (the tool) — when the healing budget is exhausted
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> fail <ticket_id> --lease <token> --report "<what failed, denoised>"
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
/loop 5m run the codoop-execute skill against <toml>
```
In Codex, use a recurring automation or explicitly ask Codex to run the skill
again against the same config. The guardrail CLI holds a **lease** on each
in_progress ticket: a run resumes it only when it presents the owning
`lease_token` (or the ticket is unowned). If another active runner owns it,
`pick` returns `blocked_by_active_runner` (exit non-zero) and the automation
must stop cleanly — it will **not** skip ahead to another ticket. That's
intentional: a stuck ticket waits for a human, it doesn't get silently bypassed.

## When a ticket is stuck (human hand-off)

Leases never expire on their own — liveness is your call. To see how far an
in_progress ticket got:
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> status
```
Each `in_progress` entry shows `held_by`, `acquired_at`, `todo` (e.g. `3/8`),
`worktree_dirty`, and `dev_commits` — enough to judge "unfinished, needs a
fresh runner." A ticket is by definition unfinished as long as it sits under
`in_progress/` (finishing moves it to `done/`).

To hand a stuck ticket to a new runner (voids the old lease, mints a new one):
```
python3 $SKILL/scripts/codoop_tools.py --config <toml> takeover <ticket_id>
```
Use the returned `lease_token` for the rest of that run.

## Guardrails recap (why the split)

| Deterministic → `scripts/codoop_tools.py` | Intelligent → you (in-session) |
|---|---|
| pick / move folders / worktree lifecycle | write code, self-heal |
| lease / ownership arbitration (one runner per ticket) | resume vs. stop decision (follow the CLI's `reason`) |
| run tests + UI screenshot gate | review judgment (subagents if available, serial otherwise) |
| commit / archive done\|failed | living-doc sync, commit message |

Trust the tool for the deterministic parts; never re-derive them yourself.
