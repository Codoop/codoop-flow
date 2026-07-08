# Loop 3: Agent-Centric (Implementation)

## Overview

**Loop 3** is the third and final loop in codoop-flow's Triple-Loop Model. It is a fully automated, end-to-end ticket execution pipeline that reliably implements, verifies, reviews, and ships software tickets.

**What it solves:** Getting an AI coding agent to implement a ticket without hallucinating infrastructure decisions or shipping untested code. Loop 3 splits labor deliberately: intelligence (agent) writes code and reasons about design; determinism (guardrail CLI) manages git, runs tests, and archives artifacts. The only thing the agent can do wrong without breaking the pipeline is write bad code — and that's caught by review personas.

**Position in pipeline:** Reads Loop 2 outputs from `docs/tickets/pending/<ticket_id>/` → executes in an isolated git worktree on branch `dev/<ticket_id>` → produces code commit + updated living docs + archives to `docs/tickets/done/` (or `failed/`).

---

## Quick Start

In any AI coding tool, say:

```
Use the codoop-execute skill to run a ticket against /path/to/codoop_flow.toml
```

Or schedule it to run continuously:

```
/loop 5m run the codoop-execute skill against /path/to/codoop_flow.toml
```

The skill picks the oldest pending ticket, builds it in an isolated worktree, runs tests, gathers review feedback, self-heals on failure, and ships the result when ready.

---

## Workflow

### Step 1 — Pick (CLI)

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> pick
```

**The CLI:**
- Checks `in_progress/` first. If a ticket is already there, rebuilds its worktree (if deleted) and reports it for resume (don't start a new one)
- If `pending/` is empty, reports "no pending tickets"
- Otherwise, picks the **oldest** pending ticket, creates an isolated `git worktree` on branch `dev/<ticket_id>`, and returns full ticket metadata

**Output JSON:**
```json
{
  "picked": true,
  "ticket_id": "ticket_001",
  "title": "Add user search feature",
  "ticket_dir": "/abs/path/to/in_progress/ticket_001",
  "worktree": "/abs/path/to/worktrees/ticket_001",
  "branch": "dev/ticket_001",
  "modules": ["backend", "web"],
  "ui_capture": false,
  "screenshot_dir": null
}
```

**The agent's job:** Parse the JSON. If already in_progress, resume. If no pending tickets, stop. If picked is true, proceed to Build.

### Step 2 — Build (Agent)

The agent reads the ticket package from `ticket_dir`:
- `module_prd.md` — 100% business description
- `spec.md` — API contract, data schema, UI interactions
- `plan.md` — step-by-step execution plan
- `todo.md` — atomic checkbox tasks

The agent also reads project architectural boundaries from `docs/tech/project-structure.md` and `docs/tech/tech-standards.md`.

**Implementation discipline:** Use the `/skill incremental-implementation` workflow: implement one thin vertical slice, test, verify, then move to the next. Work through `todo.md` items in order, checking them off as you go (`- [x]`).

**Edit-scope guidance:** Prefer to create or modify files within the scope described in `spec.md` — stay in scope unless the task genuinely requires touching adjacent files.

### Step 3 — Verify (CLI)

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> verify <ticket_id>
```

**Two hard gates run sequentially**:

1. **Tests gate** — Runs `test_command[module]` for each module in `modules`. All must exit 0. Fails on first non-zero exit.

2. **UI screenshot gate** (only if `ui_capture: true`) — Checks `ticket_dir/public/qa-screenshots/` for at least one file with recognized image extension (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`). Fails if none exist.

**Output JSON:**
```json
{
  "ticket_id": "ticket_001",
  "ok": true,
  "reasons": [],
  "test_output": "..."
}
```

Or on failure:
```json
{
  "ticket_id": "ticket_001",
  "ok": false,
  "reasons": ["backend tests failed: AssertionError in test_search_api()"],
  "test_output": "..."
}
```

**Exit code:** 0 if `ok: true`, 1 if `ok: false`.

### Step 4 — Self-Heal (Agent, on verify failure)

On verify failure, the agent applies `/skill debugging-and-error-recovery`:

1. Denoise `test_output` to find the real traceback
2. Fix only the **root cause** with a minimal change; stay in scope
3. Re-run `verify`

**Budget:** Up to `max_healing_attempts` retries (default 3, per ticket in `metadata.json`). Both verify failures AND review rejections count against this budget. If still failing after exhausting retries → Fail Path.

### Step 5 — Review (Agent, after verify passes)

The agent runs review personas from `<SKILL>/_shared/agents/` against the `git diff` in the worktree.

**Approval is unanimous** — any Critical or Important finding blocks release.

**Static personas (always run — 3 people):**

1. **code-reviewer** — evaluates correctness, readability, architecture, security, performance. Output: APPROVE or REQUEST CHANGES (findings categorized as Critical / Important / Suggestion). Critical or Important = REJECT.

2. **security-auditor** — identifies exploitable vulnerabilities. Maps findings to OWASP Top 10 and OWASP LLM Top 10. Severity: Critical / High / Medium / Low / Info. Critical or High = REJECT.

3. **test-engineer** — analyzes test strategy, coverage, pyramid level, test quality. Output: Gaps identified, recommended tests by priority.

**Dynamic UI/UX personas (only if `ui_capture: true` — 2 additional people):**

4. **evidence-collector** — screenshot-obsessed QA. Gets `screenshot_dir` to inspect rendered screens. Uses Playwright output, before/after interaction screenshots. Requires visual proof for every claim. Default assumption: 3–5 issues minimum on first implementation. Automatic fail triggers: zero-issues claims, perfect scores.

5. **reality-checker** — integration and deployment readiness. Gets `screenshot_dir` to cross-validate QA findings. Defaults to "NEEDS WORK" unless overwhelming evidence supports READY. Checks end-to-end user journeys, spec compliance, performance (>3s load = fail).

**If any reviewer rejects:** Findings are fed back to the agent for a fix → re-verify → re-review (still within healing budget).

### Step 6 — Ship Living Docs (Agent, after unanimous approval)

Before finishing, the agent syncs living documentation **inside the worktree**:

- Update `docs/prd/` with changed business logic
- Update `docs/tech/project-structure.md` for new/moved files
- Append concise entry to `docs/tech/changelog.md`

Style: second person, present tense, active voice, one concept per section, no broken code examples.

### Step 7 — Finish (CLI)

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> finish <ticket_id> --message "<conventional commit>"
```

**The CLI:**
- Stages all changes excluding generated noise (`__pycache__`, `*.pyc`, `node_modules`, etc.)
- Commits with the provided message (or template fallback)
- Moves `in_progress/<ticket_id>` to `done/<ticket_id>`
- Removes the worktree with `git worktree remove --force`

**Output JSON:**
```json
{
  "ticket_id": "ticket_001",
  "state": "done",
  "committed": true,
  "commit": "abc1234deadbeef..."
}
```

**Pushing is your call.** The agent tells you "branch `dev/<ticket_id>` is ready to push; decide whether to push to origin."

### Fail Path — Budget Exhausted

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> fail <ticket_id> --report "<summary>"
```

**The CLI:**
- Moves `in_progress/<ticket_id>` to `failed/<ticket_id>`
- Writes the report to `failed/<ticket_id>/healing_report.md`
- Removes the worktree

The ticket and report travel to `failed/` for manual human intervention.

---

## Guardrail CLI — All Subcommands

All commands require `--config <toml>`. All output is JSON to stdout.

### `status`

**Output:** Lists all ticket names in each pipeline stage.

```json
{
  "pending": ["ticket_a", "ticket_b"],
  "in_progress": ["ticket_c"],
  "done": ["ticket_d", "ticket_e"],
  "failed": []
}
```

Exit 0 always.

### `pick`

**Behavior:** Picks oldest pending ticket or resumes in_progress. Creates worktree on `dev/<ticket_id>`.

**Output:** Full ticket metadata (see Step 1).

Exit 0 always.

### `verify <ticket_id>`

**Input:** Ticket ID (positional arg).

**Behavior:** Runs two hard gates: tests, UI screenshot (if applicable).

**Output:** Success or failure with specific reasons.

Exit 0 if OK, exit 1 if any gate fails.

### `finish <ticket_id> --message "<msg>"`

**Input:** Ticket ID, optional `--message`.

**Behavior:** Stages (excluding noise), commits, archives to `done/`, removes worktree. When `--message` is omitted, the fallback message is `<prefix>(<module>): <title> [<id>]`, where `<prefix>` is `fix` for `ticket_type: "fix"` and `feat` otherwise.

**Output:** Commit SHA and final state.

Exit 0 on success.

### `fail <ticket_id> --report "<text>"`

**Input:** Ticket ID, optional `--report`.

**Behavior:** Archives to `failed/`, writes healing_report.md, removes worktree.

**Output:** Path to report.

Exit 0 on success.

---

## Worktree Isolation

Each ticket executes in its own **isolated `git worktree`** — a full independent checkout on a separate branch, at a separate path.

**Branch naming:** `dev/<ticket_id>` (e.g., `dev/ticket_001`).

**Lifecycle:**

1. On first `pick`: `git worktree add -b dev/<ticket_id> <path>` (creates branch and attaches worktree)
2. On resume: `git reset --hard HEAD` to scrub any dirty state
3. On `finish` or `fail`: `git worktree remove --force <path>` (best-effort cleanup; `git worktree prune` reconciles refs on next run)

**Worktree root location:** `<worktree_root>/<ticket_id>` (default: `~/codoop_tickets/worktrees/ticket_001`). Set via `codoop_flow.toml`.

---

## Self-Heal Mechanism

**Trigger:** `verify` returns `ok: false` OR a review persona rejects.

**Budget:** `max_healing_attempts` retries (default 3, set per ticket in `metadata.json`).

**Process per attempt:**
1. Denoise `test_output` to root cause
2. Fix the root cause (not symptoms), minimal change, stay in scope
3. Re-run `verify`
4. If still failing, retry (if budget remains)

**Budget exhausted:** Call `fail` with denoised summary. Ticket moves to `failed/`.

---

## Review Personas

### Static Group (always runs)

**1. code-reviewer** (`_shared/agents/code-reviewer.md`)
- Checks: Correctness (logic, specs), Readability (naming, structure), Architecture (patterns, abstraction), Security (no obvious vulns), Performance (efficient algorithms)
- Verdict: APPROVE or REQUEST CHANGES
- Blocking: Critical (must fix) and Important (should fix)
- Non-blocking: Suggestion

**2. security-auditor** (`_shared/agents/security-auditor.md`)
- Checks: Input Handling, Auth/Authz, Data Protection, Infrastructure, Third-Party Integrations, AI/LLM Features
- Maps to: OWASP Top 10 and OWASP LLM Top 10
- Severity: Critical / High / Medium / Low / Info
- Blocking: Critical and High

**3. test-engineer** (`_shared/agents/test-engineer.md`)
- Checks: Test pyramid (unit/integration/E2E), behavior vs. implementation, test quality, coverage gaps
- Output: Coverage analysis and recommended tests by priority

### Dynamic UI/UX Group (when `ui_capture: true`)

**4. evidence-collector** (`_shared/agents/testing-evidence-collector.md`)
- Gets `screenshot_dir` to inspect rendered screens
- Runs Playwright capture, reviews `test-results.json`
- Requires visual proof for every claim; no fantasy approvals
- Default assumption: 3–5+ issues on first implementation

**5. reality-checker** (`_shared/agents/testing-reality-checker.md`)
- Gets `screenshot_dir` to cross-validate QA findings
- End-to-end journey analysis, cross-device consistency, performance checks (>3s load = fail)
- Default status: NEEDS WORK; only READY with overwhelming evidence

**Unanimous approval required:** ALL active personas must APPROVE / PASS. Any Critical/Important from any persona = REJECT.

---

## UI Capture Mode

**Triggered by:** `"ui_capture": true` in `metadata.json`.

**What it requires:**
- Test script must write screenshots to the path given by `$CODOOP_QA_SCREENSHOT_DIR` env var (injected automatically)
- At least one file with extension `.png`, `.jpg`, `.jpeg`, `.webp`, or `.gif` must exist after tests run
- Absence of screenshots = verify fails

**Extra personas:** evidence-collector and reality-checker (the dynamic UI/UX group).

**Screenshot archival:** Screenshots travel with the ticket to `done/` or `failed/` for human inspection.

---

## Configuration

### `codoop_flow.toml`

| Field | Type | Required | Default | Meaning |
|---|---|---|---|---|
| `target_repo` | string (path) | Yes | — | Absolute path to target git repo. Expanded via `expanduser().resolve()`. |
| `worktree_root` | string (path) | No | `~/codoop_tickets/worktrees` | Directory where per-ticket worktrees are created. Expanded via `expanduser()`. |

The ticket pipeline directories (`pending/`, `in_progress/`, `done/`, `failed/`) are derived from `<target_repo>/docs/tickets/`. They are created by `codoop setup` but never configured in the TOML.

### `metadata.json` (Loop 3 consumption)

| Field | Type | Required | Default | Meaning |
|---|---|---|---|---|
| `ticket_id` | string | Yes | — | Unique identifier; matches directory name and branch name `dev/<ticket_id>` |
| `title` | string | Yes | — | Human-readable title; used in fallback commit message |
| `ticket_type` | string | No | `"feature"` | `"feature"` or `"fix"`; selects the fallback commit prefix (`feat`/`fix`) |
| `modules` | list[string] | Yes | — | Modules this ticket touches: `backend`, `web`, `mobile`, `desktop` |
| `test_command` | dict[str, str] | Yes | — | Shell command per module; must cover all modules; all must exit 0 |
| `coding_engine` | string or null | No | null | Informational; which AI tool handles this ticket |
| `max_healing_attempts` | int | No | 3 | Max self-heal retries; agent counts (CLI does not enforce) |
| `ui_capture` | bool | No | false | If true: activates screenshot gate; injects `CODOOP_QA_SCREENSHOT_DIR`; adds UI personas |

---

## Integration

### Inputs (reading from Loop 2)

Loop 3 picks a ticket from `docs/tickets/pending/<ticket_id>/` and consumes:

- `metadata.json` — drives all scheduler decisions
- `module_prd.md` + `spec.md` — progressively disclosed to the agent at startup
- `plan.md` + `todo.md` — agent reads and checks off items as completed
- `public/qa-screenshots/` — (for UI tickets) created at runtime; read by review personas

### Outputs (after finish)

**On success (finish):**
- Committed on branch `dev/<ticket_id>`: all changes + living doc updates + conventional commit message
- Archived to `done/<ticket_id>/`: full ticket directory + `public/qa-screenshots/` (if UI ticket)
- Commit SHA returned; branch ready for push (human decides whether to push)

**On failure (fail):**
- Nothing committed; worktree discarded
- Archived to `failed/<ticket_id>/`: full ticket directory + newly written `healing_report.md` with denoised failure summary

---

## What Gets Committed and Archived

### On `finish`

**Committed to `dev/<ticket_id>` branch:**
- All staged changes in the worktree (excluding generated noise)
- Living doc updates (`docs/prd/`, `docs/tech/`)
- Commit message: Conventional Commit format (type: scope: subject, optional body)

**Archived to `done/<ticket_id>/`:**
- The entire ticket directory: `metadata.json`, `module_prd.md`, `spec.md`, `plan.md`, `todo.md` (all checkboxes ticked), and for UI tickets, `public/qa-screenshots/` with all visual evidence

### On `fail`

**Not committed:** No code commit runs.

**Archived to `failed/<ticket_id>/`:**
- The ticket directory as-is
- Newly written `healing_report.md` with denoised failure summary from the agent

---

## Skeleton Tests

The project includes `tests/test_skeleton.py` which exercises only the deterministic guardrails (no AI, no mocking). Each test gets a fresh temporary git repo and worktrees directory.

Key tests:
- `test_pick_moves_and_creates_worktree` — pick moves ticket from pending to in_progress and creates worktree
- `test_verify_fails_on_failing_tests` — test command non-zero exit fails verify
- `test_ui_capture_gate` — UI ticket without screenshots fails; with screenshots passes
- `test_finish_commits_and_archives` — finish commits on `dev/<id>`, archives to done/, removes worktree
- `test_ticket_lifecycle` — Human-Centric path: init → fill → validate → promote

Run with: `python tests/test_skeleton.py` (no pytest needed).

---

## Key Design Principles

- **Determinism Over Cleverness** — The CLI is small, fully deterministic, never guesses. The agent owns all intelligence.
- **Two Hard Gates in Sequence** — tests → UI screenshot (if applicable). All must pass before review.
- **Unanimous Approval** — Review is only done when all personas agree. Any Critical/Important blocks.
- **Self-Heal Within Budget** — Failures trigger retry (if budget permits), not immediate failure. Budget exhaustion moves to failed/ for human intervention.
- **Isolated Worktrees** — Each ticket gets its own branch and checkout path; main repo is never touched.
- **Living Docs Kept in Sync** — After code ships, living docs (`docs/prd/`, `docs/tech/`) are updated so they remain authoritative.

