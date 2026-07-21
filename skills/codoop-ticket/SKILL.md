---
name: codoop-ticket
description: Design work tickets (PRD → Spec → Plan) in three stages. Describe features in natural language; codoop-ticket orchestrates PM and Architect agents, calls spec and planning skills, and auto-infers metadata. Its terminal responsibility is promoting an approved ticket to pending/; it never executes the ticket.
---

# Codoop-Ticket — Ticket Design Orchestration

Help users systematically design work tickets in-session through three stages: requirements, technical specs, and task breakdown.

## Scope Boundary

This skill ends after an explicitly approved ticket is validated, committed, and
promoted to `pending/`. Do not implement, run, verify, review, or ship the
ticket; do not invoke `codoop-execute` or otherwise consume the pending queue.
Those are Phase 3 responsibilities and require a separate user request.

## What is a Ticket?

A ticket is a complete design document package for one feature module:

| File | Purpose | Author |
|------|---------|--------|
| `module_prd.md` | Business requirements (pure business language, no tech) | PM agent |
| `spec.md` | Technical specification (APIs, DB, implementation details) | Architect agent |
| `preview.html` | Static, reviewable preview of a user-visible feature | Ticket agent, when required |
| `plan.md` | Implementation plan (steps) | Auto-inferred |
| `todo.md` | Atomic task list (≤100 lines code/task) | Auto-inferred |
| `metadata.json` | Ticket metadata (modules, test commands) | Auto-inferred |

The table above shows a **feature** ticket (需求单). A **fix** ticket (修复单) is
lighter — see "Ticket Types" below.

## Ticket Types

Every ticket has a `ticket_type` (stored in `metadata.json`, default `feature`):

| Type | For | Required docs | Skips |
|------|-----|---------------|-------|
| `feature` (需求单) | New capability from a business need | `module_prd.md` + `spec.md` | — |
| `fix` (修复单) | Repairing an existing bug/defect | `bug_report.md` | PRD + Spec stages |

`plan.md` + `todo.md` are recommended (not blocking) for **both** types.

**Inferring the type — always confirm.** At the start, infer the type from the
user's description (signals like "fix / bug / 报错 / 异常 / 坏了 / 回归 / 修复" →
`fix`; otherwise `feature`), then **state your inference and ask the user to
confirm** before scaffolding. Do not silently pick — `ticket_type` is a routing
switch (it decides which docs are required and which flow runs), so a wrong
guess forces rework. The user can correct it in one word.

Example:

```
User: 搜索结果分页有时候会越界报错，帮我处理一下
codoop-ticket: 这看起来是「修复单 (fix)」——已存在的 bug，我会用 bug_report.md
              轻量流程（跳过 PRD/Spec）。确认吗？还是当作需求单 (feature)？
User: 对，修 bug
codoop-ticket: 好，创建 fix 类型草稿…
```

When initializing via CLI, pass the type explicitly:
`codoop-ticket.py ticket init <id> --type fix --config <toml>` (no inference —
the user already specified it).

## When to Use

- ✅ Design a complete ticket from business requirements
- ✅ Phase 1 has produced product and design specs; now design incremental feature tickets
- ✅ Need human review and feedback at each stage

## Implementation Notes

This skill uses shared modules from `_shared/codoop_lib_v1/` (which are also used by `codoop-execute`). The CLI automatically imports these from the parent `_shared/` directory, so you can invoke both `codoop-ticket.py` (Loop 2) and `codoop_tools.py` (Loop 3) without worrying about module location — they share the same library code.

## Three Stages of Ticket Design

> **Applies to `feature` tickets.** For a `fix` ticket, skip Phase 1 (PRD) and
> Phase 2 (Spec): scaffold `bug_report.md` and guide the user to fill in
> Symptom / Reproduction / Root Cause / Expected Behavior / Scope, then go
> straight to task breakdown (`plan.md` + `todo.md`), metadata inference,
> validate, and promote. A fix may still add a `spec.md` voluntarily if it
> touches a contract/data-model change, but it is not required.

### 【Phase 1】Requirement Design (module_prd.md)

**Goal**: Understand business requirements and define feature boundaries.

**Process**:
1. Describe what feature you want to build (natural language)
2. codoop-ticket discusses requirements, boundaries, dependencies with you
3. codoop-ticket reads Phase 1 outputs from `docs/backlog/` (product specs, design specs, architecture)
4. PM agent writes `module_prd.md` based on discussion and Phase 1 context
5. You review, provide feedback, modify until satisfied

**Example**:
```
User: Design an e-commerce product search feature
       - Need keyword, category, and price range filtering
       - Should integrate with existing product catalog

codoop-ticket: Clarifying questions
       - Search scope: product name, description, SKU?
       - Filter logic: OR or AND combination?
       - Result sorting: relevance or sales?
       
Reading Phase 1:
       - docs/backlog/product/commerce-strategy.md
       - docs/backlog/interface/search-ux.md
       
PM agent output:
       ✅ module_prd.md: business needs, user stories, acceptance criteria
```

### User-Facing Clarification Policy

**Keep asking; change the language, not the rigor.** In codoop-ticket
conversations, the user decides product outcomes, while the agent owns routine
implementation choices. These rules also apply when this skill invokes
`spec-driven-development` or `planning-and-task-breakdown`.

| Decision | How to handle it |
|----------|------------------|
| User goal, business rule, scope, priority, or acceptance experience | Ask the user in plain language. |
| Privacy, compliance, payment/cost, destructive or irreversible behavior | Explain the user-facing consequence and ask explicitly. |
| API shape, database/index choice, framework pattern, state management, or test layout | Inspect existing project conventions, choose a sound approach, and record it in `spec.md`; do not ask by default. |
| A technical choice that materially changes user experience, delivery scope, cost, or a global architecture contract | Ask about that consequence in plain language; keep the implementation detail as supporting context only if useful. |

Before asking a question, first use the ticket context and existing codebase to
resolve what can be resolved. Do not turn an internal uncertainty into a user
question merely because there are several valid technical implementations.

**Question format.** Ask at most 1–3 high-value questions at a time. State the
user-visible situation, give 2–3 everyday-language choices, and recommend one
when appropriate. Avoid unexplained terms such as API, schema, JWT, index,
AND/OR logic, or state management.

```text
Avoid: “Should the filters use AND or OR?”

Ask: “When someone chooses ‘running shoes’ and ‘under ¥300’, should the list
show only products that meet both conditions, or products that meet either one?
I recommend ‘both’, so the results feel more precise.”
```

The agent may translate the user's plain-language answer into formal user
stories, acceptance criteria, BDD, and technical constraints in the documents.
`module_prd.md` remains business-only; `spec.md` remains precise and technical.

**Review summaries.** At each phase gate, lead with a short plain-language
summary: what users can do, what is intentionally out of scope, and which
decision (if any) needs approval. Offer the detailed PRD, spec, or plan for
review rather than requiring the user to understand it before they can respond.
The existing explicit approvals for ticket type, phase progression, and
promotion remain mandatory.

### 【Phase 2】Technical Spec (spec.md)

**Goal**: Design the technical contract and ensure implementation alignment.

**Process**:
1. Load `/skill spec-driven-development`
2. Design `spec.md` based on `module_prd.md`:
   - API interface design (backend, web, mobile platforms)
   - Database fields and data models
   - UI interaction flows
3. Decide whether the feature creates or materially changes a user-visible screen, primary task flow, or interaction state. If it does, set `visual_preview: true` in `metadata.json` and generate `preview.html` before asking the user to review the phase. Otherwise leave it `false` and state that no visual preview is needed.
4. You review, provide feedback, modify until satisfied

#### Visual Preview (`preview.html`)

Generate this file only for a `feature` ticket with `visual_preview: true`. It is a single, self-contained HTML file for discussing the ticket's local UI change; it is not a production implementation or a full-product shell.

- Base its visual language on `docs/backlog/interface/design-system.md` when available. Do not invent a conflicting visual direction.
- Cover the new or changed local screen/area, one primary user path, and the states needed to understand it (for example: empty, loading, error, success, confirmation, or permission state).
- Make only the key interactions clickable with local mock data and client-side state. Do not call real APIs, require login, add dependencies, or reproduce unrelated product flows.
- Use clear placeholder content only where final content is unknown; do not leave the whole page as a wireframe or a static screenshot.
- Present the preview and ask for explicit feedback before Phase 3. Apply approved feedback to `module_prd.md` and `spec.md`, then regenerate the preview if the change affects it.

`visual_preview: true` makes `preview.html` a promotion requirement. It is independent from `ui_capture`, which checks screenshots of the real implementation after development.

**Example**:
```
spec.md includes:

## Backend API
- GET /api/products/search?q=...&category=...&price_min=...&price_max=...
- Response: { items: [...], total: N, page: 1 }

## Database
- Add columns to products table: search_vector (tsvector for full-text search)
- Add index: products_search_vector_idx

## Web UI
- SearchBar component: keyword input + filter sidebar
- ResultsList component: grid/list view toggle
- ResultItem component: product card with quick add-to-cart
```

### 【Phase 3】Task Breakdown (plan.md + todo.md)

**Goal**: Decompose into implementable, ordered atomic tasks.

**Process**:
1. Load `/skill planning-and-task-breakdown`
2. Break down tasks based on `spec.md`:
   - `plan.md`: implementation steps (Step 1, Step 2, etc.)
   - `todo.md`: atomic task list (each ≤100 lines code)
3. Reference `/skill definition-of-done` to understand completion standards
4. You review, provide feedback, modify until satisfied

**Example**:
```
plan.md:
- Step 1: Backend API implementation + database migration
- Step 2: Web frontend SearchBar and ResultsList components
- Step 3: Web filter logic and state management
- Step 4: Mobile platform adaptation

todo.md:
- [ ] Task 1: Create search API endpoint (backend)
- [ ] Task 2: Add database full-text search index
- [ ] Task 3: Implement SearchBar React component
- ...（each task has acceptance criteria and verification steps）
```

### 【Auto Metadata Inference】Update metadata.json

**Process**:
1. Automatically infer from `spec.md`:
   - `modules`: extract from spec headers (## Backend → backend, ## Web → web)
   - `test_command`: preserve the user-defined commands; require one explicit command per module before validation
2. Inspect the confirmed spec for new or changed user-visible screens,
   interactions, or task flows:
   - Keep `visual_preview: true` only when the Phase 2 preview was required
     and reviewed; otherwise keep it `false`. Never enable it for a pure
     backend, infrastructure, refactoring, or non-visual configuration ticket.
   - If present, explain in plain language that the delivery can also check the
     actual screens and interactions, save screenshots, and have UI/UX reviewers
     inspect them. Recommend enabling it and ask the user to confirm.
   - If the work is backend-only, infrastructure, refactoring, or otherwise has
     no user-visible behavior, keep it off and state that no screenshot check is
     needed.
3. Set `ui_capture` from that decision, then show the complete inferred
   `metadata.json`; the user confirms or modifies it.

Ask about the outcome, not the field name. For example:

```text
This change affects what people see and click. Should delivery also check the
actual screens and interactions? If enabled, the test run saves screenshots and
UI/UX reviewers inspect them, which can catch layout and flow problems. I
recommend enabling it. Confirm?
```

**Example**:
```json
{
  "ticket_id": "ticket_001",
  "title": "E-commerce Product Search Feature",
  "modules": ["backend", "web", "mobile"],
  "test_command": {
    "backend": "npm run test -- backend",
    "web": "npm run test -- web",
    "mobile": "flutter test"
  },
  "max_healing_attempts": 3,
  "visual_preview": true,
  "ui_capture": true
}
```

`ui_capture: true` requires the target project's test script to write
screenshots to `$CODOOP_QA_SCREENSHOT_DIR`; no screenshots is a verification
failure. Use `false` when no user-visible behavior needs checking.

### 【Finalize】Validate & Release

**Process**:
1. Call `tickets_cli validate` to verify ticket completeness
2. Show the ticket summary (id / title / modules) and **ask the
   user to confirm** promotion
3. Only after explicit approval, run `codoop-ticket.py ticket promote` to move
   the ticket to `pending/` and create a dedicated `docs(ticket): add <ticket_id>`
   commit. The command stages and commits only that ticket directory; it must
   not include other working-tree changes.
4. Ticket complete: stop after the commit and `pending/` promotion. Do not
   start Phase 3 development or invoke `codoop-execute`.

**Promote requires explicit user approval.** Never promote a draft to
`pending/` without the user confirming in the current conversation. Do not
pass `--force` (or pipe `yes` into the prompt) unless the user has already
approved — `pending/` is the Loop 3 pickup queue, so an unreviewed promote
means an agent may start building from an unapproved design.

---

## How to Use

### Launch Ticket Design

Describe what you want to build in natural language:

```
/skill codoop-ticket
I want to design an e-commerce product search feature with keyword, category, and price range filtering that integrates with the existing catalog.
```

Or concisely:

```
/skill codoop-ticket
Design the e-commerce search feature for our platform.
```

### Phase Confirmation Flow

After each phase, you review and confirm:

```
User: This PRD looks good, move to spec phase
codoop-ticket: OK, loading spec-driven-development, starting technical spec...

（Spec design complete）

User: I need to change the API to use POST instead of GET...
codoop-ticket: Updated. Do you want to proceed?
User: Yes, move to task breakdown phase

...and so on
```

---

## Integration with Other Phases

### Integration with Phase 1 (Venture-Discovery)

codoop-ticket automatically reads Phase 1 outputs:

- `docs/backlog/product/` — product specifications
- `docs/backlog/interface/` — interface specifications
- `docs/backlog/architecture/` — architecture specifications
- `docs/backlog/modules/` — module breakdown

These serve as context to PM and Architect agents, ensuring tickets align with the global plan.

### Handoff to Phase 3 (Agent-Centric)

When the ticket is complete, Phase 3 receives via `metadata.json`:

- `modules`: which test suites to run?
- `test_command`: verification standards

The ticket is now available for Phase 3 to pick up in a separate execution
request; codoop-ticket must stop here.

---

## Design Guidance

### Agent Scope Instructions

When calling PM and Architect agents, codoop-ticket clarifies scope:

```
This is a ticket design phase for "<module_name>" PRD.
Focus on business requirements, user stories, acceptance criteria for this module.
If business model, GTM strategy, or cross-module impact surfaces, confirm with user.
```

```
This is ticket-scoped technical spec design, building on existing architecture.
Focus on "<module_name>" APIs, database changes, implementation details per platform.
If global architecture changes, performance overhauls, or scope expansion surfaces, confirm with user.
```

This lets agents intelligently flag "out of scope" decisions rather than guessing.

### Quick & Precise vs. Global Discovery

Ticket design differs from Phase 1 discovery:

- **Phase 1**: Global 0→1, requires consistency audit, multi-role debate, comprehensive specs
- **Phase 2**: Incremental module scope, needs speed & precision, just PM + Architect, module-focused

No need for global consistency checks at ticket level (Phase 1's job).

---

## Command-Line Interface (CLI)

### Standalone Usage

Loop 2 can be used independently via CLI without requiring codoop-flow:

```bash
# Initialize a new ticket draft (feature by default)
python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket init ticket_001 --config codoop_flow.toml --title "Add user search"

# Initialize a fix ticket (scaffolds bug_report.md instead of PRD + Spec)
python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket init ticket_002 --type fix --config codoop_flow.toml --title "Fix pagination overflow"

# Validate ticket completeness
python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket validate ticket_001 --config codoop_flow.toml

# Promote a confirmed ticket from drafts/ to pending/ and commit that ticket
python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket promote ticket_001 --config codoop_flow.toml

# Update metadata.json from docs
python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket update-metadata ticket_001 --config codoop_flow.toml
```

### Completely Independent

Loop 2 has no dependencies on Loop 3 (codoop-flow). 
Only requirement: a `codoop_flow.toml` pointing to the target project.

For setup, use: `python skills/codoop-execute/scripts/codoop.py setup <target-repo>`
