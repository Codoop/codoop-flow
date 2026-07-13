---
name: codoop-ux-walkthrough
description: Simulate a real task from a chosen user persona and write an evidence-backed, non-blocking experience report. Use after building a user-facing feature, when reviewing a runnable product flow, or when product owners want user-perspective improvement ideas without changing code automatically.
---

# User Experience Walkthrough

Run a qualitative, first-person walkthrough of a real product task. This skill
produces hypotheses and improvement ideas for human review; it does **not**
approve or reject a release, edit code, or create follow-up tickets.

## Core Rules

- Read `$SKILL/../_shared/agents/persona-walkthrough.md` and use it as the
  persona prompt without changing its contents.
- Distinguish what was observed from what was inferred. This is a qualitative
  simulation, not user research or statistical evidence.
- Ground every finding in an actual screen, interaction, log, or explicitly
  stated limitation. Never invent product behavior or user feedback.
- Keep the persona independent. The product's stated user role, goal, and
  acceptance criteria constrain the task being tested; they do not force the
  persona's identity.
- Never change source code, tests, tickets, or scope as a result of this report.
  A human decides whether an idea becomes a later ticket.

## Inputs

Gather the smallest useful context:

1. **Persona profile** — use one supplied by the user, or propose a concrete
   profile and label it as an assumption. It may be a core, adjacent, or
   stress-test user, but must plausibly use the product.
2. **Task contract** — when a ticket exists, read `module_prd.md` for its user
   role, goal, scope, and acceptance criteria. Otherwise ask for the task the
   persona should accomplish and what success means.
3. **Runnable evidence** — use the live app, browser, simulator, screenshots,
   or test output available in the current environment. State what was and was
   not available.

For ticket work, pass the persona prompt this runtime context:

```text
This is a task-flow walkthrough, not a release gate.

Ticket contract:
- Product user role: <from module_prd.md>
- Goal: <from module_prd.md>
- Acceptance criteria: <from module_prd.md>
- Scope: <from module_prd.md>

Chosen persona:
- Profile: <persona profile>
- Relationship to the product role: core / adjacent / stress-test

Use the contract to select and assess the task. Keep the persona independent.
Prioritize completing the actual workflow over landing-page or conversion
frameworks. Record only evidence-backed observations. Write a non-blocking
experience_report.md; do not request code changes or create tickets.
```

## Workflow

1. Read the original persona prompt in
   `$SKILL/../_shared/agents/persona-walkthrough.md`.
2. State the persona, the task to complete, the available evidence, and any
   assumptions.
3. Experience the primary path. When feasible, also try one recovery/error path
   and one relevant boundary path.
4. Capture the persona's plain-language reaction separately from the analyst's
   observation. For applications, follow task steps and state changes rather
   than forcing a scroll-by-scroll landing-page review.
5. Write the report to `experience_report.md`. For a Loop 3 ticket, write it
   directly into the ticket directory so it is archived with the ticket.

## Required Report Format

```markdown
# Experience Report: <feature or ticket title>

> This is a qualitative persona simulation, not validated user research. It
> does not block release, change code, or create a follow-up ticket.

## Walkthrough Context
- Persona: <profile>
- Relationship to product role: core / adjacent / stress-test
- Task and success condition: <from PRD or user input>
- Evidence used: <live app, screenshots, test output, etc.>
- Limitations and assumptions: <what could not be verified>

## Journey
### <step name>
- Persona voice: "<plain-language first-person reaction>"
- Observed: <what actually happened, with screenshot/state reference>
- Experience hypothesis: <why this may help or hinder the persona>

## Improvement Ideas
| Idea | Evidence and user benefit | Impact | Suggested next action |
|------|---------------------------|--------|-----------------------|
| <idea> | <evidence> | High / Medium / Low | Human review / consider a new ticket |

## What Worked
- <evidence-backed positive observation>

## Human Decision
- [ ] No action needed
- [ ] Discuss an idea
- [ ] Create a separate ticket from selected idea(s)
```

## Loop 3 Integration

When `codoop-execute` invokes this skill after technical approval:

- Run it only for a ticket with a user-visible, runnable behavior. Skip pure
  infrastructure, refactoring, or internal-only changes and say why.
- Read the ticket's `module_prd.md` and supply its facts as runtime context.
- Write `experience_report.md` in the ticket directory before `finish` moves
  the ticket to `done/`.
- Do not treat findings as review findings: no rejection, self-healing retry,
  scope expansion, or ticket creation follows automatically.
- If the feature cannot be exercised, produce a short report that records the
  missing evidence instead of fabricating a walkthrough.

## Standalone Use

```text
/skill codoop-ux-walkthrough
Act as a first-time operations manager and walk through creating a weekly report
in this app. Use docs/tickets/done/ticket_042/module_prd.md as the task context
and write experience_report.md beside it.
```

Use the report as a product conversation starter. A human may later turn a
selected idea into a separate codoop-ticket; this skill never does so itself.
