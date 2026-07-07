# Definition of Done

Project-level completion standard checklist.

## Quick Start

Before a task claims to be "done", run the Definition of Done checklist:

```
/skill definition-of-done
```

## What is a Definition of Done?

A Definition of Done is a **project-level quality baseline**, different from per-task acceptance criteria:

- **Acceptance Criteria**: "Did we build this correctly?" (varies per task)
- **Definition of Done**: "Can we confidently ship this?" (fixed and consistent)

## 5 Dimensions of Definition of Done

### 1. Correctness
✅ All acceptance criteria met + no regressions + edge cases handled

### 2. Quality
✅ Code is clear + no duplication + no dead code

### 3. Integration
✅ Works with the rest of the system + backward compatible + config correct

### 4. Documentation
✅ APIs documented + architectural decisions recorded + current state described

### 5. Ship-readiness
✅ Security reviewed + observability in place + rollback path exists + human approval

## How to Use

### Within Ticket Orchestration

`codoop-ticket` prompts users to reference this skill in phase 3:

```
11. User references /skill definition-of-done to check completion standards
```

### Independent Check

When any development is complete:

```
I've completed the user search feature implementation. Use /skill definition-of-done to verify it meets our completion standards.
```

## Key Principles

1. **Fixed and Unchanging** — Once defined, DoD is the project's quality floor. Time pressure doesn't override it.
2. **No Exceptions** — There's no "this time we can skip tests" or "we'll document this later".
3. **Repeatable** — Every task uses the same standard, ensuring consistent quality.

## Relationship with Other Skills

- **planning-and-task-breakdown** — Each task it breaks down must meet this standard upon completion
- **spec-driven-development** — Spec requirements + this standard = true "done"

