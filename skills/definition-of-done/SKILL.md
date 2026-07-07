---
name: definition-of-done
description: Project-level completion standard checklist. Every task must meet these criteria before completion—includes code quality, test coverage, documentation, security, and ship-readiness checks.
---

# Definition of Done

Project-level standards that every completed task must satisfy. Unlike acceptance criteria (which vary per task), DoD is a fixed quality baseline.

## Definition of Done vs. Acceptance Criteria

| | Acceptance Criteria | Definition of Done |
|---|---|---|
| **Scope** | Specific to one task or spec | Applies to every increment |
| **Changes** | Different per task | Fixed and unchanging |
| **Answers** | "Did we build this correctly?" | "Can we confidently ship this?" |
| **Defined By** | During task planning | Project-level standard |
| **Example** | "User can reset password" | "Tests pass, no regressions, docs updated" |

**Key**: A task is only done when it meets **both** its acceptance criteria **and** the Definition of Done.

---

## Completion Standards Checklist

Before declaring a task complete, ensure all items below are satisfied:

### Correctness

- [ ] All acceptance criteria are met
- [ ] Code runs and behaves as intended (verified at runtime, not just compiled or typechecked)
- [ ] New functionality is covered by tests: tests fail without the change, pass with it
- [ ] Existing tests still pass (no regressions)
- [ ] Edge cases and error paths are handled, not just the happy path

### Quality

- [ ] Code clearly expresses intent through naming and structure; no comments needed to understand what it does
- [ ] No duplicated business logic
- [ ] No dead code, debug output, or commented-out blocks
- [ ] Changes are scoped to the task; no unrelated refactors snuck in
- [ ] Code passes linting and formatting checks

### Integration

- [ ] Change works with the rest of the system, not just in isolation
- [ ] Database migrations, config changes, and feature flags are accounted for
- [ ] Backward compatibility is considered for any public interface or API change

### Documentation

- [ ] Public interfaces, APIs, and user-facing behavior are documented
- [ ] Architectural decisions worth preserving are recorded (see ADRs)
- [ ] Documentation describes the current state in timeless language (not "change history")

### Ship-readiness

- [ ] Security implications reviewed for any untrusted input, auth, or data handling
- [ ] Observability in place for critical paths (logs, metrics, traces)
- [ ] Rollback path exists for anything risky
- [ ] Human review and approval completed

---

## How to Apply

### Per Task

- Before checking off a task, verify Correctness and Quality sections
- Confirm before marking complete

### Per Feature

- Before considering a feature complete, verify Integration and Documentation sections
- Do before end-to-end testing

### Per Release

- Before shipping, the full checklist is the floor
- The `shipping-and-launch` skill adds deploy-specific gates on top

---

## Universal Principles

- **Define once, reuse unchanged** — Project-level DoD is set once and stays stable. It's not renegotiated every sprint.
- **No exceptions standard** — Time pressure is not a reason to skip tests or docs. The standard's value is protecting quality when schedules are tight.
- **Review quarterly** — Check every quarter whether DoD still applies and needs adjustment. But don't change it frequently.

---

## Common "Done" Traps

| Trap | Reality |
|---|---|
| "It runs but isn't verified" | Running ≠ correct. Tests must prove it. |
| "Tests pass" = Done | Tests passing is only part of DoD. Still need regression checks, docs, integration. |
| "Tight deadline so we'll lower standards" | Lowering standards creates tech debt and long-term delays. Keep standards. |
| "Acceptance criteria = Done" | Acceptance criteria = "built correctly". DoD = "safe to ship". Both required. |
| "Done before human review" | Automation matters, but human review is also the floor. |

