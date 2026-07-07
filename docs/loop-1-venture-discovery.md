# Loop 1: Venture-Discovery (Product Design)

## Overview

**Loop 1** is the first of three nested loops in codoop-flow's Triple-Loop Model. It is a structured, in-session collaborative product discovery process for **0→1 product design** — invoked *before* any code is written.

**What it solves:** Development teams (especially AI-assisted teams) often jump straight into building without completing rigorous product design, business validation, and architectural planning. This leads to wrong assumptions baked into code, misaligned business/technical decisions, inconsistent specifications, and expensive rework. Loop 1 runs a decentralized multi-role expert pipeline entirely inside a chat session, producing a locked, consistent set of specification documents that becomes the **Single Source of Truth** before a single ticket is written.

**Position in pipeline:** Produces `docs/backlog/` → feeds Loop 2 (human-centric ticket design) and Loop 3 (automated implementation).

---

## Quick Start

In any AI coding tool (Claude Code, Codex, Cursor, Gemini CLI), just say:

```
/skill codoop-discover I want to build a SaaS project management tool for remote teams
```

The skill will ask clarifying questions, run a multi-role expert session with you as the director, and produce complete design specifications in `docs/backlog/` within one session.

---

## Workflow

### Step 1 — Clarification (SNAP: Strict Non-Assumption Principle)

When the orchestrator encounters any ambiguous requirement (pricing model, platform scope, tech stack, feature boundaries), it halts and presents structured options:

```
[AGENT INQUIRY]: Should we build web-only or also support mobile?
- Option A: Web only, fastest to market [Pros: focused scope, faster; Cons: limiting UX]
- Option B: Web + mobile later [Pros: future-ready; Cons: initial complexity]
- Recommendation: Option A, then add mobile as Loop 2 ticket #2
```

You choose. The session does not proceed past any ambiguity unresolved.

### Step 2 — Shared Design Workspace

A temporary collaborative file is created: `docs/backlog/design-draft.md`. This serves as the "shared room" where all expert agents collaborate, surface conflicts, and track resolution.

### Step 3 — Multi-Role Collaborative Drafting

Seven expert agents are invoked in turn (or in parallel if your host supports subagents). They work through the design-draft.md using a structured protocol:

- `[CHALLENGE: <Role A> → <Role B>] <Objection>` — raises a cross-role conflict
- `[RESOLVED: <Role>] <Resolution>` — documents the agreed fix
- `[APPROVED: <Role>]` — role sign-off on consensus

If you need to override an agent, place a `[HUMAN DIRECTIVE]` block directly in `design-draft.md`. All sub-agents unconditionally obey it on their next invocation.

### Step 4 — Product Strategy (PM Agent)

The **product-sprint-prioritizer** agent drafts:
- `module_prd.md` — business overview, user stories, state transitions, and Gherkin BDD acceptance criteria
- `user-journey.md` — end-to-end user journeys and personas

**Hard constraint:** 100% pure business language. No database tables, API fields, or code.

### Step 5 — Go-To-Market Strategy (GTM Agent)

The **sales-offer-lead-gen-strategist** produces:
- `monetization-plan.md` — subscription tiers, pricing via the Value Equation formula, entitlements, lead magnets, and go-to-market channel sequencing

### Step 6 — UX/UI Design (Design Agents)

The **design-ux-architect** and **design-ui-designer** collaborate on:
- `design-system.md` — information architecture, CSS foundations, responsive breakpoints, accessible component patterns
- `ui-mockups.md` — ASCII wireframes, design tokens (color, typography, spacing), responsive frameworks, and animation parameters

### Step 7 — Technical Architecture (Architect Agents)

The **engineering-backend-architect** and **engineering-software-architect** jointly produce:
- `architecture.md` — system architecture patterns, data flow, deployment strategy, caching layers, security architecture
- `database-schema.sql` — complete DDL with indexes and constraints
- `openapi.yaml` — production-grade OpenAPI 3.0 specification for all APIs

### Step 8 — Module-Level BDD Specifications

For each functional unit, a `modules/module-<name>.md` file is written with Gherkin Given-When-Then test cases covering happy paths, edge cases, and error flows.

### Step 9 — Bridge Documents

Three files under `bridge/`:
- `human-preparation.md` — non-technical external setup checklist (register accounts, obtain API keys, set up payment gateways, register domains)
- `ai-co-dev-guide.md` — non-technical roadmap explaining spec roles, logical coding sequence, and AI collaboration principles
- `scaffolding-blueprint.md` — technical blueprint for directory layout, boilerplate config files, and core code structure

### Step 10 — Consistency Audit (Alignment Agent)

The **alignment-agent** runs independently after all specs are generated. It:

1. Reads all files across all directories
2. Writes `alignment-report.md` with severity levels, responsible roles, and resolution status
3. Raises `[ALIGNMENT CHALLENGE]` blocks in `design-draft.md` for each conflict found
4. Responsible roles re-draft fixes and mark them `[RESOLVED]`
5. Alignment Agent re-audits; if 100% aligned, appends `[ALIGNMENT APPROVED]` to `design-draft.md`

### Step 11 — Human Review and Lock

PM appends `[WAITING FOR HUMAN REVIEW]` to `design-draft.md` only after receiving `[ALIGNMENT APPROVED]`. You review the entire backlog and approve.

### Step 12 — Archive

Once locked, the Architect Agent verifies all specs are intact, then deletes `design-draft.md` to keep the repo clean.

---

## Outputs

All output lands under `docs/backlog/` with this exact structure:

```
docs/backlog/
├── design-draft.md              # Temporary workspace (deleted after approval)
├── alignment-report.md          # Consistency audit findings
├── product/
│   ├── requirements.md          # PRD: scope, state transitions, Gherkin BDD scenarios
│   ├── user-journey.md          # User journeys and personas
│   └── monetization-plan.md     # Pricing tiers, entitlements, GTM plan
├── interface/
│   ├── design-system.md         # Visual tokens, responsive breakpoints, components
│   └── ui-mockups.md            # ASCII wireframes, animation parameters
├── architecture/
│   ├── architecture.md          # Tech stack, data flow, deployment, caching
│   ├── database-schema.sql      # Complete DDL with indexes and constraints
│   └── openapi.yaml             # Production-grade OpenAPI 3.0 contract
├── modules/
│   └── module-<name>.md         # Per-module Gherkin BDD test cases
└── bridge/
    ├── human-preparation.md     # External setup checklist (non-technical)
    ├── ai-co-dev-guide.md       # How to continue with AI coding tools
    └── scaffolding-blueprint.md # Physical directory structure + boilerplate specs
```

All files are **locked by design** — no file is ever placed at the root of `docs/backlog/` except the two root files. A `specs/` directory is never created. These constraints are enforced by the Alignment Agent's directory audit.

---

## Skills Involved

### The Seven Expert Agents

All agents are defined in `/skills/_shared/agents/` and are orchestrated by the `codoop-discover` skill:

| Agent | File | Role |
|---|---|---|
| **PM / Product Strategy** | `product-sprint-prioritizer.md` | Defines product scope, user journeys, BDD scenarios; applies RICE/MoSCoW prioritization |
| **GTM & Pricing** | `sales-offer-lead-gen-strategist.md` | Designs pricing tiers, monetization, go-to-market channels |
| **UX Architect** | `design-ux-architect.md` | Establishes IA, CSS foundations, responsive breakpoints, accessibility baselines |
| **UI Designer** | `design-ui-designer.md` | Visual design system, component libraries, WCAG AA compliance, design tokens |
| **Backend Architect** | `engineering-backend-architect.md` | System architecture, database schemas, API contracts, security-first design |
| **Software Architect** | `engineering-software-architect.md` | Domain modeling, ADRs, architecture patterns, scaffolding blueprint |
| **Alignment Auditor** | `alignment-agent.md` | Cross-references all specs for inconsistencies, runs final consistency audit |

---

## CLI Reference

Loop 1 has **no dedicated CLI commands**. It is invoked purely in-session via the `codoop-discover` skill.

The `codoop.py` documentation references a `discover` subcommand in the README expand block, but the current implementation delegates this entirely to the in-session skill. The CLI tool chain (`codoop.py setup`, `codoop.py install`, `codoop.py ticket`) is for Loops 2 and 3.

---

## Configuration

Loop 1 requires no configuration file. It reads from your existing `codoop_flow.toml` (if present) only to determine the `target_repo` so it can write outputs to the correct `docs/backlog/` directory.

**No `metadata.json` is used in Loop 1** — all output is human-readable markdown and YAML specifications.

---

## Integration

### Inputs (before Loop 1)

Loop 1 takes a free-form product idea as input:
```
I want to build a SaaS project management tool for remote teams
```

That's it. All further inputs are gathered interactively during the session via SNAP clarification.

### Outputs (feeding Loop 2)

After Loop 1 approval, the human reviews `docs/backlog/` and decides on ticket breakdown. Loop 2 begins by:

1. Promoting core content from `docs/backlog/` into evergreen doc trees (`docs/prd/` and `docs/tech/`)
2. Reading the backlog files as context when designing individual feature tickets
3. Invoking `/skill codoop-ticket <feature description>` for each module

**Example transition:** `docs/backlog/architecture/database-schema.sql` from Loop 1 directly feeds into the `## Data Schema` section of the `spec.md` file in Loop 2 tickets.

### Outputs (feeding Loop 3)

Loop 1's `docs/backlog/bridge/scaffolding-blueprint.md` becomes the direct input for the first Loop 3 ticket: `ticket_001_project_scaffolding`.

All backlog specs (architecture, schema, API contract) are referenced by Loop 2 tickets, which are then executed by Loop 3 via `codoop-execute`.

---

## Lightweight Beta-Ready Definition of Done (BR-DoD)

Loop 1 applies four conditional quality requirements to all generated designs:

1. **UX Wiring Over Console Logs** (always) — all async states must have UI representations; no silent failures; loading states, error toasts, and a Settings Panel if the product has configurable settings
2. **Credential Persistence & Session Recovery** (if auth is involved) — registration, login, token refresh, and DB seeding must be designed
3. **External Services & Sandbox Completeness** (if external integrations exist) — all services must support full sandbox/mock mode; payment test cards; notification dual-track mode
4. **Frictionless Distribution** (conditional on platform) — unsigned build scripts for desktop/mobile; docker-compose or PaaS for web backends

---

## Key Design Principles

- **Human as Director, AI as Orchestrator** — The user is not bypassed. Every ambiguous decision is escalated to you via structured AGENT INQUIRY blocks.
- **Document-Driven, Not Code-Driven** — Loop 1 produces zero code. `scaffolding-blueprint.md` is an architectural drawing, not executable scaffolding.
- **Decentralized Drafting Before Centralized Audit** — All roles draft independently and raise `[CHALLENGE]` flags. The Alignment Agent runs last as an independent auditor.
- **SNAP as Non-Negotiable** — The skill explicitly refuses to make assumptions. Every ambiguity resolved during Loop 1 avoids 10x cost during implementation.
- **Output Language Adaptation** — If your session is in Chinese, output is in Chinese. No forced language.

