# Loop 3 Sub-Skills Elevation Plan

## Problem Statement

The third loop (Loop 3: Agent-Centric) currently contains three powerful sub-skills buried in its internal references:

- `incremental-implementation` — building changes incrementally with test-verify-commit cycles
- `debugging-and-error-recovery` — systematic root-cause debugging and recovery
- `test-driven-development` — TDD discipline (red → green → refactor)

These skills live under `skills/codoop-flow/references/skills/` and are only referenced internally by the Loop 3 orchestration. However, they represent **universal engineering disciplines** that apply to any code development, not just Loop 3 tickets.

**Question:** Should these be elevated to top-level skills like Loop 2's four skills (codoop-ticket, spec-driven-development, planning-and-task-breakdown, definition-of-done)?

---

## Current Architecture

### Loop 3 Sub-Skills (Internal References)

Location: `skills/codoop-flow/references/skills/`

```
references/skills/
├── incremental-implementation/SKILL.md
├── debugging-and-error-recovery/SKILL.md
└── test-driven-development/SKILL.md
```

**Usage in Loop 3 workflow:**

| Step | Skill | Called By | Purpose |
|---|---|---|---|
| 2. Build | incremental-implementation | Agent (you write code) | Implement features in thin vertical slices, test after each slice, verify, commit, repeat |
| 4. Self-heal | debugging-and-error-recovery | Agent (on verify failure) | Triage failures to root cause; fix root cause with minimal change; retry within budget |
| (Optional) | test-driven-development | Agent (optional reference) | TDD discipline for test-first development |

### Loop 3 Review Personas (Also Internal)

Location: `skills/codoop-flow/references/agents/`

```
references/agents/
├── code-reviewer.md                    (Always runs)
├── security-auditor.md                 (Always runs)
├── test-engineer.md                    (Always runs)
├── testing-evidence-collector.md       (Runs if ui_capture=true)
├── testing-reality-checker.md          (Runs if ui_capture=true)
└── engineering-technical-writer.md     (Ship living docs phase)
```

**Status:** These are agent personas (read as system prompts), not skills. They don't need elevation — they're already being used in Loop 3's review pipeline.

---

## Comparison with Loop 2

Loop 2 elevated four related skills to top level:

```
skills/
├── codoop-ticket/                 ← orchestrator
├── spec-driven-development/       ← sub-skill, also standalone
├── planning-and-task-breakdown/   ← sub-skill, also standalone
└── definition-of-done/            ← reference skill
```

All are registered in marketplace.json and documented. Users can:
```
/skill spec-driven-development Design a technical spec independently
/skill planning-and-task-breakdown Break a spec into tasks independently
/skill codoop-ticket Orchestrate all three phases
```

Loop 3's sub-skills have similar potential for standalone use.

---

## Why Elevation Makes Sense

### 1. Universal Value

- **incremental-implementation**: Any multi-file code change benefits from this discipline. Not Loop-3-specific.
- **debugging-and-error-recovery**: Every developer faces test failures, build breaks, runtime bugs. This is a universal debugging framework.
- **test-driven-development**: TDD is a general development methodology applicable outside Loop 3.

### 2. Discovery & Reuse

- Users working on non-codoop-flow code might want: `/skill incremental-implementation How do I break this large refactor into safe steps?`
- Users stuck in debugging: `/skill debugging-and-error-recovery My tests are failing and I can't find why`
- Teams adopting TDD: `/skill test-driven-development How do I write this feature using TDD?`

### 3. Consistency

- Loop 2 already established the pattern: sub-skills are elevated to top level with README.md describing both standalone and integrated use.
- Elevating Loop 3's sub-skills follows the same pattern.

### 4. Reduced Coupling

- Currently, the sub-skills are only documented in Loop 3's SKILL.md.
- Elevating them makes them first-class citizens, reducing the coupling to Loop 3.
- Users of Loop 1 or Loop 2 or standalone workflows could benefit.

---

## Why Not Elevate

### 1. Context Dependency

- These skills are tightly coupled to Loop 3's pipeline steps.
- Outside Loop 3, they might need different entry points or adaptation.

### 2. Maturity

- They're internal implementation details of Loop 3.
- Elevating them signals they're stable public APIs.

### 3. Namespace Pollution

- Three new top-level skills adds noise to the skill list.
- Might be overkill if users rarely need them independently.

---

## Recommended Plan: Full Elevation

**Decision:** Elevate all three sub-skills to top-level in `skills/`.

**Rationale:**
1. These are universal engineering disciplines, not Loop-3-specific artifacts.
2. Consistent with Loop 2's elevation model.
3. Maximizes discoverability for users who need incremental development, debugging frameworks, or TDD.
4. Clear that these are *also* useful in Loop 3, but not *only* in Loop 3.

---

## Implementation Roadmap

### Phase 1: File Structure

```
skills/
├── incremental-implementation/
│   ├── SKILL.md                   (copied from references/skills/...)
│   ├── README.md                  (new: standalone + Loop 3 context)
│   └── examples/                  (optional: detailed examples)
├── debugging-and-error-recovery/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
└── test-driven-development/
    ├── SKILL.md
    ├── README.md
    └── examples/
```

### Phase 2: README Documentation

Each README.md should describe:

1. **What it is** — one-sentence summary
2. **When to use** — standalone scenarios
3. **How to invoke** — `/skill incremental-implementation ...`
4. **Workflow** — step-by-step discipline
5. **In Loop 3 context** — how it's used in the Agent-Centric loop
6. **Examples** — concrete scenarios and output

### Phase 3: Manifest Registration

Update `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`:

```json
{
  "name": "incremental-implementation",
  "description": "Build code changes incrementally: implement one slice, test, verify, commit, repeat. Use for large refactors, multi-file features, or whenever you're tempted to write >100 lines without testing.",
  "source": "local:skills/incremental-implementation"
},
{
  "name": "debugging-and-error-recovery",
  "description": "Systematic root-cause debugging. Stop the line, preserve evidence, apply structured triage, fix the root cause. Use when tests fail, builds break, or behavior doesn't match expectations.",
  "source": "local:skills/debugging-and-error-recovery"
},
{
  "name": "test-driven-development",
  "description": "Test-Driven Development discipline: write tests first, then code (red → green → refactor). Use when starting a new feature or when tests will clarify requirements before coding.",
  "source": "local:skills/test-driven-development"
}
```

### Phase 4: Documentation Updates

1. **docs/install.md** — Add a note that these three are also available as independent skills (in addition to being used in Loop 3)
2. **docs/loop-3-agent-centric.md** — Add a section: "Sub-Skills Used in Loop 3" pointing to their standalone documentation
3. **README.md** — Update the "Three Loops + Six Skills" section to mention these three as *bonus* skills for universal use
4. **skills/*/README.md** — Each sub-skill README cross-references Loop 3 where it's used

### Phase 5: CLI Integration (Optional)

Ensure `codoop install` and install documentation mention all nine skills:
- 6 top-level Loop skills (discover, ticket, spec, planning, dod, codoop-flow)
- 3 sub-skills now elevated (incremental-implementation, debugging-and-error-recovery, test-driven-development)

---

## Scope & Effort

| Task | Effort | Notes |
|---|---|---|
| Copy three skills to top level | 10 min | Simple file copy; no content changes |
| Write three README.md files | 1-2 hours | Describe standalone + Loop 3 context for each |
| Update manifests | 15 min | Add three entries to .claude-plugin/ and .agents/plugins/ |
| Update docs/install.md | 30 min | Add note about bonus skills |
| Update docs/loop-3-agent-centric.md | 30 min | Add section linking to elevated skills |
| Update README.md | 20 min | Mention nine skills (6+3) |
| (Optional) Create docs/skill-incremental-implementation.md etc. | 1-2 hours | Detailed user guides if desired |
| **Total** | **~3-5 hours** | Most time on documentation |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Duplicate files (in references/ + skills/) | Decision: Keep both, but document that skills/ is the authoritative version. references/ remains internal backup. Consider symlink from references/ to skills/ in future. |
| Unclear which version to update | In SKILL.md header, add comment: "Authoritative location: skills/incremental-implementation/. This skill is also referenced internally by Loop 3 at references/skills/incremental-implementation/" |
| Users confused about 9 skills vs 6 skills | Clarify in docs: "Six core skills per loop (discover, 4× human-centric, codoop-flow). Three additional universal skills (incremental, debugging, tdd) are also available." |
| Over-proliferation of skills | Set a bar: only elevate if truly universal (applies outside codoop-flow). Don't elevate Loop-3-specific agents (the five review personas). |

---

## Next Steps

1. **Get approval** — Is this plan aligned?
2. **Create task** — Implement Phase 1-4 above
3. **Test** — Verify /skill incremental-implementation works standalone
4. **Commit** — Single commit with all three skills, manifests, and docs
5. **Announce** — Update CHANGELOG / release notes

---

## Open Questions

1. Should we keep files in references/ after copying, or delete them?
   - **Recommendation:** Keep both. references/ is internal reference library; skills/ is public API.
   
2. Should we create separate docs/skill-incremental-implementation.md files, or just update docs/loop-3-agent-centric.md?
   - **Recommendation:** Add a "Skills Used" section in docs/loop-3-agent-centric.md with links to the top-level skills. If detailed guides are needed, create separate docs.

3. Should these three skills be marked as "bonus" or "advanced" in the install guide?
   - **Recommendation:** No. Treat them equally with the six core skills. Just clarify their purpose: "Universal engineering disciplines, useful in and out of codoop-flow."

