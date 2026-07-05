# codoop-flow

**给 AI coding agent 用的工单流水线：挑单 → 写码 → 验证 → 评审 → 归档，一单一闭环。**

codoop-flow 的核心理念是**"skill 编排 + 确定性护栏"**：

- **智力活**（写代码、自愈、评审判断、文档同步）交给会话里的 Claude —— 它本来就擅长；
- **体力活**（挑单、搬文件夹、管 git worktree、跑测试、卡越界白名单、提交）交给一个不会幻觉的小 CLI 当护栏。

它是一个**可迁移的工具**，本身不含任何业务代码。你用一份 `codoop_flow.toml` 把它指向你真正要开发的目标工程，它就在那个工程的 `docs/tickets/` 里流转工单。

---

## 三个环

| 环 | 谁在干 | 入口 |
|---|---|---|
| **探索环** 把想法拆成需求 | 人 + Claude 交互会话 | `codoop.py discover` |
| **人工提单环** 把需求写成工单 | 人（写 PRD/spec） | `codoop.py ticket init/validate/promote` |
| **Agent 自动环** 把工单做成代码 | Claude 在会话里自动跑 | `codoop-flow` skill + `codoop_tools.py` |

日常最常用的是**第三个环**：你把工单放进 `pending/`，然后让 Claude 读 skill 自动跑完到 `done/`。

---

## 快速上手

### 前提

- 目标机器有 `python3`（只用标准库，无第三方依赖）。
- 你的**目标工程**是一个 git 仓库，且有目录 `docs/tickets/{pending,in_progress,done,failed}/`。

### 1. 安装 skill

**Claude Code（推荐，插件市场）：**

```
/plugin marketplace add your-org/codoop-flow
/plugin install codoop-flow@codoop-flow
```

**本地开发调试：**

```bash
git clone https://github.com/your-org/codoop-flow.git
claude --plugin-dir /path/to/codoop-flow
```

其他 agent（Cursor / Codex / Gemini 等）见 [`docs/install.md`](./docs/install.md)——skill 是自包含目录，直接拷 `skills/codoop-flow/` 过去即可。

### 2. 写配置

复制样例并改成你的目标工程路径：

```bash
cp codoop_flow.toml.example codoop_flow.toml
```

```toml
# 指向你要开发的目标工程（不是 codoop-flow 自己）
target_repo = "/path/to/your/target-repo"
# 每个工单的隔离 worktree 建在哪
worktree_root = "~/codoop_tickets/worktrees"
```

### 3. 验证装好了

`$SKILL` = skill 所在目录（插件装完后在插件目录下的 `skills/codoop-flow`）。

```bash
python3 $SKILL/scripts/codoop_tools.py --config codoop_flow.toml status
```

能打印出各阶段工单计数（JSON）就说明护栏 CLI 就位、config 正确。

---

## 怎么用

### A. 提一个工单

```bash
# 起草：在 drafts/ 里生成 metadata + 空文档骨架
python3 $SKILL/scripts/codoop.py ticket init ticket_001 --config codoop_flow.toml --title "add hello module"
```

然后编辑 `docs/tickets/drafts/ticket_001/` 里的：

- `module_prd.md` —— 纯业务描述（用户故事、验收条件），**不涉及代码**；
- `spec.md` —— 技术契约（API / Schema / **`files_to_edit` 白名单**）；
- `plan.md` / `todo.md` —— 执行步骤、原子任务（可选但建议）。

同时改 `metadata.json` 的关键字段（见下方 schema）。

```bash
# 校验必填文档是否填了实质内容
python3 $SKILL/scripts/codoop.py ticket validate ticket_001 --config codoop_flow.toml
# 通过后搬进 pending/，等 Claude 来做
python3 $SKILL/scripts/codoop.py ticket promote ticket_001 --config codoop_flow.toml
```

### B. 让 Claude 自动做工单

在 Claude Code 会话里直接说：

```
读 codoop-flow skill，针对 codoop_flow.toml 跑一轮工单
```

Claude 会自动走完：`pick`（挑单+建 worktree）→ 在 worktree 里按 todo 写码 → `verify`（跑测试+卡越界）→ 失败自愈 → 用 Task 派 subagent 多重评审（全票才过）→ 同步常青文档 → `finish`（提交到 `dev/<id>` 分支 + 归档到 done）。

**定时跑整个队列：**

```
/loop 5m run the codoop-flow skill against codoop_flow.toml
```

`/loop` 单会话单线程，一次只做一单，天然无需锁。

> **push 是人的决定。** `finish` 只在本地 commit 到 `dev/<id>` 分支，是否 push 由你决定。

### C. 探索一个新想法（可选）

```bash
CODOOP_CLAUDE_MODEL=sonnet python3 $SKILL/scripts/codoop.py discover --config codoop_flow.toml "想做个 XX 应用"
```

起一个交互式设计会话，Claude 扮演 PM / GTM / UI-UX / Architect / Alignment 多角色帮你把想法打磨成 `docs/backlog/` 里的需求文档，再用上面的 ticket 流程拆单。

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
| `files_to_edit` | **白名单 glob**（fnmatch 语法）。Claude 改了白名单外的文件，`verify` 直接判 fail |
| `max_healing_attempts` | 自愈重试预算（默认 3） |
| `ui_capture` | 为 true 时：测试脚本须往 `$CODOOP_QA_SCREENSHOT_DIR` 写截图（没截图硬 fail），评审额外加 2 个 UI persona 真看图 |

必填：`ticket_id / title / modules / test_command / files_to_edit`。

---

## 护栏 CLI（`codoop_tools.py`）

skill 会自动调用，也可手工调试。所有子命令吃 `--config <toml>`、输出 JSON。

| 子命令 | 行为 |
|---|---|
| `status` | 打印各阶段工单列表 |
| `pick` | 挑最旧 pending 工单 → 搬进 in_progress → 建 worktree（`dev/<id>` 分支）。已有 in_progress 则报告它、不新挑 |
| `verify <id>` | 在 worktree 跑测试 + 越界白名单 + (UI) 截图三重硬门禁 |
| `finish <id> --message` | 排除生成物后 commit 到 `dev/<id>` → 搬到 done → 删 worktree |
| `fail <id> --report` | 搬到 failed → 写 `healing_report.md` → 删 worktree |

---

## 目录结构

```
codoop-flow/
├── codoop_flow.toml.example       # 配置样例
├── .claude-plugin/                # Claude Code 插件声明
├── skills/codoop-flow/            # ★自包含 skill 包（可整个拷到别的 agent）
│   ├── SKILL.md                   #   Agent 环编排说明书
│   ├── scripts/                   #   护栏 CLI + 人面向 CLI + 确定性模块
│   └── references/                #   评审 persona / 子技能 / 探索子代理
├── tests/test_skeleton.py         # 12 个骨架测试（子进程调 CLI，不依赖 AI）
├── docs/
│   └── install.md                 # 多 agent 安装说明
└── engineering-design.md          # 设计蓝图（三环闭环模型）
```

---

## 运行测试

```bash
python3 tests/test_skeleton.py   # 应输出 ALL SKELETON TESTS PASSED
```

骨架测试用临时 git 仓库 + 子进程调 CLI，只覆盖**确定性护栏 + 工单生命周期**，不依赖 AI，秒级完成。

---

## 深入了解

- [`engineering-design.md`](./engineering-design.md) —— 三环闭环设计蓝图
- [`docs/install.md`](./docs/install.md) —— 各 coding agent 的安装方式
