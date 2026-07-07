# codoop-flow 第一环改造：Venture-Discovery Loop 升级为会话内可调用 Skill

> 状态：✅ **完成** (2025-07-06)
> 目标读者：项目维护者 + 本次对话参与者
> 关联文档：
> - [`refactor-plan.zh-CN.md`](./refactor-plan.zh-CN.md) — 完整三环改造总体计划
> - [`engineering-design.md`](./engineering-design.md) — 三环架构蓝图（§2 Venture-Discovery Loop）

---

## 背景与问题

### 当前状态

**第一环（Venture-Discovery Loop）** 的 SKILL.md 和 5 个 discovery-agent persona 已经存在，但**当前会话里调不动**：

1. **扫不到**：`product-discovery-loop/SKILL.md` 埋在 `skills/codoop-flow/references/skills/` 子目录，插件只注册顶层 `skills/codoop-flow/` 一个 skill，发现机制扫不到它
2. **被禁用**：frontmatter 写着 `disable-model-invocation: true`
3. **设计成另起进程**：`codoop.py discover` 用 `subprocess.run()` 启动全新的 `claude`/`codex` 进程，不是在当前会话内编排

→ **问题**：用户已经在 Claude Code/Codex/Cursor 会话里，想直接调用第一环来设计产品，但无法调用；必须另起一个新窗口。

### 使用场景（本次改造的真实诉求）

- **触发点**：用户在 AI coding 工具会话内有了产品想法
- **操作**：用户在会话里说 `/skill codoop-discover` 或调用第一环 skill
- **流程**：
  1. SKILL 与用户讨论澄清基础问题（SNAP - 反假设原则）
  2. 用户确认方向后
  3. SKILL 调用多个 sub-agent 专家角色（从 `source/agency-agents-main/` 读取）
  4. Sub-agents 在会话内协作起草 `docs/backlog/` 中的所有文档
  5. 完成后，文档落地到磁盘，用户转入第二环（Human-Centric，工单撰写）

→ **改造目标**：把第一环做成**当前会话内可直接调用**的一等公民 skill，跨 Claude Code / Codex 一致。

---

## 改造目标与范围

### 核心目标

三个维度的升级：

| 维度 | 当前状态 | 改造后 |
|---|---|---|
| **发现** | 埋在 `references/` 子目录，插件扫不到 | 提升到顶层 `skills/` 平级 |
| **调用** | 禁用 + 另起进程 | 会话内直接可调用，删除 `disable-model-invocation: true` |
| **编排** | 无状态 launcher（只负责进程启动） | 智能编排（SNAP 问题澄清 → sub-agent 协作 → 文档落地） |
| **Sub-agents** | 自定义设计 | 集成 `source/agency-agents-main/` 的专家角色 |

### 改造不包括

- ❌ `codoop.py discover` 的 subprocess launcher 不再使用（可删可保留为遗留代码，但不推荐用）
- ❌ 第二环（ticket 撰写）的改造 — 留待后续
- ❌ 第三环（agent-centric）的改造 — 已完成

---

## 改造步骤

### Phase 1.0 — 目录结构升级：建立共享 agents 库

**当前结构**：
```
skills/
└── codoop-flow/
    ├── SKILL.md
    ├── scripts/
    └── references/
        ├── agents/
        ├── discovery-agents/
        └── skills/
            └── product-discovery-loop/
                ├── SKILL.md
                └── README.md
```

**改造后结构**：
```
skills/
├── _shared/
│   └── agents/
│       ├── product-sprint-prioritizer.md (从 source 复制)
│       ├── sales-offer-lead-gen-strategist.md (从 source 复制)
│       ├── design-ux-architect.md (从 source 复制)
│       ├── design-ui-designer.md (从 source 复制)
│       ├── engineering-backend-architect.md (从 source 复制)
│       ├── engineering-software-architect.md (从 source 复制)
│       └── alignment-agent.md (本地定制的一致性审计角色)
│
├── codoop-discover/
│   ├── SKILL.md (改造版本，删除 disable-model-invocation，改成会话内编排)
│   └── README.md
│
├── codoop-flow/
│   ├── SKILL.md (第三环 Agent-Centric)
│   ├── scripts/
│   └── references/
│       └── agents/ (review personas for 第三环 - 与共享不重复)
│
└── (未来的其他 skills)
```

**具体操作**：

1. 创建 `skills/_shared/agents/` 目录
2. 从 `source/agency-agents-main/` 复制上述专家角色文件到 `skills/_shared/agents/`（保持原文件名）
3. 复制 `skills/codoop-flow/references/skills/product-discovery-loop/` → `skills/codoop-discover/`
4. **删除** `skills/codoop-flow/references/` 下的 `discovery-agents/` 和 `skills/product-discovery-loop/` 目录
5. 本地定制或新建 `alignment-agent.md` 放在 `skills/_shared/agents/`

### Phase 1.1 — SKILL.md 改造：从 subprocess launcher 改成会话内编排

**当前逻辑**（`references/skills/product-discovery-loop/SKILL.md`）：
- Frontmatter: `disable-model-invocation: true` （禁用）
- 描述：复杂的多 agent 框架，但**没有给当前会话内的 orchestrator 具体的步骤**

**改造方向**：

1. **删除 frontmatter 中的 `disable-model-invocation: true`**
2. **改写 description**，让宿主知道触发条件：
   ```yaml
   ---
   name: codoop-discover
   description: Launch a collaborative product discovery session with multi-role experts (PM, GTM, UX/UI, Architect). Use when exploring 0-to-1 design for a new product or feature. Orchestrates expert agents to draft comprehensive backlog documentation.
   ---
   ```

3. **改写核心编排逻辑**：从"启动 subprocess"改成"会话内步骤编排"
   - **第 1 步**：与用户讨论澄清基础问题（SNAP）
   - **第 2 步**：用户确认方向（如：平台范围、商业模式、技术栈等）
   - **第 3 步**：调用 PM agent 起草需求
   - **第 4 步**：调用 GTM agent 起草商业策略
   - **第 5 步**：调用 UX/UI agents 起草交互和视觉设计
   - **第 6 步**：调用 Architect agents 起草技术架构
   - **第 7 步**：调用 Alignment agent 执行一致性硬审计
   - **第 8 步**：如有冲突，回到对应角色修复；通过审计后，落地文档到 `docs/backlog/`

### Phase 1.2 — Sub-Agent Persona 集成（从共享库读取）

**方向**：SKILL.md 从集中的 `skills/_shared/agents/` 读取所有 sub-agent，实现跨 skill 共用。

根据 `engineering-design.md` §2.3 的映射，SKILL.md 中引用这些共享的专家角色：

```markdown
## Sub-Agent Expert Roles

This skill invokes the following expert personas from the shared agents library 
(`../../_shared/agents/`):

- **PM / Product Strategy**: `../../_shared/agents/product-sprint-prioritizer.md`
- **GTM & Pricing**: `../../_shared/agents/sales-offer-lead-gen-strategist.md`
- **UX & UI Designer**: `../../_shared/agents/design-ux-architect.md` + `design-ui-designer.md`
- **System Architect**: `../../_shared/agents/engineering-backend-architect.md` + `engineering-software-architect.md`
- **Alignment Auditor**: `../../_shared/agents/alignment-agent.md`
```

**具体操作**：

1. 不需要在 `codoop-discover/` 下放这些文件，只在 SKILL.md 中引用相对路径
2. 其他未来的 skill 如果需要用这些角色，也用相同的相对路径引用（如果在同级目录）或调整路径
3. `skills/_shared/agents/` 作为**单一真相源**，维护所有跨 skill 共用的专家角色

### Phase 1.3 — Docs Backlog 输出规范

在改写的 SKILL.md 中明确定义 `docs/backlog/` 中的输出文档结构（参考 `engineering-design.md` §2.2）：

```
docs/backlog/
├── design-draft.md          # 多角色协作草稿（包含 CHALLENGE 和 RESOLVED 标记）
├── alignment-report.md      # 一致性硬审计报告
├── product/
│   ├── requirements.md
│   ├── user-journey.md
│   └── monetization-plan.md
├── interface/
│   ├── design-system.md
│   └── ui-mockups.md
├── architecture/
│   ├── architecture.md
│   ├── database-schema.sql
│   └── openapi.yaml
├── modules/
│   └── module-<name>.md (多个)
└── bridge/
    ├── human-preparation.md
    ├── ai-co-dev-guide.md
    └── scaffolding-blueprint.md
```

SKILL.md 应该指导 orchestrator 如何生成这些文档。

### Phase 1.4 — 插件 manifest 注册

在三处 manifest 中让新 skill 可被发现：

1. **`.claude-plugin/plugin.json`**：无需修改（仍指向 `.`)
2. **`.codex-plugin/plugin.json`**：检查 `"skills": "./skills/"` 是否已指向目录（是的话，自动扫 `codoop-discover/`）
3. **`.claude-plugin/marketplace.json`** 和 **`.agents/plugins/marketplace.json`**：补充 `codoop-discover` 入口描述

示例 marketplace 条目：
```json
{
  "name": "codoop-discover",
  "version": "0.1.0",
  "source": "skills/codoop-discover/",
  "description": "Venture-Discovery Loop: collaborative product discovery with multi-role expert agents (PM, GTM, UX/UI, Architect). Generates comprehensive backlog documentation.",
  "keywords": ["discovery", "product", "design", "backlog", "agents"]
}
```

### Phase 1.5 — 测试与文档

1. **`tests/test_skeleton.py`**：
   - 更新 discover 相关的断言（路径从 `references/skills/product-discovery-loop/` 改成 `skills/codoop-discover/`）
   - 受影响的测试：
     - `test_discover_claude_command_build` — 检查 SKILL 路径是否正确
     - `test_discover_codex_command_build` — 同上
     - `test_discover_agent_aliases` — 同上
   - **注意**：这些测试原本是在测 subprocess launcher 的命令构建，改造后可能需要转变视角（或删掉，因为不再用 launcher）

2. **`skills/codoop-discover/README.md`**：
   - 说明如何在会话内调用第一环
   - 给出一个基础工作流示例（伪代码）
   - 指向 `source/agency-agents-main/` 的专家角色说明

3. **主 README**：补充第一环 skill 的入口说明

---

## 改造前必读的关键上下文

### A. 关键文件现状

- **发现 skill（要提升的）**：`skills/codoop-flow/references/skills/product-discovery-loop/SKILL.md` + `README.md`
  - 特点：frontmatter 有 `disable-model-invocation: true`，逻辑写得很完整但针对的是"多 agent 框架"
  
- **Discovery agents（要迁移到共享库的）**：`skills/codoop-flow/references/discovery-agents/`
  - 需要被提取到 `skills/_shared/agents/` 的角色：
    - 从 `source/` 复制：`product-sprint-prioritizer.md`, `sales-offer-lead-gen-strategist.md`, `design-ux-architect.md`, `design-ui-designer.md`, `engineering-backend-architect.md`, `engineering-software-architect.md`
    - 本地定制或保留：`alignment-agent.md`

- **Launcher 代码（不再使用）**：
  - `skills/codoop-flow/scripts/codoop_flow/discover.py` — `build_command()` 和 `launch()`
  - `skills/codoop-flow/scripts/codoop.py` 中的 `_cmd_discover()`

- **Subprocess 调用点**：
  - 在 `discover.py:launch()` 中：`subprocess.run(cmd, cwd=str(config.target_repo))`

### B. 为什么第一环"当前会话里调不动"（三重因素）

1. **扫不到**：插件只注册顶层 `skills/codoop-flow/`，discovery skill 埋在其子目录
2. **被禁用**：frontmatter `disable-model-invocation: true`
3. **设计成另起会话**：launcher 用 `subprocess.run()` 启动全新的 `claude`/`codex` 进程

→ 改造必须**同时**解决这三点。

### C. 改造前的代码检查清单

在动手改造前，确认：

- [ ] `source/agency-agents-main/` 目录结构（确保 PM、GTM、UX/UI、Architect 的专家角色文件存在）
- [ ] 目前 `docs/backlog/` 是否有现存的示例文档（改造后用作参考）
- [ ] `tests/test_skeleton.py` 中有多少 discover 相关的测试
- [ ] `.codex-plugin/plugin.json` 的 `"skills"` 字段值是什么

---

## 改造后的预期形态

改造完成后，第一环 skill 将能够：

| 功能 | 实现方式 | 例子 |
|---|---|---|
| **会话内直接调用** | 宿主识别 `skills/codoop-discover/SKILL.md` 并提供 invoke 接口 | 用户：`/skill codoop-discover 想做一个 SaaS 产品` |
| **SNAP 澄清** | SKILL 与用户交互式讨论基础假设 | SKILL：你说的"SaaS"是什么行业？多少个终端用户？ |
| **多角色协作** | SKILL 读取 `source/agency-agents-main/` 中的专家角色，在会话内逐个调用 | PM 角色起草需求 → GTM 角色起草商业模式 → ... |
| **一致性硬审计** | Alignment agent 检查所有输出文档的一致性 | 发现"数据库设计与 API 契约不符"，反馈修复 |
| **文档落地** | 所有输出文档自动写入 `docs/backlog/` | 用户完成后，目录结构完整，可直接转入第二环 |

---

## 待确认的问题

1. **Launcher 代码处理**：删除 `discover.py` 和相关 CLI 还是保留为遗留代码？
2. **测试重写**：关于 subprocess 的测试是删除还是改写成 SKILL 内部逻辑的单元测试？
3. **Backlog 初始化**：改造后首次使用 skill 时，如果 `docs/backlog/` 不存在，SKILL 是否应该自动创建目录结构？

---

## 附录：改造影响范围速查

### 受影响的文件列表

- ✏️ **改写**：
  - `skills/codoop-flow/references/skills/product-discovery-loop/SKILL.md`
  - `tests/test_skeleton.py`（discover 相关测试）
  - `.claude-plugin/marketplace.json`
  - `.codex-plugin/plugin.json`（如需更新）

- 🚚 **移动**：
  - `skills/codoop-flow/references/skills/product-discovery-loop/` → `skills/codoop-discover/`
  - `skills/codoop-flow/references/discovery-agents/` → `skills/codoop-discover/agents/`

- 🗑️ **删除**（可选，根据决策）：
  - `skills/codoop-flow/scripts/codoop_flow/discover.py`
  - `skills/codoop.py` 中的 `_cmd_discover()` 命令

- 📖 **新增**：
  - `skills/codoop-discover/README.md`（说明文档）

---

## 改造完成总结

✅ **Phase 1.0-1.5 全部完成，第一环已升级为会话内可直接调用的 Skill**

### 关键成果

1. **目录结构升级** — `skills/codoop-discover/` 提升到顶层，插件自动扫描
2. **共享 agents 库** — `skills/_shared/agents/` 集中管理 7 个专家角色（单一真相源）
3. **会话内编排** — SKILL.md 改造为完整的 8 步在线协作流程
4. **插件注册** — 两处 manifest 已更新，CLaude Code 和 Agents 均可发现
5. **文档齐备** — README / engineering-design / install 全部更新，用户指南完成

### 改造后的使用

**在 Claude Code / Codex / Cursor 中，用户只需一句话：**

```
/skill codoop-discover I want to build a SaaS project management tool
```

SKILL 自动编排：SNAP 澄清 → 多角色协作 → 一致性审计 → 生成 docs/backlog/

### 下一步

**Phase 2** — Human-Centric Loop (第二环工单设计 skill) 和 **Phase 3** — 完整系统验证
