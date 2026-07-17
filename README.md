<div align="center">

# codoop-flow

**English** · [简体中文](./README.zh-CN.md)

**Turn "AI writes code" into a ticket pipeline with guardrails**
pick → build → verify → multi-review → archive, one ticket per closed loop

![Codex Skill](https://img.shields.io/badge/Codex-skill-111827)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-8A63D2)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Zero deps](https://img.shields.io/badge/deps-zero-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

**codoop-flow** is a three-loop AI-driven development system for turning "AI writes code" into a reliable engineering pipeline.

**You steer Codex or Claude in plain language; guardrails backstop the grunt work.** The thinking (writing code, self-healing, review judgment) happens in the active agent session; the mechanical must-be-exact work (claiming tickets, managing git worktrees, running tests) goes to a deterministic Python CLI that can't hallucinate. It's a portable tool with no business code — point one `codoop_flow.toml` at the project you want to build.

**Three independent loops** that work together or standalone:
- **Loop 1**: Multi-role product design sessions (0→1 planning)
- **Loop 2**: Detailed ticket design (PRD + spec + task breakdown)
- **Loop 3**: Continuous ticket execution (build → verify → review → merge)

```
        you say one line                       you decide whether to push
             │                                     ▲
             ▼                                     │
  ┌───────────────── Codex/Claude reads SKILL.md and orchestrates ──────────────┐
  │                                                                             │
  │   pick ──▶ build ──▶ verify ──▶ review ──▶ ship docs ──▶ finish            │
  │ [script] [agent]   [script]  [reviewers] [agent]       [script]           │
  │  claim    write     run tests  multi-      sync docs     commit &          │
  │  ticket   code      +UI        review                    archive           │
  │ +worktree           gate       unanimous                 dev/<id>          │
  │                        │           │                                       │
  │                        └─ fail ────┴─▶ self-heal (retry within budget)     │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## Install

### Codex (Desktop or CLI)

Install from the GitHub marketplace repo:

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

Or ask Codex:

```text
Install the codoop-flow Codex plugin from Codoop/codoop-flow, then set up this repo for codoop-flow.
```

Then restart/open Codex. The normal workflow is just:

```text
Use $codoop-flow to set up this repo for codoop-flow.
Use $codoop-flow to run the next ticket against codoop_flow.toml.
```

Local development fallback:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/codoop-execute "${CODEX_HOME:-$HOME/.codex}/skills/"
```

### Claude Code

Install the plugin:

```text
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

Or tell Claude Code to install the codoop-flow plugin from `Codoop/codoop-flow`
and then run it against your repo.

> SSH error? Use the full HTTPS URL: `/plugin marketplace add https://github.com/Codoop/codoop-flow.git`
> Local development: `claude --plugin-dir /path/to/codoop-flow`
> Other agents (Cursor / Gemini): see [`docs/install.md`](./docs/install.md).

**Prerequisites**: the target project is a git repo; the machine has `python3` (standard library only, zero third-party deps).

---

## The Three Loops

codoop-flow implements a **Triple-Loop** system for AI-driven development:

### 🔍 Loop 1: Venture-Discovery (Product Design)
**Use when**: You have a product idea and need comprehensive 0→1 design before coding.

**Invoke in-session**:
```
/skill codoop-discover I want to build a SaaS project management tool for remote teams
```

The skill orchestrates expert agents (PM, GTM, UX/UI, Architect) through:
- **SNAP clarification** — removes ambiguities via structured questions
- **Multi-role drafting** — experts collaborate in-session
- **Consistency audit** — catches cross-document conflicts
- **Backlog generation** — outputs complete specs to `docs/backlog/`

**Output**: Design documents in `docs/backlog/` ready for Loop 2

[Learn more about codoop-discover →](./skills/codoop-discover/README.md)

### 📋 Loop 2: Human-Centric (Ticket Design)
Design work tickets through three stages: requirements (PRD) → technical spec → task breakdown. Ready for the agent loop.

**Main orchestrator**:
```
/skill codoop-ticket Design the user search feature for our e-commerce platform
```

**Standalone tools** (also called by codoop-ticket):
```
/skill spec-driven-development Design technical specs before coding
/skill planning-and-task-breakdown Break specs into ordered, implementable tasks
/skill definition-of-done Check if completed work meets quality standards
```

**User experience walkthrough** — use it independently after a feature is
runnable, or let Loop 3 invoke it after technical approval. It simulates a
chosen persona completing a task and writes an advisory `experience_report.md`;
only a human decides whether an idea becomes a new ticket.

```
/skill codoop-ux-walkthrough
Experience this feature as a first-time operations manager and write an experience report.
```

These skills work independently or as phases in the codoop-ticket workflow.

**Output**: Ticket specifications in `docs/tickets/pending/` ready for Loop 3

[Learn more about codoop-ticket →](./skills/codoop-ticket/README.md)

### 🤖 Loop 3: Agent-Centric (Implementation)
Pick a ticket → build in isolated worktree → verify → multi-review → merge & archive.

**Main orchestrator**:
```
/loop 20m run the codoop-execute skill against codoop_flow.toml
```

**How it works**:
1. **Pick** — Claims oldest pending ticket, creates isolated git worktree on `dev/<ticket_id>` branch
2. **Build** — Agent writes code following ticket specs inside worktree
3. **Verify** — Hard gates: tests pass, UI screenshots (if needed)
4. **Review** — Multiple reviewer personas check code (unanimous approval required)
5. **Merge** — Agent asks: "Merge `dev/<ticket_id>` to `main`?" → You decide
6. **Archive** — Moves ticket to `done/`, removes worktree

**Key features**:
- **Idempotent**: Same command safely called repeatedly (resumes in-progress tickets)
- **Self-healing**: Automatically retries on verify failure (up to 3 attempts by default)
- **Deterministic verification**: Tests + screenshots cannot be bypassed
- **Async-friendly**: Timing controlled by `/loop` (Agent's scheduler, not Python)

**Output**: Merged code in `main` branch, tickets archived in `docs/tickets/done/`

[Learn more about codoop-execute →](./docs/loop-3-agent-centric.md)

---

## Quick start

### For Loop 1 (Product Design)

```
/skill codoop-discover I want to build [your product idea]
```

Outputs design specs to `docs/backlog/`.

### For Loop 2 (Ticket Design)

```
/skill codoop-ticket Design [specific feature name]
```

Outputs ticket specs to `docs/tickets/pending/ticket_001/`.

### For Loop 3 (Implementation) — Complete Workflow

**① One-time setup** (creates ticket pipeline + config):

In Claude Code, ask:

```text
Use the codoop-execute skill to set up this repo for codoop-flow.
```

Or manually:

```bash
python3 skills/codoop-execute/scripts/codoop.py setup /path/to/your/repo \
  --config /path/to/your/repo/codoop_flow.toml
```

**② Add tickets** to `docs/tickets/pending/ticket_001/`, each containing:
- `metadata.json` ([fields](#ticket-metadatajson))
- `module_prd.md` (business requirements)
- `spec.md` (technical contract)
- `plan.md` (execution plan)
- `todo.md` (atomic tasks)

**③ Process queue continuously** in Claude Code:

```
/loop 20m run the codoop-execute skill against codoop_flow.toml
```

The Agent will:
1. Pick oldest pending ticket
2. Build code in isolated worktree
3. Verify (tests + UI)
4. Review (multi-reviewer approval)
5. Ask: "Merge to main?" → You decide
6. Archive and loop

**No push step needed** — all changes are local. You control when to merge to `main`.

---

## Single-ticket workflow (manual)

If you don't want continuous `/loop`, run once:

```
Use the codoop-execute skill to run a ticket against codoop_flow.toml
```

Agent picks the oldest pending ticket and runs the complete pipeline (pick → build → verify → review → ask merge). You decide whether to merge.

---

## How it works

Once installed you barely need to remember commands — **the skill is written for the coding agent to read**. You say one line, and the agent follows the skill to chain the whole thing together:

### The Three Components

1. **Skill orchestration** (`SKILL.md`): Agent reads the workflow and knows what to do in each phase.

2. **Script guardrail** (`codoop_tools.py`): The deterministic CLI that handles all must-be-exact work:
   - Claim a ticket (from pending → in_progress)
   - Create isolated git worktree on `dev/<ticket_id>` branch
   - Verify: run tests, check UI screenshots
   - Commit and archive (in_progress → done)
   - Handle failures gracefully

3. **Review personas** (in `_shared/agents/`): After verify passes, agent runs multiple reviewers:
   - `code-reviewer` — correctness, readability, security, performance
   - `security-auditor` — vulnerability scanning
   - `test-engineer` — test strategy and coverage
   - `evidence-collector` — UI/UX validation (UI tickets only)
   - `reality-checker` — deployment readiness (UI tickets only)

4. **Experience walkthrough** (`codoop-ux-walkthrough`): After technical
   approval, a runnable user-facing ticket may be experienced by a chosen
   persona. The resulting `experience_report.md` is archived with the ticket
   and is advisory only: it never blocks release or changes code automatically.

**Approval must be unanimous** — any rejection triggers self-heal (automatic retry within budget).

### Design Philosophy

**In a nutshell: thinking goes to the agent, counting-and-checking goes to the script.**

- **Agent decides**: What code to write, how to fix failures, whether improvements are needed
- **Script guarantees**: Ticket isolation, worktree lifecycle, test execution (unhackable)
- **You control**: Whether to merge to main, timing of ticket intake, long-term prioritization

### Key Properties

| Property | Benefit |
|----------|---------|
| **Deterministic verification** | Hard gates (tests + UI) cannot be bypassed by AI hallucination |
| **Self-healing** | Failed verify/review = automatic retry (up to `max_healing_attempts`, default 3) |
| **Isolated worktrees** | Each ticket builds independently; no cross-ticket interference |
| **Local-first** | Requires only local git repo; remote push optional (you decide) |
| **Agent-agnostic** | Timing from `/loop` (Agent's scheduler), not Python internal timers |
| **Transparent** | All state in git branches + file system; fully auditable and reversible |

<details>
<summary>Filing tickets by hand (expand if you don't want the agent to do it)</summary>

After `setup`, you can also use the human-facing CLI to turn an idea into a ticket:

```bash
# Draft: scaffold metadata + empty docs under drafts/
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
# Edit drafts/ticket_001/: module_prd.md (business), spec.md (contract)
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket validate ticket_001 --config codoop_flow.toml   # check required docs
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket promote  ticket_001 --config codoop_flow.toml   # confirmed drafts → pending + dedicated ticket commit
```

To explore a brand-new idea (multi-role design session, output to `docs/backlog/`), invoke the skill in-session:

```
/skill codoop-discover an idea for an XX app
```
</details>

---

## Ticket metadata.json

```json
{
  "ticket_id": "ticket_001",
  "title": "add hello module",
  "ticket_type": "feature",
  "modules": ["backend"],
  "test_command": {"backend": "<project-specific test command>"},
  "max_healing_attempts": 3,
  "ui_capture": false
}
```

| Field | Meaning |
|---|---|
| `ticket_type` | `feature` (需求单, default) or `fix` (修复单). Selects required docs in Loop 2 and the commit prefix (`feat`/`fix`) in Loop 3 |
| `modules` | Modules involved; each must have an entry in `test_command` |
| `test_command` | module → explicitly configured shell command; `verify` runs one per module (no default is inferred) |
| `max_healing_attempts` | self-heal retry budget (default 3) |
| `ui_capture` | when true: the test script must write screenshots to `$CODOOP_QA_SCREENSHOT_DIR` (no screenshots = hard fail), and review adds 2 UI personas that actually look at the images |

Required: `ticket_id / title / modules / test_command`. `ticket_type` (default `feature`) is optional.

---

<details>
<summary>Guardrail CLI reference (<code>codoop_tools.py</code>, called by the agent automatically — you rarely type it)</summary>

Every subcommand takes `--config <toml>` and emits JSON.

| Subcommand | Behavior |
|---|---|
| `status` | Print tickets per stage |
| `pick` | Claim the oldest pending ticket → move to in_progress → create worktree (`dev/<id>` branch). If one is already in_progress, report it instead of picking a new one |
| `verify <id>` | In the worktree: run tests + (UI) screenshot hard gate |
| `finish <id> --message` | Commit (excluding generated noise) to `dev/<id>` → move to done → remove worktree |
| `fail <id> --report` | Move to failed → write `healing_report.md` → release lease and retain the worktree for human recovery |

</details>

---

## Repository layout

```
codoop-flow/
├── codoop_flow.toml.example       # config sample
├── .agents/plugins/marketplace.json # Codex marketplace manifest
├── .claude-plugin/                # Claude Code plugin manifests
├── .codex-plugin/                 # Codex plugin manifest
├── skills/
│   ├── _shared/                   # shared code & agents (used by all skills)
│   │   ├── codoop_lib_v1/         #   shared libraries (ticket, config, verify, etc.)
│   │   └── agents/                #   review personas (code-reviewer, security-auditor, etc.)
│   ├── codoop-execute/            # ★Loop 3: Agent-Centric code execution
│   ├── codoop-ticket/             # ★Loop 2: Human-Centric ticket design  
│   ├── codoop-discover/           # ★Loop 1: Venture-Discovery product design
│   ├── codoop-ux-walkthrough/     # ★Persona-based, non-blocking experience insight
│   └── [6 other skills]/          # standalone disciplines
├── tests/test_skeleton.py         # 14 skeleton tests (subprocess CLI calls, no AI)
├── LICENSE                         # MIT
└── docs/
    ├── install.md                 # multi-agent install guide
    └── engineering-design.md      # design blueprint (three-loop model)
```

> Chinese docs carry a `.zh-CN` suffix (e.g. `docs/install.zh-CN.md`); the suffix-less files are English.

---

## Running tests

```bash
python3 tests/test_skeleton.py   # should print ALL SKELETON TESTS PASSED
```

The skeleton tests use a temp git repo + subprocess CLI calls, covering only the **deterministic guardrail + ticket lifecycle** — no AI, runs in seconds.

---

## Compatible agents

The skill is a self-contained directory; any coding agent that can read files and run Bash can use it. Subagents improve review isolation but are not mandatory.

| Agent | Status | How to install |
|---|---|---|
| Codex Desktop | ✅ first-class | `codex plugin marketplace add Codoop/codoop-flow`, then `codex plugin add codoop-flow@codoop-flow` |
| Codex CLI | ✅ first-class | same plugin install flow |
| Claude Code | ✅ first-class | plugin marketplace (see [Install](#install)) |
| Claude CLI | ✅ first-class | same local `claude` command used by Claude Code |
| Cursor / Gemini | 🟡 generic copy | copy the `skills/` dir, see [`docs/install.md`](./docs/install.md) |

> If the host lacks a subagent tool, run the review personas serially in the same session.

---

## FAQ

**General**

**What's the difference between the three loops?**
- **Loop 1**: Multi-role product design (0→1 planning) → `docs/backlog/`
- **Loop 2**: Single-ticket design (PRD + spec + tasks) → `docs/tickets/pending/`
- **Loop 3**: Implementation (build + verify + review + merge) → `main` branch

**Can I use all three loops together?**
Yes. Typical workflow: Loop 1 (once per project) → Loop 2 (once per feature) → Loop 3 (continuous queue processing).

**Do I need all three loops?**
No. Each is independent. You can use just Loop 3 if you already have ticket specs.

**Loop 3 Specific**

**Where do my code changes end up?**
In `dev/<ticket_id>` branches. Agent asks you to merge to `main` after review passes. You decide yes/no.

**Can I use codoop-flow with existing ticket systems?**
Yes. Just populate `docs/tickets/pending/` with the required structure. Loop 2 generates that format, but you can create it manually too.

**What if I don't want continuous `/loop`?**
Run single tickets manually: "Use the codoop-execute skill to run a ticket." Agent processes one ticket, asks to merge, then stops.

**What happens if verify/review fails?**
Agent automatically retries (up to 3 times by default). If still failing after budget exhausted, the ticket moves to `failed/` with `healing_report.md` explaining why. Its worktree and uncommitted changes are retained for human recovery; the report gives its path and branch.

**Can multiple agents process tickets in parallel?**
Currently no — only one ticket in `in_progress/` at a time. Future version could support multiple.

**`/plugin marketplace add` throws an SSH error?**
It clones over SSH by default. Without an SSH key, use the full HTTPS URL: `/plugin marketplace add https://github.com/Codoop/codoop-flow.git`.

**`setup` reports "not a git repository"?**
The target project must be `git init`-ed first. codoop-flow flows tickets inside your project's git repo.

**The agent says it can't find the skill / command?**
For Claude Code, confirm the plugin is installed. Then verify the guardrail is in place: `python3 skills/codoop-execute/scripts/codoop_tools.py --config codoop_flow.toml status`.

**A ticket is stuck in `failed/`?**
Open `failed/<id>/healing_report.md` for why self-heal ran out of budget — usually tests too strict or the spec too ambitious for the healing budget. Edit the ticket and push it back to `pending/`.

---

## Learn more

### Deep Dives

- [`docs/loop-3-agent-centric.md`](./docs/loop-3-agent-centric.md) — Complete Loop 3 mechanics (worktrees, verification, local workflow)
- [`docs/engineering-design.md`](./docs/engineering-design.md) — The three-loop design blueprint
- [`docs/install.md`](./docs/install.md) — Install guides for each coding agent

### Skill READMEs

- [`skills/codoop-discover/README.md`](./skills/codoop-discover/README.md) — Loop 1 details
- [`skills/codoop-ticket/README.md`](./skills/codoop-ticket/README.md) — Loop 2 details
- [`skills/codoop-execute/SKILL.md`](./skills/codoop-execute/SKILL.md) — Loop 3 instructions (what the Agent reads)
- [`skills/codoop-ux-walkthrough/SKILL.md`](./skills/codoop-ux-walkthrough/SKILL.md) — Persona walkthrough and experience report

---

<div align="center">
MIT License
</div>
