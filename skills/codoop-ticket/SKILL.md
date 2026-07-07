---
name: codoop-ticket
description: Design work tickets (PRD → Spec → Plan) in three stages. Describe features in natural language; codoop-ticket orchestrates PM and Architect agents, calls spec and planning skills, and auto-infers metadata. Outputs complete ticket package for Phase 3.
---

# Codoop-Ticket — Ticket Design Orchestration

Help users systematically design work tickets in-session through three stages: requirements, technical specs, and task breakdown.

## What is a Ticket?

A ticket is a complete design document package for one feature module:

| File | Purpose | Author |
|------|---------|--------|
| `module_prd.md` | Business requirements (pure business language, no tech) | PM agent |
| `spec.md` | Technical specification (APIs, DB, implementation details) | Architect agent |
| `plan.md` | Implementation plan (steps) | Auto-inferred |
| `todo.md` | Atomic task list (≤100 lines code/task) | Auto-inferred |
| `metadata.json` | Ticket metadata (modules, test commands, edit scope) | Auto-inferred |

## When to Use

- ✅ Design a complete ticket from business requirements
- ✅ Phase 1 has produced product and design specs; now design incremental feature tickets
- ✅ Need human review and feedback at each stage

## Three Stages of Ticket Design

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

### 【Phase 2】Technical Spec (spec.md)

**Goal**: Design the technical contract and ensure implementation alignment.

**Process**:
1. Load `/skill spec-driven-development`
2. Design `spec.md` based on `module_prd.md`:
   - API interface design (backend, web, mobile platforms)
   - Database fields and data models
   - UI interaction flows
   - Editable files whitelist (`files_to_edit`)
3. You review, provide feedback, modify until satisfied

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

## Editable Files
- backend/**
- web/src/**
- mobile/lib/**
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
   - `files_to_edit`: extract from "## Editable Files" section
   - `test_command`: generate defaults based on modules
2. Show inferred metadata.json; you confirm or modify

**Example**:
```json
{
  "ticket_id": "ticket_001",
  "title": "E-commerce Product Search Feature",
  "modules": ["backend", "web", "mobile"],
  "files_to_edit": ["backend/**", "web/src/**", "mobile/lib/**"],
  "test_command": {
    "backend": "npm run test -- backend",
    "web": "npm run test -- web",
    "mobile": "flutter test"
  },
  "max_healing_attempts": 3,
  "ui_capture": false
}
```

### 【Finalize】Validate & Release

**Process**:
1. Call `tickets_cli validate` to verify ticket completeness
2. Call `tickets_cli promote` to move to `pending/`
3. Ticket complete, ready for Phase 3 development

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
- `files_to_edit`: edit scope whitelist (guardrails)
- `test_command`: verification standards

Phase 3 automatically picks up the ticket and develops in a worktree.

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

