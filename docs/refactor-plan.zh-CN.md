# codoop-flow 改造计划:把两个"人工环"的能力抽成一等公民

> 状态:待评审(3 个决策点未拍板)
> 目标读者:项目维护者
> 关联文档:[`engineering-design.zh-CN.md`](./engineering-design.zh-CN.md)(三环设计蓝图)

---

## 背景与问题

codoop-flow 的设计是**三层嵌套闭环**:

| 环 | 名称 | 职责 | 当前状态 |
|---|---|---|---|
| 第一环 | Venture-Discovery Loop | 0→1 商业/架构论证,多角色 challenge + 一致性硬审计,产出 `docs/backlog/` 设计资产 | ⚠️ 能力被锁在 subprocess 启动器里 |
| 第二环 | Human-Centric Loop | 人写 PRD/spec/plan/todo,promote 到 `pending/` | ❌ 智能撰写能力从未实现 |
| 第三环 | Agent-Centric Loop | 隔离 worktree 里 build/verify/review/ship | ✅ 已做成会话内可调用 skill(样板) |

**只有第三环真正被"抽成了给 agent 用的能力"**:`SKILL.md` 写给当前 agent 读,读了就能编排 `pick→build→verify→review→ship`,确定性部分交给 `codoop_tools.py`。另外两个环各有缺陷:

- **第一环**:`product-discovery-loop/SKILL.md` 其实写得很完整(编排 + challenge loop + 一致性审计 + 5 类产出),它引用的 5 个 sub-agent persona(`pm/gtm/ui-ux/architect/alignment-agent.md`)也都在。**但**:
  1. 它埋在 `skills/codoop-flow/references/skills/` 里,插件只注册了顶层 `skills/codoop-flow/` 一个 skill,扫不到它;
  2. frontmatter 写着 `disable-model-invocation: true`;
  3. `codoop.py discover` 是 `subprocess.run(["claude"/"codex", ...])` **另起一个新交互会话**,把 skill 用 `--append-system-prompt` 注进去。
  - 三重因素叠加 → 对已经在 Claude/Codex 会话里的用户,这个能力**当前会话里根本调不动**,体验割裂。
- **第二环**:连 skill 都没有。`tickets_cli.py` 只做确定性搬运(`init` 刷空模板 / `validate` 校验 / `promote` 搬运),**撰写 PRD/spec/plan/todo 的"智能编排"从来没写成能力**。personas 也是 discovery 导向,不是工单撰写导向。

## 改造目标

两个环的共同点:**都需要人一步步参与产出文档,无法全自动**。所以改造目标**不是"自动化掉人"**,而是把它们做成**当前会话内可直接调用**——像第三环那样,agent 读了 SKILL 就能编排,人只在决策点介入。确定性搬运继续留给 CLI。

**核心判断:可移植基元 = skill。** Claude Code 和 Codex 都通过 `skills/` 目录发现技能,所以三个环都做成 `skills/*/SKILL.md` 是最干净、跨宿主一致的做法。

---

## Phase 0 — 目录重构:让 skill 能被扫到

把埋在 `references/` 里的 discovery skill 提升到 `skills/` 顶层,与 `codoop-flow` 平级:

```
skills/
├── codoop-flow/        (第三环:Agent-Centric,已存在)
├── codoop-discover/    (第一环:Venture-Discovery,从 references 提升)
└── codoop-ticket/      (第二环:Human-Centric,新建)
```

共享 persona 归一到一个位置(建议 `skills/_shared/agents/` 或各 skill 内 `agents/`),修好相对路径引用。

## Phase 1 — 第一环:codoop-discover 变成可直接调用

1. 移动 `references/skills/product-discovery-loop/` → `skills/codoop-discover/`,连带 5 个 discovery-agent persona。
2. **删掉 `disable-model-invocation: true`**,改写 frontmatter description 让宿主能识别触发(如"用户想探索新产品/新功能的 0→1 设计时")。
3. 修正 persona 相对路径(现在写死 `../../discovery-agents/`)。
4. `codoop.py discover` 的 subprocess launcher:保留还是废弃,见决策点 B。
5. 确定性部分(创建 `docs/backlog/` 目录、归档清理)可加进 `codoop_tools.py` 或保留在 skill 里用 bash。

## Phase 2 — 第二环:新建 codoop-ticket 撰写 skill

这是**从零写**的部分(现在完全缺失)。

1. 新建 `skills/codoop-ticket/SKILL.md`,编排工单撰写全流程:
   - 调 `codoop.py ticket init`(确定性刷脚手架)
   - **在会话内**,借 PM persona 写 `module_prd.md`(纯业务)、architect persona 写 `spec.md`(契约 + `files_to_edit` 白名单)、再拆 `plan.md`/`todo.md`
   - 调 `codoop.py ticket validate` + `promote`(确定性搬运到 `pending/`)
2. 撰写 persona 复用还是新建,见决策点 C。
3. SKILL 明确区分:智能撰写 = 会话内;搬运/校验 = `tickets_cli.py`。与第三环护栏哲学保持一致。

## Phase 3 — 插件注册

在三处 manifest 里让新 skill 可被发现/触发:

- `.claude-plugin/plugin.json` + `marketplace.json`
- `.codex-plugin/plugin.json`(`"skills": "./skills/"` 已指向目录,新增子目录即可被扫)
- `skills/codoop-flow/agents/openai.yaml` 的 `default_prompt` 补充 discover/ticket 入口

## Phase 4 — 测试与文档

- `tests/test_skeleton.py`:discover 现有的 command-build 断言随路径调整;新增 ticket 撰写 skill 的确定性边界测试(`init→validate→promote` 已覆盖,补校验新脚手架)。撰写本身是 AI 活,不进 skeleton 测试。
- `README.md` / `README.zh-CN.md`:三个 skill 的入口说明。
- `docs/engineering-design.md`:标注"三环现均为会话内可调用 skill",修正设计与实现的偏差描述。

---

## 需要拍板的三个决策点

- **A. persona 形态**:纯 markdown 由 skill 读取(全宿主通用) vs 额外注册 Claude 原生 `agents/`(隔离更好但 Codex 用不上)。
  - *推荐*:纯 markdown 为单一真相源;Claude 原生 agent 作为可选增强。
- **B. discover 的 subprocess launcher**:保留为可选 headless 入口 vs 废弃只留会话内。
  - *推荐*:保留但降级为可选,SKILL.md 把"当前会话内直接编排"作为首选路径。
- **C. 工单撰写 persona**:复用 discovery 的 `pm-agent`/`architect-agent` vs 新建工单尺度的精简版。
  - *推荐*:新建两个轻量 persona(`ticket-pm.md`、`ticket-architect.md`)。discovery 是 0→1 全局,工单是增量小尺度,语气/产出粒度不同,避免用大炮打蚊子。

---

## 改造后的形态(预期)

三个环都成为**当前会话内可直接调用**的一等公民 skill,跨 Claude Code / Codex 一致:

| 环 | Skill | 智能活(会话内) | 确定性活(CLI) |
|---|---|---|---|
| 第一环 | `codoop-discover` | 多角色 challenge、一致性审计、5 类设计文档撰写 | 建 `docs/backlog/`、归档清理 |
| 第二环 | `codoop-ticket` | PRD/spec/plan/todo 撰写 | `init` 脚手架、`validate`、`promote` |
| 第三环 | `codoop-flow` | 写代码、自愈、review 判断、文档同步 | `pick`/`verify`/`finish`/`fail`、worktree、白名单 |

---

## 附录:实施前必读的关键上下文(供新对话冷启动)

> 这一节记录本次调研得出的、重新读代码才能拿到的关键事实。下次开新对话处理本计划时,先读这一节,能省去从头摸一遍代码的时间。**但注意:文件可能已被改动,动手前请对涉及的路径/符号做一次核实。**

### A. 关键文件地图

- **第三环样板(照着抄)**:`skills/codoop-flow/SKILL.md`(8 步编排,写给 agent 读)+ `skills/codoop-flow/scripts/codoop_tools.py`(护栏 CLI:`status/pick/verify/finish/fail`)。
- **第一环 skill(要提升的)**:`skills/codoop-flow/references/skills/product-discovery-loop/SKILL.md` + 同目录 `README.md`。它引用的 5 个 persona 在 `skills/codoop-flow/references/discovery-agents/`(`pm-agent.md` / `gtm-agent.md` / `ui-ux-agent.md` / `architect-agent.md` / `alignment-agent.md`,外加 `product-architect.md`)。
- **第一环 launcher**:`skills/codoop-flow/scripts/codoop_flow/discover.py` —— `build_command()` 组装 `claude --append-system-prompt <skill内容> --add-dir <references>` 或 `codex --cd <repo> --add-dir <references> <prompt>`;`launch()` 用 `subprocess.run` 另起会话。`codoop.py discover` 是其 CLI 入口。
- **第二环 CLI(纯确定性,无撰写智能)**:`skills/codoop-flow/scripts/codoop_flow/tickets_cli.py` —— `init_draft`(刷空模板)/ `validate_draft`(必需 `module_prd.md`+`spec.md` 被"有意义填充")/ `promote`(drafts→pending 搬运)。`init_draft` 刷的模板正文是中文脚手架标题。
- **确定性模块**:`config.py`(TOML 加载,`Config` 派生 `pending/in_progress/done/failed_dir`)、`ticket.py`(`Ticket.load` 校验 `metadata.json`,必需字段 `ticket_id/title/modules/test_command/files_to_edit`;`screenshot_dir` = `<ticket>/public/qa-screenshots`)、`worktree.py`(worktree 生命周期,分支 `dev/<id>`,支持重试复用)、`verify.py`(三重硬门:白名单 fnmatch + 测试 + UI 截图)、`gitutil.py`、`ignore.py`(生成噪音过滤)。
- **测试**:`tests/test_skeleton.py`,14 个纯确定性 subprocess 测试(无 AI),含 `test_discover_claude_command_build` / `test_discover_codex_command_build` / `test_discover_agent_aliases` —— **移动 discover skill 路径后这几个断言会受影响,需同步改**。
- **插件 manifest(Phase 3 要改)**:`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`;`.codex-plugin/plugin.json`(`"skills": "./skills/"` 已指向目录,新增子目录即可被扫);`.agents/plugins/marketplace.json`;`skills/codoop-flow/agents/openai.yaml`(`default_prompt`)。

### B. 为什么第一环"当前会话里调不动"(三重因素,缺一不可全解)

1. **扫不到**:插件只注册顶层 `skills/codoop-flow/` 一个 skill,discovery skill 埋在其 `references/skills/` 子目录里,不会被宿主当独立 skill 发现。
2. **被禁用模型调用**:`product-discovery-loop/SKILL.md` frontmatter 有 `disable-model-invocation: true`。
3. **设计成另起会话**:`discover.py` 用 `subprocess.run` 起一个**全新的** `claude`/`codex` 交互进程,而不是在当前会话内编排。

→ Phase 1 必须**同时**解决这三点,只改一个没用。

### C. 术语澄清(本次对话确认)

- 用户口中的 **"Cortex" = OpenAI Codex**(不是新 agent,也不是 Anthropic 产品)。现有代码已支持 codex,双引擎适配的重点不在"新增引擎",而在把两个人工环做成跨 Claude/Codex 一致的会话内 skill。

### D. 用户对本次改造的明确意图(原话要点)

- 三环大结构已搭好,但其中两个环需要人工参与、逐步产出文档,**目前无法全自动 AI 实现**,用户也认可这一点——目标不是自动化掉人。
- 诉求:把这两个人工环**用到的 skill 和 sub-agent 单独抽出来**,让用户在**外部/会话内能直接调用**,而不是像现在这样"通过内部脚本刷一套空模板"。
- 本文档就是应用户要求先导出的计划稿,用户明天将**开启新对话**据此实施。

### E. 三个决策点尚未拍板

见上一节。动手前需要用户先就 A(persona 形态)/ B(launcher 去留)/ C(撰写 persona 复用还是新建)给出方向。文档里已附推荐值,若用户说"按推荐来"即可采用推荐值。
