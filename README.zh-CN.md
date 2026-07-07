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

**你只需用自然语言指挥 Codex 或 Claude，脏活累活由脚本护栏兜底。** 智力活（写码、自愈、评审判断、文档同步）交给当前 agent 会话；体力活（挑单、管 git worktree、跑测试、卡越界白名单、提交）交给一个不会幻觉的确定性 CLI。它是可迁移工具，本身不含业务代码——用一份 `codoop_flow.toml` 指向你真正要开发的工程即可。

```
         你说一句话                          你决定是否 push
             │                                     ▲
             ▼                                     │
  ┌──────────────────────── Codex/Claude 读 SKILL.md 编排 ─────────────────────────┐
  │                                                                                │
  │   pick ──▶ build ──▶ verify ──▶ review ──▶ ship docs ──▶ finish               │
  │  [脚本]   [agent]    [脚本]    [reviewers]  [agent]      [脚本]                 │
  │   挑单     写码      跑测试     多重评审      同步文档     提交归档                │
  │  建worktree         卡越界      全票才过                  dev/<id>              │
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

内置探索 CLI 也接受 `--agent codex-cli`；`--agent codex` 映射到同一个本地 `codex` 命令。

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

探索环 CLI 同时接受 `--agent claude-code` 和 `--agent claude`，二者都会拉起本地 `claude` 命令。

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
- **多角色起草** — 专家在会话内协作
- **一致性审计** — 发现和解决跨文档冲突
- **生成 Backlog** — 输出完整规格到 `docs/backlog/`

[了解 codoop-discover →](./skills/codoop-discover/README.md)

### 📋 第二环：人工设计（工单设计）
通过三个阶段精心设计工单：需求文档（PRD）→ 技术规格（Spec）→ 任务分解（Plan）。准备好交给 Agent 环。

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

这些 skill 既可独立使用，也可作为 codoop-ticket 流程的各个阶段。

[了解 codoop-ticket →](./skills/codoop-ticket/README.md)

### 🤖 第三环：AI 编排（实现）
挑单 → 隔离 worktree 写码 → 验证 → 多重评审 → 归档。

---

## 快速上手

**① 接入你的工程**（建好工单目录 + 生成配置）：

在 Codex 里直接说：

```text
使用 $codoop-flow，帮这个仓库初始化 codoop-flow。
```

或者从本地克隆仓库手动跑 CLI：

```bash
python3 skills/codoop-flow/scripts/codoop.py setup /path/to/your/repo \
  --config /path/to/your/repo/codoop_flow.toml
```

**② 放一个工单**到 `你的工程/docs/tickets/pending/ticket_001/`，里面至少有一个 `metadata.json`（[字段说明见下](#工单-metadatajson)）和一份需求文档。

**③ 在 Codex 或 Claude Code 会话里说一句话：**

```
使用 $codoop-flow，针对 codoop_flow.toml 跑一轮工单
```

agent 就会自动跑完整条流水线，并把结果提交到 `dev/<id>` 分支、归档到 `done/`。**是否 push 由你决定。**

想让它持续处理整个队列，用当前 agent 的定时/循环能力。Claude Code 示例：

```
/loop 5m run the codoop-execute skill against codoop_flow.toml
```

---

## 它是怎么工作的

装好后你几乎不用记命令——**skill 是写给 coding agent 读的**，你说一句话，agent 就照着 skill 串起整条链：

1. **Skill 编排**（`SKILL.md`）：Codex/Claude 读它，知道该按什么顺序做。
2. **脚本护栏**（`codoop_tools.py`）：必须 100% 确定、不能幻觉的活——挑单、建隔离 worktree、跑测试、卡"只准改白名单内文件"、提交归档。
3. **评审 persona**：测试过了之后，agent 运行 code-reviewer / security-auditor / test-engineer 等评审；有 subagent 工具就并行派发，没有就串行执行，**全票才放行**，否则打回自愈重来（UI 工单还会加派两个真看截图的 persona）。

一句话：**动脑的交给 agent，数数对答案的交给脚本。**

<details>
<summary>手动提工单（不想让 agent 代劳时展开）</summary>

`setup` 之后，也可以自己用人面向 CLI 把想法沉淀成工单：

```bash
# 起草：在 drafts/ 生成 metadata + 空文档骨架
python3 skills/codoop-flow/scripts/codoop.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
# 编辑 drafts/ticket_001/ 里的 module_prd.md（业务）、spec.md（契约 + files_to_edit 白名单）
python3 skills/codoop-flow/scripts/codoop.py ticket validate ticket_001 --config codoop_flow.toml   # 校验必填文档
python3 skills/codoop-flow/scripts/codoop.py ticket promote  ticket_001 --config codoop_flow.toml   # drafts → pending
```

想从零探索一个新想法（多角色设计会话，产出到 `docs/backlog/`）：

```bash
python3 skills/codoop-flow/scripts/codoop.py discover --agent codex-cli --config codoop_flow.toml "想做个 XX 应用"
# 这些别名也可用：--agent codex、--agent claude-code、--agent claude
```
</details>

---

## 工单 metadata.json

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

| 字段 | 说明 |
|---|---|
| `modules` | 涉及的模块，每项都必须在 `test_command` 里有对应命令 |
| `test_command` | 模块 → shell 命令；`verify` 对每个模块跑一次 |
| `files_to_edit` | **白名单 glob**（fnmatch 语法）。agent 改了白名单外的文件，`verify` 直接判 fail |
| `max_healing_attempts` | 自愈重试预算（默认 3） |
| `ui_capture` | 为 true 时：测试脚本须往 `$CODOOP_QA_SCREENSHOT_DIR` 写截图（没截图硬 fail），评审额外加 2 个 UI persona 真看图 |

必填：`ticket_id / title / modules / test_command / files_to_edit`。

---

<details>
<summary>护栏 CLI 参考（<code>codoop_tools.py</code>，agent 自动调用，一般不用手敲）</summary>

所有子命令吃 `--config <toml>`、输出 JSON。

| 子命令 | 行为 |
|---|---|
| `status` | 打印各阶段工单列表 |
| `pick` | 挑最旧 pending 工单 → 搬进 in_progress → 建 worktree（`dev/<id>` 分支）。已有 in_progress 则报告它、不新挑 |
| `verify <id>` | 在 worktree 跑测试 + 越界白名单 + (UI) 截图三重硬门禁 |
| `finish <id> --message` | 排除生成物后 commit 到 `dev/<id>` → 搬到 done → 删 worktree |
| `fail <id> --report` | 搬到 failed → 写 `healing_report.md` → 删 worktree |

</details>

---

## 目录结构

```
codoop-flow/
├── codoop_flow.toml.example       # 配置样例
├── .agents/plugins/marketplace.json # Codex marketplace 清单
├── .claude-plugin/                # Claude Code 插件声明
├── .codex-plugin/                 # Codex 插件声明
├── skills/codoop-execute/         # ★自包含 Codex/agent skill 包
│   ├── SKILL.md                   #   Agent 环编排说明书
│   ├── agents/openai.yaml         #   Codex UI/发现元数据
│   ├── scripts/                   #   护栏 CLI + 人面向 CLI + 确定性模块
│   └── references/                #   评审 persona / 子技能 / 探索子代理
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
| Codex CLI | ✅ 一等公民 | 同一套插件安装流程；探索环支持 `--agent codex-cli` / `--agent codex` |
| Claude Code | ✅ 一等公民 | 插件市场（见[安装](#安装)）；`--agent claude-code` 也可用 |
| Claude CLI | ✅ 一等公民 | `--agent claude` 映射到 Claude Code 使用的同一个本地 `claude` 命令 |
| Cursor / Gemini | 🟡 通用拷贝 | 拷 `skills/codoop-flow/` 目录，见 [`docs/install.zh-CN.md`](./docs/install.zh-CN.md) |

> 如果宿主没有 subagent 工具，就在同一个会话里串行运行评审 persona。

---

## 常见问题

**`/plugin marketplace add` 报 SSH 错？**
默认走 SSH 克隆。没配 SSH key 就用完整 HTTPS：`/plugin marketplace add https://github.com/Codoop/codoop-flow.git`。

**`setup` 报 "not a git repository"？**
目标工程必须先 `git init`。codoop-flow 在你工程的 git 仓库里流转工单。

**agent 说找不到 skill / 命令？**
Codex 确认 `codex plugin list` 里有 `codoop-flow@codoop-flow`；Claude Code 确认插件已安装。再手动验证护栏就位：`python3 <skill>/scripts/codoop_tools.py --config codoop_flow.toml status`。

**工单一直卡在 `failed/`？**
打开 `failed/<id>/healing_report.md` 看自愈耗尽的原因，通常是测试写得太严或 `files_to_edit` 白名单太窄。

---

## 深入了解

- [`docs/engineering-design.zh-CN.md`](./docs/engineering-design.zh-CN.md) —— 三环闭环设计蓝图
- [`docs/install.zh-CN.md`](./docs/install.zh-CN.md) —— 各 coding agent 的安装方式

---

<div align="center">
MIT License
</div>
