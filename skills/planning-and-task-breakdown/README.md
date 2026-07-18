# Planning and Task Breakdown

Break down technical specs into implementable, ordered task lists.

## How to Use

### Standalone Invocation (Generate Complete Plan)

When you have a technical spec (spec.md) and need to break it into implementation tasks:

```
/skill planning-and-task-breakdown
Based on the search feature technical spec, break it down into implementation plan and atomic tasks.
```

### As Phase 3 of Codoop-Ticket Orchestration

The `codoop-ticket` skill automatically calls this skill in phase 3:

```
【Phase 3】Task Breakdown (plan.md + todo.md)
9. codoop-ticket loads /skill planning-and-task-breakdown
10. Break down implementation tasks based on spec.md and the reviewed preview.html when present
11. User reviews and confirms
```

## Key Outputs of Task Breakdown

### plan.md — Implementation Plan

Steps organized by dependencies and execution order:

```markdown
# Implementation Plan: [Feature Name]

## Overview
[One-line summary of what we're building]

## Architecture Decisions
- [Decision 1 and rationale]
- [Decision 2 and rationale]

## Task List

### Phase 1: Foundation
- Task 1: ...
- Task 2: ...

### Checkpoint: Foundation
- [ ] All tests pass
- [ ] Build succeeds

### Phase 2: Core Features
- Task 3: ...
- Task 4: ...

### Checkpoint: Core Features
- [ ] End-to-end flow works
```

### todo.md — Atomic Task List

Each task ≤100 lines of code with clear acceptance criteria:

```markdown
## Task 1: Create search API endpoint

**Description:** Implement GET /api/search endpoint with keyword, category, price filtering.

**Acceptance criteria:**
- [ ] Endpoint accepts query params: q, category, min_price, max_price
- [ ] Returns paginated results with 20 items per page
- [ ] Validates input and returns 400 on invalid params
- [ ] Performance: responds < 500ms on 1M document dataset

**Verification:**
- [ ] Tests pass: npm test -- search.test.ts
- [ ] Build succeeds: npm run build
- [ ] Manual: curl endpoint with sample params

**Dependencies:** None

**Files likely touched:**
- src/api/search.ts
- tests/api/search.test.ts
- src/db/queries.ts

**Estimated scope:** Small (1-2 files)
```

## Core Design Principles

### 1. Vertical Slicing

❌ **Horizontal Slicing** — Layer-by-layer implementation (DB first, then API, then UI)
```
Task 1: Entire database schema
Task 2: All API endpoints
Task 3: All UI components
```

✅ **Vertical Slicing** — End-to-end features (each task delivers value)
```
Task 1: Search API + search box UI (user can search)
Task 2: Results list + DB query optimization (user can see results)
Task 3: Filter feature + frontend state management (user can filter)
```

### 2. Task Sizing Guidelines

| Size | Files | Time | When to Split |
|-----|-------|------|--------|
| XS | 1 | < 30 min | Single function or config |
| S | 1-2 | 30 min - 1h | Single component or endpoint |
| **M** | 3-5 | 1-2h | **Recommended range** |
| L | 5-8 | 2-4h | Multi-component work |
| XL | 8+ | 4h+ | ❌ **Split into smaller tasks** |

### 3. Checkpoints

Set a checkpoint after every 2-3 tasks to ensure the system still works:

```markdown
## Checkpoint: After Tasks 1-3

- [ ] All tests pass
- [ ] Build succeeds
- [ ] End-to-end flow works
- [ ] Confirm with user before continuing
```

## Relationship with definition-of-done

Each task broken down by this skill must meet the standards defined in `/skill definition-of-done` after completion. Refer to that skill for detailed requirements on Correctness, Quality, Integration, Documentation, and Ship-readiness.

## Best Practices

1. **Make dependencies explicit** — Clearly mark which tasks must be sequential vs parallel
2. **Specific acceptance criteria** — "Tests pass" is not enough; specify test types and coverage
3. **Include risk identification** — List known pitfalls in Risks and Mitigations
4. **Conservative estimates** — If unsure a task fits in 1-2 hours, split it further
