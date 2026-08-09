# 安装 codoop-flow skills 到各 coding agent

[English](./install.md) · **简体中文**

codoop-flow 包含 **12 个独立 Skill**，分别应对 AI 驱动开发的不同阶段：

| Skill | 用途 | 阶段 |
|-------|------|------|
| **codoop-init** | 分析已有项目的自定义目录，或创建新项目的标准空目录 | 初始化 |
| **grilling** | 每次只问一个大白话问题，确认产品决策 | 探索 / 工单需求确认 |
| **codoop-discover** | 产品设计与架构规划（0→1 阶段） | 开码前 |
| **codoop-ticket** | 工单编排（PRD → Spec → Plan） | 工单设计 |
| **spec-driven-development** | 设计技术规格 | 工单设计 / 独立使用 |
| **planning-and-task-breakdown** | 分解规格为有序任务 | 工单设计 / 独立使用 |
| **definition-of-done** | 项目级完成标准检查清单 | 质量守门 |
| **codoop-execute** | 代码实现与交付（隔离 worktree） | 编码 & 发布 |
| **codoop-ux-walkthrough** | 用指定 persona 体验流程并产出非阻塞体验报告 | 独立使用 / 第三环批准后 |
| **incremental-implementation** | 把大改动拆成可逐步验证的小改动 | 第三环写码 / 独立使用 |
| **debugging-and-error-recovery** | 定位根因并指导失败恢复 | 第三环排错 / 独立使用 |
| **test-driven-development** | 按先写测试、再实现的方式开发 | 第三环验证 / 独立使用 |

每个 skill 都可以在完整的 codoop-flow 插件中独立触发。确定性 CLI、共享
Python 模块和评审 persona 只保留一份，统一放在
`runtime/codoop-flow/`；skill 不再各自携带脚本。

> 前提：目标机器有 `python3`(标准库即可,无第三方依赖);目标工程是一个 git 仓库,
> 且有 `docs/tickets/{pending,in_progress,done,failed}/`。准备一份 `codoop_flow.toml`
> 指向目标工程(见 `codoop_flow.toml.example`)。

---

## 一键安装（全部 12 个 Skill）

克隆一次，然后运行：

```bash
git clone https://github.com/Codoop/codoop-flow.git
bash codoop-flow/scripts/install-skills.sh
```

这会把全部 12 个 Skill 和一份共享 Runtime 安装到两个 agent。Codex
使用 `~/.codex/runtime/codoop-flow/`，Claude 使用
`~/.claude/runtime/codoop-flow/`。再跑一次就是原地更新。用
`--agent codex` 或 `--agent claude` 只装到某一个 agent。用 `--dry-run`
预览但不实际复制。

---

## Codex

从 GitHub marketplace 仓库安装 codoop-flow Codex 插件：

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

然后重启/打开 Codex。日常流程只需要两句话：

```text
使用 $codoop-init，分析这个仓库并初始化 codoop-flow。
使用 codoop-execute skill，针对 /path/to/codoop_flow.toml 跑下一张工单。
```

本地开发时也可以不走插件安装，改为克隆并用安装脚本：

```bash
git clone https://github.com/Codoop/codoop-flow.git
bash codoop-flow/scripts/install-skills.sh --agent codex
```

## Claude Code

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

请安装完整的 `codoop-flow` 插件项。各 Skill 共用插件 Runtime，不再作为
独立 Claude 插件发布。

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

装好后，可以在会话内直接调用核心 skill：

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

**6. codoop-execute**（第三环：代码实现）— 在会话内调用：
```
使用 codoop-execute skill，针对 /path/to/codoop_flow.toml 跑下一张工单
```

或用循环定时跑：
```
/loop 5m 使用 codoop-execute skill，针对 /path/to/codoop_flow.toml 跑下一张工单
```

**7. codoop-ux-walkthrough**（独立使用 / 技术批准后的洞察）— 让指定 persona 体验任务，写一份非阻塞报告：
```
/skill codoop-ux-walkthrough 请以首次使用的运营人员身份体验这个功能，并写入 experience_report.md。
```

---

## 通用拷贝(Cursor / Gemini / 其他)

请保持插件结构完整。如果某个 agent 必须复制 skill 目录，就把公开 skill
和 Runtime 分别复制到同一个 agent 根目录下的 `skills/` 与 `runtime/`：

```bash
git clone https://github.com/Codoop/codoop-flow.git
# 拷全部 12 个 Skill — 每个都自带 SKILL.md
for skill in codoop-init grilling codoop-discover codoop-ticket spec-driven-development \
             planning-and-task-breakdown definition-of-done codoop-execute \
             codoop-ux-walkthrough incremental-implementation \
             debugging-and-error-recovery test-driven-development; do
  cp -R "codoop-flow/skills/$skill"  <目标 agent 的技能目录>/
done
mkdir -p <agent根目录>/runtime
cp -R codoop-flow/runtime/codoop-flow <agent根目录>/runtime/
```

各 agent 的落脚点(参考各自文档,可能随版本变化):

| Agent | 放哪 | 怎么触发 |
|---|---|---|
| Cursor | 每个 `SKILL.md` 放进 `.cursor/rules/`，或让 agent 引用整个 `skills/` | 在对话里引用规则 |
| 其他 agent | skill 是纯 Markdown，把每个 `SKILL.md` 内容作为 system prompt / instructions 喂进去 | 直接对话 |
| Gemini CLI | 放进其 skills 目录 | 自动发现 |

**关键**：保持 `<agent根目录>/skills/` 和
`<agent根目录>/runtime/codoop-flow/` 同级。每个 Skill 都从自己的
`SKILL.md` 相对定位 Runtime；只搬 Skill 文件夹会找不到 CLI 和评审 persona。

---

## 验证装好了

```bash
codex plugin list
python3 <agent根目录>/runtime/codoop-flow/codoop_tools.py --config <toml> status
```
能打印出各阶段工单计数(JSON)就说明护栏 CLI 就位、config 正确。

> 注意:如果宿主 agent 没有 subagent 工具,就在同一个会话里串行运行评审 persona。
