# Spec-Driven Development

设计技术规格（Spec），在编码前明确系统契约和实现细节。

## 使用方式

### 独立调用（生成完整规格）

当你有明确的业务需求（PRD），需要设计技术规格时：

```
/skill spec-driven-development
基于用户搜索功能的业务需求，设计后端 API、数据库和前端交互规格
```

### 作为工单编排的第二阶段

`codoop-ticket` skill 会在第二阶段自动调用此 skill：

```
【第二阶段】技术规格 (spec.md)
6. codoop-ticket 加载 /skill spec-driven-development
7. 基于 module_prd.md 设计 spec.md
8. 用户 review 并确认
```

## 规格设计的关键产出

**spec.md** 应包含：

- **Objective** — 技术目标、成功标准
- **Commands** — 构建、测试、开发的完整命令
- **Project Structure** — 文件组织和目录布局
- **Code Style** — 代码风格示例和约定
- **Testing Strategy** — 测试框架、覆盖率要求
- **Boundaries** — Always / Ask First / Never 的操作边界

对于工单编排场景，特别需要包含：

- **API Contract** — 各端（Backend/Web/Mobile/Desktop）的接口定义
- **Data Schema** — 数据库字段变更和模型设计
- **UI Interactions** — 前端交互流程和状态管理
- **Editable Files** — `files_to_edit` 白名单（供第三环使用）

## 与 planning-and-task-breakdown 的关系

此 skill 的输出（spec.md）是 `planning-and-task-breakdown` skill 的输入。spec 定义了"要建什么"，plan 定义了"怎么建"。

## 最佳实践

1. **表格化关键信息** — 用表格而非段落描述接口、字段、命令
2. **包含代码示例** — 展示实际的代码片段，而非概念性描述
3. **明确边界** — Boundaries 部分要清晰，避免后续实现时的歧义
4. **与团队风格对齐** — Code Style 要反映项目的现有约定

