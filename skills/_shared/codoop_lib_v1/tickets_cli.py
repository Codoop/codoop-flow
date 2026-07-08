"""Human-Centric ticket lifecycle (design §4.1) — the deterministic part.

The intelligent work (writing PRD / spec / plan / todo) is the human's + their
product agent's job. This module only does the conveyor-belt plumbing around
that: scaffold a draft, validate it's complete, and promote it to pending/
(which the codoop-execute skill then picks up via codoop_tools.py).

    drafts/<id>/  --init-->  (human/AI fills docs)  --validate-->  --promote-->  pending/<id>/
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .ticket import METADATA_FILE, VALID_TICKET_TYPES, Ticket

# Docs the human authors, keyed by ticket_type. For "feature" tickets module_prd
# + spec are hard-required (a ticket with no business + no contract is not
# ready). For "fix" tickets only a bug_report is required (PRD/spec would be
# make-work for a small defect). plan/todo are recommended for both but not
# blocking (small tickets may inline them).
REQUIRED_DOCS = {
    "feature": ("module_prd.md", "spec.md"),
    "fix": ("bug_report.md",),
}
RECOMMENDED_DOCS = ("plan.md", "todo.md")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _drafts_dir(config: Config) -> Path:
    return config.tickets_dir / "drafts"


def init_draft(
    config: Config,
    ticket_id: str,
    title: str = "",
    language: str = "auto",
    ticket_type: str = "feature",
) -> Path:
    """Scaffold docs/tickets/drafts/<ticket_id>/ with a metadata stub + empty
    design docs. Returns the draft dir. Refuses to clobber an existing draft.

    Args:
        config: Config object
        ticket_id: Ticket identifier
        title: Ticket title
        language: Template language. "auto" (default) detects from title, "zh" or "en" explicit.
        ticket_type: "feature" (需求单, scaffolds module_prd.md + spec.md) or
            "fix" (修复单, scaffolds bug_report.md). plan.md + todo.md are
            scaffolded for both.
    """
    if ticket_type not in VALID_TICKET_TYPES:
        raise ValueError(
            f"ticket_type must be one of {VALID_TICKET_TYPES}, got {ticket_type!r}"
        )

    draft = _drafts_dir(config) / ticket_id
    if draft.exists():
        raise FileExistsError(f"draft already exists: {draft}")
    draft.mkdir(parents=True)

    # Detect language: if title contains Chinese characters, use Chinese; otherwise English
    if language == "auto":
        if title:
            has_cjk = any('一' <= c <= '鿿' for c in title)
            language = "zh" if has_cjk else "en"
        else:
            language = "zh"

    stub = {
        "ticket_id": ticket_id,
        "title": title or ticket_id,
        "ticket_type": ticket_type,
        "modules": ["backend"],
        "test_command": {"backend": "bash script/test-backend.sh"},
        "max_healing_attempts": 3,
        "ui_capture": False,
    }
    (draft / METADATA_FILE).write_text(
        json.dumps(stub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if language == "zh":
        if ticket_type == "fix":
            (draft / "bug_report.md").write_text(
                f"# {title or ticket_id} — Bug 修复单\n\n"
                "## 现象 (Symptom)\n> 用户/系统观察到的错误表现,附截图或日志。\n\n"
                "## 复现步骤 (Reproduction)\n> 1. ... 2. ... 3. → 出现 X(期望 Y)\n\n"
                "## 根因 (Root Cause)\n> 定位到的原因(可在修复中补充)。\n\n"
                "## 预期行为 (Expected Behavior)\n> 修好之后应该是什么样。\n\n"
                "## 影响范围 (Scope)\n> 受影响的模块 / 文件。\n",
                encoding="utf-8",
            )
        else:
            (draft / "module_prd.md").write_text(
                f"# {title or ticket_id} — 业务 PRD\n\n"
                "> 100% 纯业务描述,不涉及任何代码/表结构/API 字段。\n\n"
                "## 核心业务大图\n\n## 用户故事 (User Stories)\n\n"
                "## 业务流转状态图\n\n## Definition of Done (验收条件)\n",
                encoding="utf-8",
            )
            (draft / "spec.md").write_text(
                "# 技术规格 (Spec)\n\n> 基于 module_prd.md,定义 API 契约 / 数据 Schema / "
                "UI 交互。\n\n"
                "## API 契约\n\n## 数据 Schema\n\n## UI 交互约定\n",
                encoding="utf-8",
            )
        (draft / "plan.md").write_text(
            "# 执行步骤计划 (Plan)\n\n- 步骤 1: ...\n", encoding="utf-8"
        )
        (draft / "todo.md").write_text(
            "# 原子任务 (Todo)\n\n- [ ] [backend] ...\n", encoding="utf-8"
        )
    else:  # English
        if ticket_type == "fix":
            (draft / "bug_report.md").write_text(
                f"# {title or ticket_id} — Bug Fix\n\n"
                "## Symptom\n> The observed erroneous behavior; attach screenshots or logs.\n\n"
                "## Reproduction\n> 1. ... 2. ... 3. → X happens (expected Y)\n\n"
                "## Root Cause\n> The identified cause (may be filled in during the fix).\n\n"
                "## Expected Behavior\n> What it should do once fixed.\n\n"
                "## Scope\n> Affected modules / files.\n",
                encoding="utf-8",
            )
        else:
            (draft / "module_prd.md").write_text(
                f"# {title or ticket_id} — Business PRD\n\n"
                "> 100% business description, no code/schema/API details.\n\n"
                "## Business Overview\n\n## User Stories\n\n"
                "## State Flow\n\n## Acceptance Criteria\n",
                encoding="utf-8",
            )
            (draft / "spec.md").write_text(
                "# Technical Spec\n\n> Based on module_prd.md, define API contract / data schema / "
                "UI interactions.\n\n"
                "## API Contract\n\n## Data Schema\n\n## UI Interactions\n",
                encoding="utf-8",
            )
        (draft / "plan.md").write_text(
            "# Implementation Plan\n\n- Step 1: ...\n", encoding="utf-8"
        )
        (draft / "todo.md").write_text(
            "# Atomic Tasks (Todo)\n\n- [ ] [backend] ...\n", encoding="utf-8"
        )

    return draft


def _is_meaningfully_filled(path: Path) -> bool:
    """A doc counts as filled if it has non-heading, non-blockquote content —
    i.e. the human wrote something beyond the scaffolded headings."""
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">"):
            continue
        # Bare scaffold list markers ("- Step 1: ..." / "- [ ] ...") don't count.
        if s.rstrip(". ").endswith("...") or s in ("- [ ]", "-"):
            continue
        return True
    return False


def validate_draft(config: Config, ticket_id: str) -> ValidationResult:
    """Check a draft is ready to promote: metadata parses + required docs are
    meaningfully filled. Returns errors (blocking) and warnings (advisory)."""
    draft = _drafts_dir(config) / ticket_id
    errors: list[str] = []
    warnings: list[str] = []

    if not draft.exists():
        return ValidationResult(False, [f"draft not found: {draft}"])

    # metadata.json must parse + satisfy the Ticket schema. Its ticket_type
    # selects which docs are required; default to "feature" if metadata is
    # unreadable (the parse error above already reports the real problem).
    ticket_type = "feature"
    try:
        ticket = Ticket.load(draft)
        ticket_type = ticket.ticket_type
    except ValueError as e:
        errors.append(f"metadata invalid: {e}")

    for doc in REQUIRED_DOCS.get(ticket_type, REQUIRED_DOCS["feature"]):
        p = draft / doc
        if not p.exists():
            errors.append(f"missing required doc: {doc}")
        elif not _is_meaningfully_filled(p):
            errors.append(f"required doc still empty (only scaffold): {doc}")

    for doc in RECOMMENDED_DOCS:
        p = draft / doc
        if not p.exists() or not _is_meaningfully_filled(p):
            warnings.append(f"recommended doc empty: {doc}")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)


def update_metadata_from_docs(config: Config, ticket_id: str) -> dict:
    """Intelligently update metadata.json based on the design docs (spec, plan, todo).

    Infers:
    - modules: extracted from spec.md's "## Backend", "## Web", etc. section headers
    - test_command: recommended based on modules (can be overridden by user)

    Returns the updated metadata dict (but does NOT write to disk yet).
    User can review and accept/modify before validate().
    """
    draft = _drafts_dir(config) / ticket_id
    meta_path = draft / METADATA_FILE

    if not meta_path.exists():
        raise ValueError(f"metadata.json not found: {meta_path}")

    # Load current metadata
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    spec_path = draft / "spec.md"
    plan_path = draft / "plan.md"
    todo_path = draft / "todo.md"

    # Infer modules from spec.md section headers (e.g., "## Backend", "## Web")
    modules = set()
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        spec_lines = spec_text.splitlines()
        for line in spec_lines:
            if line.startswith("## "):
                section = line[3:].strip().lower()
                # Common module names
                if any(m in section for m in ["backend", "api", "server"]):
                    modules.add("backend")
                if any(m in section for m in ["web", "frontend", "react", "vue"]):
                    modules.add("web")
                if any(m in section for m in ["mobile", "ios", "android", "flutter"]):
                    modules.add("mobile")
                if any(m in section for m in ["desktop", "electron", "tauri"]):
                    modules.add("desktop")

    # Default to backend if nothing inferred
    if not modules:
        modules = {"backend"}

    modules = sorted(list(modules))

    # Infer test_command for each module (can be overridden by user)
    test_command = metadata.get("test_command", {})
    for module in modules:
        if module not in test_command:
            # Provide sensible defaults
            if module == "backend":
                test_command[module] = "bash script/test-backend.sh"
            elif module == "web":
                test_command[module] = "npm test -- --coverage"
            elif module == "mobile":
                test_command[module] = "flutter test"
            elif module == "desktop":
                test_command[module] = "cargo test"

    # Update metadata dict
    updated = {
        **metadata,
        "modules": modules,
        "test_command": test_command,
    }
    updated.pop("files_to_edit", None)

    return updated


def write_metadata(config: Config, ticket_id: str, metadata: dict) -> None:
    """Write updated metadata dict to metadata.json."""
    draft = _drafts_dir(config) / ticket_id
    meta_path = draft / METADATA_FILE
    meta_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )


def promote(config: Config, ticket_id: str) -> Path:
    """Validate, then move drafts/<id> -> pending/<id> so the codoop-execute skill
    can pick it up. Raises ValueError if validation fails."""
    result = validate_draft(config, ticket_id)
    if not result.ok:
        raise ValueError(
            "cannot promote — validation failed:\n"
            + "\n".join(f"  - {e}" for e in result.errors)
        )
    draft = _drafts_dir(config) / ticket_id
    config.pending_dir.mkdir(parents=True, exist_ok=True)
    dest = config.pending_dir / ticket_id
    if dest.exists():
        raise FileExistsError(f"pending ticket already exists: {dest}")
    shutil.move(str(draft), str(dest))
    return dest
