# Codoop-Ticket — Ticket Design Orchestration

Help users systematically design tickets in-session. Three stages progressively complete business requirements, technical specs, and task breakdown.

## Quick Start

Start ticket design with natural language:

```
/skill codoop-ticket
I want to design a user search feature for my e-commerce platform with keyword, category, and price range filtering.
```

## Workflow Overview

```
【Phase 1】Requirement Design (module_prd.md)
  ↓ (you review and say "OK, move to next phase")
【Phase 2】Technical Spec (spec.md)
  ↓ (you review and say "OK, move to next phase")
【Phase 3】Task Breakdown (plan.md + todo.md)
  ↓ (you review and say "OK, move to next phase")
【Auto Metadata Inference】Update metadata.json
  ↓ (you confirm or modify)
【Finalize】Validate & Release
  ↓
Ticket complete, ready for Phase 3 development ✅
```

## Final Outputs

Ticket directory `docs/tickets/pending/ticket_001/`:

```
ticket_001/
├── metadata.json      ← Auto-inferred: modules, test_command, files_to_edit
├── module_prd.md      ← PM-written: business requirements (pure business)
├── spec.md            ← Architect-designed: technical spec (APIs, DB, UI)
├── plan.md            ← Auto-decomposed: implementation plan (steps)
└── todo.md            ← Auto-decomposed: atomic task list (≤100 lines/task)
```

## Relationship with Other Skills

### Invocations within Ticket Design

- **Phase 2** → `/skill spec-driven-development` (design spec based on PRD)
- **Phase 3** → `/skill planning-and-task-breakdown` (break down tasks based on spec)
- **Throughout** — reference `/skill definition-of-done` (completion standards)

### Cross-Phase Integration

- **Phase 1 (Venture-Discovery)** — automatically reads `docs/backlog/` product/design/architecture specs as context
- **Phase 3 (Agent-Centric)** — passes complete ticket package via `metadata.json` and docs

## Key Actions Per Phase

### Phase 1: Requirement Design

**You**:
1. Describe what feature you want to build (natural language)
2. Answer clarifying questions from codoop-ticket and PM agent
3. Review generated `module_prd.md`
4. Provide feedback until satisfied
5. Say "OK, move to next phase"

**codoop-ticket + PM agent**:
- Parse your description
- Ask clarifying questions (scope, goals, acceptance criteria)
- Read Phase 1 product/design specs
- Write business requirements document (pure business, no technical details)

### Phase 2: Technical Spec

**codoop-ticket**:
- Load `/skill spec-driven-development`
- Trigger spec design based on your confirmed PRD

**spec-driven-development**:
- Design API interfaces (for each platform: backend/web/mobile/desktop)
- Design database fields and data models
- Design UI interaction flows
- Define editable files whitelist

**You**:
- Review `spec.md`
- Provide feedback and modifications
- Say "OK, move to next phase"

### Phase 3: Task Breakdown

**codoop-ticket**:
- Load `/skill planning-and-task-breakdown`
- Trigger task decomposition based on your confirmed spec

**planning-and-task-breakdown**:
- Generate `plan.md`: step-by-step implementation plan
- Generate `todo.md`: atomic task list (each ≤100 lines of code)

**You**:
- Reference `/skill definition-of-done` to understand completion standards
- Review `plan.md` and `todo.md`
- Provide feedback and modifications
- Say "OK, move to next phase"

### Auto Metadata Inference

**codoop-ticket automatically**:
- Extract `modules` from spec.md (## Backend, ## Web, etc. sections)
- Extract `files_to_edit` from spec.md (## Editable Files section)
- Generate `test_command` defaults based on modules

**You**:
- Review the inferred metadata.json
- Modify if needed
- Say "OK, publish ticket"

## Best Practices

1. **Phase 1 focus on business** — Don't include technical details in module_prd.md; that's Phase 2's job
2. **Discuss requirements thoroughly** — Ask "why" multiple times before locking PRD to avoid spec changes later
3. **Make specs explicit** — Use tables rather than paragraphs for APIs; complete field lists
4. **Keep tasks small** — If a task takes more than 2 hours, break it into smaller pieces
5. **Reference DoD early** — Don't wait until Phase 3 to think about "what is done"; reference definition-of-done in phase 3

## Troubleshooting

### Q: Ticket is stuck in a phase. What do I do?
A: Clearly tell codoop-ticket what changes you want, for example:
```
In the spec API section: change GET to POST, pass params in body, add request_id to response
```
codoop-ticket will regenerate or modify that section.

### Q: Metadata inference is wrong. How do I fix it?
A: Tell codoop-ticket what to change:
```
modules should be ["backend", "web"], not mobile
test_command for backend should be "npm run test:backend"
```

### Q: Ticket spec conflicts with Phase 1 standards. What happens?
A: codoop-ticket will alert you. If you truly need to break Phase 1 guidelines, explicit user confirmation is required.

