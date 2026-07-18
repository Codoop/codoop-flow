# codoop-discover: Venture-Discovery Loop Skill

> **In-session collaborative product discovery with multi-role expert agents**

## Overview

`codoop-discover` is a skill for Claude Code, Codex, Cursor, and other AI coding tools that enables **in-session product discovery and design** for 0-to-1 scenarios.

When you have a product idea and want to design it comprehensively before building, invoke this skill to orchestrate a collaborative session with expert agents:

- **PM (Product Strategy)** — defines scope, user journeys, and BDD scenarios
- **GTM (Go-To-Market)** — designs monetization, pricing, and business strategy
- **UI Design** — establishes a visual design system and page-composition rules
- **System Architect** — designs technical stack, APIs, databases, and deployment
- **Alignment Auditor** — ensures consistency across all specifications

## Quick Start

### In Claude Code, Codex, or similar AI tools:

```
User: /skill codoop-discover I want to build a SaaS project management tool for remote teams

SKILL: [Starts SNAP clarification questions]
SKILL: Based on your answers, invokes PM, GTM, UI, Architect agents in-session
SKILL: Generates comprehensive backlog documentation in docs/backlog/
```

## How It Works

### The 8-Step Workflow

1. **SNAP Clarification** — Agent asks you structured questions to remove ambiguities (pricing model, target users, tech stack preferences, etc.)
2. **User Confirmation** — You confirm key decisions (platform scope, business model, timeline, etc.)
3. **PM Drafting** — PM agent writes requirements, user journeys, and BDD scenarios
4. **GTM Strategy** — GTM agent designs monetization and commercial structure
5. **UI Design** — UI agent creates the visual design system and page-composition rules
6. **Technical Architecture** — Architect agent designs technical stack, APIs, and databases
7. **Consistency Audit** — Alignment agent audits all documents for inconsistencies and conflicts
8. **Resolution & Lock-In** — Conflicts resolved, documents finalized and saved to `docs/backlog/`

### SNAP Principle

**Strict Non-Assumption Principle (SNAP)**: The skill refuses to assume ambiguous requirements. If a decision is unclear:

```
[AGENT INQUIRY]: Should this be web-only or cross-platform (web + mobile)?

- **Option A**: Web-only (React web app) — Faster to market, lower cost, but limits mobile users
- **Option B**: Cross-platform (Web + iOS + Android) — Broader reach, but ~3x dev time
- **Recommendation**: Start with web-only (12 weeks), launch mobile Phase 2 (post-revenue)
```

You choose, and the skill adapts accordingly.

## Output Structure

The skill starts each backlog document from the matching file under `assets/templates/backlog/`. Templates fix the document structure only: the agent fills product-specific content, removes irrelevant optional sections, and leaves no placeholders in the final output.

After the skill completes, `docs/backlog/` contains:

```
docs/backlog/
├── design-draft.md          # Shared collaboration draft with [CHALLENGE] and [RESOLVED] markers
├── alignment-report.md      # Consistency audit results
├── product/
│   ├── requirements.md      # PRD with user stories and state transitions
│   ├── user-journey.md      # User journeys and personas
│   └── monetization-plan.md # Pricing, tiers, entitlements
├── interface/
│   └── design-system.md     # Visual direction, system, components, and page composition
├── architecture/
│   ├── architecture.md      # Tech stack, data flow, deployment
│   ├── database-schema.sql  # Complete database design
│   └── openapi.yaml         # API contract
├── modules/
│   └── module-*.md          # Per-module BDD specifications
└── bridge/
    ├── human-preparation.md # External setup checklist
    ├── ai-co-dev-guide.md   # How to continue with AI coding tools
    └── scaffolding-blueprint.md # Project directory structure
```

## Next Steps

After discovery is complete:

1. **Review** the generated backlog documents
2. **Decide** on ticket breakdown (which features to build first)
3. **Transition** to `codoop-ticket` skill to draft work tickets
4. **Implement** using the `codoop-execute` agent-centric skill to build in isolated worktrees

## Expert Agents

This skill reads expert personas from `skills/_shared/agents/`:

- `product-sprint-prioritizer.md` — PM/Product Strategy expert
- `sales-offer-lead-gen-strategist.md` — GTM/Business Strategy expert
- `design-ui-designer.md` — UI Design expert
- `engineering-backend-architect.md` — Backend Architecture expert
- `engineering-software-architect.md` — Software Architecture expert
- `alignment-agent.md` — Consistency & Alignment auditor

These are **shared across all skills** — if you use other discovery or planning skills, they reference the same experts for consistency.

## Tips & Tricks

### Keep Decisions Recorded

As the skill asks questions, **record your answers in a sticky note or doc**. You'll reference them during implementation.

### Use Challenge-Loop for Debates

If you disagree with a design decision:

```
[HUMAN DIRECTIVE]: I disagree with the free-tier limits. Let's use 5,000 API calls/month instead of 1,000.
```

The skill will adjust and re-audit consistency.

### Backlog as SSoT

Once locked, `docs/backlog/` becomes your **Single Source of Truth**. Don't modify it by hand — reference it when building tickets.

## Troubleshooting

**Q: The skill asks too many questions**
A: This is by design (SNAP principle). Every ambiguity must be resolved to avoid rework later. Answer clearly, and the skill moves on.

**Q: I want to change a design decision mid-way**
A: Add a `[HUMAN DIRECTIVE]` block in `docs/backlog/design-draft.md`. The skill will re-audit and update.

**Q: Can I skip the alignment audit?**
A: No. Inconsistencies in discovery cause 10x cost during implementation. Better to fix now.

---

**Learn more**: See `SKILL.md` for the full orchestration logic, or check `engineering-design.md` for the complete system architecture.
