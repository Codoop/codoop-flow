# 第二环：人工设计（工单设计）

## 概述

**第二环**是 codoop-flow 三环系统的第二个环。是一套结构化的、人类驱动的流程，用于设计确定性的、机器可读的工单包，使 AI 编码代理能够可靠地执行。

**解决的问题：** AI 编码代理在给定模糊或不完整的需求时会失败或产生不可用的输出。第二环为人工（或产品经理）提供强制约束，生成如此精确的"工单包"，以至于自主编码引擎（第三环）可以不含歧义地执行它。循环防止范围蔓延、基于假设的实现和不可验证的输出。

**在管道中的位置：** 从 `docs/backlog/` 读取第一环输出 → 在 `docs/tickets/drafts/` 中生成工单包 → 提升到 `docs/tickets/pending/` 让第三环拾取。

---

## 工单类型

每个工单在 `metadata.json` 中带有 `ticket_type`（缺省 `feature`）。类型决定哪些文档是必需项，从而让流程贴合工作性质：

| 类型 | 适用 | 必需文档 | 推荐文档 |
|---|---|---|---|
| `feature`（需求单） | 由业务需求驱动的新能力 | `module_prd.md` + `spec.md` | `plan.md`、`todo.md` |
| `fix`（修复单） | 修复一个已存在的 bug / 缺陷 | `bug_report.md` | `plan.md`、`todo.md` |

`feature` 走下面完整的三阶段流程。`fix` 更轻量：跳过 PRD 与 Spec 阶段，改用 `bug_report.md` 记录缺陷（现象 / 复现 / 根因 / 预期行为 / 影响范围），然后进入任务拆解、metadata 推断、validate 与 promote。修复若确实涉及契约 / 数据模型变更，可自愿补一份 `spec.md`，但不强制。

`codoop-ticket` 会根据你的描述推断类型，并在生成脚手架前**总是请你确认**——类型是分流开关，判错会造成返工。通过 CLI 时用 `--type feature|fix` 显式指定。

---

## 快速开始

在任何 AI 编码工具中，说：

```
/skill codoop-ticket 我想设计一个电商产品搜索功能，支持关键词、分类和价格范围筛选
```

这个 skill 编排一个 PM 和架构师，以你为指挥官，通过三个阶段（PRD → Spec → 任务）引导你，生成准备好给第三环用的完整工单包。

---

## 工作流程

### 阶段 1 — 需求设计（module_prd.md）

1. **澄清** — `codoop-ticket` 询问关于范围、用户意图和验收标准的澄清问题
2. **上下文** — 从 `docs/backlog/product/`、`docs/backlog/interface/`、`docs/backlog/architecture/`、`docs/backlog/modules/` 读取第一环输出，把工单锚定在既有产品策略中
3. **起草** — PM 代理基于澄清问题写入 `module_prd.md`，包括业务概览、用户故事、状态图、验收标准
4. **审查** — 你审查并确认"这份 PRD 很好，移到 spec 阶段"

**硬约束：** `module_prd.md` 是 100% 纯业务语言。没有数据库表、没有 API 字段、没有代码细节。

### 阶段 2 — 技术规格（spec.md）

1. **触发** — 你确认阶段 1 完成；`codoop-ticket` 加载 `/skill spec-driven-development`
2. **设计** — 架构师代理基于确认的 `module_prd.md` 写入 `spec.md`
3. **内容** — 包括 API 契约（按平台：后端/网页/移动/桌面）、数据模式字段级、UI 交互和状态管理、代码示例、测试策略、Always/Ask First/Never 边界，以及 `## 可编辑文件` 部分列出的 glob，为第三环提供编辑范围提示（给代理的参考，`verify` 不强制）
4. **审查** — 你审查并确认或请求更改

### 阶段 3 — 任务分解（plan.md + todo.md）

1. **触发** — 你确认阶段 2 完成；`codoop-ticket` 加载 `/skill planning-and-task-breakdown`
2. **分解** — 规格分解为两个文件：
   - `plan.md` — 分阶段实现计划，明确依赖、架构决策和检查点
   - `todo.md` — 原子的检查框任务列表（`- [ ]`），每个任务 ≤100 行、≤5 个文件，带平台前缀（`[后端]`、`[网页]`等）
3. **参考** — skill 提示你审查 `/skill definition-of-done` 所以任务验收标准与项目范围完成定义对齐
4. **审查** — 你审查并确认

### 阶段 3 后 — 元数据自动推断

阶段 3 后，`codoop-ticket` 调用 `update_metadata_from_docs` 从你的 `spec.md` 和任务文件自动推断 `metadata.json`。人工审查结果并在验证前确认或修改。

### 验证和提升

1. **验证** — `codoop ticket validate <ticket_id>` 确保所有必需字段都存在且有意义地填充
2. **提升** — `codoop ticket promote <ticket_id>` 把工单从 `drafts/<ticket_id>/` 移到 `pending/<ticket_id>/`，唤醒第三环的调度器

---

## 输出

每个工单是管道中的一个目录，位于以下阶段之一：

```
docs/tickets/
  drafts/<ticket_id>/              ← 被设计（人类面向）
  pending/<ticket_id>/             ← 设计完成，等待第三环
  in_progress/<ticket_id>/         ← 第三环正在执行
  done/<ticket_id>/                ← 已发布和归档
  failed/<ticket_id>/              ← 自愈耗尽；需要人工干预
```

**每个工单目录内的文件：**

| 文件 | 作者 | 必需 | 用途 |
|---|---|---|---|
| `metadata.json` | 自动推断；人工确认 | 是 | 第三环的机器可读配置：工单类型、模块、测试命令、编辑范围、自愈预算、UI 捕获标志 |
| `module_prd.md` | PM 代理 + 人工 | `feature` 必需 | 100% 纯业务描述 — 用户故事、状态流、验收标准 |
| `spec.md` | 架构师代理 + 人工 | `feature` 必需 | 技术契约 — API、数据模式、UI 交互、`files_to_edit` 范围提示 |
| `bug_report.md` | 人工（+ 代理） | `fix` 必需 | 缺陷记录 — 现象 / 复现 / 根因 / 预期行为 / 影响范围 |
| `plan.md` | 自动分解 + 人工审查 | 推荐（两类） | 分阶段实现计划，带检查点 |
| `todo.md` | 自动分解 + 人工审查 | 推荐（两类） | 原子检查框任务列表，每个 ≤100 行，带平台前缀 |

---

## 涉及的 Skills

| Skill | 角色 |
|---|---|
| **codoop-ticket** | 主编排器。引导你通过所有三个阶段并调用 sub-skills。 |
| **spec-driven-development** | 阶段 2（规格设计）。也可以独立调用。 |
| **planning-and-task-breakdown** | 阶段 3（任务分解）。也可以独立调用。 |
| **definition-of-done** | 参考工具。不作为动作生产者调用，但在阶段 3 中审查以通知验收标准。 |

### 独立使用

**spec-driven-development** 可以在有需求但没有规格时直接调用：

```
/skill spec-driven-development 基于这份 PRD，设计技术规格。
```

**planning-and-task-breakdown** 可以在有规格但需要分解为任务时直接调用：

```
/skill planning-and-task-breakdown 基于这份规格，把它分解为实现任务。
```

两者在独立模式中的工作方式与作为 `codoop-ticket` 调用时相同，除了输出路径不同（独立 skills 使用 `tasks/`，集成 skills 使用工单目录）。

**definition-of-done** 在阶段 3 中被参考（不被调用）。你阅读参考并在 `todo.md` 中写入验收标准时应用其五维检查清单（正确性、质量、集成、文档、发布就绪）。

---

## CLI 参考

Loop 2 有独立的 CLI 工具 `codoop-ticket.py`，完全独立于 Loop 3 的 `codoop-execute`。

所有命令都可以通过以下方式调用：

```bash
python skills/codoop-ticket/scripts/codoop-ticket.py ticket <command> <args>
```

或者在 AI 编码工具中直接调用 skill：

```
/skill codoop-ticket 设计工单
```

### `codoop-ticket ticket init <ticket_id> --config <toml> [--title "..."] [--language auto|zh|en] [--type feature|fix]`

**创建** `docs/tickets/drafts/<ticket_id>/`，包含：
- `metadata.json` 存根（占位符值，含 `ticket_type`）
- 按类型生成脚手架文档：`feature` → `module_prd.md`、`spec.md`、`plan.md`、`todo.md`；`fix` → `bug_report.md`、`plan.md`、`todo.md`

**参数：**
- `--title` — 工单标题（如果 `--language auto` 则检测语言）
- `--language` — `auto`（默认，检测 CJK → `zh`，否则 `en`），或明确 `zh` / `en`
- `--type` — `feature`（默认）或 `fix`；决定脚手架与必需文档规则
- `--config` — `codoop_flow.toml` 的路径

**退出码：** 成功返回 0，如果草稿已存在则抛出 `FileExistsError`。

### `codoop-ticket ticket validate <ticket_id> --config <toml>`

**验证**草稿准备好提升。

**检查（阻止性）：**
- `metadata.json` 清洁解析并满足完整模式（所有必需字段存在、类型正确、每个模块都有测试命令、`ticket_type` 合法）
- 该类型的必需文档存在并包含有意义的（非样板、非空）内容：`feature` → `module_prd.md` + `spec.md`；`fix` → `bug_report.md`

**检查（建议警告）：**
- `plan.md` 和 `todo.md` 存在且有意义地填充

**退出码：** 成功返回 0，任何阻止错误返回 1。

### `codoop-ticket ticket update-metadata <ticket_id> --config <toml>`

从当前 `spec.md`（和可选的 `plan.md`/`todo.md`）**自动推断** `metadata.json`，写回磁盘，并打印以供人工审查。

**推断逻辑：**
- `modules` — 从 `spec.md` 标题扫描（`## 后端`、`## 网页`等），映射到：后端、网页、移动、桌面
- `files_to_edit` — 从 `## 可编辑文件` 部分提取（如果部分缺失则回退：从模块名称派生）
- `test_command` — 如果不存在则按模块用默认值填充（后端：`bash script/test-backend.sh`、网页：`npm test`、移动：`flutter test`、桌面：`cargo test`）

通常在阶段 3 完成后、验证和提升前调用。

### `codoop ticket promote <ticket_id> --config <toml>`

**提升**草稿到 pending（准备好供第三环拾取）。

**内部：**
- 首先调用 `validate`；如果任何错误则失败
- 使用 `shutil.move` 将 `docs/tickets/drafts/<ticket_id>/` 移到 `docs/tickets/pending/<ticket_id>/`
- 拒绝覆盖既有的 pending 工单

**输出：** 目标路径和 `codoop_tools.py pick` 将下一步拾取它的消息。

**退出码：** 成功返回 0，验证或移动失败返回 1。

---

## 配置

### `codoop_flow.toml`

对第二环只有一个字段重要：

| 字段 | 类型 | 必需 | 含义 |
|---|---|---|---|
| `target_repo` | 字符串（路径） | 是 | 你的目标 git 仓库路径。第二环在 `<target_repo>/docs/tickets/` 下写入工单目录。 |

### `metadata.json` 模式

每个工单的 `metadata.json` 必须满足这个模式：

**必需字段：**

| 字段 | 类型 | 含义 |
|---|---|---|
| `ticket_id` | 字符串 | 与目录名称匹配的标识符（例如 `ticket_001`） |
| `title` | 字符串 | 人类可读的工单标题 |
| `modules` | 字符串列表 | 这个工单涉及的平台模块：`backend`、`web`、`mobile`、`desktop` |
| `test_command` | dict[字符串, 字符串] | 每个模块的测试命令运行（键必须覆盖所有 `modules` 条目） |
| `files_to_edit` | 字符串列表 | Glob 模式，提示代理应把改动集中在哪里（第三环的编辑范围参考；`verify` 不强制） |

**可选字段：**

| 字段 | 类型 | 默认 | 含义 |
|---|---|---|---|
| `ticket_type` | 字符串 | `"feature"` | `"feature"`（需求单）或 `"fix"`（修复单）。决定第二环的必需文档，以及第三环的 commit 前缀（`feat`/`fix`） |
| `coding_engine` | 字符串或 null | null | 这个工单用哪个 AI 工具：`claude`、`codex`、`cursor`。如果缺失，使用全局默认。 |
| `max_healing_attempts` | int | 3 | 第三环的最大自愈重试次数，之后移到 `failed/` |
| `ui_capture` | bool | false | 如果为真，第三环的测试脚本写入截图；审查添加 UI/UX personas |

**验证：** 所有必需字段必须存在且类型正确；`modules` 中的每个模块都必须在 `test_command` 中有对应条目。缺少其中任何一个是阻止验证错误。

---

## 集成

### 输入（从第一环读取）

在阶段 1（需求设计）中，`codoop-ticket` 主动读取第一环的 backlog 输出：

- `docs/backlog/product/` — requirements.md、user-journey.md、monetization-plan.md
- `docs/backlog/interface/` — design-system.md、ui-mockups.md
- `docs/backlog/architecture/` — architecture.md、database-schema.sql、openapi.yaml
- `docs/backlog/modules/` — 单模块详细设计

这把每个工单锚定在全局产品策略中，而不是孤立地发明。

### 输出（供第三环使用）

`promote` 命令的文件系统移动（`drafts/` → `pending/`）是唯一的交接机制。第三环的调度器轮询 `pending/`，拾取最旧的工单，并消费：

- `metadata.json` — 驱动所有调度器决策（模块、测试命令、files_to_edit、自愈预算、ui_capture 标志）
- `module_prd.md` + `spec.md` — 在启动时逐步披露给编码引擎
- `plan.md` + `todo.md` — 第三环逐步读取任务列表，随着完成检查项
- `public/qa-screenshots/` — 由第三环的测试脚本在运行时创建（UI 工单）

工单目录随工单通过所有阶段传播：`pending/` → `in_progress/` → `done/`（或 `failed/`），在实现制品旁边保留完整设计记录。

---

## 完成定义

第二环向人工介绍项目范围的**完成定义 (DoD)** — 一个固定的五维检查清单，每个任务在被认为完成前必须满足：

1. **正确性** — 验收标准满足、运行时验证、测试证明变更、无回归、边界情况处理
2. **质量** — 意图清晰的命名、无重复逻辑、无死代码、无不相关重构、linting 通过
3. **集成** — 与完整系统协作、迁移和配置处理、向后兼容性考虑
4. **文档** — 公开接口文档化、架构决策记录、永恒语言
5. **发布就绪** — 安全审查、可观测性到位、回滚路径存在、人工批准完成

**与验收标准的关键区别：** `todo.md` 中的验收标准回答"我们是否正确构建了这个？"，每个任务不同。DoD 回答"我们能自信地发布这个吗？"，在所有任务和工单中固定。

在阶段 3 中，你被鼓励引用 `/skill definition-of-done` 以使任务验收标准强大到足以满足项目范围标准。

---

## 独立 Skill 使用

### 独立使用 spec-driven-development

```
/skill spec-driven-development 我有这份 PRD，设计技术规格。
```

这个 skill 引导你通过四个阶段（Specify → Plan → Tasks → Implement），为独立使用生成 `tasks/spec.md`、`tasks/plan.md`、`tasks/todo.md`。所有六个核心规格区域都涵盖：目标、命令、项目结构、代码风格、测试策略、边界。

### 独立使用 planning-and-task-breakdown

```
/skill planning-and-task-breakdown 我有这份规格，把它分解为可实现的任务。
```

这个 skill 读取规格、建立依赖图、垂直切片（按功能而非按层）、写入带验收标准 + 验证 + 依赖 + 文件列表 + 大小估计的任务，并保存到 `tasks/plan.md` 和 `tasks/todo.md`。它强制规则：规划中不写任何代码。

---

## 关键设计原则

- **确定性输入产生确定性输出** — 高保真需求使第三环能可靠执行而不猜测。
- **三阶段人工协作** — 阶段 1（PRD）→ 阶段 2（规格）→ 阶段 3（任务），每个阶段之间有明确的人工确认。
- **类型贴合流程** — `feature` 工单走完整的 PRD → Spec → 任务流程；`fix` 工单用更轻量的 `bug_report.md` 流程。类型在开始时与人工确认，绝不静默猜测。
- **元数据自动推断** — 第二环从规格内容自动推断 `metadata.json`，省去人工手动、容易出错的配置。
- **双模 Sub-Skills** — spec-driven-development 和 planning-and-task-breakdown 既可独立工作，也可作为 codoop-ticket 的集成阶段。
- **不写代码** — 第二环是纯文档。代码仅在第三环写入。

