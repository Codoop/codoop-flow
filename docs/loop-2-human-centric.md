# Loop 2: Human-Centric (Ticket Design)

## Overview

**Loop 2** is the second of three nested loops in codoop-flow's Triple-Loop Model. It is a structured, human-driven process for designing deterministic, machine-readable work tickets that an AI coding agent can execute reliably.

**What it solves:** AI coding agents fail or produce unusable output when given vague or incomplete requirements. Loop 2 provides a forcing function for the human (or product manager) to produce a precise "ticket package" with such fidelity that an autonomous coding engine (Loop 3) can execute it without ambiguity. The loop prevents scope creep, assumption-driven implementation, and unverifiable output.

**Position in pipeline:** Reads Loop 1 outputs from `docs/backlog/` → produces ticket packages in `docs/tickets/drafts/` → promotes to `docs/tickets/pending/` for Loop 3 to pick up.

---

## Ticket Types

Every ticket carries a `ticket_type` in `metadata.json` (default `feature`). The type selects which documents are required, so the flow fits the work:

| Type | For | Required docs | Recommended docs |
|---|---|---|---|
| `feature` (需求单) | A new capability driven by a business need | `module_prd.md` + `spec.md` | `plan.md`, `todo.md` |
| `fix` (修复单) | Repairing an existing bug/defect | `bug_report.md` | `plan.md`, `todo.md` |

`feature` runs the full three-phase flow below. `fix` is lighter: it skips the PRD and Spec phases and instead captures the defect in `bug_report.md` (Symptom / Reproduction / Root Cause / Expected Behavior / Scope), then proceeds to task breakdown, metadata inference, validate, and promote. A fix may voluntarily add a `spec.md` if it touches a contract/data-model change, but it is not required.

`codoop-ticket` infers the type from your description and **always asks you to confirm** before scaffolding — the type is a routing switch, so a wrong guess would force rework. Via CLI, pass it explicitly with `--type feature|fix`.

---

## Quick Start

In any AI coding tool, say:

```
/skill codoop-ticket I want to design an e-commerce product search feature with keyword, category, and price range filtering.
```

The skill orchestrates a PM and Architect with you as director, guiding you through three phases (PRD → Spec → Tasks) and producing a complete ticket package ready for Loop 3.

---

## Workflow

### Phase 1 — Requirement Design (module_prd.md)

1. **clarify** — `codoop-ticket` asks clarifying questions about scope, user intent, and acceptance criteria
2. **context** — reads Loop 1 outputs from `docs/backlog/product/`, `docs/backlog/interface/`, `docs/backlog/architecture/`, `docs/backlog/modules/` to anchor the ticket in existing product strategy
3. **draft** — PM agent writes `module_prd.md` with business overview, user stories, state diagrams, acceptance criteria
4. **review** — you review and confirm "this PRD is good, move to spec phase"

**Hard constraint:** `module_prd.md` is 100% pure business language. No database tables, no API fields, no code details.

### Phase 2 — Technical Spec (spec.md)

1. **trigger** — you confirm Phase 1 is done; `codoop-ticket` loads `/skill spec-driven-development`
2. **design** — Architect agent writes `spec.md` based on the confirmed `module_prd.md`
3. **content** — includes API contracts (per platform: backend/web/mobile/desktop), data schema field-level, UI interactions and state management, code examples, testing strategy, Always/Ask First/Never boundaries
4. **review** — you review and confirm or request changes

### Phase 3 — Task Breakdown (plan.md + todo.md)

1. **trigger** — you confirm Phase 2 is done; `codoop-ticket` loads `/skill planning-and-task-breakdown`
2. **decompose** — spec is decomposed into two files:
   - `plan.md` — phased implementation plan with explicit dependencies, architecture decisions, and checkpoints
   - `todo.md` — atomic checkbox task list (`- [ ]`), each task ≤100 lines, each touching ≤5 files, with platform prefixes (`[backend]`, `[web]`, etc.)
3. **reference** — skill prompts you to review `/skill definition-of-done` so task acceptance criteria are aligned with project-wide completion standards
4. **review** — you review and confirm

### Post-Phase 3 — Metadata Auto-Inference

After Phase 3, `codoop-ticket` calls `update_metadata_from_docs` to automatically infer `metadata.json` from your `spec.md` and task files. It also checks whether the confirmed spec changes user-visible screens, interactions, or task flows. If it does, it asks in plain language whether delivery should inspect the actual experience with saved screenshots and UI/UX review; it recommends enabling that check. Backend-only, infrastructure, refactoring, and internal-only work keep it off without an unnecessary question. The human reviews the result and confirms or modifies before validation.

### Validation & Promotion

1. **validate** — `codoop ticket validate <ticket_id>` ensures all required fields are present and filled meaningfully
2. **promote** — `codoop ticket promote <ticket_id>` moves the ticket from `drafts/<ticket_id>/` to `pending/<ticket_id>/`, waking Loop 3's scheduler

---

## Outputs

Every ticket is a directory at one of these pipeline stages:

```
docs/tickets/
  drafts/<ticket_id>/              ← being designed (human-facing)
  pending/<ticket_id>/             ← design complete, awaiting Loop 3
  in_progress/<ticket_id>/         ← Loop 3 is executing
  done/<ticket_id>/                ← shipped and archived
  failed/<ticket_id>/              ← self-healing exhausted; needs human intervention
```

**Files inside each ticket directory:**

| File | Author | Required | Purpose |
|---|---|---|---|
| `metadata.json` | Auto-inferred; human confirms | Yes | Machine-readable config for Loop 3: ticket type, modules, test commands, self-heal budget, UI capture flag |
| `module_prd.md` | PM agent + human | Yes for `feature` | 100% pure-business description — user stories, state flows, acceptance criteria |
| `spec.md` | Architect agent + human | Yes for `feature` | Technical contract — APIs, data schema, UI interactions |
| `bug_report.md` | Human (+ agent) | Yes for `fix` | Defect record — Symptom / Reproduction / Root Cause / Expected Behavior / Scope |
| `plan.md` | Auto-decomposed + human review | Recommended (both) | Step-by-step implementation plan with phases and checkpoints |
| `todo.md` | Auto-decomposed + human review | Recommended (both) | Atomic checkbox task list, each ≤100 lines, with platform prefixes |

---

## Skills Involved

| Skill | Role |
|---|---|
| **codoop-ticket** | Main orchestrator. Guides you through all three phases and calls sub-skills. |
| **spec-driven-development** | Phase 2 (spec design). Can also be invoked standalone. |
| **planning-and-task-breakdown** | Phase 3 (task breakdown). Can also be invoked standalone. |
| **definition-of-done** | Reference tool. Not called as an action-producer, but reviewed during Phase 3 to inform acceptance criteria. |

### Standalone Usage

**spec-driven-development** can be invoked directly when you have a requirement but no spec:

```
/skill spec-driven-development Based on this PRD, design the technical spec.
```

**planning-and-task-breakdown** can be invoked directly when you have a spec but need to break it into tasks:

```
/skill planning-and-task-breakdown Based on this spec, break it into implementation tasks.
```

Both work identically in standalone mode as they do when called by `codoop-ticket`, except the output paths differ (standalone skills use `tasks/`, integrated skills use the ticket directory).

**definition-of-done** is referenced (not called) during Phase 3. You read the reference and apply its five-dimension checklist (Correctness, Quality, Integration, Documentation, Ship-readiness) when writing acceptance criteria in `todo.md`.

---

## CLI Reference

Loop 2 has an independent CLI tool `codoop-ticket.py` that is completely independent of Loop 3's `codoop-execute`.

All commands can be invoked via:

```bash
python skills/codoop-ticket/scripts/codoop-ticket.py ticket <command> <args>
```

Or directly call the skill in any AI coding tool:

```
/skill codoop-ticket Design a work ticket for this feature
```

### `codoop-ticket ticket init <ticket_id> --config <toml> [--title "..."] [--language auto|zh|en] [--type feature|fix]`

**Creates** `docs/tickets/drafts/<ticket_id>/` with:
- `metadata.json` stub (placeholder values, including `ticket_type`)
- Scaffold docs per type: `feature` → `module_prd.md`, `spec.md`, `plan.md`, `todo.md`; `fix` → `bug_report.md`, `plan.md`, `todo.md`

**Args:**
- `--title` — ticket title (detected for language if `--language auto`)
- `--language` — `auto` (default, detects CJK → `zh`, otherwise `en`), or explicit `zh` / `en`
- `--type` — `feature` (default) or `fix`; selects the scaffold and the required-docs rule
- `--config` — path to `codoop_flow.toml`

**Exit codes:** 0 on success, raises `FileExistsError` if draft already exists.

### `codoop-ticket ticket validate <ticket_id> --config <toml>`

**Validates** a draft is ready to promote.

**Checks (blocking):**
- `metadata.json` parses cleanly and satisfies the full schema (all required fields present, correct types, every module has a test command, valid `ticket_type`)
- The type's required docs exist and contain meaningful (non-scaffold, non-empty) content: `feature` → `module_prd.md` + `spec.md`; `fix` → `bug_report.md`

**Checks (advisory warnings):**
- `plan.md` and `todo.md` exist and are meaningfully filled

**Exit codes:** 0 on success, 1 on any blocking error.

### `codoop-ticket ticket update-metadata <ticket_id> --config <toml>`

**Auto-infers** `metadata.json` from the current `spec.md` (and optionally `plan.md`/`todo.md`), writes the result back to disk, and prints it for human review.

**Inference logic:**
- `modules` — scanned from `spec.md` headers (`## Backend`, `## Web`, etc.) mapped to: backend, web, mobile, desktop
- `test_command` — preserved as provided; define one command for every listed module before validation (no default is inferred)

Typically called after Phase 3 is complete, before validating and promoting.

### `codoop-ticket ticket promote <ticket_id> --config <toml>`

**Promotes** a draft to pending (ready for Loop 3 pickup).

**Internally:**
- Calls `validate` first; fails if any error
- Shows the ticket summary (id / title / modules) and asks for interactive confirmation (`--force` skips the prompt)
- Moves `docs/tickets/drafts/<ticket_id>/` to `docs/tickets/pending/<ticket_id>/` using `shutil.move`
- Refuses to clobber existing pending tickets

**Human approval is required.** `pending/` is Loop 3's pickup queue — an unreviewed promote means an agent may start building from an unapproved design. When `codoop-ticket` (the skill) drives the flow, it must ask the user to confirm before promoting and must not use `--force` without prior approval.

**Output:** Path to destination and message that `codoop_tools.py pick` will pick it up next.

**Exit codes:** 0 on success, 1 on validation failure, cancelled confirmation, or move failure.

---

## Configuration

### `codoop_flow.toml`

Only one field matters for Loop 2:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `target_repo` | string (path) | Yes | Path to your target git repo. Loop 2 writes ticket directories under `<target_repo>/docs/tickets/`. |

### `metadata.json` Schema

Every ticket's `metadata.json` must satisfy this schema:

**Required fields:**

| Field | Type | Meaning |
|---|---|---|
| `ticket_id` | string | Identifier matching the directory name (e.g., `ticket_001`) |
| `title` | string | Human-readable ticket title |
| `modules` | list[string] | Which platform modules this ticket touches: `backend`, `web`, `mobile`, `desktop` |
| `test_command` | dict[string, string] | Shell command to run tests per module (keys must cover all `modules` entries) |

**Optional fields:**

| Field | Type | Default | Meaning |
|---|---|---|---|
| `ticket_type` | string | `"feature"` | `"feature"` (需求单) or `"fix"` (修复单). Selects required docs in Loop 2 and the commit prefix (`feat`/`fix`) in Loop 3 |
| `coding_engine` | string or null | null | Which AI tool for this ticket: `claude`, `codex`, `cursor`. If absent, uses global default. |
| `max_healing_attempts` | int | 3 | Maximum self-healing retries in Loop 3 before moving to `failed/` |
| `ui_capture` | bool | false | If true, Loop 3's test script writes screenshots; review adds UI/UX personas |

**Validation:** All required fields must be present with correct types; every module in `modules` must have a corresponding entry in `test_command`. Missing any of these is a blocking validation error.

---

## Integration

### Inputs (reading from Loop 1)

During Phase 1 (requirement design), `codoop-ticket` proactively reads Loop 1's backlog outputs:

- `docs/backlog/product/` — requirements.md, user-journey.md, monetization-plan.md
- `docs/backlog/interface/` — design-system.md (visual-design source of truth)
- `docs/backlog/architecture/` — architecture.md, database-schema.sql, openapi.yaml
- `docs/backlog/modules/` — per-module detailed designs

This anchors every ticket to the global product strategy rather than inventing in isolation.

### Outputs (feeding Loop 3)

The `promote` command's filesystem move (`drafts/` → `pending/`) is the only handoff mechanism. Loop 3's scheduler polls `pending/`, picks the oldest ticket, and consumes:

- `metadata.json` — drives all scheduler decisions (modules, test commands, self-heal budget, ui_capture flag)
- `module_prd.md` + `spec.md` — progressively disclosed to the coding engine at startup
- `plan.md` + `todo.md` — Loop 3 reads the todo list step-by-step and checks off items as they complete
- `public/qa-screenshots/` — created at runtime by Loop 3's test scripts (for UI tickets)

The ticket directory travels with the ticket through all stages: `pending/` → `in_progress/` → `done/` (or `failed/`), preserving the full design record alongside implementation artifacts.

---

## Definition of Done

Loop 2 introduces the human to the project-wide **Definition of Done (DoD)** — a fixed five-dimension checklist that every task must satisfy before being considered complete:

1. **Correctness** — acceptance criteria met, runtime-verified, tests prove the change, no regressions, edge cases handled
2. **Quality** — intent-clear naming, no duplicated logic, no dead code, no unrelated refactors, linting passes
3. **Integration** — works with the full system, migrations and config handled, backward compatibility considered
4. **Documentation** — public interfaces documented, architectural decisions recorded, timeless language
5. **Ship-readiness** — security reviewed, observability in place, rollback path exists, human approval completed

**Key distinction from acceptance criteria:** Acceptance criteria in `todo.md` answer "did we build this correctly?" and vary per task. DoD answers "can we confidently ship this?" and is fixed across all tasks and tickets.

During Phase 3, you are encouraged to reference `/skill definition-of-done` so task acceptance criteria are strong enough to satisfy the project-wide standard.

---

## Standalone Skill Usage

### Using spec-driven-development independently

```
/skill spec-driven-development I have this PRD, design the technical spec.
```

The skill guides you through four phases (Specify → Plan → Tasks → Implement), producing `tasks/spec.md`, `tasks/plan.md`, `tasks/todo.md` for standalone use. All six core spec areas are covered: Objective, Commands, Project Structure, Code Style, Testing Strategy, Boundaries.

### Using planning-and-task-breakdown independently

```
/skill planning-and-task-breakdown I have this spec, break it into implementable tasks.
```

The skill reads the spec, builds a dependency graph, slices vertically (feature-by-feature), writes tasks with acceptance criteria + verification + dependency + file list + size estimate, and saves to `tasks/plan.md` and `tasks/todo.md`. It enforces the rule: no code is written during planning.

---

## Key Design Principles

- **Deterministic Input for Deterministic Output** — High fidelity requirements enable Loop 3 to execute reliably without guessing.
- **Three-Phase Human Collaboration** — Phase 1 (PRD) → Phase 2 (Spec) → Phase 3 (Tasks), with explicit human confirmation between each phase.
- **Type-Fit Flow** — `feature` tickets run the full PRD → Spec → Tasks flow; `fix` tickets use a lighter `bug_report.md` flow. The type is confirmed with the human up front, never silently guessed.
- **Metadata Auto-Inference** — Loop 2 automatically infers `metadata.json` from spec content, saving humans from manual, error-prone configuration.
- **Dual-Mode Sub-Skills** — spec-driven-development and planning-and-task-breakdown work both standalone and as integrated phases of codoop-ticket.
- **No Code Written** — Loop 2 is pure documentation. Code is written only in Loop 3.
