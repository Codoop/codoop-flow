# 安装 codoop-flow skills 到各 coding agent

[English](./install.md) · **简体中文**

codoop-flow 包含**六个独立 skill**，分别应对 AI 驱动开发的不同阶段：

| Skill | 用途 | 阶段 |
|-------|------|------|
| **codoop-discover** | 产品设计与架构规划（0→1 阶段） | 开码前 |
| **codoop-ticket** | 工单编排（PRD → Spec → Plan） | 工单设计 |
| **spec-driven-development** | 设计技术规格 | 工单设计 / 独立使用 |
| **planning-and-task-breakdown** | 分解规格为有序任务 | 工单设计 / 独立使用 |
| **definition-of-done** | 项目级完成标准检查清单 | 质量守门 |
| **codoop-flow** | 代码实现与交付（隔离 worktree） | 编码 & 发布 |

每个 skill 都是**自包含**的：带了编排说明书(`SKILL.md`)、确定性 CLI 和共享的 sub-agent personas。所以无论装到哪个 agent，只要那个目录能被读到、且能跑 `python3`，技能就能工作。

> 前提：目标机器有 `python3`(标准库即可,无第三方依赖);目标工程是一个 git 仓库,
> 且有 `docs/tickets/{pending,in_progress,done,failed}/`。准备一份 `codoop_flow.toml`
> 指向目标工程(见 `codoop_flow.toml.example`)。

---

## Codex

从 GitHub marketplace 仓库安装 codoop-flow Codex 插件：

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

然后重启/打开 Codex。日常流程只需要两句话：

```text
使用 $codoop-flow，帮这个仓库初始化 codoop-flow。
使用 $codoop-flow，针对 /path/to/codoop_flow.toml 跑下一张工单。
```

本地开发时也可以不走插件安装，改为克隆并复制 skill：

```bash
git clone https://github.com/Codoop/codoop-flow.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codoop-flow/skills/codoop-flow "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## Claude Code

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

> SSH 报错?市场默认用 SSH 克隆。没配 SSH key 就用完整 HTTPS:
> ```
> /plugin marketplace add https://github.com/Codoop/codoop-flow.git
> /plugin install codoop-flow@codoop-flow
> ```

**本地 / 开发**:
```bash
git clone https://github.com/Codoop/codoop-flow.git
claude --plugin-dir /path/to/codoop-flow
```

装好后，可以在会话内直接调用六个 skill：

**1. codoop-discover**（第一环：产品设计）— 在会话内调用：
```
/skill codoop-discover 我想做一个 SaaS 项目管理工具，面向远程团队
```

**2. codoop-ticket**（第二环：工单编排）— 在会话内调用：
```
/skill codoop-ticket 帮我设计电商平台的用户搜索功能工单
```

**3. spec-driven-development**（第二环：规格设计）— 独立使用或由 codoop-ticket 调用：
```
/skill spec-driven-development 基于工单 PRD，设计技术规格
```

**4. planning-and-task-breakdown**（第二环：任务分解）— 独立使用或由 codoop-ticket 调用：
```
/skill planning-and-task-breakdown 基于规格，分解成实现任务
```

**5. definition-of-done**（质量守门：完成标准）— 开发中参考：
```
/skill definition-of-done 检查我完成的任务是否符合完成标准
```

**6. codoop-flow**（第三环：代码实现）— 在会话内调用：
```
使用 codoop-flow skill，针对 /path/to/codoop_flow.toml 跑下一张工单
```

或用循环定时跑：
```
/loop 5m 使用 codoop-flow skill，针对 /path/to/codoop_flow.toml 跑下一张工单
```

---

## 通用拷贝(Cursor / Gemini / 其他)

skill 是自包含目录,任何 agent 都可以直接把它拷进自己的技能/规则目录:

```bash
git clone https://github.com/Codoop/codoop-flow.git
# 拷这一个目录即可,它自带 scripts/ 和 references/
cp -R codoop-flow/skills/codoop-flow  <目标 agent 的技能目录>/
```

各 agent 的落脚点(参考各自文档,可能随版本变化):

| Agent | 放哪 | 怎么触发 |
|---|---|---|
| Cursor | 把 `SKILL.md` 放进 `.cursor/rules/`,或让 agent 引用整个 `skills/codoop-flow/` | 在对话里引用规则 |
| 其他 agent | skill 是纯 Markdown,把 `SKILL.md` 内容作为 system prompt / instructions 喂进去 | 直接对话 |
| Gemini CLI | 放进其 skills 目录 | 自动发现 |

**关键**:拷完后确保 `skills/codoop-flow/scripts/` 和 `references/` 跟 `SKILL.md`
保持在同一父目录下——SKILL.md 里所有路径都是相对自己(`$SKILL/scripts/...`、
`$SKILL/references/...`),拆开就找不到 CLI 和评审 persona 了。

---

## 验证装好了

```bash
codex plugin list
python3 <skill路径>/scripts/codoop_tools.py --config <toml> status
```
能打印出各阶段工单计数(JSON)就说明护栏 CLI 就位、config 正确。

> 注意:如果宿主 agent 没有 subagent 工具,就在同一个会话里串行运行评审 persona。
