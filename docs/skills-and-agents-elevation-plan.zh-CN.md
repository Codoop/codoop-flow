# Skills 和 Agents 提升计划

## 概述

codoop-flow 项目当前有多个来自 `source/agent-skills-main/` 的通用 skills 和 agents，这些原本作为原始资源库中的能力，现在需要被提升到项目根目录，成为 codoop-flow 的一等公民。

**现状：** 
- 主分支中：6 个 skills（codoop-discover, codoop-ticket, spec-driven-development, planning-and-task-breakdown, definition-of-done, codoop-flow）
- 主分支中：7 个 agents 在 `skills/_shared/agents/`（7 个发现 personas）

**目标：**
- 新增 24 个 skills 到 `skills/` 顶层
- 新增 4 个 agents 到 `skills/_shared/agents/`
- 总共：30 个 skills + 11 个 agents（3 个已有 + 4 个新增 Loop 3 + 4 个通用）

---

## 待提升的 24 个 Skills

来源：`source/agent-skills-main/skills/`

### 工程纪律类（5 个）
1. **incremental-implementation** — 增量实现纪律
2. **test-driven-development** — TDD 纪律
3. **debugging-and-error-recovery** — 调试和恢复纪律
4. **spec-driven-development** — 规格驱动开发（已有副本）
5. **planning-and-task-breakdown** — 任务分解（已有副本）

### 开发工程类（8 个）
6. **api-and-interface-design** — API 和接口设计
7. **source-driven-development** — 源码驱动开发
8. **context-engineering** — 上下文工程
9. **code-simplification** — 代码简化
10. **frontend-ui-engineering** — 前端 UI 工程
11. **browser-testing-with-devtools** — DevTools 浏览器测试
12. **ci-cd-and-automation** — CI/CD 和自动化
13. **git-workflow-and-versioning** — Git 工作流和版本控制

### 质量保证类（3 个）
14. **code-review-and-quality** — 代码审查和质量
15. **performance-optimization** — 性能优化
16. **observability-and-instrumentation** — 可观测性和监测

### 运维和上线类（4 个）
17. **security-and-hardening** — 安全加固
18. **deprecation-and-migration** — 弃用和迁移
19. **documentation-and-adrs** — 文档和 ADR
20. **shipping-and-launch** — 发布和上线

### 思维方法类（4 个）
21. **doubt-driven-development** — 疑惑驱动开发
22. **interview-me** — 面试我（交互式思考）
23. **idea-refine** — 想法细化
24. **using-agent-skills** — 使用 Agent Skills 指南

---

## 待提升的 4 个 Agents

来源：`source/agent-skills-main/agents/`

目标位置：`skills/_shared/agents/`

1. **code-reviewer.md** — 代码审查员
2. **security-auditor.md** — 安全审计员
3. **test-engineer.md** — 测试工程师
4. **web-performance-auditor.md** — 网页性能审计员

> 注：这些与已有的 7 个 personas（product-sprint-prioritizer, sales-offer-lead-gen-strategist, design-ux-architect, design-ui-designer, engineering-backend-architect, engineering-software-architect, alignment-agent）共享同一个 `skills/_shared/agents/` 目录

---

## 提升的理由

### 1. 这些是通用工程能力

这 24 个 skills 和 4 个 agents 不是 codoop-flow 特有的，而是通用的、经过验证的工程实践：
- 增量实现、TDD、调试恢复 = 通用编码纪律
- API 设计、前端工程、性能优化 = 领域专业知识
- CI/CD、安全、文档 = DevOps 和运维最佳实践
- 疑惑驱动、想法细化、面试 = 思维方法论

### 2. 用户需要直接访问这些能力

当前这些 skills 被隐藏在 `source/` 中，用户无法通过 `/skill` 直接调用。提升后：
```
/skill incremental-implementation 我如何分解这个大型重构？
/skill debugging-and-error-recovery 测试失败了，怎样找到根本原因？
/skill performance-optimization 这个算法太慢了，如何优化？
/skill shipping-and-launch 代码完成了，如何安全发布？
```

### 3. 与三环系统的一致性

- Loop 1（Venture-Discovery）：使用 7 个发现 personas（现已在 `_shared/agents/`）
- Loop 2（Human-Centric）：使用 4 个 skills（spec, planning, codoop-ticket, dod）
- Loop 3（Agent-Centric）：使用 5 个 review personas + 3 个 sub-skills

新增的 4 个 agents（code-reviewer, security-auditor, test-engineer, web-performance-auditor）属于 Loop 3，应该与其他 personas 共享存放。

新增的 24 个 skills 是通用工程能力库，让用户在任何地方都能使用。

### 4. 降低复杂性

- 不再需要用户查看 `source/` 目录
- 统一的 `skills/` 和 `skills/_shared/agents/` 位置
- 清晰的一等公民地位

---

## 提升方案

### 步骤 1：复制 Skills

```bash
cp -R source/agent-skills-main/skills/* skills/
```

结果：
- 新增 24 个目录到 `skills/`
- 每个 skill 包含 `SKILL.md`（某些还有其他文件如示例、脚本）
- 现有的 6 个 skills 不受影响（同名会覆盖，但内容相同或增强）

### 步骤 2：复制 Agents

```bash
cp source/agent-skills-main/agents/*.md skills/_shared/agents/
```

结果：
- 新增 4 个 `.md` 文件到 `skills/_shared/agents/`
- 与现有 7 个 personas 并存
- 总共 11 个 personas

### 步骤 3：更新 Manifests

在 `.claude-plugin/marketplace.json` 和 `.agents/plugins/marketplace.json` 中注册所有 30 个 skills。

### 步骤 4：更新安装文档

更新 `docs/install.md` 和 `docs/install.zh-CN.md`，列出所有可用的 skills：
- 6 个核心循环 skills
- 24 个通用工程 skills

### 步骤 5：验证和提交

- 验证目录结构
- 检查没有冲突
- 单个提交，包含所有新增的 skills 和 agents

---

## 工作量

| 任务 | 工作量 |
|---|---|
| 复制 24 个 skills 到 skills/ | 5 分钟 |
| 复制 4 个 agents 到 _shared/agents/ | 2 分钟 |
| 更新 manifests（手动或脚本生成） | 10-20 分钟 |
| 更新安装文档 | 20 分钟 |
| 验证和提交 | 10 分钟 |
| **合计** | **~1 小时** |

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 文件冲突（同名 skills） | 低 | 低 | 覆盖是安全的（source 中有更新版本） |
| Manifest 注册漏掉项 | 中 | 低 | 脚本生成 manifest，不手动编辑 |
| 用户混淆新增的 skills | 低 | 低 | 文档清晰说明哪些是核心、哪些是通用 |
| 项目变得过于庞大 | 低 | 低 | 30 个 skills 仍在合理范围，文档导航清晰即可 |

---

## 提升后的结构

```
skills/
├── _shared/
│   ├── agents/
│   │   ├── alignment-agent.md                      (现有)
│   │   ├── code-reviewer.md                        (新增)
│   │   ├── design-ui-designer.md                   (现有)
│   │   ├── design-ux-architect.md                  (现有)
│   │   ├── engineering-backend-architect.md        (现有)
│   │   ├── engineering-software-architect.md       (现有)
│   │   ├── product-sprint-prioritizer.md           (现有)
│   │   ├── sales-offer-lead-gen-strategist.md      (现有)
│   │   ├── security-auditor.md                     (新增)
│   │   ├── test-engineer.md                        (新增)
│   │   └── web-performance-auditor.md              (新增)
│   └── ...
├── (现有 6 个 skills)
├── (新增 24 个 skills)
└── ...
```

---

## 后续影响

### docs/install.md 会变成什么样

需要更新以列出所有 30 个 skills。建议分类显示：
- **核心循环 Skills**（6 个）— Loop 1/2/3 的主要 orchestrators
- **通用工程 Skills**（24 个）— 分类：工程纪律、开发工程、质量保证、运维、思维方法

### Marketplace 会变成什么样

`.claude-plugin/marketplace.json` 会从：
```json
{
  "plugins": [
    { "name": "codoop-discover", ... },
    { "name": "codoop-ticket", ... },
    { "name": "spec-driven-development", ... },
    { "name": "planning-and-task-breakdown", ... },
    { "name": "definition-of-done", ... },
    { "name": "codoop-flow", ... }
  ]
}
```

变成：
```json
{
  "plugins": [
    // 核心 Loop skills
    { "name": "codoop-discover", ... },
    { "name": "codoop-ticket", ... },
    { "name": "spec-driven-development", ... },
    { "name": "planning-and-task-breakdown", ... },
    { "name": "definition-of-done", ... },
    { "name": "codoop-flow", ... },
    // 24 个通用工程 skills
    { "name": "incremental-implementation", ... },
    { "name": "test-driven-development", ... },
    { "name": "debugging-and-error-recovery", ... },
    // ... 其他 21 个
  ]
}
```

---

## 待讨论的问题

1. **Manifest 生成策略** — 是否需要自动脚本从目录名生成 manifest 条目？
2. **分类导航** — 在安装指南中如何最好地组织 30 个 skills？
3. **迁移时机** — 是否在完成其他工作后进行？
4. **向后兼容** — `source/agent-skills-main/` 目录是否保留还是删除？

