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
| **工单编排 SKILL** | ❌ 不存在 — `codoop-ticket/SKILL.md` |
| **Spec SKILL** | 🔲 隐藏在 source/ — 应提升到顶层 `skills/spec-driven-development/` |
| **Plan SKILL** | 🔲 隐藏在 source/ — 应提升到顶层 `skills/planning-and-task-breakdown/` |
| **工单 CLI** | ✅ 存在（`tickets_cli.py`），但仅做确定性操作：`init`、`validate`、`promote` |
| **工单撰写能力** | ❌ 无 — 需要新建 `codoop-ticket` skill |
| **用户直接使用** | 🔲 Spec/Plan 只能通过工单编排调用 | 应该让 spec-driven-development、planning-and-task-breakdown 也**独立可调用** |

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

**三个新 skills 各司其职 + 工单编排整合**：

| Skill | 现状 | 改造后 |
|-------|------|--------|
| **codoop-ticket** | ❌ 无 | 新建 — 工单设计三阶段编排 + 调用下游 skills |
| **spec-driven-development** | 🔲 source/ 隐藏 | 提升到顶层 — 用户可独立调用生成 spec 文档 |
| **planning-and-task-breakdown** | 🔲 source/ 隐藏 | 提升到顶层 — 用户可独立调用生成 plan/todo 文档 |
| **工单 CLI** | ✅ tickets_cli | 保持原样 — init/validate/promote 的确定性操作 |

**用户使用场景**：

| 场景 | 调用方式 |
|------|---------|
| 完整工单设计（PRD→Spec→Plan） | `/skill codoop-ticket draft ticket_001` |
| 只生成 spec 文档 | `/skill spec-driven-development` 直接调用 |
| 只生成 plan/todo | `/skill planning-and-task-breakdown` 直接调用 |
| 工单生命周期管理 | `python codoop.py ticket init/validate/promote` |

### 改造不包括

- ❌ `tickets_cli.py` 的修改 — 确定性部分继续保留
- ❌ 第一环（Venture-Discovery）的进一步改造 — 已完成
- ❌ 第三环（Agent-Centric）的改造 — 已完成
- ❌ 全局安装方案 — 留待三环完成后统一处理

---

## 改造步骤

### Phase 2.0 — 目录结构升级：新建三个顶层 skills

**当前结构**：
```
skills/
├── codoop-discover/
├── codoop-flow/
└── _shared/
    └── agents/

source/
└── agent-skills-main/
    └── skills/
        ├── spec-driven-development/     (← 资源，待复制）
        └── planning-and-task-breakdown/ (← 资源，待复制）
```

**改造后结构**：
```
skills/
├── codoop-discover/
├── codoop-ticket/          (← 新增，工单编排编排）
│   ├── SKILL.md
│   └── README.md
├── spec-driven-development/       (← 新增，从 source/ 复制提升）
│   ├── SKILL.md
│   └── README.md
├── planning-and-task-breakdown/   (← 新增，从 source/ 复制提升）
│   ├── SKILL.md
│   └── README.md
├── definition-of-done/            (← 新增，从 source/ 复制提升，planning 依赖）
│   ├── SKILL.md
│   └── README.md
├── codoop-flow/
└── _shared/
    └── agents/
        ├── product-sprint-prioritizer.md
        ├── engineering-backend-architect.md
        ├── engineering-software-architect.md
        └── alignment-agent.md
```

**关键点**：
- ✅ 从 `source/agent-skills-main/` 中**复制** spec 和 plan 的内容
- ✅ 提升为顶层 `skills/spec-driven-development/` 和 `skills/planning-and-task-breakdown/`
- ✅ 使其成为独立可调用的 skills（用户可直接 `/skill spec-driven-development` 或 `/skill planning-and-task-breakdown`）
- ✅ `codoop-ticket` 会调用这两个 skills 作为子步骤
- 📌 改造完成后由用户自行清理 `source/` 资源

**具体操作**：

1. 创建 `skills/codoop-ticket/` 目录
2. 新建 `SKILL.md`（工单编排的主逻辑，明确指引工单设计范围）
3. 新建 `README.md`（用户指南）
4. **不新增 personas** — 直接复用 `skills/_shared/agents/` 中的：
   - `product-sprint-prioritizer.md`（PM agent）
   - `engineering-backend-architect.md` + `engineering-software-architect.md`（Architect agents）

### Phase 2.1 — 复制并提升 spec-driven-development、planning-and-task-breakdown 和 definition-of-done

**复制清单**：
- `source/agent-skills-main/skills/spec-driven-development/SKILL.md` → `skills/spec-driven-development/SKILL.md`
- `source/agent-skills-main/skills/planning-and-task-breakdown/SKILL.md` → `skills/planning-and-task-breakdown/SKILL.md`
- `source/agent-skills-main/references/definition-of-done.md` → 转换为 `skills/definition-of-done/SKILL.md`（planning 依赖）

**为什么提升到顶层**：
1. 这三个 skills **独立价值高** — 用户可能单独需要调用，不一定走完整工单编排流程
2. **跨项目复用** — 其他项目也可能单独引用这些 skills
3. **一级入口** — 让用户可以直接 `/skill spec-driven-development`、`/skill planning-and-task-breakdown` 和 `/skill definition-of-done`

**新建文件**：
- `skills/spec-driven-development/README.md` — 说明独立调用方式 + 作为工单子步骤的行为
- `skills/planning-and-task-breakdown/README.md` — 说明独立调用方式 + 作为工单子步骤的行为
- `skills/definition-of-done/README.md` — 说明如何在工单流程中引用此标准

**调整**：
- planning SKILL.md 中的引用改为：`See /skill definition-of-done` 而非指向文件路径
- definition-of-done.md 的内容改写为 SKILL.md 格式（加上 YAML frontmatter）

### Phase 2.2 — 工单 CLI 增强：元数据自动推断

**新增功能**：`update_metadata_from_docs()` 和 `write_metadata()`

**智能推断逻辑**：
- `modules` — 从 spec.md 的标题中提取（"## Backend"、"## Web" 等）
- `files_to_edit` — 从 spec.md 的"## Editable Files"部分提取
- `test_command` — 根据 modules 生成默认值（可被用户覆盖）

**工作流**：
1. AI agent 完成 spec.md 撰写
2. codoop-ticket SKILL 调用 `tickets_cli update-metadata`
3. 自动推断 modules、files_to_edit、test_command
4. 显示推断结果给用户 review
5. 用户确认或修改后进行 validate + promote

**CLI 支持**：
```bash
python codoop.py ticket update-metadata <ticket_id>
```

### Phase 2.3 — 新建 codoop-ticket SKILL.md（工单编排编排）

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
5. 调用 spec-driven-development skill（已提升到顶层 skills/）
6. 基于 module_prd.md 设计 spec.md — 包含：
   - API 接口定义（各端：backend / web / mobile / desktop）
   - 数据库字段变更
   - 业务逻辑约束
   - files_to_edit 白名单（第三环会用到）
7. 人类确认 — 用户审阅、反馈、修改，直到满意

【第三阶段】任务分解 (plan.md + todo.md)
8. 调用 planning-and-task-breakdown skill（已提升到顶层 skills/）
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

### Phase 2.3 — codoop-ticket 使用 PM + Architect Agents，工单范围通过 SKILL.md 指引

**复用 Discovery 中的 agents**：
- `product-sprint-prioritizer.md`（PM agent）
- `engineering-backend-architect.md` + `engineering-software-architect.md`（Architect agents）

**SKILL.md 中的工单范围上下文**：

在调用 PM agent 之前：
```
这是一个工单设计阶段，我们的目标是为"<module_name>"模块设计 PRD。
聚焦在这个模块的业务需求、用户故事、验收标准。
如果涉及商业模式、GTM 策略或跨模块影响，请主动确认用户是否需要讨论。
```

在调用 Architect agent 之前：
```
这是一个工单设计的技术规格阶段，基于已有的系统架构（见 docs/backlog/architecture/）。
聚焦在"<module_name>"模块的：API 接口设计、DB 字段变更、各端实现细节。
如果涉及全局架构变更、性能重构等超出工单范围的事项，请主动确认用户。
```

**设计指导**：
- ✅ 复用已验证的高质量 agents
- ✅ 保持思维框架一致性
- ✅ agents 智能识别"超出范围"的决策点，主动找用户确认
- ✅ 减少维护负担，无需为工单尺度创建新 personas

### Phase 2.4 — 插件 manifest 注册

在两处 manifest 中添加三个新 skills 入口：

1. `.claude-plugin/marketplace.json`
   - codoop-ticket
   - spec-driven-development
   - planning-and-task-breakdown

2. `.agents/plugins/marketplace.json`
   - codoop-ticket
   - spec-driven-development
   - planning-and-task-breakdown

（参考 Phase 1.4 的做法）

### Phase 2.5 — 更新文档

1. **`skills/codoop-ticket/README.md`**：
   - 说明如何在会话内调用 `/skill codoop-ticket`
   - 工单三阶段工作流示例
   - 与第一环、第三环的协作关系

2. **`skills/spec-driven-development/README.md`**：
   - 说明独立调用方式：`/skill spec-driven-development`
   - 说明作为 codoop-ticket 子步骤时的行为
   - 规格设计指南

3. **`skills/planning-and-task-breakdown/README.md`**：
   - 说明独立调用方式：`/skill planning-and-task-breakdown`
   - 说明作为 codoop-ticket 子步骤时的行为
   - 任务分解指南

4. **`docs/install.md` 更新**：
   - 补充三个新 skills 的安装和使用说明

5. **`README.md` 更新**：
   - 更新"Three Loops"表格，添加 spec-driven-development 和 planning-and-task-breakdown

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

**source/agent-skills-main 中的资源**（待复制提升到 skills/）：
- **spec-driven-development** — `source/agent-skills-main/skills/spec-driven-development/`
  - 将复制到 `skills/spec-driven-development/`
  - 指导如何从业务需求设计出技术契约
  - 产出 spec.md（API、DB、各端实现细节）

- **planning-and-task-breakdown** — `source/agent-skills-main/skills/planning-and-task-breakdown/`
  - 将复制到 `skills/planning-and-task-breakdown/`
  - 指导如何从技术契约分解出实现步骤和原子任务
  - 产出 plan.md（步骤）和 todo.md（任务清单）

### B. 设计约束

1. **不能改 tickets_cli.py** — 确定性部分是护栏，不能动
2. **codoop-ticket SKILL.md 必须调用 tickets_cli** — 流程最后还是要用 CLI 来 validate + promote
3. **Spec 和 Plan 的独立性** — 复制后的 spec-driven-development 和 planning-and-task-breakdown 应该能：
   - ✅ 独立被调用（`/skill spec-driven-development` 或 `/skill planning-and-task-breakdown`）
   - ✅ 在 codoop-ticket 中被调用作为子步骤
   - ✅ 路径相对正确（指向本地 agents、references 等资源）
4. **不复用轻量 personas** — PM 和 Architect agents 直接复用 Discovery 版本，由 SKILL.md 的上下文来指引工单范围

### C. 改造前的代码检查清单

在动手改造前，确认：

- [ ] `skills/codoop-flow/scripts/codoop_flow/tickets_cli.py` 的接口稳定（validate、promote 的返回值）
- [ ] `tests/test_skeleton.py` 中 ticket lifecycle 的断言是否覆盖全
- [ ] 查看 `source/agent-skills-main/skills/spec-driven-development/` 的结构，确认复制后的路径依赖
- [ ] 查看 `source/agent-skills-main/skills/planning-and-task-breakdown/` 的结构，确认复制后的路径依赖
- [ ] 确认 spec-driven-development 和 planning-and-task-breakdown 是否有对 source/ 目录的硬引用，需要调整为相对路径

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

1. **Spec 和 Plan 的提升策略**：
   - 复制 `source/` 中的 spec 和 plan skills 到顶层 `skills/` 时，是否需要修改它们的 SKILL.md 和相对路径？
   - 这两个 skills 在"作为 codoop-ticket 的子步骤"和"独立调用"时的行为是否需要区分？
   - **建议**：保持相同逻辑，通过上下文区分（工单编排模式 vs 独立模式）

2. **第一环产出物的读取**：
   - codoop-ticket SKILL 中如何读取 `docs/backlog/` 下的产品规范、设计规范、架构文档？
   - 是否应该自动扫描并提供给 PM 和 Architect agents 作为上下文？
   - **建议**：是的，自动读取并注入到 sub-agent prompts 中

3. **spec-driven-development 和 planning-and-task-breakdown 在 codoop-ticket 中的调用方式**：
   - codoop-ticket SKILL.md 中如何调用这两个 skills？
   - 是否需要将前一阶段的输出（如 module_prd.md 的内容）作为上下文传入？
   - **建议**：通过 SKILL.md 中的清晰指引，或通过文本上下文传递关键信息

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

- 📝 **新增目录**：
  - `skills/codoop-ticket/` — 工单编排 skill
    - `SKILL.md`（编排逻辑）
    - `README.md`（使用指南）
  - `skills/spec-driven-development/` — 从 source/ 复制提升
    - `SKILL.md`（spec 设计逻辑）
    - `README.md`（使用指南）
  - `skills/planning-and-task-breakdown/` — 从 source/ 复制提升
    - `SKILL.md`（任务分解逻辑）
    - `README.md`（使用指南）
  - `skills/definition-of-done/` — 从 source/ 复制提升，planning 依赖
    - `SKILL.md`（DoD 标准，由 references/definition-of-done.md 转换）
    - `README.md`（使用指南）

- ✏️ **修改**：
  - `.claude-plugin/marketplace.json` （添加 codoop-ticket、spec-driven-development、planning-and-task-breakdown 条目）
  - `.agents/plugins/marketplace.json` （添加三个新 skills 条目）
  - `docs/install.md` 和 `.zh-CN.md` （补充三个新 skills 说明）
  - 主 `README.md` 和 `.zh-CN.md` （更新 Three Loops 表格）

- 🚫 **不动**：
  - `tickets_cli.py` （确定性护栏，保持原样）
  - `test_skeleton.py` （现有 ticket 测试不改）
  - `source/` （改造完成后由用户自行清理）

---

## 下一步

确认上述"待确认的决策点"后，即可开始 Phase 2 的实施。

预计工作量：中等（复制 spec + plan skills 到顶层，新建 codoop-ticket 编排 skill，更新三处 manifest）。

**核心清单**：
- [ ] 从 `source/agent-skills-main/skills/spec-driven-development/SKILL.md` 复制到 `skills/spec-driven-development/SKILL.md`
- [ ] 从 `source/agent-skills-main/skills/planning-and-task-breakdown/SKILL.md` 复制到 `skills/planning-and-task-breakdown/SKILL.md`
- [ ] 从 `source/agent-skills-main/references/definition-of-done.md` 转换为 `skills/definition-of-done/SKILL.md`（添加 YAML frontmatter）
- [ ] 新建 `skills/codoop-ticket/SKILL.md`（工单三阶段编排）
- [ ] 新建 `skills/codoop-ticket/README.md`
- [ ] 新建 `skills/spec-driven-development/README.md`
- [ ] 新建 `skills/planning-and-task-breakdown/README.md`
- [ ] 新建 `skills/definition-of-done/README.md`
- [ ] 更新 `skills/planning-and-task-breakdown/SKILL.md` 中对 definition-of-done 的引用（改为 skill 链接而非文件路径）
- [ ] 更新 `.claude-plugin/marketplace.json`（+4 entries：codoop-ticket、spec-driven-development、planning-and-task-breakdown、definition-of-done）
- [ ] 更新 `.agents/plugins/marketplace.json`（+4 entries）
- [ ] 更新 `docs/install.md` 和 `install.zh-CN.md`
- [ ] 更新 `README.md` 和 `README.zh-CN.md`（Three Loops 表格）
- [ ] 验证各 SKILL.md 中的相对路径正确
