<div align="center">

# codoop-flow

**English** · [简体中文](./README.zh-CN.md)

**Turn "AI writes code" into a ticket pipeline with guardrails**
pick → build → verify → multi-review → archive, one ticket per closed loop

![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-8A63D2)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Zero deps](https://img.shields.io/badge/deps-zero-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

**You just steer Claude in plain language; the grunt work is backstopped by a script guardrail.** The thinking (writing code, self-healing, review judgment, doc sync) goes to Claude in-session; the mechanical, must-be-exact work (claiming tickets, managing the git worktree, running tests, enforcing the edit-scope whitelist, committing) goes to a deterministic CLI that can't hallucinate. It's a portable tool with no business code of its own — point one `codoop_flow.toml` at the project you actually want to build.

```
        you say one line                       you decide whether to push
             │                                     ▲
             ▼                                     │
  ┌──────────────────── Claude reads SKILL.md and orchestrates ─────────────────┐
  │                                                                             │
  │   pick ──▶ build ──▶ verify ──▶ review ──▶ ship docs ──▶ finish            │
  │ [script] [Claude]  [script]  [SubAgent]  [Claude]      [script]           │
  │  claim    write     run tests  multi-      sync docs     commit &          │
  │  ticket   code      +scope     review                    archive           │
  │ +worktree           gate       unanimous                 dev/<id>          │
  │                        │           │                                       │
  │                        └─ fail ────┴─▶ self-heal (retry within budget)     │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## Install

In Claude Code:

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

> SSH error? Use the full HTTPS URL: `/plugin marketplace add https://github.com/Codoop/codoop-flow.git`
> Local development: `claude --plugin-dir /path/to/codoop-flow`
> Other agents (Cursor / Codex / Gemini): see [`docs/install.md`](./docs/install.md).

**Prerequisites**: the target project is a git repo; the machine has `python3` (standard library only, zero third-party deps).

---

## Quick start

**① Onboard your project in one command** (creates the ticket dirs + generates config):

```bash
python3 <plugin-dir>/skills/codoop-flow/scripts/codoop.py setup /path/to/your/repo
```

**② Drop a ticket** into `your-repo/docs/tickets/pending/ticket_001/`, containing at least a `metadata.json` ([fields below](#ticket-metadatajson)) and a spec doc.

**③ Say one line in a Claude Code session:**

```
read the codoop-flow skill and run a ticket against codoop_flow.toml
```

Claude runs the whole pipeline, commits the result to the `dev/<id>` branch, and archives it to `done/`. **Whether to push is up to you.**

To keep working the queue continuously, use Claude Code's `/loop`:

```
/loop 5m run the codoop-flow skill against codoop_flow.toml
```

---

## How it works

Once installed you barely need to remember commands — **the skill is written for Claude to read**. You say one line, and Claude follows the skill to chain the whole thing together:

1. **Skill orchestration** (`SKILL.md`): Claude reads it and knows what order to do things in.
2. **Script guardrail** (`codoop_tools.py`): the work that must be 100% exact and never guessed — claim a ticket, create the isolated worktree, run tests, enforce "only edit whitelisted files," commit and archive.
3. **SubAgent review**: after tests pass, Claude uses the Task tool to dispatch reviewers (code-reviewer / security-auditor / test-engineer, etc.) in parallel; approval must be **unanimous**, otherwise it's kicked back to self-heal (UI tickets add two personas that actually look at screenshots).

In a nutshell: **thinking goes to Claude, counting-and-checking goes to the script.**

<details>
<summary>Filing tickets by hand (expand if you don't want Claude to do it)</summary>

After `setup`, you can also use the human-facing CLI to turn an idea into a ticket (`$SKILL` = the `skills/codoop-flow` dir inside the plugin):

```bash
# Draft: scaffold metadata + empty docs under drafts/
python3 $SKILL/scripts/codoop.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
# Edit drafts/ticket_001/: module_prd.md (business), spec.md (contract + files_to_edit whitelist)
python3 $SKILL/scripts/codoop.py ticket validate ticket_001 --config codoop_flow.toml   # check required docs
python3 $SKILL/scripts/codoop.py ticket promote  ticket_001 --config codoop_flow.toml   # drafts → pending
```

To explore a brand-new idea (multi-role design session, output to `docs/backlog/`):

```bash
python3 $SKILL/scripts/codoop.py discover --config codoop_flow.toml "an idea for an XX app"
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
| `files_to_edit` | **whitelist globs** (fnmatch syntax). If Claude edits a file outside the whitelist, `verify` fails |
| `max_healing_attempts` | self-heal retry budget (default 3) |
| `ui_capture` | when true: the test script must write screenshots to `$CODOOP_QA_SCREENSHOT_DIR` (no screenshots = hard fail), and review adds 2 UI personas that actually look at the images |

Required: `ticket_id / title / modules / test_command / files_to_edit`.

---

<details>
<summary>Guardrail CLI reference (<code>codoop_tools.py</code>, called by Claude automatically — you rarely type it)</summary>

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
├── .claude-plugin/                # Claude Code plugin manifests
├── skills/codoop-flow/            # ★self-contained skill package (copy the whole dir to other agents)
│   ├── SKILL.md                   #   Agent-loop orchestration guide
│   ├── scripts/                   #   guardrail CLI + human CLI + deterministic modules
│   └── references/                #   review personas / sub-skills / discovery sub-agents
├── tests/test_skeleton.py         # 12 skeleton tests (subprocess CLI calls, no AI)
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

The skill is a self-contained directory; any coding agent that can read files, run Bash, and dispatch sub-agents can use it.

| Agent | Status | How to install |
|---|---|---|
| Claude Code | ✅ first-class | plugin marketplace (see [Install](#install)) |
| Cursor / Codex / Gemini | 🟡 generic copy | copy the `skills/codoop-flow/` dir, see [`docs/install.md`](./docs/install.md) |

> If a non-Claude agent lacks an equivalent to the Task tool (dispatching sub-agents), the review step may need to be rewritten as serial.

---

## FAQ

**`/plugin marketplace add` throws an SSH error?**
It clones over SSH by default. Without an SSH key, use the full HTTPS URL: `/plugin marketplace add https://github.com/Codoop/codoop-flow.git`.

**`setup` reports "not a git repository"?**
The target project must be `git init`-ed first. codoop-flow flows tickets inside your project's git repo.

**Claude says it can't find the skill / command?**
Confirm the plugin is `install`-ed and the `codoop_flow.toml` path is correct. Manually verify the guardrail is in place: `python3 <plugin>/skills/codoop-flow/scripts/codoop_tools.py --config codoop_flow.toml status`.

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
