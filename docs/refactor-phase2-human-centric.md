# codoop-flow 第二环改造：Human-Centric Loop 升级为会话内可调用 Skill

> 状态：规划中
> 目标读者：项目维护者
> 关联文档：
> - [`refactor-plan.zh-CN.md`](./refactor-plan.zh-CN.md) — 完整三环改造总体计划
> - [`engineering-design.md`](./engineering-design.md) — 三环架构蓝图（§4 Human-Centric Loop）
> - [`refactor-phase1-venture-discovery.md`](./refactor-phase1-venture-discovery.md) — 第一环改造参考

---

## 背景与问题

### 当前状态

**第二环（Human-Centric Loop）** 的职责是帮助用户精心设计工单（ticket），在代码实现前明确业务需求和技术契约。

**现状分析**：

| 维度 | 当前状态 |
|------|---------|
| **SKILL.md** | ❌ 不存在 |
| **CLI** | ✅ 存在（`tickets_cli.py`），但仅做确定性操作：`init`、`validate`、`promote` |
| **撰写能力** | ❌ 完全缺失 — 没有 sub-agent 协助用户撰写 PRD、Spec、Plan、Todo |
| **Sub-agents** | ❌ 未定义 — 没有工单尺度的专家角色 |
| **工单输出** | 🔲 手工阶段 — 用户需要自己或找 AI 帮忙写 4 个文档 |

### 使用场景（本次改造的真实诉求）

**三阶段工作流程，人类全程参与决策**：

- **触发点**：用户从第一环（Venture-Discovery）生成的 `docs/backlog/` 中梳理出一个工单想法
- **操作**：用户在会话里说 `/skill codoop-ticket draft <ticket_id>`

**第一阶段：需求设计 (module_prd.md)**
1. Skill 与用户讨论工单范围、目标、依赖
2. 结合第一环产出的设计规范、产品文档（`docs/backlog/product/`、`docs/backlog/interface/` 等）
3. PM sub-agent 帮助撰写 `module_prd.md`（纯业务，无技术细节）
4. **人类确认** module_prd 完整无误后，进入下一阶段

**第二阶段：技术规格 (spec.md)**
1. 调用 `source/agent-skills-main/skills/spec-driven-development` skill
2. 基于 module_prd.md，设计 spec.md（API 接口、DB 字段、各端实现细节、edit-scope 白名单）
3. **人类确认** spec 完整后，进入下一阶段

**第三阶段：任务分解 (plan.md + todo.md)**
1. 调用 `source/agent-skills-main/skills/planning-and-task-breakdown` skill
2. 基于 spec.md，分解成 plan.md（实现步骤）和 todo.md（原子任务清单）
3. **人类确认** 完成定稿

**最终**：工单文件组完整，迁移到 `pending/`，等待第三环自动 pick 并开发

→ **改造目标**：把第二环做成**当前会话内可直接调用**的工单设计 skill，与第一环深度联动，复用现有 spec 和 planning skills，每阶段都融合人类决策。

---

## 改造目标与范围

### 核心目标

两个维度的升级：

| 维度 | 当前状态 | 改造后 |
|------|--------|--------|
| **工单编排** | 无 SKILL — 工单设计无流程 | `codoop-ticket` skill 提供三阶段编排 |
| **需求撰写** | 纯手工或另起 AI 窗口 | 会话内编排：PM 撰写 PRD |
| **规格设计** | 调用外部 skill 需手动 | SKILL.md 自动加载 spec-driven-development |
| **任务分解** | 手工或另起 AI | SKILL.md 自动加载 planning-and-task-breakdown |
| **第一环联动** | 无关联 | 结合 `docs/backlog/` 的产品规范、设计规范 |
| **人类参与** | 每阶段都需 | 三阶段都有明确的人类确认点 |
| **确定性部分** | ✅ 已有 CLI | 保持不变，继承 `tickets_cli.py` init/validate/promote |

### 改造不包括

- ❌ `tickets_cli.py` 的修改 — 确定性部分继续保留
- ❌ 第一环（Venture-Discovery）的进一步改造 — 已完成
- ❌ 第三环（Agent-Centric）的改造 — 已完成
- ❌ 全局安装方案 — 留待三环完成后统一处理

---

## 改造步骤

### Phase 2.0 — 目录结构升级：新建 codoop-ticket skill

**当前结构**：
```
skills/
├── codoop-discover/
├── codoop-flow/
└── _shared/
    └── agents/
```

**改造后结构**：
```
skills/
├── codoop-discover/
├── codoop-ticket/          (← 新增，第二环 Human-Centric)
│   ├── SKILL.md
│   ├── README.md
│   └── agents/
│       ├── ticket-pm.md (轻量工单 PM persona)
│       └── ticket-architect.md (轻量工单架构师 persona)
├── codoop-flow/
└── _shared/
    └── agents/
```

**具体操作**：

1. 创建 `skills/codoop-ticket/` 目录
2. 新建 `ticket-pm.md` 和 `ticket-architect.md`（轻量版 personas）
3. 新建 `SKILL.md`（工单编排的主逻辑）
4. 新建 `README.md`（用户指南）

### Phase 2.1 — 创建轻量工单 Personas

**为什么需要新 personas？**

- Discovery 的 PM 和 Architect 是**全局 0→1 阶段**，内容庞大复杂
- 工单设计是**增量小范围阶段**，只关心"这个模块做什么"，不需要商业论证

**新 personas 的特点**：

| 角色 | Discovery 版本 | 工单轻量版 |
|------|---------------|----------|
| **ticket-pm.md** | 撰写全局 PRD、OST、用户旅程、商业模式 | 只写这个工单的 PRD：业务需求、验收标准、edge cases |
| **ticket-architect.md** | 设计全局架构、DB schema、OpenAPI | 只写这个工单的契约：API 接口、DB 字段、edit-scope 白名单 |

**内容来源**：
- 参考 Discovery 版本的结构，但去掉大规模论证部分
- 聚焦工单尺度的快速、精准撰写

### Phase 2.2 — 新建 codoop-ticket SKILL.md

**三阶段编排流程**：

```
【第一阶段】需求设计 (module_prd.md)
1. 初始化 — 创建 tickets/drafts/<ticket_id>/ 骨架（调用 tickets_cli init）
2. 需求澄清 — 与用户讨论：
   - 工单范围、目标、依赖
   - 结合第一环产出的 docs/backlog/{product/interface/architecture/modules/}
3. PRD 撰写 — PM sub-agent 基于用户输入和第一环文档撰写 module_prd.md
4. 人类确认 — 用户审阅、反馈、修改，直到满意

【第二阶段】技术规格 (spec.md)
5. 加载 spec-driven-development skill — 从 source/agent-skills-main/skills/spec-driven-development
6. 基于 module_prd.md 设计 spec.md — 包含：
   - API 接口定义（各端：backend / web / mobile / desktop）
   - 数据库字段变更
   - 业务逻辑约束
   - files_to_edit 白名单（第三环会用到）
7. 人类确认 — 用户审阅、反馈、修改，直到满意

【第三阶段】任务分解 (plan.md + todo.md)
8. 加载 planning-and-task-breakdown skill — 从 source/agent-skills-main/skills/planning-and-task-breakdown
9. 基于 spec.md 分解任务 — 生成：
   - plan.md（实现步骤：Step 1, Step 2, ...）
   - todo.md（原子任务清单，≤100 行代码/任务）
10. 人类确认 — 用户审阅、反馈、修改，直到满意

【最终化】
11. 验证完整 — 调用 tickets_cli validate 检查必要字段
12. Promote — 调用 tickets_cli promote 移到 pending/，工单完成设计定稿
```

**Frontmatter**：

```yaml
---
name: codoop-ticket
description: Draft work tickets with intelligent PRD, spec, and plan guidance. Use when designing incremental features ready for implementation. Guides PM and Architect agents through structured ticket design, outputting module_prd.md, spec.md, plan.md, and todo.md.
---
```

**关键差异 vs Discovery**：
- 不需要"一致性硬审计"（工单范围小，冲突少）
- 不需要多个角色协作辩论（只有 PM + Architect）
- 重点是"快速精准"而非"全局论证"

### Phase 2.3 — Sub-Agent 轻量 Personas 设计

**ticket-pm.md 应该包含**：
- 工单 PRD 的快速模板（业务需求、用户故事、验收标准）
- 强调"这个工单解决什么问题"，不需要 OST 或商业模式
- 示例：电商系统添加"优惠券功能"的工单 PRD（几百字，不是几千字）

**ticket-architect.md 应该包含**：
- 工单契约定义（API 端点、DB 表、权限范围）
- 强调"这个工单改什么代码，改什么数据"，不需要全栈架构论证
- 示例：优惠券功能的 spec（新增哪些 API、哪些 DB 字段、白名单限制）

### Phase 2.4 — 插件 manifest 注册

在两处 manifest 中添加 `codoop-ticket` 入口：

1. `.claude-plugin/marketplace.json`
2. `.agents/plugins/marketplace.json`

（参考 Phase 1.4 的做法）

### Phase 2.5 — 测试与文档

1. **`tests/test_skeleton.py`**：
   - 新增 ticket lifecycle 测试（已存在）
   - 新增 ticket SKILL 的单步验证（可选）

2. **`skills/codoop-ticket/README.md`**：
   - 说明如何在会话内调用 `/skill codoop-ticket`
   - 工单工作流示例
   - 与第一环、第三环的协作关系

3. **`docs/install.md` 更新**：
   - 补充 codoop-ticket 的安装和使用说明

---

## 改造前必读的关键上下文

### A. 关键文件现状

**codoop-flow 项目内**：
- **工单 CLI（确定性部分）**：`skills/codoop-flow/scripts/codoop_flow/tickets_cli.py`
  - `init_draft()` — 创建 `drafts/<id>/` 骨架，写空模板
  - `validate_draft()` — 检查 `module_prd.md` 和 `spec.md` 是否有意义内容
  - `promote()` — 移动 `drafts/<id>/` → `pending/<id>/`

- **工单配置**：`skills/codoop-flow/scripts/codoop_flow/ticket.py`
  - 定义 `metadata.json` 的必需字段（ticket_id、title、modules、test_command、files_to_edit 等）

- **第二环现有文档**：`docs/engineering-design.md` §4 Human-Centric Loop
  - 定义了 PRD / Spec / Plan / Todo 的输出规范

**source/agent-skills-main 中的外部 skills**（需要在 codoop-ticket SKILL.md 中调用）：
- **spec-driven-development** — `source/agent-skills-main/skills/spec-driven-development/`
  - 指导如何从业务需求设计出技术契约
  - 产出 spec.md（API、DB、各端实现细节）

- **planning-and-task-breakdown** — `source/agent-skills-main/skills/planning-and-task-breakdown/`
  - 指导如何从技术契约分解出实现步骤和原子任务
  - 产出 plan.md（步骤）和 todo.md（任务清单）

### B. 设计约束

1. **不能改 tickets_cli.py** — 确定性部分是护栏，不能动
2. **SKILL.md 必须调用 tickets_cli** — 流程最后还是要用 CLI 来 validate + promote
3. **相对路径** — ticket-pm.md / ticket-architect.md 应该放在 `skills/codoop-ticket/agents/` 还是 `skills/_shared/agents/`？
   - **建议**：放在 `skills/codoop-ticket/agents/`（工单专用，不跨环复用）

### C. 改造前的代码检查清单

在动手改造前，确认：

- [ ] `skills/codoop-flow/scripts/codoop_flow/tickets_cli.py` 的接口稳定（validate、promote 的返回值）
- [ ] `tests/test_skeleton.py` 中 ticket lifecycle 的断言是否覆盖全
- [ ] Discovery 的 PM/Architect personas 中，哪些部分可以作为"轻量版"的参考

---

## 改造后的预期形态

改造完成后，第二环 skill 将能够：

| 功能 | 实现方式 | 例子 |
|------|--------|------|
| **会话内直接调用** | 宿主识别 `skills/codoop-ticket/SKILL.md` | 用户：`/skill codoop-ticket draft ticket_001` |
| **工单初始化** | 调用 `tickets_cli init` | 创建 `docs/tickets/drafts/ticket_001/` 骨架 |
| **需求澄清** | SKILL 与用户对话，读取第一环输出 | 基于 `docs/backlog/` 的产品规范、设计规范进行讨论 |
| **第一阶段：PRD 撰写** | PM sub-agent 基于讨论和第一环文档 | 产出 `module_prd.md`（纯业务） |
| **人类确认 #1** | 用户 review + 反馈 + 修改 | 直到用户满意 PRD 内容 |
| **第二阶段：Spec 设计** | 加载 spec-driven-development skill | 基于 PRD 产出 `spec.md`（API、DB、各端细节） |
| **人类确认 #2** | 用户 review + 反馈 + 修改 | 直到用户满意 Spec 内容 |
| **第三阶段：任务分解** | 加载 planning-and-task-breakdown skill | 基于 Spec 产出 `plan.md` + `todo.md` |
| **人类确认 #3** | 用户 review + 反馈 + 修改 | 直到用户满意任务分解 |
| **完整性验证** | 调用 `tickets_cli validate` | 检查必需字段、files_to_edit、test_command 等 |
| **工单发布** | 调用 `tickets_cli promote` | 移至 `pending/`，等待第三环自动 pick 和开发 |

---

## 待确认的决策点

1. **第一环产出物的读取**：
   - codoop-ticket SKILL 中如何读取 `docs/backlog/` 下的产品规范、设计规范、架构文档？
   - 是否应该自动扫描并提供给 PM 和 Architect agents 作为上下文？
   - **建议**：是的，自动读取并注入到 sub-agent prompts 中

2. **spec-driven-development 和 planning-and-task-breakdown 的集成方式**：
   - SKILL.md 中是否直接 include 这两个 skill 的内容？
   - 还是通过文本描述 + 指引用户？
   - **建议**：直接 include 或清晰引用，让编排流程无缝衔接

3. **ticket-pm 和 ticket-architect personas 的设计粒度**：
   - 相比 Discovery 版本，应该如何精简？
   - 是否需要明确工单范围限制（"只涉及 module X，不考虑全局"）？
   - **建议**：精简到工单尺度，强调"增量、小范围"的设计原则

4. **人类确认的触发方式**：
   - 每个阶段完成后，SKILL 如何让用户确认？
   - 是否需要自动 validate 后提示？
   - **建议**：明确的"确认点"，用户 review 后说"OK，进入下一阶段"

5. **工单从 draft → pending 的自动检查**：
   - promote 前是否需要额外的完整性检查？
   - 比如检查 files_to_edit 是否合理、test_command 是否完整？
   - **建议**：复用 tickets_cli validate，但可考虑增强检查规则

---

## 附录：改造影响范围速查

### 受影响的文件列表

- 📝 **新增**：
  - `skills/codoop-ticket/SKILL.md`
  - `skills/codoop-ticket/README.md`
  - `skills/codoop-ticket/agents/ticket-pm.md`
  - `skills/codoop-ticket/agents/ticket-architect.md`

- ✏️ **修改**：
  - `.claude-plugin/marketplace.json` （添加 codoop-ticket 条目）
  - `.agents/plugins/marketplace.json` （添加 codoop-ticket 条目）
  - `docs/install.md` 和 `.zh-CN.md` （补充 codoop-ticket 说明）
  - 主 `README.md` 和 `.zh-CN.md` （补充三环介绍）

- 🚫 **不动**：
  - `tickets_cli.py` （确定性护栏，保持原样）
  - `test_skeleton.py` （现有 ticket 测试不改）

---

## 下一步

确认上述"待确认的决策点"后，即可开始 Phase 2 的实施。

预计工作量：较 Phase 1 稍轻（复用第一环的框架，新建 2 个轻量 personas + SKILL）。
