---
name: codoop-execute
description: Drive the codoop-flow Agent-Centric ticket pipeline in-session from Codex, Claude Code, or another coding agent. Use when the user asks to run tickets, process the pending queue, or work a specific ticket through build/verify/review/ship. Orchestrates the plugin-level deterministic Runtime plus the current agent's coding, review, and self-healing work.
---

# codoop-execute orchestration

You are the orchestrator of the codoop-flow Agent-Centric loop (Loop 3, engineering
design §5). You do the intelligent work **in this session**: writing code,
self-healing, review judgment, and living-doc sync. A small guardrail CLI
(`runtime/codoop-flow/codoop_tools.py`) handles everything that must be
100% deterministic — claiming tickets, moving folders, managing the isolated git
worktree, checking the UI screenshot gate, committing.
**Never do the CLI's job by hand** (don't move ticket folders or create worktrees
yourself) — always call the tool, because those steps must never be guessed.

## Plugin Runtime

Codex and Claude install the whole plugin. All skills call the same Runtime:

```
$SKILL/../../runtime/codoop-flow/
├── codoop_tools.py                guardrail CLI (Loop 3)
├── codoop.py                      setup CLI
├── codoop-ticket.py               ticket lifecycle CLI
├── codoop_lib_v1/                 shared Python modules
└── agents/                        shared review personas
```

**First, locate `$SKILL`** — the absolute path of the directory containing this
SKILL.md. Build every path below from it and invoke the Runtime by absolute path.

## Prerequisites

- A `codoop_flow.toml` pointing at the target repo. All CLI calls take
  `--config <path>`. Ask the user for the path if it isn't obvious; reuse it for
  every call in the run.

Read `output_language` from that config before starting. Use it for all
user-facing replies and generated prose, including reports and delegated agent
prompts. `"auto"` or a missing field follows the user's current language. An
explicit request for the current task overrides the config. Do not translate
source-code identifiers, commands, logs, or required protocol literals.

## Setup a target repo

If the user asks to onboard, install, set up, or initialize codoop-flow for a
target project, read `$SKILL/../codoop-init/SKILL.md` and follow it. Do not call
the setup CLI without the project mappings selected by `codoop-init`. After
setup, tell the user to add or draft a ticket, then run the normal loop below
against the generated config.

## The loop (one ticket, end to end)

### 1. Pick
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> pick
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
module_prd.md / spec.md / optional preview.html / plan.md / todo.md), `worktree` (the ISOLATED clone you
must edit in), `ui_capture`, `screenshot_dir`.

### 1a. Resume a failed ticket (human-approved)

When a human explicitly asks to retry a specific failed ticket, do **not** move
it to `pending/` or call ordinary `pick`; that path can reset a reused branch
and discard recovery work. Instead run:
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> resume <ticket_id>
```
This moves `failed/<ticket_id>` back to `in_progress/`, mints a new lease, and
reuses the retained worktree without a reset. Read `previous_report` from the
JSON when present, then continue at **Build** with the returned lease token and
a fresh `max_healing_attempts` budget. If `worktree_recreated:true`, tell the
human that the retained worktree was already absent; only committed branch
history could be recovered. The prior `healing_report.md` is preserved under a
`healing_report.previous*.md` filename.

### 2. Build (your work)
- Read the ticket's design docs from `ticket_dir`: `module_prd.md` (business),
  `spec.md` (contract), `preview.html` when present (reviewed local visual
  flow), and `plan.md` + `todo.md` (steps). Also read the target
  repo's `docs/tech/project-structure.md` and `docs/tech/tech-standards.md` if
  present — respect them as hard architectural boundaries.
- Read `[project_paths]` from `codoop_flow.toml` and map the ticket's `modules`
  to their real directories. Keep implementation inside those mapped paths;
  repository workflow docs remain allowed. Never create or modify an
  unconfigured backend or platform project. External API requirements guide
  client code only.
- Load `$SKILL/../incremental-implementation/SKILL.md` discipline
  and implement the ticket **inside the `worktree` directory only**.
- **Edit-scope rule:** A `Scope` heading in `spec.md` or `bug_report.md` is
  guidance, not an implicit allowlist. Prefer it, but make the smallest
  adjacent root-cause fix when a required gate needs it; record the file and
  reason in the delivery report.
- Work the `todo.md` items in order; check them off (`- [x]`) as you go.

### 3. Verify (independent steps + tool)
Before editing, capture a **baseline** by running the ticket's declared
validation as ordered, independent steps: lint, build, focused test, then UI
capture when required. Do not accept or create a single `lint && build && ...`
command. Run every later step that does not depend on a failed one, preserving
its stdout, stderr, exit status, and screenshots.

For every baseline diagnostic, record a normalized fingerprint containing:
`module`, `step`/command, file path, line (when present), lint rule or error
code, and normalized error text. After the change, run the same steps again and
compare the diagnostics with `git diff --name-only`:

- New or changed diagnostics, or any diagnostic in a changed file, are ticket
  failures.
- An identical diagnostic outside the changed files is a **baseline blocker**.
  Keep it in the report, but do not self-heal it, consume an attempt, or fail
  this ticket for it.

Never use a broad ignore rule or permanent allowlist: the exact fingerprint is
the only baseline match. A changed rule, line/text, file, or new diagnostic is
failing again.

Then run the deterministic screenshot gate:
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> verify <ticket_id> --lease <token>
```
Exit 0 / `ok:true` = the UI screenshot gate passed (when `ui_capture` is
enabled). Otherwise read `reasons`.

### 4. Self-heal (your work) — only on ticket failures
- Apply `$SKILL/../debugging-and-error-recovery/SKILL.md` triage to the
  reported ticket failure or reviewer finding, never to a baseline blocker.
- Fix the **root cause** with a minimal change; follow Scope guidance and
  report any necessary exception. Re-run the independent validation steps and
  `verify`.
- Budget: retry up to the ticket's `max_healing_attempts` (default 3). If still
  failing, go to **Fail**.

### 4a. Baseline-only outcome
If build, focused tests, required UI capture, deterministic `verify`, and
review all pass, baseline blockers alone do not prevent completion. Write their
full fingerprints, commands, outputs, and the diff file list to the ticket's
verification report; the finish handoff must include `baseline_warnings`.

If the target configuration explicitly requires a repository-wide clean run,
record `blocked_by_baseline` instead of `failed`: retain the worktree and all
evidence for recovery. Do not spend healing attempts on it. This exception is
for exact baseline fingerprints only, never a repository-wide lint exemption.

### 5. Review (your reviewers) — after verify passes
Run the review personas from `$SKILL/../../runtime/codoop-flow/agents/` against `git diff` in
the worktree. Prefer parallel subagents when the host provides them (for example
Codex multi-agent tools or Claude Code Task). If no subagent facility is
available, perform the same reviews serially in this session. Approval must be
**unanimous**; any Critical/Important defect = REJECT.

Always run these three (static group):
- `code-reviewer` → `$SKILL/../../runtime/codoop-flow/agents/code-reviewer.md`
- `security-auditor` → `$SKILL/../../runtime/codoop-flow/agents/security-auditor.md`
- `test-engineer` → `$SKILL/../../runtime/codoop-flow/agents/test-engineer.md`

If `ui_capture` is true, ALSO run these two (dynamic UI/UX group), and give them
the `screenshot_dir` to actually inspect the rendered screens:
- `evidence-collector` → `$SKILL/../../runtime/codoop-flow/agents/testing-evidence-collector.md`
- `reality-checker` → `$SKILL/../../runtime/codoop-flow/agents/testing-reality-checker.md`

For each reviewer: read its markdown, use it as the review persona, hand it the
diff, verification report, and screenshot dir for the UI two, and require a
verdict. If **any** reviewer rejects, collect the findings and go back to
**Self-heal** (still within the healing budget) to fix them, then re-verify and
re-review.

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
(`$SKILL/../../runtime/codoop-flow/agents/engineering-technical-writer.md`).

### 8. Finish (the tool)
Draft a Conventional Commit message, then:
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> finish <ticket_id> --lease <token> --message "<conventional commit>"
```
This stages (excluding generated noise), commits on `dev/<ticket_id>`, moves the
ticket to `done/`, and removes the worktree. **Pushing is the human's call** —
tell the user the branch is ready; only push if they ask.

### Fail (the tool) — when the healing budget is exhausted
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> fail <ticket_id> --lease <token> --report "<what failed, denoised>"
```
Writes `healing_report.md` into `failed/<ticket_id>/`, releases the lease, and
retains the worktree with its uncommitted changes. The report identifies the
worktree path and branch so a human can continue the investigation. Report back
so the human can intervene; do not move the failed ticket back to `pending/`
with the ordinary `pick` flow, because that flow resets a reused worktree.

## Human-facing CLI (out of the autonomous loop)

The same package ships a human CLI for the other two loops (design §2 / §4):
```
# One-shot target repo setup: use the sibling codoop-init skill.
# Venture-Discovery: interactive multi-role design session -> docs/backlog/
python3 $SKILL/../../runtime/codoop-flow/codoop.py discover --config <toml> "an idea"
# Human-Centric ticket lifecycle:
python3 $SKILL/../../runtime/codoop-flow/codoop.py ticket init <id> --config <toml> --title "..."
python3 $SKILL/../../runtime/codoop-flow/codoop.py ticket validate <id> --config <toml>
python3 $SKILL/../../runtime/codoop-flow/codoop.py ticket promote  <id> --config <toml>
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
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> status
```
Each `in_progress` entry shows `held_by`, `acquired_at`, `todo` (e.g. `3/8`),
`worktree_dirty`, and `dev_commits` — enough to judge "unfinished, needs a
fresh runner." A ticket is by definition unfinished as long as it sits under
`in_progress/` (finishing moves it to `done/`).

To hand a stuck ticket to a new runner (voids the old lease, mints a new one):
```
python3 $SKILL/../../runtime/codoop-flow/codoop_tools.py --config <toml> takeover <ticket_id>
```
Use the returned `lease_token` for the rest of that run.

## Guardrails recap (why the split)

| Deterministic → `runtime/codoop-flow/codoop_tools.py` | Intelligent → you (in-session) |
|---|---|
| pick / move folders / worktree lifecycle | write code, self-heal |
| lease / ownership arbitration (one runner per ticket) | resume vs. stop decision (follow the CLI's `reason`) |
| UI screenshot gate | review judgment (subagents if available, serial otherwise) |
| commit / archive done\|failed | living-doc sync, commit message |

Trust the tool for the deterministic parts; never re-derive them yourself.
