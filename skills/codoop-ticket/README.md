# Codoop-Ticket 工单设计编排

在会话内帮助用户系统性地设计工单，三个阶段逐步完成业务需求、技术规格和任务分解。

## 快速开始

用自然语言启动工单设计：

```
/skill codoop-ticket
我想为电商平台设计用户搜索功能，需要支持关键词、分类、价格范围过滤
```

## 工作流概览

```
【第一阶段】需求设计 (module_prd.md)
  ↓ (你审阅并说"OK，进下一阶段")
【第二阶段】技术规格 (spec.md)
  ↓ (你审阅并说"OK，进下一阶段")
【第三阶段】任务分解 (plan.md + todo.md)
  ↓ (你审阅并说"OK，进下一阶段")
【元数据推断】自动更新 metadata.json
  ↓ (你确认或修改)
【最终化】验证与发布
  ↓
工单完成，等待第三环开发 ✅
```

## 最终产物

工单目录 `docs/tickets/pending/ticket_001/`：

```
ticket_001/
├── metadata.json      ← 自动推断：模块、测试命令、编辑范围
├── module_prd.md      ← PM 撰写：业务需求（纯业务）
├── spec.md            ← Architect 设计：技术规格（API、DB、UI）
├── plan.md            ← 自动分解：实现计划（分步骤）
└── todo.md            ← 自动分解：原子任务清单（≤100行/任务）
```

## 与其他 Skills 的关系

### 工单内的调用

- **第二阶段** → `/skill spec-driven-development`（基于 PRD 设计规格）
- **第三阶段** → `/skill planning-and-task-breakdown`（基于 Spec 分解任务）
- **整个过程** 参考 `/skill definition-of-done`（完成标准）

### 与其他环的联动

- **第一环（Venture-Discovery）** — 自动读取 `docs/backlog/` 的产品/设计/架构规范作为 context
- **第三环（Agent-Centric）** — 工单完成后，通过 `metadata.json` 和文档包交接

## 每个阶段的关键动作

### 第一阶段：需求设计

**你**：
1. 用自然语言描述要做什么
2. 回答 codoop-ticket 和 PM agent 的澄清问题
3. Review 生成的 `module_prd.md`
4. 提供反馈直到满意
5. 说"OK，进下一阶段"

**codoop-ticket + PM agent 做**：
- 解析你的描述
- 提出澄清问题（范围、目标、验收条件）
- 读取第一环的产品/设计规范
- 撰写业务需求文档（纯业务，无技术细节）

### 第二阶段：技术规格

**codoop-ticket 做**：
- 加载 `/skill spec-driven-development`
- 基于你确认的 PRD 触发规格设计

**spec-driven-development 做**：
- 设计 API 接口（各端：backend/web/mobile/desktop）
- 设计数据库字段和模型
- 设计 UI 交互流程
- 定义编辑范围白名单

**你**：
- Review `spec.md`
- 提供反馈和修改
- 说"OK，进下一阶段"

### 第三阶段：任务分解

**codoop-ticket 做**：
- 加载 `/skill planning-and-task-breakdown`
- 基于你确认的 Spec 触发任务分解

**planning-and-task-breakdown 做**：
- 生成 `plan.md`：分步骤的实现计划
- 生成 `todo.md`：原子任务清单（每个 ≤100 行代码）

**你**：
- 参考 `/skill definition-of-done` 了解完成标准
- Review `plan.md` 和 `todo.md`
- 提供反馈和修改
- 说"OK，进下一阶段"

### 元数据推断

**codoop-ticket 自动做**：
- 从 spec.md 提取 `modules`（## Backend、## Web 等章节）
- 从 spec.md 提取 `files_to_edit`（## Editable Files 部分）
- 根据 modules 生成 `test_command` 默认值

**你**：
- Review 推断的 metadata.json
- 修改（如有需要）
- 说"OK，发布工单"

## 最佳实践

1. **第一阶段聚焦业务** — module_prd.md 里不要写技术细节，那是第二阶段的事
2. **充分讨论需求** — 在 PRD 锁定前多问几个"为什么"，省得后面改规格
3. **Spec 要明确** — API 用表格而非段落描述，字段列表要齐全
4. **Task 足够小** — 如果一个任务超过 2 小时，拆分成更小的
5. **参考完成标准** — 不要等到第三环再想"什么是完成"，第三阶段就要看 definition-of-done

## 故障排除

### Q: 工单卡在某个阶段，怎么办？
A: 清楚地告诉 codoop-ticket 你的修改意见，例如：
```
Spec 的 API 部分，GET 改成 POST，参数改成 body 传，返回值加上 request_id 字段
```
codoop-ticket 会重新生成或修改相关部分。

### Q: 元数据推断不对怎么办？
A: 直接告诉 codoop-ticket 要改什么：
```
modules 应该是 ["backend", "web"]，不需要 mobile
test_command 的 backend 改成 "npm run test:backend"
```

### Q: 工单和第一环的规范冲突怎么办？
A: codoop-ticket 会提醒这点。如果确实需要突破第一环的规范，需要明确的用户确认。

