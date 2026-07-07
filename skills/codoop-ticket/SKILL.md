---
name: codoop-ticket
description: 设计工单（PRD、规格、计划）。用自然语言描述要做什么功能，codoop-ticket 会通过三个阶段帮助设计完整的工单文档。最终产出 module_prd.md、spec.md、plan.md、todo.md 和自动推断的 metadata.json。
---

# Codoop-Ticket — 工单设计编排

帮助用户系统性地设计工单（ticket），通过三个阶段逐步完成业务需求、技术规格和任务分解。

## 什么是工单？

工单是一个完整的功能模块的设计文档包，包含：

| 文件 | 作用 | 作者 |
|------|------|------|
| `module_prd.md` | 业务需求（纯业务语言，无技术细节） | PM agent |
| `spec.md` | 技术规格（API、数据库、各端实现细节） | Architect agent |
| `plan.md` | 实现计划（分步骤） | 自动推断 |
| `todo.md` | 原子任务清单（≤100行代码/任务） | 自动推断 |
| `metadata.json` | 工单元数据（模块、测试命令、编辑范围） | 自动推断 |

## 何时使用

- ✅ 要从业务需求设计出完整的工单
- ✅ 第一环已产出产品规范和设计文档，现在需要设计增量功能工单
- ✅ 需要人类参与每个阶段的审查和反馈

## 工单设计的三个阶段

### 【第一阶段】需求设计 (module_prd.md)

**目标**：理解业务需求，定义功能边界和验收标准。

**流程**：
1. 你描述要做什么功能（自然语言）
2. codoop-ticket 与你讨论需求细节、边界、依赖
3. codoop-ticket 读取 `docs/backlog/` 下的第一环产出（产品规范、设计规范、架构文档）
4. PM agent 基于讨论和第一环文档撰写 `module_prd.md`（纯业务）
5. 你审阅、反馈、修改，直到满意

**示例**：
```
用户：帮我设计电商平台的用户搜索功能
       - 需要支持关键词、分类、价格范围过滤
       - 要和现有的商品库集成

codoop-ticket：讨论需求
       - 搜索范围：商品名称、描述、SKU 都搜吗？
       - 过滤逻辑：OR 还是 AND 组合？
       - 结果排序：相关性排序还是销量排序？
       
读取第一环：
       - docs/backlog/product/commerce-strategy.md（商业策略）
       - docs/backlog/interface/search-ux.md（搜索 UX 规范）
       
PM agent 输出：
       ✅ module_prd.md：业务需求、用户故事、验收条件
```

### 【第二阶段】技术规格 (spec.md)

**目标**：设计技术契约，确保实现方向一致。

**流程**：
1. 加载 `/skill spec-driven-development`
2. 基于 `module_prd.md` 设计 `spec.md`：
   - API 接口设计（后端、Web、移动端各端）
   - 数据库字段和数据模型
   - UI 交互流程
   - 编辑范围白名单（`files_to_edit`）
3. 你审阅、反馈、修改，直到满意

**示例**：
```
spec.md 包含：

## Backend API
- GET /api/products/search?q=...&category=...&price_min=...&price_max=...
- Response: { items: [...], total: N, page: 1 }

## Database
- Add columns to products table: search_vector (tsvector for full-text search)
- Add index: products_search_vector_idx

## Web UI
- SearchBar component: keyword input + filter sidebar
- ResultsList component: grid/list view toggle
- ResultItem component: product card with quick add-to-cart

## Files to Edit
- backend/**
- web/src/**
- mobile/lib/**
```

### 【第三阶段】任务分解 (plan.md + todo.md)

**目标**：分解成可实施的、有序的原子任务。

**流程**：
1. 加载 `/skill planning-and-task-breakdown`
2. 基于 `spec.md` 分解任务：
   - `plan.md`：实现步骤（Step 1、Step 2 等）
   - `todo.md`：原子任务清单（每个 ≤100 行代码）
3. 参考 `/skill definition-of-done` 了解完成标准
4. 你审阅、反馈、修改，直到满意

**示例**：
```
plan.md:
- Step 1: Backend API 实现 + 数据库迁移
- Step 2: Web 前端 SearchBar 和 ResultsList 组件
- Step 3: Web 过滤逻辑和状态管理
- Step 4: Mobile 端适配

todo.md:
- [ ] Task 1: Create search API endpoint (backend)
- [ ] Task 2: Add database full-text search index
- [ ] Task 3: Implement SearchBar React component
- ...（每个任务都有验收条件和验证步骤）
```

### 【元数据推断】自动更新 metadata.json

**流程**：
1. 基于 `spec.md` 自动推断：
   - `modules`：从 spec 的标题提取（## Backend → backend、## Web → web）
   - `files_to_edit`：从 spec 的"## Editable Files"提取
   - `test_command`：根据 modules 生成默认值
2. 显示推断结果，你确认或修改

**示例**：
```json
{
  "ticket_id": "ticket_001",
  "title": "电商平台用户搜索功能",
  "modules": ["backend", "web", "mobile"],
  "files_to_edit": ["backend/**", "web/src/**", "mobile/lib/**"],
  "test_command": {
    "backend": "npm run test -- backend",
    "web": "npm run test -- web",
    "mobile": "flutter test"
  },
  "max_healing_attempts": 3,
  "ui_capture": false
}
```

### 【最终化】验证与发布

**流程**：
1. 调用 `tickets_cli validate` 检查工单完整性
2. 调用 `tickets_cli promote` 移至 `pending/`
3. 工单完成，等待第三环 codoop-flow skill pick 并开发

---

## 使用方式

### 启动工单设计

用自然语言描述你要做什么功能：

```
/skill codoop-ticket
我想为电商平台设计用户搜索功能，需要支持关键词、分类、价格范围过滤，并和现有商品库集成
```

或简洁版：

```
/skill codoop-ticket
帮我设计电商搜索功能的工单
```

### 流程中的确认

每个阶段完成后，你需要 review 并确认：

```
用户：看起来不错，PRD 完整，进入下一阶段
codoop-ticket：OK，现在加载 spec-driven-development，开始设计技术规格...

（Spec 设计完成）

用户：Spec 的 API 设计我改一下，改成 POST 而不是 GET...
codoop-ticket：已修改，用户满意吗？
用户：OK，进入下一阶段

...依此类推
```

---

## 与其他环的关系

### 与第一环（Venture-Discovery）的联动

codoop-ticket 会自动读取第一环的输出：

- `docs/backlog/product/` — 产品规范
- `docs/backlog/interface/` — 界面规范
- `docs/backlog/architecture/` — 架构规范
- `docs/backlog/modules/` — 模块拆分

这些作为 context 输入给 PM 和 Architect agents，确保工单与全局规划对齐。

### 与第三环（Agent-Centric）的交接

工单完成后，通过 `metadata.json` 向第三环传递：

- `modules`：要调用哪些测试？
- `files_to_edit`：编辑范围白名单（护栏）
- `test_command`：验证标准

第三环会自动 pick 工单并在 worktree 中开发。

---

## 设计指导

### Agents 的工单范围指引

codoop-ticket 在调用 PM 和 Architect agents 时，会明确告诉它们：

```
这是一个工单设计阶段，我们的目标是为"<module_name>"模块设计 PRD。
聚焦在这个模块的业务需求、用户故事、验收标准。
如果涉及商业模式、GTM 策略或跨模块影响，请主动确认用户是否需要讨论。
```

```
这是一个工单设计的技术规格阶段，基于已有的系统架构。
聚焦在"<module_name>"模块的 API 接口设计、DB 字段变更、各端实现细节。
如果涉及全局架构变更、性能重构等超出工单范围的事项，请主动确认用户。
```

这样 agents 能智能识别"超出范围"的决策点，主动找用户确认，而不是憋着或假设。

### 快速精准 vs 全局论证

工单设计与第一环的产品发现不同：

- **第一环**：全局 0→1，要一致性审计，多角色辩论，产出全套规范
- **第二环**：增量小范围，要快速精准，只有 PM + Architect，聚焦这个模块

无需在工单级别做全局一致性检查（那是第一环的职责）。

