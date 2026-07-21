<div align="center">

# codoop-flow

[English](./README.md) · **简体中文**

**把"AI 写代码"变成一条有护栏的工单流水线**
挑单 → 写码 → 验证 → 多重评审 → 归档，一单一闭环

![Codex Skill](https://img.shields.io/badge/Codex-skill-111827)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-8A63D2)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Zero deps](https://img.shields.io/badge/deps-zero-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

**codoop-flow** 是一个三环 AI 驱动开发系统，把"AI 写代码"变成一条可靠的工程流水线。

**你只需用自然语言指挥 Codex 或 Claude，脏活累活由脚本护栏兜底。** 智力活（写码、自愈、评审判断）交给当前 agent 会话；体力活（挑单、管 git worktree、跑测试、提交）交给一个不会幻觉的确定性 CLI。它是可迁移工具，本身不含业务代码——用一份 `codoop_flow.toml` 指向你真正要开发的工程即可。

**三个独立循环，可单独或合用：**
- **第一环**：多角色产品设计（0→1 规划）
- **第二环**：精细工单设计（PRD + 规格 + 按需视觉预览 + 任务分解）
- **第三环**：连续工单执行（写码 → 验证 → 评审 → 合并）

```
         你说一句话                          你决定是否 push
             │                                     ▲
             ▼                                     │
  ┌──────────────────────── Codex/Claude 读 SKILL.md 编排 ─────────────────────────┐
  │                                                                                │
  │   pick ──▶ build ──▶ verify ──▶ review ──▶ ship docs ──▶ finish               │
  │  [脚本]   [agent]    [脚本]    [reviewers]  [agent]      [脚本]                 │
  │   挑单     写码      跑测试     多重评审      同步文档     提交归档                │
  │  建worktree         +UI 截图    全票才过                  dev/<id>              │
  │                        │           │                                          │
  │                        └─ 失败 ────┴─▶ self-heal 自愈（预算内重试）             │
  └────────────────────────────────────────────────────────────────────────────┘
```

---

## 安装

### Codex（Desktop 或 CLI）

从 GitHub marketplace 仓库安装：

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

或者直接对 Codex 说：

```text
安装 Codoop/codoop-flow 里的 codoop-flow Codex 插件，然后帮这个仓库初始化 codoop-flow。
```

然后重启/打开 Codex。日常流程只需要两句话：

```text
使用 $codoop-flow，帮这个仓库初始化 codoop-flow。
使用 $codoop-flow，针对 codoop_flow.toml 跑下一张工单。
```

本地开发备用方式：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/codoop-execute "${CODEX_HOME:-$HOME/.codex}/skills/"
```

### Claude Code

通过插件安装：

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

也可以直接告诉 Claude Code：从 `Codoop/codoop-flow` 安装 codoop-flow 插件，然后针对当前仓库运行。

> SSH 报错就改用完整 HTTPS：`/plugin marketplace add https://github.com/Codoop/codoop-flow.git`
> 本地开发：`claude --plugin-dir /path/to/codoop-flow`
> 其他 agent（Cursor / Gemini）见 [`docs/install.zh-CN.md`](./docs/install.zh-CN.md)。

**前提**：目标工程是一个 git 仓库；机器有 `python3`（仅标准库，无第三方依赖）。

---

## 三环系统

codoop-flow 实现了 **三环** AI 驱动开发体系：

### 🔍 第一环：创业探索（产品设计）
**适用场景**：你有产品想法，需要在写代码前做完整的 0→1 设计。

**在会话内调用**：
```
/skill codoop-discover 我想做一个 SaaS 项目管理工具，面向远程团队
```

Skill 编排多个专家角色（PM、GTM、UX/UI、架构师）协作：
- **SNAP 澄清** — 通过结构化问题消除假设
- **冷启动引导** — 先用少量大白话问题确认产品、核心流程和视觉方向，再分派专家角色
- **多角色起草** — 专家在会话内协作
- **一致性审计** — 发现和解决跨文档冲突
- **生成 Backlog** — 输出完整规格到 `docs/backlog/`

**输出**：设计文档存放在 `docs/backlog/`，准备好交给第二环

[了解 codoop-discover →](./skills/codoop-discover/README.md)

### 📋 第二环：人工设计（工单设计）
通过需求文档（PRD）→ 技术规格（Spec）→ 按需视觉预览 → 任务分解（Plan）精心设计工单。准备好交给第三环。澄清时先讨论用户能直接判断的目标和体验；技术实现由 agent 写入专业、明确的 Spec，只有会影响体验、成本、安全或范围时才需要你确认。

**主要编排工具**：
```
/skill codoop-ticket 帮我设计电商平台的用户搜索功能工单
```

**独立工具**（也被 codoop-ticket 调用）：
```
/skill spec-driven-development 设计技术规格（不需要手工编排）
/skill planning-and-task-breakdown 把规格分解成有序的实现任务
/skill definition-of-done 检查完成的工作是否达到质量标准
```

**用户体验走查** — 功能可运行后可独立调用，也可由第三环在技术批准后动态调用。它让指定 persona 完成一项任务，产出只供人工判断的 `experience_report.md`；是否将建议转为新工单，完全由你决定。

```
/skill codoop-ux-walkthrough
请以首次使用的运营人员身份体验这个功能，并写一份体验报告。
```

这些 skill 既可独立使用，也可作为 codoop-ticket 流程的各个阶段。

**输出**：工单规格存放在 `docs/tickets/pending/`，准备好交给第三环

[了解 codoop-ticket →](./skills/codoop-ticket/README.md)

### 🤖 第三环：Agent 编排（实现）
挑单 → 隔离 worktree 写码 → 验证 → 多重评审 → 合并 → 归档。

**主要编排工具**：
```
/loop 20m run the codoop-execute skill against codoop_flow.toml
```

**工作流程**：
1. **挑单** — 挑最旧的 pending 工单，建隔离 worktree 在 `dev/<ticket_id>` 分支
2. **写码** — Agent 按工单规格在 worktree 内写代码
3. **验证** — 硬门：测试全过、UI 截图（如需）
4. **评审** — 多个 reviewer persona 评审代码（全票才放行）
5. **合并** — Agent 问你："要合并到 main 吗？" → 你决定
6. **归档** — 工单搬到 `done/`，删除 worktree

**核心特性**：
- **幂等性**：同一命令可安全重复调用（自动恢复进行中的工单）
- **自愈能力**：验证/评审失败自动重试（默认预算 3 次）
- **确定性验证**：测试 + 截图门禁无法绕过
- **异步友好**：定时由 `/loop`（Agent 的调度器）控制，不由 Python 内部定时

**输出**：代码合并到 `main` 分支，工单归档到 `docs/tickets/done/`

[深入了解第三环 →](./docs/loop-3-agent-centric.zh-CN.md)

---

## 快速上手

### 第一环（产品设计）

```
/skill codoop-discover 我想做 [你的产品想法]
```

输出设计规格到 `docs/backlog/`。

### 第二环（工单设计）

```
/skill codoop-ticket 帮我设计 [具体功能名]
```

输出工单规格到 `docs/tickets/pending/ticket_001/`。

### 第三环（实现）— 完整工作流

**① 一次性初始化**（建好工单流水线 + 生成配置）：

在 Claude Code 里直接说：

```text
使用 codoop-execute skill，帮这个仓库初始化 codoop-flow。
```

或手动运行：

```bash
python3 skills/codoop-execute/scripts/codoop.py setup /path/to/your/repo \
  --config /path/to/your/repo/codoop_flow.toml
```

**② 放工单**到 `docs/tickets/pending/ticket_001/`，每个工单包含：
- `metadata.json`（[字段说明](#工单-metadatajson)）
- `module_prd.md`（业务需求）
- `spec.md`（技术规格）
- `preview.html`（仅在 `metadata.json.visual_preview: true` 的需求单中必需）
- `plan.md`（执行计划）
- `todo.md`（原子任务）

**③ 持续处理队列**，在 Claude Code 里运行：

```
/loop 20m run the codoop-execute skill against codoop_flow.toml
```

Agent 会：
1. 挑最旧的 pending 工单
2. 在隔离 worktree 写代码
3. 验证（测试 + UI）
4. 评审（多个 reviewer 全票）
5. 问你："要合并到 main 吗？" → 你决定
6. 归档并循环

**无需 push 步骤** — 所有改动都在本地。你完全掌控何时合并到 `main`。

---

## 单个工单（手动模式）

不想用持续 `/loop`，就手动跑一次：

```
使用 codoop-execute skill，针对 codoop_flow.toml 跑一轮工单
```

Agent 挑最旧的 pending 工单，跑完整流程（挑单 → 写码 → 验证 → 评审 → 问合并）。你决定是否合并。

---

## 它是怎么工作的

装好后你几乎不用记命令——**skill 是写给 coding agent 读的**，你说一句话，agent 就照着 skill 串起整条链：

### 三个组件

1. **Skill 编排**（`SKILL.md`）：Agent 读工作流，知道每个阶段该做什么。

2. **脚本护栏**（`codoop_tools.py`）：必须 100% 确定、不能幻觉的活——
   - 挑单（pending → in_progress）
   - 建隔离 worktree 在 `dev/<ticket_id>` 分支
   - 验证：跑测试、检查 UI 截图
   - 提交和归档（in_progress → done）
   - 优雅处理失败

3. **评审 persona**（在 `_shared/agents/` 中）：验证通过后，agent 运行多个评审者——
   - `code-reviewer` — 正确性、可读性、安全性、性能
   - `security-auditor` — 漏洞扫描
   - `test-engineer` — 测试策略和覆盖率
   - `evidence-collector` — UI/UX 验证（UI 工单）
   - `reality-checker` — 部署就绪检查（UI 工单）

4. **体验走查**（`codoop-ux-walkthrough`）：技术批准后，可让指定 persona 实际体验可运行的用户功能。生成的 `experience_report.md` 会随工单归档，但只供人工参考，不阻塞发布，也不会自动修改代码。

**全票才放行** — 任何拒绝都会触发自愈（自动重试，有预算）。

### 设计哲学

**一句话：动脑的交给 agent，数数对答案的交给脚本。**

| 对象 | 职责 | 例子 |
|------|------|------|
| **Agent** | 写什么代码、怎么修复、需不需要改进 | 分析 todo、编写函数、判断是否需要重构 |
| **脚本** | 保证隔离、测试、无法绕过 | worktree 生命周期、验证门禁 |
| **你** | 决定是否合并、整体优先级、长期方向 | 合并时机、工单取舍 |

### 关键特性

| 特性 | 好处 |
|------|------|
| **确定性验证** | 硬门（测试 + UI）无法被 AI 幻觉绕过 |
| **自愈能力** | 验证/评审失败 = 自动重试（预算内） |
| **隔离工作树** | 每个工单独立，互不干扰 |
| **本地优先** | 只需本地 git 仓库，远程可选 |
| **Agent 无关定时** | `/loop` 由 Agent 调度器控制，不由 Python 内部定时 |
| **完全可审计** | 所有状态在 git 分支 + 文件系统中，完全透明和可逆 |

<details>
<summary>手动提工单（不想让 agent 代劳时展开）</summary>

`setup` 之后，也可以自己用人面向 CLI 把想法沉淀成工单：

```bash
# 起草：在 drafts/ 生成 metadata + 空文档骨架
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
# 编辑 drafts/ticket_001/ 里的 module_prd.md（业务）、spec.md（契约）；visual_preview 为 true 时还需编辑 preview.html
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket validate ticket_001 --config codoop_flow.toml   # 校验必填文档
python3 skills/codoop-ticket/scripts/codoop-ticket.py ticket promote  ticket_001 --config codoop_flow.toml   # drafts → pending
```

想从零探索一个新想法（多角色设计会话，产出到 `docs/backlog/`），在会话内调用 skill：

```
/skill codoop-discover 想做个 XX 应用
```
</details>

---

## 工单 metadata.json

```json
{
  "ticket_id": "ticket_001",
  "title": "add hello module",
  "ticket_type": "feature",
  "modules": ["backend"],
  "max_healing_attempts": 3,
  "visual_preview": false,
  "ui_capture": false
}
```

| 字段 | 说明 |
|---|---|
| `ticket_type` | `feature`（需求单，默认）或 `fix`（修复单）。决定第二环的必需文档与第三环的 commit 前缀（`feat`/`fix`） |
| `modules` | 涉及的模块 |
| `max_healing_attempts` | 自愈重试预算（默认 3） |
| `visual_preview` | 为 true 时：需求单必须在任务拆分前生成并经人工评审 `preview.html`；用于讨论局部界面与关键交互，不是实际实现 |
| `ui_capture` | 为 true 时：交付过程须在 `public/qa-screenshots/` 放置截图（没截图硬 fail），评审额外加 2 个 UI persona 真看图 |

必填：`ticket_id / title / modules`。`ticket_type`（默认 `feature`）可选。

---

<details>
<summary>护栏 CLI 参考（<code>codoop_tools.py</code>，agent 自动调用，一般不用手敲）</summary>

所有子命令吃 `--config <toml>`、输出 JSON。

| 子命令 | 行为 |
|---|---|
| `status` | 打印各阶段工单列表 |
| `pick` | 挑最旧 pending 工单 → 搬进 in_progress → 建 worktree（`dev/<id>` 分支）。已有 in_progress 则报告它、不新挑 |
| `verify <id>` | 在 worktree 跑测试 + (UI) 截图硬门禁 |
| `finish <id> --message` | 排除生成物后 commit 到 `dev/<id>` → 搬到 done → 删 worktree |
| `fail <id> --report` | 搬到 failed → 写 `healing_report.md` → 释放 lease 并保留 worktree 供人工恢复 |

</details>

---

## 目录结构

```
codoop-flow/
├── codoop_flow.toml.example       # 配置样例
├── .agents/plugins/marketplace.json # Codex marketplace 清单
├── .claude-plugin/                # Claude Code 插件声明
├── .codex-plugin/                 # Codex 插件声明
├── skills/
│   ├── _shared/                   # 共享代码 & agent personas（所有 skills 使用）
│   │   ├── codoop_lib_v1/         #   共享库（ticket、config、verify 等）
│   │   └── agents/                #   评审 persona（code-reviewer、security-auditor 等）
│   ├── codoop-execute/            # ★第三环：Agent 编排执行
│   ├── codoop-ticket/             # ★第二环：人类工单设计
│   ├── codoop-discover/           # ★第一环：创意探索设计
│   ├── codoop-ux-walkthrough/     # ★基于 persona 的非阻塞体验洞察
│   └── [其他 6 个 skill]/         # 独立学科
├── tests/test_skeleton.py         # 14 个骨架测试（子进程调 CLI，不依赖 AI）
├── LICENSE                         # MIT
└── docs/
    ├── install.md                 # 多 agent 安装说明
    └── engineering-design.md      # 设计蓝图（三环闭环模型）
```

> 中文文档带 `.zh-CN` 后缀（如 `docs/install.zh-CN.md`）；无后缀的是英文版。

---

## 运行测试

```bash
python3 tests/test_skeleton.py   # 应输出 ALL SKELETON TESTS PASSED
```

骨架测试用临时 git 仓库 + 子进程调 CLI，只覆盖**确定性护栏 + 工单生命周期**，不依赖 AI，秒级完成。

---

## 兼容的 Agent

skill 是自包含目录，任何有"读文件 + 跑 Bash"能力的 coding agent 都能用；有子代理能力会让评审隔离性更好，但不是硬要求。

| Agent | 状态 | 怎么装 |
|---|---|---|
| Codex Desktop | ✅ 一等公民 | `codex plugin marketplace add Codoop/codoop-flow`，然后 `codex plugin add codoop-flow@codoop-flow` |
| Codex CLI | ✅ 一等公民 | 同一套插件安装流程 |
| Claude Code | ✅ 一等公民 | 插件市场（见[安装](#安装)） |
| Claude CLI | ✅ 一等公民 | 使用与 Claude Code 相同的本地 `claude` 命令 |
| Cursor / Gemini | 🟡 通用拷贝 | 拷 `skills/` 目录，见 [`docs/install.zh-CN.md`](./docs/install.zh-CN.md) |

> 如果宿主没有 subagent 工具，就在同一个会话里串行运行评审 persona。

---

## 常见问题

### 通用问题

**三个环的区别是什么？**
- **第一环**：多角色产品设计（0→1 规划）→ `docs/backlog/`
- **第二环**：单个工单设计（PRD + 规格 + 按需视觉预览 + 任务）→ `docs/tickets/pending/`
- **第三环**：实现（写码 + 验证 + 评审 + 合并）→ `main` 分支

**三个环可以一起用吗？**
可以。典型流程：第一环（每个项目一次） → 第二环（每个功能一次） → 第三环（连续处理队列）。

**一定要用全部三个环吗？**
不用。各自独立。只有规格文档的话，直接用第三环。

### 第三环相关

**我的代码改动最后到哪里去了？**
到 `dev/<ticket_id>` 分支。Agent 评审通过后问你是否合并到 `main`。你决定。

**能和现有工单系统集成吗？**
可以。只要按要求格式放工单到 `docs/tickets/pending/` 即可。第二环会生成这个格式，也可以手动创建。

**我不想要连续 `/loop`，可以吗？**
可以。手动跑单个工单："使用 codoop-execute skill 跑一轮工单"。Agent 处理一个工单，问你是否合并，然后停止。

**验证/评审失败会怎样？**
Agent 自动重试（默认预算 3 次）。全部失败后，工单搬到 `failed/` 并写 `healing_report.md` 说明原因。worktree 及未提交改动会保留给人工恢复，报告中会给出对应路径和分支。

**能多个 agent 并行处理工单吗？**
目前不行 — 同时只有一个 in_progress 工单。未来版本可能支持。

### 安装相关

**`/plugin marketplace add` 报 SSH 错？**
默认走 SSH 克隆。没配 SSH key 就用完整 HTTPS：`/plugin marketplace add https://github.com/Codoop/codoop-flow.git`。

**`setup` 报 "not a git repository"？**
目标工程必须先 `git init`。codoop-flow 在你工程的 git 仓库里流转工单。

**agent 说找不到 skill / 命令？**
Claude Code 确认插件已安装。再手动验证护栏就位：`python3 skills/codoop-execute/scripts/codoop_tools.py --config codoop_flow.toml status`。

**工单一直卡在 `failed/`？**
打开 `failed/<id>/healing_report.md` 看自愈耗尽的原因，通常是测试写得太严或规格对自愈预算来说太庞大。编辑工单后重新推进到 `pending/`。

---

## 深入了解

### 深潜阅读

- [`docs/loop-3-agent-centric.zh-CN.md`](./docs/loop-3-agent-centric.zh-CN.md) —— 第三环完整机制（worktree、验证、本地工作流）
- [`docs/engineering-design.zh-CN.md`](./docs/engineering-design.zh-CN.md) —— 三环闭环设计蓝图
- [`docs/install.zh-CN.md`](./docs/install.zh-CN.md) —— 各 coding agent 的安装方式

### Skill 说明文档

- [`skills/codoop-discover/README.md`](./skills/codoop-discover/README.md) —— 第一环详解
- [`skills/codoop-ticket/README.md`](./skills/codoop-ticket/README.md) —— 第二环详解
- [`skills/codoop-execute/SKILL.md`](./skills/codoop-execute/SKILL.md) —— 第三环工作流（Agent 的读物）
- [`skills/codoop-ux-walkthrough/SKILL.md`](./skills/codoop-ux-walkthrough/SKILL.md) —— Persona 走查与体验报告

---

<div align="center">
MIT License
</div>
