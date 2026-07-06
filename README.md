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

**You steer Codex or Claude in plain language; the grunt work is backstopped by a script guardrail.** The thinking (writing code, self-healing, review judgment, doc sync) happens in the active agent session; the mechanical, must-be-exact work (claiming tickets, managing the git worktree, running tests, enforcing the edit-scope whitelist, committing) goes to a deterministic CLI that can't hallucinate. It's a portable tool with no business code of its own — point one `codoop_flow.toml` at the project you actually want to build.

```
        you say one line                       you decide whether to push
             │                                     ▲
             ▼                                     │
  ┌───────────────── Codex/Claude reads SKILL.md and orchestrates ──────────────┐
  │                                                                             │
  │   pick ──▶ build ──▶ verify ──▶ review ──▶ ship docs ──▶ finish            │
  │ [script] [agent]   [script]  [reviewers] [agent]       [script]           │
  │  claim    write     run tests  multi-      sync docs     commit &          │
  │  ticket   code      +scope     review                    archive           │
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
cp -R skills/codoop-flow "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The bundled discovery CLI also accepts `--agent codex-cli`; `--agent codex` is
an alias for the same local `codex` command.

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

The discovery CLI accepts both `--agent claude-code` and `--agent claude`; both
launch the local `claude` command.

**Prerequisites**: the target project is a git repo; the machine has `python3` (standard library only, zero third-party deps).

---

## Quick start

**① Onboard your project** (creates the ticket dirs + generates config):

In Codex, ask:

```text
Use $codoop-flow to set up this repo for codoop-flow.
```

Or run the CLI manually from a local clone:

```bash
python3 skills/codoop-flow/scripts/codoop.py setup /path/to/your/repo \
  --config /path/to/your/repo/codoop_flow.toml
```

**② Drop a ticket** into `your-repo/docs/tickets/pending/ticket_001/`, containing at least a `metadata.json` ([fields below](#ticket-metadatajson)) and a spec doc.

**③ Say one line in Codex or Claude Code:**

```
Use $codoop-flow to run a ticket against codoop_flow.toml
```

The agent runs the whole pipeline, commits the result to the `dev/<id>` branch, and archives it to `done/`. **Whether to push is up to you.**

To keep working the queue continuously, use your agent's scheduler. In Claude Code:

```
/loop 5m run the codoop-flow skill against codoop_flow.toml
```

---

## How it works

Once installed you barely need to remember commands — **the skill is written for the coding agent to read**. You say one line, and the agent follows the skill to chain the whole thing together:

1. **Skill orchestration** (`SKILL.md`): Codex/Claude reads it and knows what order to do things in.
2. **Script guardrail** (`codoop_tools.py`): the work that must be 100% exact and never guessed — claim a ticket, create the isolated worktree, run tests, enforce "only edit whitelisted files," commit and archive.
3. **Review personas**: after tests pass, the agent runs code-reviewer / security-auditor / test-engineer, etc. with subagents if available or serially otherwise; approval must be **unanimous**, or the ticket goes back to self-heal (UI tickets add two personas that actually look at screenshots).

In a nutshell: **thinking goes to the agent, counting-and-checking goes to the script.**

<details>
<summary>Filing tickets by hand (expand if you don't want the agent to do it)</summary>

After `setup`, you can also use the human-facing CLI to turn an idea into a ticket:

```bash
# Draft: scaffold metadata + empty docs under drafts/
python3 skills/codoop-flow/scripts/codoop.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
# Edit drafts/ticket_001/: module_prd.md (business), spec.md (contract + files_to_edit whitelist)
python3 skills/codoop-flow/scripts/codoop.py ticket validate ticket_001 --config codoop_flow.toml   # check required docs
python3 skills/codoop-flow/scripts/codoop.py ticket promote  ticket_001 --config codoop_flow.toml   # drafts → pending
```

To explore a brand-new idea (multi-role design session, output to `docs/backlog/`):

```bash
python3 skills/codoop-flow/scripts/codoop.py discover --agent codex-cli --config codoop_flow.toml "an idea for an XX app"
# aliases also work: --agent codex, --agent claude-code, --agent claude
```
</details>

---

## Ticket metadata.json

```json
{
  "ticket_id": "ticket_001",
  "title": "add hello module",
  "modules": ["backend"],
  "test_command": {"backend": "bash script/test-backend.sh"},
  "files_to_edit": ["backend/**"],
  "max_healing_attempts": 3,
  "ui_capture": false
}
```

| Field | Meaning |
|---|---|
| `modules` | Modules involved; each must have an entry in `test_command` |
| `test_command` | module → shell command; `verify` runs one per module |
| `files_to_edit` | **whitelist globs** (fnmatch syntax). If the agent edits a file outside the whitelist, `verify` fails |
| `max_healing_attempts` | self-heal retry budget (default 3) |
| `ui_capture` | when true: the test script must write screenshots to `$CODOOP_QA_SCREENSHOT_DIR` (no screenshots = hard fail), and review adds 2 UI personas that actually look at the images |

Required: `ticket_id / title / modules / test_command / files_to_edit`.

---

<details>
<summary>Guardrail CLI reference (<code>codoop_tools.py</code>, called by the agent automatically — you rarely type it)</summary>

Every subcommand takes `--config <toml>` and emits JSON.

| Subcommand | Behavior |
|---|---|
| `status` | Print tickets per stage |
| `pick` | Claim the oldest pending ticket → move to in_progress → create worktree (`dev/<id>` branch). If one is already in_progress, report it instead of picking a new one |
| `verify <id>` | In the worktree: run tests + edit-scope whitelist + (UI) screenshot triple hard gate |
| `finish <id> --message` | Commit (excluding generated noise) to `dev/<id>` → move to done → remove worktree |
| `fail <id> --report` | Move to failed → write `healing_report.md` → remove worktree |

</details>

---

## Repository layout

```
codoop-flow/
├── codoop_flow.toml.example       # config sample
├── .agents/plugins/marketplace.json # Codex marketplace manifest
├── .claude-plugin/                # Claude Code plugin manifests
├── .codex-plugin/                 # Codex plugin manifest
├── skills/codoop-flow/            # ★self-contained Codex/agent skill package
│   ├── SKILL.md                   #   Agent-loop orchestration guide
│   ├── agents/openai.yaml         #   Codex UI/discovery metadata
│   ├── scripts/                   #   guardrail CLI + human CLI + deterministic modules
│   └── references/                #   review personas / sub-skills / discovery sub-agents
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
| Codex CLI | ✅ first-class | same plugin install flow; discovery accepts `--agent codex-cli` / `--agent codex` |
| Claude Code | ✅ first-class | plugin marketplace (see [Install](#install)); `--agent claude-code` also works |
| Claude CLI | ✅ first-class | `--agent claude` maps to the same local `claude` command used by Claude Code |
| Cursor / Gemini | 🟡 generic copy | copy the `skills/codoop-flow/` dir, see [`docs/install.md`](./docs/install.md) |

> If the host lacks a subagent tool, run the review personas serially in the same session.

---

## FAQ

**`/plugin marketplace add` throws an SSH error?**
It clones over SSH by default. Without an SSH key, use the full HTTPS URL: `/plugin marketplace add https://github.com/Codoop/codoop-flow.git`.

**`setup` reports "not a git repository"?**
The target project must be `git init`-ed first. codoop-flow flows tickets inside your project's git repo.

**The agent says it can't find the skill / command?**
For Codex, confirm `codex plugin list` shows `codoop-flow@codoop-flow` installed. For Claude Code, confirm the plugin is installed. Then verify the guardrail is in place: `python3 <skill>/scripts/codoop_tools.py --config codoop_flow.toml status`.

**A ticket is stuck in `failed/`?**
Open `failed/<id>/healing_report.md` for why self-heal ran out of budget — usually tests too strict or the `files_to_edit` whitelist too narrow.

---

## Learn more

- [`docs/engineering-design.md`](./docs/engineering-design.md) — the three-loop design blueprint
- [`docs/install.md`](./docs/install.md) — install guides for each coding agent

---

<div align="center">
MIT License
</div>
