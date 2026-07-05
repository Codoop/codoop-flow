---
name: product-discovery-loop
description: Executes a collaborative, multi-role (PM, GTM, UI/UX, Architect) product discovery, commercial monetization design, and technical architecture planning. Use when a new feature, module, or product is being conceptualized or researched.
disable-model-invocation: true
---

# Product Discovery & Design Loop

This skill guides the AI to act as an **Orchestrator** running a decentralized, multi-role collaborative pipeline to discover, validate, and architect products or features. It ensures strict avoidance of assumptions, leverages multi-perspective analysis, and produces production-grade BDD specifications and system architectures.

It is designed to be fully compatible with **Cursor Desktop** and **Claude Code (Co)**.

---

## 1. Operating Architecture

### 1.1 Human as Director, AI as Orchestrator
- **Human Director**: The user acts as the ultimate director, decision-maker, and bridge.
- **Orchestrator Agent**: The main chat agent does not directly claim to be all roles. Instead, it acts as the **Orchestrator/Coordinator**, reading the current state of the design and dispatching specialized sub-agents via the **Task tool (sub-processes)** to prevent context pollution.

### 1.2 Sub-Agent Context Isolation & Invocation
To prevent "Context Pollution", the Orchestrator MUST invoke specialized sub-agents (PM, GTM, UI/UX, Architect, Alignment) in isolated environments.
- **Strict Calling Protocol**: Before spawning a sub-agent, the Orchestrator **MUST locate and read the corresponding prompt file in `../../discovery-agents/`** using file tools:
  - PM Agent ➔ Read `../../discovery-agents/pm-agent.md`
  - GTM Agent ➔ Read `../../discovery-agents/gtm-agent.md`
  - UI/UX Agent ➔ Read `../../discovery-agents/ui-ux-agent.md`
  - Architect Agent ➔ Read `../../discovery-agents/architect-agent.md`
  - Alignment Agent ➔ Read `../../discovery-agents/alignment-agent.md`
- **Spawn Task**: After reading, the Orchestrator calls the **Task tool**, passing the exact file contents of the selected agent markdown as the system prompt for that sub-task.

---

## 2. External & Sibling Skills Integration

To achieve high-fidelity output, this loop relies on several specialized sibling skills (`ui-ux-pro-max`, `gsap-skills`, `pm-skills`). 
- **Rule**: The Orchestrator and spawned sub-agents MUST proactively load, read, and follow these sibling skills.
- **Reference Manual**: For specific file paths, relative routing, and configuration metrics of external integrations, refer directly to the sibling [**`README.md`**](README.md) file in this directory.

---

## 3. Core Disciplines

### 3.1 Strict Non-Assumption Principle (SNAP)
- **Rule**: Never make assumptions about business logic, pricing tiers, tech stack choices, platform ranges, layout configurations, or feature boundaries.
- **Action**: If any requirement is missing, ambiguous, or lacks evidence, you MUST halt and present options to the user.

### 3.2 Structured Querying Protocol
When querying the user, do not throw wide open-ended questions. Analyze the issue and provide 2-3 specific alternatives with clear pros and cons, along with your recommended approach.
Use this format:

```markdown
> [AGENT INQUIRY]: <Clear description of the ambiguity or decision point>
> 
> - **Option A (Option A)**: <Specific details of Option A> [Pros / Cons / Cost / Risk]
> - **Option B (Option B)**: <Specific details of Option B> [Pros / Cons / Cost / Risk]
> - **Recommendation (Recommendation)**: <Your recommended option> because <professional reasoning>.
```

---

## 4. Multi-Role Collaboration Framework

The core responsibilities, tool integrations, and detailed capabilities of each specialized role are single-sourced in their respective agent configuration files. The Orchestrator should reference these files:

- **Product Manager (PM)**: Defines product scopes, opportunity trees (OST), user journeys, and Gherkin BDD user stories. Detailed in [`../../discovery-agents/pm-agent.md`](../../discovery-agents/pm-agent.md).
- **Go-To-Market (GTM)**: Formulates subscription structures, free/paid tier boundaries, price elasticities, and GTM plans. Detailed in [`../../discovery-agents/gtm-agent.md`](../../discovery-agents/gtm-agent.md).
- **UI/UX & Animations**: Establishes visual design systems, layout constraints, interactive ASCII mockups, and GSAP fluid animation parameters. Detailed in [`../../discovery-agents/ui-ux-agent.md`](../../discovery-agents/ui-ux-agent.md).
- **System Architect**: Designs technical stack schemas, cross-platform parity specifications, OpenAPI contracts, DB tables, and red-teams assumptions. Detailed in [`../../discovery-agents/architect-agent.md`](../../discovery-agents/architect-agent.md).
- **Consistency Auditor (Alignment)**: Reads all specifications, cross-references them to identify inconsistencies, and feeds them back to PM, GTM, UI/UX, and Architect. Detailed in [`../../discovery-agents/alignment-agent.md`](../../discovery-agents/alignment-agent.md).

---

## 5. Decentralized Document-Driven Workflow

Follow this lifecycle for design packaging:

```text
Drafting & Objections             Hardening & Specifications             Alignment Audit & Lock            Development
┌─────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐      ┌────────────────┐
│ docs/backlog/           │      │ docs/backlog/             │      │ alignment-report.md       │      │ Actual coding  │
│ design-draft.md         ├─────►│ requirements.md, etc.     ├─────►│ [ALIGNMENT APPROVED]      ├─────►│ in src/, main/,│
│                         │      │                           │      │                           │      │ backend/       │
│ [CHALLENGE] [RESOLVED]  │      │                           │      │ [WAITING FOR HUMAN REVIEW]│      │                │
└─────────────────────────┘      └───────────────────────────┘      └───────────────────────────┘      └────────────────┘
```

1. **Shared Design Draft**: Create a temporary file `docs/backlog/design-draft.md` as the shared room for collaborative drafting.
2. **Review & Objections (The Challenge Loop)**:
   - Raise objections using: `[CHALLENGE: <Role A> -> <Role B>] <Objection details>`
   - Resolve them using: `[RESOLVED: <Role>] <Resolution/compromise details>`
   - Sign off when consensus is reached: `[APPROVED: <Role>]`
3. **Reactive Human Intercept (`[HUMAN DIRECTIVE]`)**:
   - The user can intervene at any time by placing a `[HUMAN DIRECTIVE]` block directly in `design-draft.md`.
   - Sub-agents must read this block on launch and unconditionally obey the directive, adjusting their designs.
4. **Structured Specifications**: Hard-lock the final design into structured spec files organized under five clear subdirectories under `docs/backlog/` (strictly avoiding flat root-level file accumulation, and not generating any `specs/` directory):
   - **`product/`** (Product & Monetization):
     - `requirements.md`: Standard Product Requirement Document (PRD) containing scope, state transitions, and Gherkin BDD scenarios.
     - `user-journey.md`: Complete user journeys and user/job stories.
     - `monetization-plan.md`: Subscription structures, free/paid tier boundaries, and entitlement configurations.
   - **`interface/`** (Visual & Interaction):
     - `design-system.md`: Visual design systems, layout constraints, and visual tokens.
     - `ui-mockups.md`: Interactive ASCII mockups, wireframes, and animation parameters.
   - **`architecture/`** (Technical Design & Contracts):
     - `architecture.md`: Technical specifications detailing system designs, physical process models, database relations, and cross-platform integrations.
     - `database-schema.sql`: Complete SQL tables, indices, and constraints.
     - `openapi.yaml`: Production-ready OpenAPI contract.
   - **`modules/`** (Module-Level Detailed Design):
     - `module-<name>.md`: Modular Gherkin BDD specifications containing Given-When-Then test cases for each functional unit.
   - **`bridge/`** (Human-AI Collaboration Bridge):
     - `human-preparation.md` (Human Preparation Checklist): A non-technical checklist of administrative and platform-specific tasks that a human must perform (e.g., registering developer accounts, obtaining API keys/credentials, registering domains, setting up payment gateways). This document must be dynamically and precisely tailored based on the application's specific design. If the application has no external platform dependencies, it should explicitly state that no preparation is needed.
     - `ai-co-dev-guide.md` (AI Co-Development Guide): A non-technical roadmap guiding the human user on how to continue AI-driven development. It explains the role of each generated specification document, outlines a logical step-by-step coding sequence, and suggests general AI collaboration principles (e.g., how to feed specifications to an AI coding assistant). It must NOT mention specific AI tool brands (such as Cursor, Claude Code, etc.) and must NOT contain concrete prompt templates.
     - `scaffolding-blueprint.md` (Scaffolding Blueprint): A technical blueprint specifying the physical directory layout, boilerplate configuration files (e.g., package managers, compiler configs, container setups), and core boilerplate code specifications. This serves as a concrete "architectural drawing" for an AI assistant to initialize the project's codebase foundation.

5. **Consistency Audit & Alignment Loop**:
   - After structured specifications are generated, the Orchestrator MUST invoke the **Alignment Agent** (reading `../../discovery-agents/alignment-agent.md`) to conduct a comprehensive consistency audit across all generated files.
   - The Alignment Agent reads all specification files across the five directories, generates `docs/backlog/alignment-report.md`, and writes any identified inconsistencies into `docs/backlog/design-draft.md` under `[ALIGNMENT CHALLENGE]` blocks:
     `[ALIGNMENT CHALLENGE: Alignment -> <Role(s)>] <Description of conflict>`
   - The corresponding roles (PM, GTM, UI/UX, Architect) must be re-dispatched to resolve these challenges, updating their respective files and writing `[RESOLVED: <Role>]` in `design-draft.md`.
   - The Alignment Agent is re-dispatched to verify the updates. Once 100% aligned, the Alignment Agent appends `[ALIGNMENT APPROVED: Alignment]` to `design-draft.md`.
6. **Final Lock-In**: PM appends **`[WAITING FOR HUMAN REVIEW]`** at the end of `design-draft.md` only after receiving the `[ALIGNMENT APPROVED: Alignment]` sign-off.
7. **Archiving & Purge (Cleanup)**: Once the user approves and marks it as `Locked`, **Architect Agent** is responsible for verifying that all specifications are intact, and then **deleting the temporary `design-draft.md`** to keep the codebase clean.

---

## 6. BDD Gherkin Writing Template

When writing module specifications, capture edge cases and core paths using Gherkin:

```gherkin
Feature: <Feature title>

  Scenario: <Context description>
    Given <Prerequisites or initial state>
    When <Action or event triggers>
    Then <Outcome or expected result>
    And <Additional outcome details>
```

---

## 7. Lightweight Beta-Ready Definition of Done

To ensure that the first internal testing version (Alpha/Beta) of any application provides a highly complete user experience while avoiding administrative, certificate, or high operational bottlenecks, this loop establishes the following generic "Lightweight Beta-Ready Definition of Done" (BR-DoD). These requirements are applied conditionally based on the application's specific design:

### 7.1 UX Wiring Over Console Logs (Always Applicable)
- **Core Principle**: Any system state, asynchronous operation, or background task must have a corresponding user-facing UI representation. Silent failures or console-only errors are strictly forbidden.
- **Hard Design Requirements**:
  - **State Feedback**: All asynchronous requests must design explicit Loading states (e.g., Spinners, skeleton screens, or progress bars) to prevent duplicate clicks and user confusion.
  - **Exception Handling**: Network failures, API errors, or permission denials must be gracefully presented to users via Toast notifications, inline banners, or Modals.
  - **Settings Panel**: If the application has user-configurable settings, a user-accessible Settings Panel UI must be designed and mounted to allow testers to modify core configurations or basic parameters directly, rather than forcing them to manually edit local JSON/YAML/ENV configuration files.

### 7.2 Credential Persistence & Session Recovery (Conditional)
- **Applicability**: Only applicable if the product design involves user accounts, authentication, or cloud data synchronization.
- **Core Principle**: Internal testers should not have to log in repeatedly every time they open the application, nor should they rely on developers manually seeding the database.
- **Hard Design Requirements**:
  - A standard registration, login, or robust mock authentication flow must be designed.
  - Session persistence and automatic recovery/token refresh on cold start must be implemented, allowing users to automatically enter the main interface after logging in once.
  - **Always Applicable**: Automated database seeding or initialization mechanisms must be provided to eliminate any dependency on manual database operations for basic testing.

### 7.3 External Services & Sandbox Completeness (Conditional)
- **Applicability**: Only applicable if the product design integrates with external third-party services (such as payments, transactional emails, SMS, OAuth, or external APIs).
- **Core Principle**: All services involving external platform integrations or premium privileges must achieve 100% functional completeness under a "sandbox/test mode".
- **Hard Design Requirements**:
  - **Sandbox-Complete**: All external integrations must support a complete sandbox/mock mode for 100% functional completeness without production credentials.
  - **Payment Sandbox (If payments are designed)**: Must integrate with payment gateway test modes (e.g., test cards, sandbox accounts). When a user purchases, the system must automatically upgrade their account (e.g., via mock/test Webhooks) and unlock premium features client-side immediately.
  - **Notification Fallback (If emails/SMS are designed)**: Notification services must support a dual-track mode: send real messages if API credentials are provided, otherwise log them to the server console and proceed automatically, ensuring testing is never blocked.

### 7.4 Frictionless Distribution (Conditional)
- **Applicability**: Applied conditionally based on the target platform (Desktop, Web, Mobile, or CLI).
- **Core Principle**: Avoid wasting development time on official code signing certificates or complex deployment pipelines, providing the fastest path to testing.
- **Hard Design Requirements**:
  - **Unsigned/Development Packaging (For Desktop/Mobile/CLI)**: Provide automated build/packaging scripts (e.g., producing unsigned binaries, zip archives, or local installers). In the distribution documentation, include clear instructions on how testers can bypass operating system security warnings (e.g., macOS "App is damaged" or Windows SmartScreen).
  - **Single-Machine Deployment (For Web/Backend)**: Backends or web servers must provide one-click containerized deployment scripts (e.g., `docker-compose.yml`) or simple configurations for PaaS platforms, avoiding complex multi-node clusters or CDN setups.

---

## 8. Output Language Rule
- **Rule**: Adapt to the conversation context and user's preferred/specified language. Do not force any specific language (e.g., Chinese or English) unless explicitly requested or implied by the project context.
