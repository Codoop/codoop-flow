# Planning and Task Breakdown

将技术规格分解为可实施的、有序的任务清单。

## 使用方式

### 独立调用（生成完整计划）

当你有技术规格（spec.md），需要分解成实现任务时：

```
/skill planning-and-task-breakdown
基于搜索功能的技术规格，分解成实现计划和原子任务清单
```

### 作为工单编排的第三阶段

`codoop-ticket` skill 会在第三阶段自动调用此 skill：

```
【第三阶段】任务分解 (plan.md + todo.md)
9. codoop-ticket 加载 /skill planning-and-task-breakdown
10. 基于 spec.md 分解实现任务
11. 用户 review 并确认
```

## 任务分解的关键产出

### plan.md — 实现计划

按依赖关系和执行顺序组织的步骤：

```markdown
# Implementation Plan: [Feature Name]

## Overview
[一句话总结要建什么]

## Architecture Decisions
- [决策 1 及其理由]
- [决策 2 及其理由]

## Task List

### Phase 1: Foundation
- Task 1: ...
- Task 2: ...

### Checkpoint: Foundation
- [ ] 测试通过
- [ ] 构建成功

### Phase 2: Core Features
- Task 3: ...
- Task 4: ...

### Checkpoint: Core Features
- [ ] 端到端流程工作
```

### todo.md — 原子任务清单

每个任务 ≤100 行代码，有明确的验收条件：

```markdown
## Task 1: Create search API endpoint

**Description:** Implement GET /api/search endpoint with keyword, category, price filtering.

**Acceptance criteria:**
- [ ] Endpoint accepts query params: q, category, min_price, max_price
- [ ] Returns paginated results with 20 items per page
- [ ] Validates input and returns 400 on invalid params
- [ ] Performance: responds < 500ms on 1M document dataset

**Verification:**
- [ ] Tests pass: npm test -- search.test.ts
- [ ] Build succeeds: npm run build
- [ ] Manual: curl endpoint with sample params

**Dependencies:** None

**Files likely touched:**
- src/api/search.ts
- tests/api/search.test.ts
- src/db/queries.ts

**Estimated scope:** Small (1-2 files)
```

## 核心设计原则

### 1. 垂直切片（Vertical Slicing）

❌ **横向分割** — 分层实现（先数据库，再 API，再 UI）
```
Task 1: 整个数据库 schema
Task 2: 所有 API 端点
Task 3: 所有 UI 组件
```

✅ **垂直切片** — 端到端功能（每个任务都能交付价值）
```
Task 1: 搜索 API + 搜索框 UI（用户能搜索）
Task 2: 搜索结果列表 + 数据库查询优化（用户能看到结果）
Task 3: 过滤功能 + 前端状态管理（用户能过滤）
```

### 2. 任务大小指南

| 大小 | 文件数 | 时间 | 何时拆分 |
|-----|-------|------|--------|
| XS | 1 | < 30 min | 单函数或配置 |
| S | 1-2 | 30 min - 1h | 单个组件或端点 |
| **M** | 3-5 | 1-2h | **推荐范围** |
| L | 5-8 | 2-4h | 多组件协作 |
| XL | 8+ | 4h+ | ❌ **拆分** |

### 3. 检查点（Checkpoints）

每 2-3 个任务后设置检查点，确保系统仍可运行：

```markdown
## Checkpoint: After Tasks 1-3

- [ ] 所有测试通过
- [ ] 构建无错误
- [ ] 端到端流程可用
- [ ] 与用户确认后再继续
```

## 与 definition-of-done 的关系

此 skill 分解出的每个任务，完成后都需要满足 `/skill definition-of-done` 中定义的标准。参考那个 skill 了解 Correctness、Quality、Integration、Documentation、Ship-readiness 的详细要求。

## 最佳实践

1. **明确依赖** — 清晰标注哪些任务必须按顺序、哪些可并行
2. **验收条件具体** — "测试通过"不够，要说明测试类型和覆盖率
3. **包含风险识别** — Risks 和 Mitigations 部分要列出已知陷阱
4. **估算保守** — 如果不确定是否能 1-2 小时内完成，拆分任务

