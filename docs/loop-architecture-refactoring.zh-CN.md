# 三环架构重构计划：独立运行设计

## 核心需求

**每个环（Loop）都应该能够抛开其他两个环独立运行。**

这意味着：
- Loop 1（Venture-Discovery）可单独使用 ✅ （已独立，只需 codoop-discover skill）
- Loop 2（Human-Centric）可单独使用 ❌ （当前依赖 codoop-flow 的工具库）
- Loop 3（Agent-Centric）可单独使用 ⚠️ （有部分共享依赖）

---

## 问题分析

### 当前架构问题

所有工具都集中在 `skills/codoop-flow/scripts/codoop_flow/`：

```
codoop_flow/
├── config.py           ← 配置（被 Loop 2 和 Loop 3 共用）
├── ticket.py           ← 工单数据结构（被 Loop 2 和 Loop 3 共用）
├── tickets_cli.py      ← Loop 2 CLI 工具（工单设计）
├── gitutil.py          ← git 工具（被 Loop 2 和 Loop 3 共用）
├── ignore.py           ← .gitignore 工具（被 Loop 2 和 Loop 3 共用）
├── verify.py           ← Loop 3 工具（验证）
└── worktree.py         ← Loop 3 工具（worktree 管理）
```

**问题：**
1. Loop 2 用户无法独立使用，必须依赖 codoop-flow skill 中的工具
2. Loop 3 用户无法独立使用，必须依赖 codoop-flow skill 中的工具
3. 代码混在一起，关注点混杂

---

## 重构目标

### 架构原则

1. **独立性** — 每个环可以完全独立运行，无需其他环的代码
2. **最小共享** — 只在必要时共享工具（如 config.py）
3. **清晰定位** — 每个 skill 的 scripts/ 中只包含该环所需的工具
4. **一致性** — 三个环使用相同的配置格式和工单结构

### 目标结构

```
skills/
├── codoop-discover/               (Loop 1 - 已独立)
│   ├── SKILL.md
│   └── README.md
│
├── codoop-ticket/                 (Loop 2 - 需要重构)
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   │   ├── codoop-ticket.py       ← 第二环 CLI（ticket init/validate/promote）
│   │   └── codoop_flow_lib/       ← Loop 2 专用库
│   │       ├── config.py          (共用配置模块)
│   │       ├── ticket.py          (共用工单结构)
│   │       ├── tickets_cli.py     (Loop 2 工单管理)
│   │       ├── gitutil.py         (共用 git 工具)
│   │       ├── ignore.py          (共用 ignore 工具)
│   │       └── __init__.py
│   └── specs/                     ← SKILL 文档引用的示例/模板
│
├── codoop-flow/                   (Loop 3 - 需要重构)
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/                    (3 个内部 UI personas)
│   │   ├── testing-evidence-collector.md
│   │   ├── testing-reality-checker.md
│   │   └── engineering-technical-writer.md
│   └── scripts/
│       ├── codoop_tools.py        ← 第三环 CLI（pick/verify/finish/fail）
│       └── codoop_flow_lib/       ← Loop 3 专用库
│           ├── config.py          (共用配置模块 - 副本或导入)
│           ├── ticket.py          (共用工单结构 - 副本或导入)
│           ├── verify.py          (Loop 3 验证)
│           ├── worktree.py        (Loop 3 worktree)
│           ├── gitutil.py         (共用 git 工具)
│           ├── ignore.py          (共用 ignore 工具)
│           └── __init__.py
│
├── spec-driven-development/       (Loop 2 支持 skill)
├── planning-and-task-breakdown/   (Loop 2 支持 skill)
├── definition-of-done/            (Loop 2 支持 skill)
├── incremental-implementation/    (Loop 3 支持 skill)
├── debugging-and-error-recovery/  (Loop 3 支持 skill)
├── test-driven-development/       (Loop 3 支持 skill)
│
└── _shared/
    └── agents/                    (共用 personas)
        ├── alignment-agent.md
        ├── ...
        ├── code-reviewer.md
        ├── security-auditor.md
        └── test-engineer.md
```

---

## 重构步骤

### 第 1 步：分析共享库需求

**绝对必须共享的（3 个）：**
- `config.py` — 配置加载，定义 Config 类和目录结构
- `ticket.py` — 工单数据结构（Ticket 类）
- `gitutil.py` — git 工具函数

**可选共享的（2 个）：**
- `ignore.py` — 生成文件过滤（可各自实现或共享）

**Loop 2 专用（2 个）：**
- `tickets_cli.py` — 工单生命周期（draft 相关）

**Loop 3 专用（2 个）：**
- `verify.py` — 测试和验证
- `worktree.py` — worktree 管理

### 第 2 步：共享库的处理方案

有三种方案可选：

#### **方案 A：复制共享库（推荐用于完全独立性）**

```
skills/codoop-ticket/scripts/codoop_flow_lib/
├── config.py          (从 codoop-flow 复制)
├── ticket.py          (从 codoop-flow 复制)
├── gitutil.py         (从 codoop-flow 复制)
├── ignore.py          (从 codoop-flow 复制)
├── tickets_cli.py     (仅 Loop 2 需要)
└── __init__.py

skills/codoop-flow/scripts/codoop_flow_lib/
├── config.py          (或保持原有)
├── ticket.py
├── gitutil.py
├── ignore.py
├── verify.py          (仅 Loop 3 需要)
├── worktree.py        (仅 Loop 3 需要)
└── __init__.py
```

**优点：** 完全独立，Loop 2 和 Loop 3 可各自更新依赖
**缺点：** 代码重复，更新时需要同步

#### **方案 B：符号链接共享库（需要 Git LFS 或特殊处理）**

```
skills/codoop-ticket/scripts/codoop_flow_lib/
├── config.py          → ../../codoop-flow/scripts/codoop_flow_lib/config.py
├── ticket.py          → ../../codoop-flow/scripts/codoop_flow_lib/ticket.py
├── gitutil.py         → ../../codoop-flow/scripts/codoop_flow_lib/gitutil.py
├── ignore.py          → ../../codoop-flow/scripts/codoop_flow_lib/ignore.py
└── tickets_cli.py     (本地实现)
```

**优点：** 单一真理源，更新自动同步
**缺点：** 符号链接不是所有环境都支持（Windows）

#### **方案 C：顶层 lib，两个环都导入（需要 Python path 配置）**

```
scripts/codoop_libs/     ← 项目顶层
├── config.py
├── ticket.py
├── gitutil.py
└── ignore.py

skills/codoop-ticket/scripts/codoop_flow_lib/
├── __init__.py         (re-export 来自 scripts/../../../codoop_libs/)
└── tickets_cli.py

skills/codoop-flow/scripts/codoop_flow_lib/
├── __init__.py         (re-export 来自 scripts/../../../codoop_libs/)
├── verify.py
└── worktree.py
```

**优点：** 真正的单一真理源，无重复
**缺点：** 需要配置 Python path，移植性差

---

### 推荐方案：A（复制共享库）

**理由：**
1. 每个环都能完全独立运行（即使 codoop-flow 项目不存在，Loop 2 也能独立使用）
2. 实现简单，无需符号链接或特殊配置
3. 可以各自演进，如果需要同步再统一
4. 符合"抛开其他两个环也能独立运行"的需求

---

## 具体改造方案

### Loop 2 改造（codoop-ticket）

#### 创建 codoop-ticket/scripts/ 目录结构

```bash
skills/codoop-ticket/scripts/
├── codoop-ticket.py                      ← 第二环 CLI
├── codoop_flow_lib/
│   ├── __init__.py
│   ├── config.py                         ← 从 codoop-flow 复制
│   ├── ticket.py                         ← 从 codoop-flow 复制
│   ├── gitutil.py                        ← 从 codoop-flow 复制
│   ├── ignore.py                         ← 从 codoop-flow 复制
│   └── tickets_cli.py                    ← 从 codoop-flow 的 tickets_cli.py 复制
└── __pycache__/
```

#### codoop-ticket.py 内容

从 `codoop-flow/scripts/codoop.py` 派生，**只保留** ticket 子命令：

```python
#!/usr/bin/env python3
"""codoop-ticket — Human-Centric ticket design CLI (Loop 2).

Standalone tool for designing work tickets: init draft → fill PRD/Spec/Plan → promote to pending.

    python codoop-ticket.py ticket init <id> --config <toml> [--title "..."]
    python codoop-ticket.py ticket validate <id> --config <toml>
    python codoop-ticket.py ticket promote <id> --config <toml>
    python codoop-ticket.py ticket update-metadata <id> --config <toml>

This tool is completely independent of codoop-flow (Loop 3).
It only requires a codoop_flow.toml pointing at the target repo.
"""

from pathlib import Path
import argparse
import sys

from codoop_flow_lib.config import load_config
from codoop_flow_lib.tickets_cli import (
    init_draft, promote, validate_draft, 
    update_metadata_from_docs, write_metadata
)

# ... (只包含 _cmd_ticket_* 函数，删除 setup 和 install)

def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop-ticket", description="Loop 2: Human-Centric ticket design")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ticket = sub.add_parser("ticket", help="ticket lifecycle (draft -> pending)")
    tsub = p_ticket.add_subparsers(dest="ticket_command", required=True)

    for name, func, extra in (
        ("init", _cmd_ticket_init, True),
        ("validate", _cmd_ticket_validate, False),
        ("update-metadata", _cmd_ticket_update_metadata, False),
        ("promote", _cmd_ticket_promote, False),
    ):
        sp = tsub.add_parser(name, help=f"{name} a draft ticket")
        sp.add_argument("ticket_id", help="e.g. ticket_001")
        sp.add_argument("--config", default=None, help="path to codoop_flow.toml")
        if extra:
            sp.add_argument("--title", default="", help="ticket title")
            sp.add_argument("--language", default="auto", choices=["auto", "zh", "en"],
                          help="template language")
        sp.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
```

#### 更新 codoop-ticket SKILL.md

在 SKILL.md 中添加 CLI 使用说明：

```markdown
## 使用 CLI 工具

对于想要在自己的开发流程中使用 Loop 2 的用户，可以直接运行 CLI：

### 设置项目

```bash
python codoop-ticket.py setup <target-repo> --config <path-to-toml>
```

### 设计工单

```bash
# 1. 初始化工单草稿
python codoop-ticket.py ticket init ticket_001 --config codoop_flow.toml --title "Add user search"

# 2. 编辑 module_prd.md + spec.md
# （手动在编辑器中编写）

# 3. 验证工单完整性
python codoop-ticket.py ticket validate ticket_001 --config codoop_flow.toml

# 4. 将工单从 drafts/ 提升到 pending/
python codoop-ticket.py ticket promote ticket_001 --config codoop_flow.toml
```

## 完全独立使用

Loop 2 可以完全独立使用，无需 codoop-flow 或任何其他环的代码。
只需要一个指向目标项目的 `codoop_flow.toml` 配置文件。
```

### Loop 3 保留原样

Loop 3（codoop-flow）的 `scripts/codoop_flow/` 继续存在，不需要改动。

但如果要让 Loop 3 也完全独立，可以按同样的方式在 `codoop-flow/scripts/codoop_flow_lib/` 中维护一份共享库的副本。

---

## 改造工作量

| 任务 | 工作量 | 说明 |
|---|---|---|
| 复制 codoop_flow_lib/ 到 codoop-ticket/scripts/ | 5 分钟 | 复制 5 个文件 |
| 创建 codoop-ticket/scripts/codoop-ticket.py | 10 分钟 | 从 codoop.py 派生，删除 setup/install |
| 更新 codoop-ticket SKILL.md 添加 CLI 文档 | 10 分钟 | 补充 CLI 使用说明 |
| 创建 codoop-ticket/README.md（可选） | 10 分钟 | 说明独立使用 |
| 验证 Loop 2 独立运行 | 10 分钟 | 测试 codoop-ticket.py |
| **合计** | **~45 分钟** | |

---

## 与 Loop 3 Sub-Skills 提升的整合

这个改造可以与前面的"Loop 3 Sub-Skills 提升"并行进行：

### 改造总体规划

```
Phase 1a（这份文档）：Loop 2 独立化
- 复制共享库到 codoop-ticket/scripts/codoop_flow_lib/
- 创建 codoop-ticket.py
- 更新 SKILL.md 文档
- 工作量：~45 分钟

Phase 1b（Loop 3 Sub-Skills 提升）：Loop 3 能力提升
- 提升 incremental-implementation 等 3 个 skills
- 提升 code-reviewer 等 3 个 agents
- 删除 references/
- 工作量：~36 分钟

Phase 2（可选）：Loop 3 独立化
- 复制共享库到 codoop-flow/scripts/codoop_flow_lib/（如果需要）
- 更新 codoop_tools.py 导入路径
- 工作量：~20 分钟
```

---

## 完成后的效果

### Loop 1 用户
```bash
/skill codoop-discover "我想做一个 SaaS 项目管理工具"
# 完全独立，输出 docs/backlog/
```

### Loop 2 用户
```bash
python skills/codoop-ticket/scripts/codoop-ticket.py ticket init ticket_001 --config codoop_flow.toml
# 完全独立，无需 codoop-flow
```

或在 AI 编码工具中：
```
/skill codoop-ticket 设计一个用户搜索功能
# 在会话内协作设计工单
```

### Loop 3 用户
```bash
python skills/codoop-flow/scripts/codoop_tools.py --config codoop_flow.toml pick
# 完全独立，从 pending/ 拾起工单执行
```

或在 AI 编码工具中：
```
/skill codoop-flow 针对 codoop_flow.toml 运行工单
# 在会话内执行第三环
```

---

## 待讨论

1. **是否采用方案 A（复制）？** 还是考虑其他方案？
2. **Loop 3 是否也需要独立化？** （复制共享库到 codoop-flow 中）
3. **全局 setup 命令的位置？** setup 目前在 codoop.py 中，应该保留在 codoop-flow 还是移到 codoop-ticket？

