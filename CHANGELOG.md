# Changelog

All notable changes to codoop-flow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  files. `verify` now has two hard gates: tests pass, and (for `ui_capture`
  tickets) UI screenshots. `files_to_edit` is also now an optional metadata field.

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
