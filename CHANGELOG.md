# Changelog

All notable changes to codoop-flow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2026-07-24

### Changed

- **Ticket test commands removed.** `metadata.json.test_command` is no longer
  generated, required, or executed by `verify`. Existing entries are ignored
  and removed when ticket metadata is updated; `verify` now only enforces the
  optional `ui_capture` screenshot gate.
- **Ticket type selection is automatic.** `codoop-ticket` now chooses `feature`
  or `fix` from the request and scaffolds immediately. Phase progression and
  promotion still require their existing explicit approvals.
- **Verification distinguishes repository debt from ticket regressions.** Agents
  capture lint, build, focused-test, and UI evidence as independent steps, then
  compare exact diagnostic fingerprints with the pre-change baseline. Only new,
  changed, or diff-file diagnostics trigger self-healing or failure; unchanged
  unrelated diagnostics remain reported baseline warnings.

## [0.1.5-alpha.3] - 2026-07-17

### Added

- **Discovery Intake.** Product discovery now begins with short, plain-language
  question rounds and a human-confirmed Discovery Brief before role dispatch.
- **Ticket visual previews.** A user-visible feature can include a reviewed,
  self-contained `preview.html` before task breakdown. When
  `metadata.json.visual_preview` is true, the ticket cannot be promoted without
  that preview; Loop 3 reads it as design context.

### Changed

- **Visual-design output is simpler.** `interface/design-system.md` is the sole
  visual-design source of truth; it is visual-only and no `ui-mockups.md` is
  produced.
- **Target-project conventions are clearer.** `deploy/` is organized by
  business with a README index, while shared product assets live in `resources/`
  with an index and `audio/` directory.

## [0.1.5-alpha.2] - 2026-07-15

### Added

- **Confirmed ticket commits.** Promoting an explicitly approved ticket now
  creates a dedicated `docs(ticket): add <ticket_id>` commit that stages only
  the promoted ticket directory.

### Changed

- **Failed worktrees are retained for recovery.** When self-healing is
  exhausted, the ticket moves to `failed/` and its lease is released, while the
  worktree and uncommitted changes remain available. `healing_report.md` now
  records the recovery worktree path and branch.

## [0.1.5-alpha.1] - 2026-07-13

### Added

- **`codoop-ux-walkthrough` skill.** A standalone, persona-based walkthrough
  that uses the shared `persona-walkthrough` role to experience a runnable task
  and write an advisory `experience_report.md`. In Loop 3 it runs only after
  technical approval for applicable user-facing tickets; it never blocks
  release, changes code, triggers self-healing, or creates another ticket.

### Changed

- **Plain-language UI evidence choice in Loop 2.** During metadata review,
  `codoop-ticket` now detects user-visible screens, interactions, or task-flow
  changes and asks whether delivery should inspect the actual experience with
  saved screenshots and UI/UX review. It recommends `ui_capture: true` when
  appropriate and keeps it off for backend-only, infrastructure, refactoring,
  and internal-only work.

## [0.1.4] - 2026-07-08

### Removed

- **`files_to_edit` removed entirely.** The concept (introduced as a permission
  whitelist, downgraded to an advisory hint in 0.1.2) is gone from the whole
  pipeline: the `Ticket` model no longer carries the field, `ticket init` no
  longer scaffolds it, the spec.md template drops its "Editable Files" section,
  `update-metadata` no longer infers it (and actively strips a stale field from
  older tickets), and `pick`/`takeover` JSON output no longer includes it.
  Edit-scope guidance now lives solely in `spec.md` prose — the agent stays
  within the scope the spec describes. Old tickets that still contain the field
  keep working: unknown metadata fields are ignored.

### Added

- **Promote requires explicit user approval (skill rule).** `codoop-ticket`'s
  Finalize stage now mandates showing the ticket summary and getting user
  confirmation before `ticket promote`, and forbids `--force` without prior
  approval — `pending/` is the Loop 3 pickup queue, so an unreviewed promote
  means an agent may start building from an unapproved design.

### Fixed

- README links to the removed `LOOP3_EXECUTION_GUIDE.md` now point to
  `docs/loop-3-agent-centric.md`; stale `skills/codoop-flow/scripts/` CLI paths
  updated to the actual `codoop-ticket`/`codoop-execute` script locations; the
  removed `discover --agent` CLI example replaced with the in-session
  `/skill codoop-discover` invocation.

## [0.1.3] - 2026-07-08

### Added

- **Ticket runner lease (concurrency guard).** `pick` now mints a random
  `lease_token` when a ticket is claimed; the owning runner presents it on later
  commands to prove ownership. A second runner that tries to resume an active
  ticket without the token is turned away with `blocked_by_active_runner` (exit
  non-zero) and the worktree is left untouched — closing the gap where two
  runners could resume the same `in_progress` ticket and clobber each other's
  worktree. Leases never expire (liveness is a human's call); a stuck ticket
  waits for a manual `takeover` rather than being silently bypassed.
- **`takeover <ticket_id>` command.** Human-triggered hand-off that voids the old
  lease and mints a new one, handing the worktree to a fresh runner.
- **`status` in_progress detail.** Each `in_progress` entry now reports
  `held_by`, `acquired_at`, `todo` (e.g. `3/8`), `worktree_dirty`, and
  `dev_commits` so a human can see how far a ticket got before deciding whether
  to take it over.
- `verify` / `finish` / `fail` accept an optional `--lease <token>` ownership
  check; `finish` / `fail` release the lease on success.

### Fixed

- **Double-first-pick race.** The `pick` bookkeeping (read in_progress → move
  pending → write lease) now runs under an atomic pipeline lock, so two
  concurrent first-picks can no longer both claim the same pending ticket.

## [0.1.2] - 2026-07-07

### Added

- **Ticket types: `feature` (需求单) and `fix` (修复单).** A new optional
  `ticket_type` field in `metadata.json` (default `feature`) selects the Loop 2
  flow: `feature` requires `module_prd.md` + `spec.md`; `fix` skips PRD/Spec and
  uses a lightweight `bug_report.md` (Symptom / Reproduction / Root Cause /
  Expected Behavior / Scope). `plan.md` + `todo.md` are recommended for both.
  `codoop-ticket ticket init` gains `--type feature|fix`, and `codoop-ticket`
  infers the type from the request but always confirms before scaffolding. Loop 3
  derives the fallback commit prefix from the type (`feat` / `fix`). Fully
  back-compatible: tickets without `ticket_type` behave as `feature`.

### Changed

- **`files_to_edit` is now advisory, not an enforced gate.** Loop 3 `verify` no
  longer fails a ticket for edits outside the `files_to_edit` whitelist — the
  edit scope defined in `spec.md` / `metadata.json` is guidance the agent reads,
  not a hard gate. This unblocks tickets that legitimately need to touch adjacent
  files. `verify` keeps the `ui_capture` screenshot gate. `files_to_edit` is
  also now an optional metadata field.

## [0.1.1] - 2026-07-07

### Added

- **LOOP3_EXECUTION_GUIDE.md** — Comprehensive deep-dive into Loop 3 mechanics:
  - Complete workflow breakdown (Pick → Build → Verify → Review → Finish)
  - Worktree architecture and git lifecycle
  - Three verification gates (edit-scope, tests, UI screenshots)
  - Self-healing mechanism with budget tracking
  - Python script execution logic for all CLI commands
  - Local repository workflow with merge decision user control
  - Idempotency guarantees and edge case handling

- **Enhanced README.md**:
  - Clear project positioning as "three-loop AI-driven development system"
  - Loop 1 (Venture-Discovery) with design output → `docs/backlog/`
  - Loop 2 (Human-Centric) with ticket output → `docs/tickets/pending/`
  - Loop 3 (Agent-Centric) with 6-step workflow and key features
  - Loop-specific Quick Start sections
  - Continuous `/loop` mode and single-ticket manual mode examples
  - Design philosophy section: "thinking to agent, counting to script"
  - Key properties table highlighting local-first, idempotent, deterministic verification
  - Expanded FAQ (15+ questions) organized by category

- **Synchronized README.zh-CN.md**:
  - Complete Chinese translation of all English README updates
  - Culturally appropriate phrasing for Chinese audience
  - Consistent terminology across both versions

### Changed

- **Local-first workflow**: Changed from "push to remote" decision to "merge to main" decision
  - User controls merge timing, not remote push
  - All changes stay local until explicit user approval
  - Agent asks: "Merge `dev/<ticket_id>` to `main`?" after review passes

- **Loop 3 documentation focus**: Restructured to emphasize:
  - Idempotency: same `/loop` command safe to call repeatedly
  - Async-friendly: timing by Agent's `/loop` scheduler, not Python internals
  - Three hard gates: cannot be bypassed by AI hallucination

- **FAQ reorganization**: Split into four categories:
  - General questions (three-loop relationships, integration)
  - Loop 3 specific (verify/review/merge behavior, parallelization)
  - Installation troubleshooting
  - Common error scenarios with recovery steps

### Fixed

- Corrected misconception about worktree deletion = data loss
  - Clarified: worktree is temporary file system, branch/commits are permanent in `.git`
  - Added detailed explanation with data flow diagrams

### Documentation

- Added "Learn more" section with deep-dive links
- Linked to LOOP3_EXECUTION_GUIDE.md for detailed mechanics
- Cross-referenced Skill README files (codoop-discover, codoop-ticket, codoop-execute)

### Backward Compatibility

✅ **Fully backward compatible** — No breaking changes

- CLI interface unchanged: `pick`, `verify`, `finish`, `fail`, `status`
- `metadata.json` format unchanged
- `codoop_flow.toml` configuration unchanged
- SKILL.md workflow logic unchanged
- Ticket directory structure unchanged

### Migration Notes

**For existing users:**

1. **Claude Code / Codex plugin users**:
   - Plugins auto-sync from marketplace (may take a few minutes)
   - May need to restart IDE or reload plugin
   - No action required — pull latest version

2. **Local development (git clone)**:
   ```bash
   git pull origin main
   # That's it! No reinstall needed.
   ```

3. **Manual copy users**:
   ```bash
   mkdir -p ~/.codex/skills
   cp -R skills/codoop-execute ~/.codex/skills/
   ```

**No database migrations or config updates needed.**

---

## [1.0.0] - Earlier Releases

See git history for details on:
- Loop 1: Venture-Discovery skill implementation
- Loop 2: Human-Centric ticket design skill
- Loop 3: Agent-Centric execution framework
- Three-loop architecture foundation
- Initial CLI and guardrail system
