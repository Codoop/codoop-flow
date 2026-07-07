# Phase 2 改造交付物清单

> 状态：规划阶段
> 目标读者：实施者、项目维护者
> 关联：[refactor-phase2-human-centric.md](./refactor-phase2-human-centric.md)

---

## 总体目标

将第二环（Human-Centric Loop）升级为**会话内可直接调用的 skills**，用户可以在任何 AI 编码工具中直接 `/skill codoop-ticket` 来进行工单设计，而无需子进程启动或手动操作。

最终产物包括：
- **4 个新 skills**（codoop-ticket、spec-driven-development、planning-and-task-breakdown、definition-of-done）
- **工单 CLI 优化**（语言自动检测）
- **文档和 manifest 更新**

---

## 📦 最终产物清单

### 1️⃣ 新建 Skills（共 4 个）

#### A. `skills/codoop-ticket/` — 工单编排 Skill（新建）

**文件**：
- `SKILL.md` — 工单三阶段编排逻辑
  - 第一阶段：需求设计 (module_prd.md)
  - 第二阶段：技术规格 (spec.md)，调用 spec-driven-development skill
  - 第三阶段：任务分解 (plan.md + todo.md)，调用 planning-and-task-breakdown skill
  - 每阶段都有人类确认点
  - 复用 `product-sprint-prioritizer` 和 `engineering-backend-architect` agents（来自 _shared/agents/）
  - 在 SKILL.md 中明确指引工单范围，agents 根据上下文识别超出范围的项

- `README.md` — 使用指南
  - 如何在会话内调用：`/skill codoop-ticket draft ticket_001`
  - 工单设计的三阶段工作流示例
  - 与第一环（Venture-Discovery）的联动方式
  - 与第三环（Agent-Centric）的交接流程

**关键特性**：
- ✅ 调用 `tickets_cli init` 创建工单骨架
- ✅ 引导用户讨论需求，结合第一环的 `docs/backlog/` 产出物
- ✅ PM agent 撰写业务 PRD（纯业务，无技术细节）
- ✅ 加载 spec-driven-development skill，基于 PRD 设计技术规格
- ✅ 加载 planning-and-task-breakdown skill，基于规格分解任务
- ✅ 调用 `tickets_cli validate` 和 `tickets_cli promote` 完成工单发布

**最终输出**（工单目录 `docs/tickets/drafts/<ticket_id>/`）：
- `metadata.json` — 工单元数据（ticket_id、title、modules、test_command、files_to_edit 等）
- `module_prd.md` — 业务需求文档（纯业务描述）
- `spec.md` — 技术规格文档（API、数据库、UI 交互）
- `plan.md` — 实现计划（分步骤）
- `todo.md` — 原子任务清单（≤100 行/任务）

---

#### B. `skills/spec-driven-development/` — 规格设计 Skill（复制提升）

**源**：`source/agent-skills-main/skills/spec-driven-development/SKILL.md`

**文件**：
- `SKILL.md` — 从业务需求设计技术规格的逻辑
  - 四个阶段：Specify → Plan → Tasks → Implement
  - 表格化规格模板（Objective、Commands、Project Structure、Code Style、Testing Strategy、Boundaries）
  - 成功条件的重构方法

- `README.md` — 使用指南
  - 独立调用方式：`/skill spec-driven-development`
  - 作为 codoop-ticket 子步骤时的行为
  - 规格设计的最佳实践
  - 与 planning-and-task-breakdown 的协作关系

**独立用途**：
- ✅ 用户可单独调用 `/skill spec-driven-development` 从已有的业务需求设计规格
- ✅ 作为 codoop-ticket 的第二阶段，基于 PRD 生成 spec

---

#### C. `skills/planning-and-task-breakdown/` — 任务分解 Skill（复制提升）

**源**：`source/agent-skills-main/skills/planning-and-task-breakdown/SKILL.md`

**文件**：
- `SKILL.md` — 从规格分解为可实施任务的逻辑
  - 五个步骤：Enter Plan Mode → Identify Dependency Graph → Slice Vertically → Write Tasks → Order and Checkpoint
  - 任务大小指南（XS 到 XL 的估算表）
  - 输出模板（plan.md 和 todo.md）
  - 并行化机会识别

- `README.md` — 使用指南
  - 独立调用方式：`/skill planning-and-task-breakdown`
  - 作为 codoop-ticket 子步骤时的行为
  - 任务分解的最佳实践
  - 与 definition-of-done 的协作关系

**独立用途**：
- ✅ 用户可单独调用 `/skill planning-and-task-breakdown` 从已有的规格分解任务
- ✅ 作为 codoop-ticket 的第三阶段，基于 spec 分解 plan 和 todo

---

#### D. `skills/definition-of-done/` — 完成定义 Skill（从 references 转换）

**源**：`source/agent-skills-main/references/definition-of-done.md`

**文件**：
- `SKILL.md` — 完成定义标准（从 markdown 转换为 SKILL.md 格式，加 YAML frontmatter）
  - 五个维度的检查清单：Correctness、Quality、Integration、Documentation、Ship-readiness
  - Definition of Done vs. Acceptance Criteria 的区别
  - 如何应用（Per task / Per feature / Per release）
  - Red Flags

- `README.md` — 使用指南
  - 如何在工单流程中引用此标准
  - 各个阶段的应用方式
  - 与 planning-and-task-breakdown 的集成

**用途**：
- ✅ 在 planning-and-task-breakdown SKILL.md 中明确引用：`See /skill definition-of-done`
- ✅ 用户可独立查看：`/skill definition-of-done`

---

### 2️⃣ 改造工单 CLI

**文件**：`skills/codoop-flow/scripts/codoop_flow/tickets_cli.py`

**改动**：

#### A. 语言自动检测
- `init_draft()` 新增 `language` 参数（auto | zh | en）
  - auto（默认）：从 title 检测 CJK 字符，自动选择语言
  - zh：中文模板（业务 PRD、技术规格等）
  - en：英文模板（Business PRD、Technical Spec 等）

#### B. 元数据自动推断（新增）
- `update_metadata_from_docs(config, ticket_id)` — 从设计文档智能推断元数据
  - 从 spec.md 的标题章节提取 `modules`（Backend、Web、Mobile、Desktop）
  - 从 spec.md 的"Editable Files"部分提取 `files_to_edit`
  - 根据 modules 生成 `test_command` 的默认值
  - 返回推断后的 metadata dict（未写入磁盘）

- `write_metadata(config, ticket_id, metadata)` — 将更新的元数据写入磁盘

#### C. 其他函数（无改动）
- `validate_draft()` — 保持原样
- `promote()` — 保持原样

**CLI 更新**：`skills/codoop-flow/scripts/codoop.py`

**新增参数和命令**：
```bash
# 初始化工单（支持语言选择）
python codoop.py ticket init <ticket_id> --title "..." --language {auto,zh,en}

# 自动更新元数据（基于 spec.md、plan.md、todo.md）
python codoop.py ticket update-metadata <ticket_id>

# 验证和发布工单
python codoop.py ticket validate <ticket_id> --config <toml>
python codoop.py ticket promote <ticket_id> --config <toml>
```

**backward compatibility**：✅ 所有现有调用无需改动
- 语言检测自动使用 auto
- update-metadata 是新增命令，不影响现有流程

---

### 3️⃣ 更新 Manifest 和文档

#### Manifest 注册（+4 个 entries）

**文件**：`.claude-plugin/marketplace.json`

新增条目：
- `codoop-ticket`
- `spec-driven-development`
- `planning-and-task-breakdown`
- `definition-of-done`

**文件**：`.agents/plugins/marketplace.json`

新增条目：同上

---

#### 文档更新

**1. `docs/install.md` 和 `install.zh-CN.md`**

更新"Three Loops"表格：

| Skill | 用途 | 阶段 |
|-------|------|------|
| **codoop-discover** | 产品设计与架构规划 | 开码前 |
| **spec-driven-development** | 独立规格设计 | 工单设计 |
| **planning-and-task-breakdown** | 独立任务分解 | 工单设计 |
| **definition-of-done** | 完成标准检查清单 | 工单设计 |
| **codoop-ticket** | 工单编排（三阶段） | 工单设计 |
| **codoop-flow** | 代码实现与交付 | 编码 & 发布 |

新增调用示例：
```
/skill spec-driven-development 基于已有的业务需求生成规格
/skill planning-and-task-breakdown 基于规格分解任务
/skill definition-of-done 查看完成标准
/skill codoop-ticket draft ticket_001 完整工单设计流程
```

---

**2. `README.md` 和 `README.zh-CN.md`**

更新"Three Loops"部分：
- 补充四个新 skills 的说明
- 说明四个 skills 的独立调用方式
- 说明 codoop-ticket 如何编排和调用这些 skills

---

### 4️⃣ 共享 Agents（无新增，已存在）

**位置**：`skills/_shared/agents/`

**使用**：codoop-ticket SKILL.md 调用
- `product-sprint-prioritizer.md` — PM agent（撰写 PRD）
- `engineering-backend-architect.md` + `engineering-software-architect.md` — Architect agents

**指引**：在 codoop-ticket SKILL.md 中明确告诉 agents：
```
"我们在做工单设计阶段，目标是为'<module_name>'模块设计 PRD/Spec。
聚焦在这个模块的业务需求/技术契约。
如果涉及商业模式、GTM 或跨模块影响，请主动确认用户。"
```

---

## 🎯 工单设计流程示例

```
用户调用：
/skill codoop-ticket draft ticket_001 --title "用户搜索功能"

流程：
┌─────────────────────────────────────────────────────┐
│ 【第一阶段】需求设计 (module_prd.md)               │
├─────────────────────────────────────────────────────┤
│ 1. codoop-ticket 初始化工单骨架（tickets_cli init）│
│ 2. 与用户讨论需求，读取 docs/backlog/ 产品文档    │
│ 3. PM agent 撰写 module_prd.md                      │
│ 4. 用户 review，提供反馈直到满意                   │
└─────────────────────────────────────────────────────┘
                          ↓ 用户确认 OK
┌─────────────────────────────────────────────────────┐
│ 【第二阶段】技术规格 (spec.md)                     │
├─────────────────────────────────────────────────────┤
│ 5. 加载 /skill spec-driven-development              │
│ 6. 基于 module_prd.md 生成 spec.md：                │
│    - API 接口定义                                  │
│    - 数据库字段变更                                │
│    - UI 交互约定                                   │
│    - files_to_edit 白名单                          │
│ 7. 用户 review，提供反馈直到满意                   │
└─────────────────────────────────────────────────────┘
                          ↓ 用户确认 OK
┌─────────────────────────────────────────────────────┐
│ 【第三阶段】任务分解 (plan.md + todo.md)           │
├─────────────────────────────────────────────────────┤
│ 8. 加载 /skill planning-and-task-breakdown          │
│ 9. 基于 spec.md 分解任务：                          │
│    - plan.md（实现步骤）                           │
│    - todo.md（原子任务清单）                       │
│ 10. 用户 review，提供反馈直到满意                  │
│ 11. 参考 /skill definition-of-done 检查完成标准    │
└─────────────────────────────────────────────────────┘
                          ↓ 用户确认 OK
┌─────────────────────────────────────────────────────┐
│ 【元数据推断】自动更新 metadata.json（AI）         │
├─────────────────────────────────────────────────────┤
│ 12. codoop-ticket 调用 tickets_cli update-metadata  │
│     - 从 spec.md 提取 modules                       │
│     - 从 spec.md 提取 files_to_edit                 │
│     - 生成 test_command 默认值                      │
│ 13. 显示推断结果，用户 review 并确认或修改         │
└─────────────────────────────────────────────────────┘
                          ↓ 用户确认 OK
┌─────────────────────────────────────────────────────┐
│ 【最终化】验证与发布                               │
├─────────────────────────────────────────────────────┤
│ 14. codoop-ticket 调用 tickets_cli validate         │
│ 15. codoop-ticket 调用 tickets_cli promote          │
│ 16. 工单移至 pending/，等待第三环 pick             │
└─────────────────────────────────────────────────────┘

最终工单在：docs/tickets/pending/ticket_001/
├── metadata.json
├── module_prd.md
├── spec.md
├── plan.md
└── todo.md
```

---

## ✅ 交付物验收清单

### 代码交付
- [ ] `skills/codoop-ticket/SKILL.md` 完整、可调用
- [ ] `skills/codoop-ticket/README.md` 清晰、有示例
- [ ] `skills/spec-driven-development/` 复制完整
- [ ] `skills/planning-and-task-breakdown/` 复制完整
- [ ] `skills/definition-of-done/` 转换完整
- [ ] `skills/codoop-flow/scripts/codoop_flow/tickets_cli.py` 语言支持 ok
- [ ] `skills/codoop-flow/scripts/codoop_flow/tickets_cli.py` 元数据推断 ok
- [ ] `skills/codoop-flow/scripts/codoop.py` CLI 参数 ok（包括 update-metadata）

### 文档交付
- [ ] `.claude-plugin/marketplace.json` +4 entries
- [ ] `.agents/plugins/marketplace.json` +4 entries
- [ ] `docs/install.md` 和 `.zh-CN.md` 更新
- [ ] `README.md` 和 `.zh-CN.md` 更新
- [ ] 所有新 SKILL.md 有对应 README.md

### 测试和验证
- [ ] 所有 skeleton 测试通过
- [ ] 工单三阶段流程手工验证（end-to-end）
- [ ] 语言自动检测验证（中文标题 → 中文模板，英文标题 → 英文模板）
- [ ] 各 skill 可独立调用验证
- [ ] manifest 注册验证（Claude Code 中可发现）

### 后续清理
- [ ] `source/` 目录资源由用户自行清理（改造完成后）

---

## 📊 统计

**新增 Skills**：4 个
- codoop-ticket（新建）
- spec-driven-development（复制提升）
- planning-and-task-breakdown（复制提升）
- definition-of-done（复制提升）

**新增 README.md**：4 个

**工单 CLI 改动**：
- `init_draft()` 参数新增 1 个（language）
- CLI 新增 1 个标志（--language）

**Manifest 条目**：+4 entries × 2 files = 8 条

**文档更新**：4 个文档（install × 2、README × 2）

---

## 🚀 使用时间表

完成后，用户可以：

**立即使用**（会话内调用）：
```
/skill codoop-ticket draft ticket_001
/skill spec-driven-development
/skill planning-and-task-breakdown
/skill definition-of-done
```

**整合工作流**（通过工单编排）：
```
/skill codoop-ticket draft ticket_001 → 三阶段编排 → 自动调用子 skills → 生成完整工单
```

**独立使用**（各 skill 独立价值）：
```
已有业务需求 → /skill spec-driven-development → 规格
已有技术规格 → /skill planning-and-task-breakdown → 任务
```

