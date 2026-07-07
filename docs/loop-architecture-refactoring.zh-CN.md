# 三环架构重构计划：文件系统协作 + 代码独立

## 核心需求

**三个环通过文件系统协作，代码上完全独立。**

- Loop 1 → 独立输出到 `docs/backlog/`
- Loop 2 → 读 `docs/backlog/`，独立输出到 `docs/tickets/pending/`
- Loop 3 → 读 `docs/tickets/pending/`，独立输出到 `docs/tickets/done/`

**每个环都应该有自己的 CLI 和配置库，无任何代码耦合。**

现状：
- Loop 1 ✅ 已独立
- Loop 2 ❌ CLI 和库混在 codoop-flow 中
- Loop 3 ❌ CLI 和库混在 codoop-flow 中

---

## 问题分析

### 当前架构的耦合问题

所有工具都集中在 `skills/codoop-flow/scripts/codoop_flow/` 中：

```
codoop_flow/
├── config.py           ← 配置（被 Loop 2 和 Loop 3 共用）
├── ticket.py           ← 工单数据结构（被 Loop 2 和 Loop 3 共用）
├── tickets_cli.py      ← Loop 2 CLI 工具
├── gitutil.py          ← git 工具（被 Loop 2 和 Loop 3 共用）
├── ignore.py           ← .gitignore 工具（被 Loop 2 和 Loop 3 共用）
├── verify.py           ← Loop 3 工具
└── worktree.py         ← Loop 3 工具
```

**问题：**
1. Loop 2 的 CLI（codoop.py）混在 codoop-flow 中，用户无法单独使用 Loop 2
2. Loop 3 的 CLI（codoop_tools.py）和 Loop 2 共享同一个 codoop_flow/ 库
3. 无法清晰地：
   - 给 Loop 2 用户一个独立的工具集
   - 给 Loop 3 用户一个独立的工具集
   - 三个环各自进化而不影响其他环

### 设计理念：文件系统协作

三个环不通过代码调用，而通过文件系统来协作：

```
Loop 1 (codoop-discover)
  ↓ 输出文档
docs/backlog/
  ↑ Loop 2 读入
Loop 2 (codoop-ticket CLI)
  ↓ 输出文档
docs/tickets/pending/
  ↑ Loop 3 读入
Loop 3 (codoop-flow CLI)
  ↓ 输出代码 + 文档
docs/tickets/done/
```

**意义：**
- 三个环的代码库可以完全独立
- 不需要任何跨环的函数调用或导入
- 用户可以只安装自己需要的环
- 易于维护、测试、演进

---

## 重构目标

### 架构原则

1. **代码独立** — 每个环的 CLI 和库完全独立，无任何 import 依赖
2. **文件系统协作** — 三个环通过读写共同的目录结构来协作
3. **清晰定位** — 每个 skill 的 scripts/ 中只包含该环所需的工具
4. **一致性** — 同一对象（Config、Ticket）在各环中定义方式相同

### 关键点：不能有 import 跨环代码

```
❌ 不允许的：
skills/codoop-ticket/scripts/... 
  import from skills/codoop-flow/scripts/

✅ 允许的：
skills/codoop-ticket/scripts/codoop_flow_lib/config.py
skills/codoop-flow/scripts/codoop_flow_lib/config.py
（两个独立的、定义相同的文件）
```

### 目标结构

```
skills/
├── codoop-discover/               (Loop 1 - 已独立 ✓)
│   ├── SKILL.md
│   └── README.md
│
├── codoop-ticket/                 (Loop 2 - 独立 CLI + 库)
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   │   ├── codoop-ticket.py       ← Loop 2 专用 CLI
│   │   └── codoop_lib_v1/         ← Loop 2 独立库（版本化）
│   │       ├── config.py
│   │       ├── ticket.py
│   │       ├── tickets_cli.py
│   │       ├── gitutil.py
│   │       ├── ignore.py
│   │       └── __init__.py
│   └── templates/                 ← 工单模板（可选）
│
├── codoop-flow/                   (Loop 3 - 独立 CLI + 库)
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/                    (3 个内部 UI personas)
│   │   ├── testing-evidence-collector.md
│   │   ├── testing-reality-checker.md
│   │   └── engineering-technical-writer.md
│   └── scripts/
│       ├── codoop_tools.py        ← Loop 3 专用 CLI
│       └── codoop_lib_v1/         ← Loop 3 独立库（版本化，同 Loop 2）
│           ├── config.py
│           ├── ticket.py
│           ├── verify.py
│           ├── worktree.py
│           ├── gitutil.py
│           ├── ignore.py
│           └── __init__.py
│
├── spec-driven-development/
├── planning-and-task-breakdown/
├── definition-of-done/
├── incremental-implementation/
├── debugging-and-error-recovery/
├── test-driven-development/
│
└── _shared/agents/
```

**说明：**
- 两个 `codoop_lib_v1/` 完全独立，但代码应该一致（同步维护）
- 如果未来 Loop 2 需要不同的 config.py，可以演进到 v2
- 两个 CLI 工具（codoop-ticket.py 和 codoop_tools.py）完全独立

---

## 重构步骤

### 第 1 步：分析库的需求

**共同需要的（两个环都要）：**
- `config.py` — 配置加载，定义 Config 类和目录结构
- `ticket.py` — 工单数据结构（Ticket 类）
- `gitutil.py` — git 工具函数
- `ignore.py` — 生成文件过滤

**Loop 2 专用：**
- `tickets_cli.py` — 工单生命周期（draft 相关）

**Loop 3 专用：**
- `verify.py` — 测试和验证
- `worktree.py` — worktree 管理

### 第 2 步：复制策略（推荐）

**不能有任何 import 跨环，必须完全独立复制。**

```
skills/codoop-ticket/scripts/codoop_lib_v1/
├── __init__.py
├── config.py          (独立副本)
├── ticket.py          (独立副本)
├── gitutil.py         (独立副本)
├── ignore.py          (独立副本)
└── tickets_cli.py     (Loop 2 专用)

skills/codoop-flow/scripts/codoop_lib_v1/
├── __init__.py
├── config.py          (独立副本)
├── ticket.py          (独立副本)
├── gitutil.py         (独立副本)
├── ignore.py          (独立副本)
├── verify.py          (Loop 3 专用)
└── worktree.py        (Loop 3 专用)
```

**为什么不能用符号链接或导入：**
1. 符号链接在某些环境不支持（Windows、某些容器）
2. 导入会产生代码耦合（违反架构原则）
3. 两个环应该能各自打包、部署、演进

**版本化命名 (codoop_lib_v1)：**
- 如果未来 Loop 2 的配置需求改变，可以创建 codoop_lib_v2
- 向后兼容性由版本号管理，不需要复杂的协调

### 同步维护策略

虽然代码复制在两个地方，但应该：
1. 在 `skills/codoop-flow/scripts/codoop_lib_v1/` 中维护"参考实现"
2. 定期（如有改动）同步到 `skills/codoop-ticket/scripts/codoop_lib_v1/`
3. 在 git commit 时同时修改两处
4. 可选：创建脚本自动检查两个版本的一致性

---

## 具体改造方案

### Loop 2 改造（codoop-ticket）

#### 创建 codoop-ticket/scripts/ 结构

```bash
skills/codoop-ticket/scripts/
├── codoop-ticket.py              ← Loop 2 独立 CLI（新建）
└── codoop_lib_v1/                ← Loop 2 独立库（从 codoop-flow 复制）
    ├── __init__.py
    ├── config.py
    ├── ticket.py
    ├── gitutil.py
    ├── ignore.py
    └── tickets_cli.py
```

#### codoop-ticket.py 内容

从 `codoop-flow/scripts/codoop.py` 派生，**删除 setup 和 install，只保留 ticket**：

```python
#!/usr/bin/env python3
"""codoop-ticket — Human-Centric ticket design CLI (Loop 2).

Standalone: init draft → fill docs → promote to pending.

    python codoop-ticket.py ticket init <id> --config <toml> [--title "..."]
    python codoop-ticket.py ticket validate <id> --config <toml>
    python codoop-ticket.py ticket promote <id> --config <toml>
    python codoop-ticket.py ticket update-metadata <id> --config <toml>

Completely independent of codoop-flow (Loop 3). No cross-loop dependencies.
"""

from pathlib import Path
import argparse
import sys

# 导入本地独立库
from codoop_lib_v1.config import load_config
from codoop_lib_v1.tickets_cli import (
    init_draft, promote, validate_draft,
    update_metadata_from_docs, write_metadata
)

def _cmd_ticket_init(args) -> int:
    # ... (从 codoop.py 复制)
    pass

# ... (其他 ticket 命令)

def main() -> int:
    parser = argparse.ArgumentParser(prog="codoop-ticket", description="Loop 2: Design tickets")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ticket = sub.add_parser("ticket", help="ticket lifecycle")
    tsub = p_ticket.add_subparsers(dest="ticket_command", required=True)

    for name, func, extra in (
        ("init", _cmd_ticket_init, True),
        ("validate", _cmd_ticket_validate, False),
        ("update-metadata", _cmd_ticket_update_metadata, False),
        ("promote", _cmd_ticket_promote, False),
    ):
        sp = tsub.add_parser(name)
        sp.add_argument("ticket_id")
        sp.add_argument("--config", default=None)
        if extra:
            sp.add_argument("--title", default="")
            sp.add_argument("--language", choices=["auto", "zh", "en"], default="auto")
        sp.set_defaults(func=func)

    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
```

#### 更新 codoop-ticket SKILL.md

添加 CLI 文档部分，说明如何独立使用：

```markdown
## 独立使用 Loop 2

除了在 AI 编码工具中调用 skill，你也可以直接使用 CLI：

### 创建项目配置

```bash
# 一次性初始化（创建 docs/tickets/{drafts,pending,done,failed}/）
# setup 命令在 codoop-flow 中，通过以下方式调用
python path/to/codoop-flow/scripts/codoop_tools.py --help  # 查看 setup
```

### 设计工单

```bash
cd /path/to/target-repo

# 1. 初始化工单草稿
python path/to/codoop-ticket/scripts/codoop-ticket.py \
  ticket init ticket_001 --config codoop_flow.toml --title "Add user search"

# 2. 编辑工单文件
# （在编辑器中打开 docs/tickets/drafts/ticket_001/module_prd.md 和 spec.md）

# 3. 验证完整性
python path/to/codoop-ticket/scripts/codoop-ticket.py \
  ticket validate ticket_001 --config codoop_flow.toml

# 4. 提升到 pending/
python path/to/codoop-ticket/scripts/codoop-ticket.py \
  ticket promote ticket_001 --config codoop_flow.toml
```

## 完全独立

Loop 2 不依赖任何其他环的代码。即使没有 codoop-flow，Loop 2 也能完整运行。
```

### Loop 3 改造（codoop-flow）

#### 重命名库目录

```bash
skills/codoop-flow/scripts/
├── codoop_tools.py               (保持不变)
└── codoop_lib_v1/                ← 改名自 codoop_flow（版本化名称）
    ├── __init__.py
    ├── config.py
    ├── ticket.py
    ├── gitutil.py
    ├── ignore.py
    ├── verify.py
    └── worktree.py
```

#### 更新 codoop_tools.py 导入

```python
# 改为导入本地库
from codoop_lib_v1.config import Config, load_config
from codoop_lib_v1.ticket import Ticket
# 等等
```

#### 更新 codoop-flow SKILL.md

说明 setup 命令的位置（全局工具）：

```markdown
## 初始化项目

codoop-flow 提供 setup 命令初始化项目结构（全局工具）：

```bash
python skills/codoop-flow/scripts/codoop_tools.py setup <target-repo> --config codoop_flow.toml
```

这创建必要的目录和配置文件。

## 运行工单

```bash
python skills/codoop-flow/scripts/codoop_tools.py --config codoop_flow.toml pick
```

详见 Step 1-7 说明。
```

---

## 改造工作量

| 任务 | 工作量 |
|---|---|
| 复制 5 个文件到 codoop-ticket/scripts/codoop_lib_v1/ | 5 分钟 |
| 创建 codoop-ticket.py（从 codoop.py 派生） | 10 分钟 |
| 修改 codoop_lib_v1/ 的导入（config.py, ticket.py 等） | 5 分钟 |
| 更新 codoop-ticket SKILL.md 添加 CLI 文档 | 10 分钟 |
| 重命名 codoop-flow/scripts/codoop_flow/ → codoop_lib_v1/ | 5 分钟 |
| 更新 codoop_tools.py 和 codoop.py 的导入 | 10 分钟 |
| 更新 codoop-flow SKILL.md | 5 分钟 |
| 验证两个环独立运行 | 10 分钟 |
| **合计** | **~60 分钟** |

---

## 改造完成后的目录结构

```
skills/codoop-ticket/scripts/
├── codoop-ticket.py              ← Loop 2 CLI (独立)
└── codoop_lib_v1/
    ├── config.py
    ├── ticket.py
    ├── gitutil.py
    ├── ignore.py
    ├── tickets_cli.py
    └── __init__.py

skills/codoop-flow/scripts/
├── codoop_tools.py               ← Loop 3 CLI (独立)
├── codoop.py                     ← 保留（setup/install 命令）
└── codoop_lib_v1/
    ├── config.py
    ├── ticket.py
    ├── gitutil.py
    ├── ignore.py
    ├── verify.py
    ├── worktree.py
    └── __init__.py
```

---

## 三个环的协作方式

### 文件系统协作流

```
User: /skill codoop-discover "我想做...的功能"
↓ 在会话内协作，输出规格文档
docs/backlog/ {product/, interface/, architecture/, ...}

Human Engineer: 阅读 backlog，为每个功能创建工单
↓

User: python codoop-ticket.py ticket init ticket_001 --config ...
  （或 /skill codoop-ticket 设计...）
↓ 协作设计工单（PRD → Spec → Plan）
docs/tickets/drafts/ticket_001/ {module_prd.md, spec.md, plan.md, metadata.json}

Human Engineer: python codoop-ticket.py ticket promote ticket_001 --config ...
↓ 工单移至 pending/
docs/tickets/pending/ticket_001/

AI Agent: /skill codoop-flow 针对 codoop_flow.toml 运行工单
  或 python codoop_tools.py --config ... pick
↓ 执行工单（Build → Verify → Review → Ship）
docs/tickets/done/ticket_001/ + 代码提交
```

**关键点：** 每个环通过文件系统状态机协作，不通过代码依赖

---

## 与 Phase 1b（Sub-Skills 提升）的协调

这份改造（Loop 2/3 独立化）与前面的"Loop 3 Sub-Skills 提升"分离：

- **loop-3-skills-elevation-plan.zh-CN.md** — 提升 incremental-implementation 等 skills
- **loop-architecture-refactoring.zh-CN.md** — 分离 Loop 2/3 CLI 和库

两者都需要进行，可以：
1. 先做 Sub-Skills 提升（独立工作）
2. 再做架构重构（这份文档）

或交叉进行，最后一起提交。

---

## 完成后的用户体验

### 完整流程（三环协作）

```bash
# 初始化
python skills/codoop-flow/scripts/codoop_tools.py setup /path/to/project

# Loop 1：产品探索（在 AI 编码工具中）
/skill codoop-discover "我想做一个 SaaS 项目管理工具"
→ outputs: docs/backlog/

# Loop 2：工单设计（命令行或 AI 编码工具）
python skills/codoop-ticket/scripts/codoop-ticket.py ticket init ticket_001
# （编辑 docs/tickets/drafts/ticket_001/ 的文件）
python skills/codoop-ticket/scripts/codoop-ticket.py ticket promote ticket_001
→ moves to: docs/tickets/pending/

# Loop 3：工单执行（命令行或 AI 编码工具）
/skill codoop-flow 针对 codoop_flow.toml 运行工单
→ outputs: docs/tickets/done/ + 代码变更
```

### 单独使用某个环

```bash
# 只用 Loop 2？直接调用 codoop-ticket.py，无需其他环

# 只用 Loop 3？直接调用 codoop_tools.py，无需其他环

# 但如果要完整流程，需要 Loop 1→2→3 的协作
```

---

## 待讨论

1. **执行顺序** — Sub-Skills 提升先还是架构重构先？建议同步进行
2. **setup 命令** — 应该放在 Loop 2 还是 Loop 3？（建议 Loop 3，全局）
3. **codoop.py 的其他命令** — install 命令何去何从？（可保留在 codoop-flow 中作为全局工具）
4. **文档位置** — 合并两份改造文档还是分开？

