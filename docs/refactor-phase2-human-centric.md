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

- **触发点**：用户从第一环（Venture-Discovery）生成的 `docs/backlog/` 中梳理出一个工单想法
- **操作**：用户在会话里说 `/skill codoop-ticket init <ticket_id>` 或 `/skill codoop-ticket draft <ticket_id>`
- **流程**：
  1. 与用户讨论工单范围和目标
  2. **PM agent** 帮助撰写 `module_prd.md`（纯业务，无技术）
  3. **Architect agent** 帮助撰写 `spec.md`（契约定义、API、DB、白名单）
  4. **可选**：撰写 `plan.md` 和 `todo.md`
  5. 验证工单完整性，promote 到 `pending/`

→ **改造目标**：把第二环做成**当前会话内可直接调用**的智能工单设计 skill，像第一环那样。

---

## 改造目标与范围

### 核心目标

两个维度的升级：

| 维度 | 当前状态 | 改造后 |
|------|--------|--------|
| **发现** | 无 SKILL — 工单设计无流程 | `codoop-ticket` skill 提供完整编排 |
| **撰写** | 纯手工或另起 AI 窗口 | 会话内智能编排：PM + Architect 多角色协作 |
| **Sub-agents** | 无 | 轻量工单专用 personas（ticket-pm、ticket-architect） |
| **确定性部分** | ✅ 已有 CLI | 保持不变，继承 `tickets_cli.py` |

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

**编排流程**：

```
1. 初始化 — 创建 tickets/drafts/<ticket_id>/ 骨架
2. 需求澄清 — 与用户讨论工单范围、目标、依赖
3. PRD 撰写 — PM agent 基于业务目标撰写 module_prd.md
4. Spec 撰写 — Architect agent 基于 PRD 撰写 spec.md
5. 可选计划 — 用户选择是否撰写 plan.md / todo.md
6. 验证完整 — 调用 tickets_cli validate 检查必要字段
7. Promote — 调用 tickets_cli promote 移到 pending/
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

- **工单 CLI（确定性部分）**：`skills/codoop-flow/scripts/codoop_flow/tickets_cli.py`
  - `init_draft()` — 创建 `drafts/<id>/` 骨架，写空模板
  - `validate_draft()` — 检查 `module_prd.md` 和 `spec.md` 是否有意义内容
  - `promote()` — 移动 `drafts/<id>/` → `pending/<id>/`

- **工单配置**：`skills/codoop-flow/scripts/codoop_flow/ticket.py`
  - 定义 `metadata.json` 的必需字段（ticket_id、title、modules、test_command、files_to_edit 等）

- **第二环现有文档**：`docs/engineering-design.md` §4 Human-Centric Loop
  - 定义了 PRD / Spec / Plan / Todo 的输出规范

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
| **需求澄清** | SKILL 与用户对话 | 明确工单范围、依赖、目标 |
| **多角色撰写** | PM + Architect agents 在会话内写文档 | PRD 和 Spec 联动完成 |
| **完整性验证** | 调用 `tickets_cli validate` | 检查必需字段和内容有意义 |
| **工单发布** | 调用 `tickets_cli promote` | 移至 `pending/`，等待第三环 pick |

---

## 待确认的决策点

1. **轻量 Persona 的程度**：
   - 相比 Discovery 版本，应该简化到什么程度？
   - 建议：保留 80% 的逻辑，去掉商业论证部分

2. **Plan & Todo 的撰写**：
   - SKILL 中是否自动撰写 `plan.md` 和 `todo.md`？
   - 还是让用户可选？
   - **推荐**：可选（PRD + Spec 是必需，Plan/Todo 可选，用户按需要求）

3. **Persona 存放位置**：
   - `skills/codoop-ticket/agents/` （工单专用）
   - 还是 `skills/_shared/agents/` （通用库）？
   - **推荐**：工单专用（discovery 和 ticket 的需求差异太大，不适合混在一起）

4. **与 Discovery 的分界**：
   - 什么时候用第一环（Discover），什么时候用第二环（Ticket）？
   - **建议**在文档和两个 README 中明确说明工作流分界

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
