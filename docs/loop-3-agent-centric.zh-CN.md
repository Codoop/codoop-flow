# 第三环：AI 编排（实现）

## 概述

**第三环**是 codoop-flow 三环系统的第三个也是最后一个环。是一套完全自动化的、端到端的工单执行管道，可靠地实现、验证、审查和发布软件工单。

**解决的问题：** 让 AI 编码代理实现工单而不幻觉基础设施决策或不发布未测试代码。第三环刻意分割劳动：智能（代理）写代码并推理设计；确定性（守栏 CLI）管理 git、运行测试、归档制品。代理唯一能做错而不破坏管道的事是写坏代码 — 那会被审查 personas 捕获。

**在管道中的位置：** 从 `docs/tickets/pending/<ticket_id>/` 读取第二环输出 → 在隔离 git worktree 上分支 `dev/<ticket_id>` 执行 → 生成代码提交 + 更新的活文档 + 归档到 `docs/tickets/done/`（或 `failed/`）。

---

## 快速开始

在任何 AI 编码工具中，说：

```
使用 codoop-execute skill，针对 /path/to/codoop_flow.toml 跑一张工单
```

或者定时运行：

```
/loop 5m 使用 codoop-execute skill，针对 /path/to/codoop_flow.toml 跑一张工单
```

这个 skill 拾取最旧的 pending 工单，在隔离 worktree 中构建它、运行测试、收集审查反馈、自愈失败、准备好时发布结果。

---

## 工作流程

### 第 1 步 — 拾取（CLI）

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> pick
```

**CLI 做：**
- 首先检查 `in_progress/`。如果已有工单，重建其 worktree（如果删除）并报告它用于恢复（不开始新的）
- 如果 `pending/` 为空，报告"没有 pending 工单"
- 否则，拾取**最旧的** pending 工单，创建隔离的 `git worktree` 在分支 `dev/<ticket_id>`，返回完整工单元数据

**输出 JSON：**
```json
{
  "picked": true,
  "ticket_id": "ticket_001",
  "title": "添加用户搜索功能",
  "ticket_dir": "/abs/path/to/in_progress/ticket_001",
  "worktree": "/abs/path/to/worktrees/ticket_001",
  "branch": "dev/ticket_001",
  "modules": ["backend", "web"],
  "ui_capture": false,
  "screenshot_dir": null
}
```

**代理的工作：** 解析 JSON。如果已 in_progress，恢复。如果没有 pending 工单，停止。如果 picked 为真，继续构建。

### 第 2 步 — 构建（代理）

代理从 `ticket_dir` 读取工单包：
- `module_prd.md` — 100% 业务描述
- `spec.md` — API 契约、数据模式、UI 交互
- `preview.html` — 存在时代表人工已审查的局部视觉流程和关键交互；将其作为设计上下文，而非实际代码
- `plan.md` — 分步执行计划
- `todo.md` — 原子检查框任务

代理还从 `docs/tech/project-structure.md` 和 `docs/tech/tech-standards.md` 读取项目架构边界。

**实现规律：** 使用 `/skill incremental-implementation` 工作流：实现一个细薄的垂直切片、测试、验证、移到下一个。按顺序通过 `todo.md` 项目，随着完成检查（`- [x]`）。

**编辑范围指引：** 优先创建或修改 `spec.md` 中描述范围内的文件——除非任务确实需要触及相邻文件，否则保持在范围内。

### 第 3 步 — 验证（CLI）

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> verify <ticket_id>
```

**UI 截图门**（仅当 `ui_capture: true`）检查
`ticket_dir/public/qa-screenshots/` 是否至少有一个具有识别图像扩展名的文件
（`.png`、`.jpg`、`.jpeg`、`.webp`、`.gif`）。如果没有则失败。

**输出 JSON：**
```json
{
  "ticket_id": "ticket_001",
  "ok": true,
  "reasons": []
}
```

或失败时：
```json
{
  "ticket_id": "ticket_001",
  "ok": false,
  "reasons": ["ui_capture 工单未产生截图"]
}
```

**退出码：** 如果 `ok: true` 返回 0，如果 `ok: false` 返回 1。

### 第 4 步 — 自愈（代理，验证失败时）

验证失败时，代理应用 `/skill debugging-and-error-recovery`：

1. 阅读报告的门禁失败原因
2. 仅修复**根本原因**，极小变更，留在范围内
3. 重新运行 `verify`

**预算：** 最多 `max_healing_attempts` 重试（默认 3，每个工单在 `metadata.json` 中）。验证失败**和**审查拒绝都计入此预算。如果在耗尽重试后仍然失败 → 失败路径。

### 第 5 步 — 审查（代理，验证通过后）

代理对 worktree 中的 `git diff` 运行来自 `<SKILL>/../../_shared/agents/` 的审查 personas。

**批准是一致的** — 任何关键或重要的发现都阻止发布。

**静态 personas（总是运行 — 3 个人）：**

1. **代码审查员** — 评估正确性、可读性、架构、安全性、性能。输出：批准或请求更改（发现分类为关键 / 重要 / 建议）。关键或重要 = 拒绝。

2. **安全审计员** — 识别可利用的漏洞。映射到 OWASP Top 10 和 OWASP LLM Top 10。严重程度：关键 / 高 / 中 / 低 / 信息。关键或高 = 拒绝。

3. **测试工程师** — 分析测试策略、覆盖、金字塔级别、测试质量。输出：覆盖分析和按优先级推荐测试。

**动态 UI/UX personas（仅当 `ui_capture: true` — 2 个额外人）：**

4. **证据收集员** — 痴迷截图的 QA。获得 `screenshot_dir` 检查渲染的屏幕。使用 Playwright 输出、交互前后截图。要求每个声称的视觉证明。默认假设：第一实现最少有 3-5+ 问题。自动失败触发：零问题声称、完美分数。

5. **现实检查员** — 集成和部署准备检查。获得 `screenshot_dir` 交叉验证 QA 发现。端到端旅程分析、跨设备一致性、性能检查（>3s 加载 = 失败）。默认状态：需要工作；仅在压倒性证据支持就绪时才就绪。

**如果任何审查员拒绝：** 发现被反馈给代理以修复 → 重新验证 → 重新审查（仍在自愈预算内）。

### 第 6 步 — 体验走查（代理，可选且非阻塞）

技术批准后，具备可运行、用户可感知行为的工单可以加载 `codoop-ux-walkthrough`。它把 PRD 中的用户角色、目标、范围和验收条件作为任务上下文交给一个独立选择的 persona，并在工单目录写入 `experience_report.md`。这是一份供人工审阅的定性产品洞察：不阻塞发布、不触发自愈、不修改代码，也不会自动创建新工单。纯基础设施、重构和内部功能工单跳过此步骤。

### 第 7 步 — 发布活文档（代理，一致批准后）

完成前，代理同步活文档**在 worktree 内**：

- 更新 `docs/prd/` 带改变的业务逻辑
- 更新 `docs/tech/project-structure.md` 对新的/移动的文件
- 向 `docs/tech/changelog.md` 追加简洁条目

风格：第二人称、现在时、主动语态、每部分一个概念、无破坏代码示例。

### 第 8 步 — 完成（CLI）

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> finish <ticket_id> --message "<conventional commit>"
```

**CLI 做：**
- 暂存所有更改排除生成的噪音（`__pycache__`、`*.pyc`、`node_modules` 等）
- 用提供的消息提交（或模板回退）
- 将 `in_progress/<ticket_id>` 移到 `done/<ticket_id>`
- 用 `git worktree remove --force` 删除 worktree

**输出 JSON：**
```json
{
  "ticket_id": "ticket_001",
  "state": "done",
  "committed": true,
  "commit": "abc1234deadbeef..."
}
```

**推送由你决定。** 代理告诉你"分支 `dev/<ticket_id>` 准备好推；决定是否推到 origin。"

### 失败路径 — 预算耗尽

```
python3 <SKILL>/scripts/codoop_tools.py --config <toml> fail <ticket_id> --report "<摘要>"
```

**CLI 做：**
- 将 `in_progress/<ticket_id>` 移到 `failed/<ticket_id>`
- 把报告写入 `failed/<ticket_id>/healing_report.md`
- 删除 worktree

工单和报告传送到 `failed/` 以供人工干预。

---

## 守栏 CLI — 所有子命令

所有命令需要 `--config <toml>`。所有输出是 JSON 到 stdout。

### `status`

**输出：** 列出每个管道阶段中的所有工单名称。

```json
{
  "pending": ["ticket_a", "ticket_b"],
  "in_progress": ["ticket_c"],
  "done": ["ticket_d", "ticket_e"],
  "failed": []
}
```

总是返回 0。

### `pick`

**行为：** 拾取最旧的 pending 工单或恢复 in_progress。在 `dev/<ticket_id>` 创建 worktree。

**输出：** 完整工单元数据（见第 1 步）。

总是返回 0。

### `verify <ticket_id>`

**输入：** 工单 ID（位置参数）。

**行为：** 运行两个硬门：测试、UI 截图（如果适用）。

**输出：** 成功或失败及具体原因。

如果 OK 返回 0，如果任何门失败返回 1。

### `finish <ticket_id> --message "<msg>"`

**输入：** 工单 ID，可选 `--message`。

**行为：** 暂存（排除噪音）、提交、归档到 `done/`、删除 worktree。省略 `--message` 时，回退消息为 `<前缀>(<module>): <title> [<id>]`，其中 `ticket_type: "fix"` 用 `fix` 前缀，否则用 `feat`。

**输出：** 提交 SHA 和最终状态。

成功返回 0。

### `fail <ticket_id> --report "<text>"`

**输入：** 工单 ID，可选 `--report`。

**行为：** 归档到 `failed/`，写入 `healing_report.md`，释放 lease，并保留 worktree（包括未提交改动）供人工恢复。报告会记录 worktree 路径和分支。

**输出：** 报告路径。

成功返回 0。

---

## Worktree 隔离

每个工单在自己的**隔离 `git worktree` 中**执行 — 在单独分支、单独路径的完整独立检出。

**分支命名：** `dev/<ticket_id>`（例如 `dev/ticket_001`）。

**生命周期：**

1. 第一个 `pick`：`git worktree add -b dev/<ticket_id> <path>`（创建分支并附加 worktree）
2. 恢复：`git reset --hard HEAD` 清除任何脏状态
3. `finish`：`git worktree remove --force <path>`（尽力清理；`git worktree prune` 在下次运行时调和）。`fail` 时保留 worktree 以便恢复。

**Worktree 根位置：** `<worktree_root>/<ticket_id>`（默认：`~/codoop_tickets/worktrees/ticket_001`）。通过 `codoop_flow.toml` 设置。

---

## 自愈机制

**触发：** `verify` 返回 `ok: false` 或审查 persona 拒绝。

**预算：** `max_healing_attempts` 重试（默认 3，每个工单在 `metadata.json` 中设置）。

**每次尝试的流程：**
1. 阅读报告的门禁失败原因以定位根因
2. 修复根本原因（非症状），极小变更，留在范围内
3. 重新运行 `verify`
4. 如果仍然失败，重试（如果预算仍然）

**预算耗尽：** 用去噪摘要调用 `fail`。工单移到 `failed/`。

---

## 审查 Personas

### 静态组（总是运行）

**1. 代码审查员**（`_shared/agents/code-reviewer.md`）
- 检查：正确性（逻辑、规格）、可读性（命名、结构）、架构（模式、抽象）、安全性（无明显漏洞）、性能（高效算法）
- 判决：批准或请求更改
- 阻止：关键（必须修复）和重要（应该修复）
- 非阻止：建议

**2. 安全审计员**（`_shared/agents/security-auditor.md`）
- 检查：输入处理、认证/授权、数据保护、基础设施、第三方集成、AI/LLM 功能
- 映射到：OWASP Top 10 和 OWASP LLM Top 10
- 严重程度：关键 / 高 / 中 / 低 / 信息
- 阻止：关键和高

**3. 测试工程师**（`_shared/agents/test-engineer.md`）
- 检查：测试金字塔（单元/集成/E2E）、行为 vs 实现、测试质量、覆盖缺口
- 输出：覆盖分析和按优先级推荐测试

### 动态 UI/UX 组（当 `ui_capture: true`）

**4. 证据收集员**（`_shared/agents/testing-evidence-collector.md`）
- 获得 `screenshot_dir` 检查渲染屏幕
- 运行 Playwright 捕获、审查 `test-results.json`
- 要求每个声称的视觉证明；无幻想批准
- 默认假设：第一实现有 3-5+ 问题

**5. 现实检查员**（`_shared/agents/testing-reality-checker.md`）
- 获得 `screenshot_dir` 交叉验证 QA 发现
- 端到端旅程分析、跨设备一致性、性能检查（>3s 加载 = 失败）
- 默认状态：需要工作；仅在压倒性证据支持时就绪

**一致批准需要：** 所有活跃 personas 必须批准/通过。任何关键/重要来自任何 persona = 拒绝。

---

## UI 捕获模式

**触发者：** `metadata.json` 中 `"ui_capture": true`。

**它需要什么：**
- 交付过程必须把截图写入 `ticket_dir/public/qa-screenshots/`
- 测试运行后至少一个文件必须以识别的图像扩展名（`.png`、`.jpg`、`.jpeg`、`.webp`、`.gif`）存在
- 没有截图 = 验证失败

**额外 personas：** 证据收集员和现实检查员（动态 UI/UX 组）。

**截图归档：** 截图随工单传送到 `done/` 或 `failed/` 以供人工检查。

---

## 配置

### `codoop_flow.toml`

| 字段 | 类型 | 必需 | 默认 | 含义 |
|---|---|---|---|---|
| `target_repo` | 字符串（路径） | 是 | — | 目标 git 仓库的绝对路径。通过 `expanduser().resolve()` 展开。 |
| `worktree_root` | 字符串（路径） | 否 | `~/codoop_tickets/worktrees` | 每个工单 worktree 的创建目录。通过 `expanduser()` 展开。 |

工单管道目录（`pending/`、`in_progress/`、`done/`、`failed/`）从 `<target_repo>/docs/tickets/` 派生。由 `codoop setup` 创建但从不在 TOML 中配置。

### `metadata.json`（第三环消费）

| 字段 | 类型 | 必需 | 默认 | 含义 |
|---|---|---|---|---|
| `ticket_id` | 字符串 | 是 | — | 唯一标识符；匹配目录名称和分支名称 `dev/<ticket_id>` |
| `title` | 字符串 | 是 | — | 人类可读标题；用于回退提交消息 |
| `ticket_type` | 字符串 | 否 | `"feature"` | `"feature"` 或 `"fix"`；决定回退提交消息前缀（`feat`/`fix`） |
| `modules` | 字符串列表 | 是 | — | 这个工单接触的模块：`backend`、`web`、`mobile`、`desktop` |
| `coding_engine` | 字符串或 null | 否 | null | 信息性；哪个 AI 工具处理这个工单 |
| `max_healing_attempts` | int | 否 | 3 | 最大自愈重试；代理计数（CLI 不强制） |
| `ui_capture` | bool | 否 | false | 如果为真：激活截图门并添加 UI personas |

---

## 集成

### 输入（从第二环读取）

第三环从 `docs/tickets/pending/<ticket_id>/` 拾取工单并消费：

- `metadata.json` — 驱动所有调度器决策
- `module_prd.md` + `spec.md` — 在启动时逐步披露给代理
- `plan.md` + `todo.md` — 代理读取并完成时检查项
- `public/qa-screenshots/` — （对 UI 工单）在运行时创建；由审查 personas 读取
- `experience_report.md` — （若运行体验走查）供人工审阅的定性体验报告，不是发布结论

### 输出（完成后）

**成功（完成）：**
- 提交到 `dev/<ticket_id>` 分支：所有更改 + 活文档更新 + 常规提交消息
- 归档到 `done/<ticket_id>/`：完整工单目录 + `public/qa-screenshots/`（如果 UI 工单）+ `experience_report.md`（如果运行体验走查；仅供人工参考）
- 返回提交 SHA；分支准备推送（你决定是否推送）

**失败（失败）：**
- 无提交；worktree 舍弃
- 归档到 `failed/<ticket_id>/`：完整工单目录 + 新写入的 `healing_report.md`，带代理的去噪失败摘要

---

## 提交和归档的内容

### 在 `finish` 时

**提交到 `dev/<ticket_id>` 分支：**
- worktree 中的所有暂存更改（排除生成噪音）
- 活文档更新（`docs/prd/`、`docs/tech/`）
- 提交消息：常规提交格式（type: scope: subject，可选 body）

**归档到 `done/<ticket_id>/`：**
- 整个工单目录：`metadata.json`、`module_prd.md`、`spec.md`、`plan.md`、`todo.md`（所有复选框勾选）和对 UI 工单，`public/qa-screenshots/` 带所有视觉证据

### 在 `fail` 时

**无提交：** 无代码提交运行。

**归档到 `failed/<ticket_id>/`：**
- 工单目录按现样
- 新写入 `healing_report.md`，带代理的去噪失败摘要

---

## 骨架测试

项目包含 `tests/test_skeleton.py`，仅练习确定性守栏（无 AI，无 mocking）。每个测试获得新鲜临时 git 仓库和 worktrees 目录。

关键测试：
- `test_pick_moves_and_creates_worktree` — pick 把工单从 pending 移到 in_progress 并创建 worktree
- `test_ui_capture_gate` — UI 工单无截图失败；有截图通过
- `test_finish_commits_and_archives` — finish 在 `dev/<id>` 提交、归档到 done/、删除 worktree
- `test_ticket_lifecycle` — 人工工单路径：init → 填充 → 验证 → 提升

运行：`python tests/test_skeleton.py`（无 pytest 需要）。

---

## 关键设计原则

- **确定性胜过聪慧** — CLI 很小、完全确定性、从不猜测。代理拥有所有智能。
- **两个硬门顺序** — 测试 → UI 截图（如果适用）。所有必须通过再审查。
- **一致批准** — 审查仅在所有 personas 同意时进行。任何关键/重要阻止。
- **预算内自愈** — 失败触发重试（如果预算允许），非立即失败。预算耗尽移到 failed/ 供人工干预。
- **隔离 Worktrees** — 每个工单获得自己的分支和检出路径；主 repo 从不接触。
- **活文档保持同步** — 代码发布后，活文档（`docs/prd/`、`docs/tech/`）被更新所以保持权威。
