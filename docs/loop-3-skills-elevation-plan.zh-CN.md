# 第三环改造计划：子 Skills 和 Review Personas 提升

## 概述

第三环（Agent-Centric Loop）当前依赖多个 sub-skills 和 review personas，这些目前被隐藏在 `skills/codoop-flow/references/` 中。本计划分析这些能力是否应该被提升到项目顶层，成为独立可调用的 skills 和 agents。

**现状：**
- **Sub-Skills**（3 个）在 `skills/codoop-flow/references/skills/`
- **Review Personas**（6 个）在 `skills/codoop-flow/references/agents/`
- 这些仅在第三环的特定步骤中被引用

**目标：**
- 决定是否提升这 3 个 sub-skills 到 `skills/` 顶层
- 决定是否提升 4 个 review agents 到 `skills/_shared/agents/`（2 个 UI personas 保持为内部引用）
- 如果提升，则执行迁移并更新文档

---

## 第三环的 Sub-Skills 分析

### 1. incremental-implementation（增量实现纪律）

**定义：** 将大型代码变更分解为小的、可验证的垂直切片（单个 checkbox），每个都经历：实现 → 测试 → 验证 → 提交 → 重复

**在第三环中的角色（Step 2: Build）：**
```
代理在 Build 阶段遵循此纪律：
- 读取 todo.md 中的原子任务
- 按顺序逐一实现（每个通常 <100 行代码）
- 每完成一个，运行测试、检查编辑范围限制
- 标记为完成 [x]，移到下一个
- 避免一次提交大量不可测试的代码
```

**独立使用价值：**
- 适用于任何大型重构、多模块重新架构、跨端同步修改
- 用户可能需要指导如何在 Loop 2 工单设计阶段分解大型功能
- 用户可能想要独立地学习和应用增量实现纪律

**可独立使用程度：** ⭐⭐⭐⭐⭐ 高度独立

---

### 2. debugging-and-error-recovery（调试和自愈纪律）

**定义：** 当测试失败时，系统采用结构化的根本原因分析流程：
1. 去噪错误日志（提取关键堆栈跟踪）
2. 分类错误类型（编译 vs 运行时 vs 断言失败）
3. 精准指向问题代码行
4. 生成高密度 Debug Prompt 注入代理
5. 代理自愈修复（最多 3 次）

**在第三环中的角色（Step 4: Debug）：**
```
当 Verify 失败时触发：
- CLI 去噪各种测试框架的原始报错
- 提取核心 Exception 和代码行号
- 重塑为结构化 Debug Prompt
- 注入编码引擎进行自愈（最大 3 次重试）
- 超限则熔断，移至 failed/
```

**独立使用价值：**
- 任何需要对失败的测试或构建进行系统化调试的场景
- 用户可能想要学习如何精准诊断编译和运行时错误
- 适用于多端项目中的交叉平台调试

**可独立使用程度：** ⭐⭐⭐⭐⭐ 高度独立

---

### 3. test-driven-development（TDD 纪律）

**定义：** 坚持 Red → Green → Refactor 循环的测试驱动开发规范：
- 先写测试，验证失败（Red）
- 实现最小代码使测试通过（Green）
- 重构代码保持测试通过（Refactor）
- 覆盖 Happy Path、边界值（null/empty）、异常情况

**在第三环中的角色（Step 5: Verify 的准备）：**
```
虽然在 codoop-flow 的 SKILL.md 中没有明确提到，但在 Verify 阶段隐含应用：
- 确保代理在修改代码时包含测试用例
- 覆盖主流程、边界情况和异常流
- 所有测试必须绿色通过
```

**独立使用价值：**
- 用户可能想要在其他项目中应用 TDD 纪律
- 适用于任何需要高覆盖率和鲁棒性的开发场景
- 是通用的工程最佳实践，不仅限于 Loop 3

**可独立使用程度：** ⭐⭐⭐⭐⭐ 高度独立

---

## 第三环的 Review Personas 分析

### 按步骤 5（Review）划分

**静态代码审查组（3 个）：**

1. **code-reviewer** — 五轴代码评估
   - 评估维度：Correctness, Readability, Architecture, Security, Performance
   - 输出：Critical/Important 问题分类

2. **security-auditor** — 安全审计员
   - 深度审计 OWASP 漏洞、敏感 token 泄露
   - 输出：安全风险分类

3. **test-engineer** — 测试工程师
   - 核对测试覆盖盲区、空值边界、测试鲁棒性
   - 输出：测试覆盖不足的问题

**动态 UI/UX 验收组（2 个，仅当 `ui_capture: true`）：**

4. **testing-evidence-collector** — UI 视觉规范验收
   - 读取本地隔离的 `responsive-*.png` 截图
   - 严格核对是否与 spec.md 定义的视觉 Token、间距、响应式对齐
   - 输出：布局/视觉细节缺陷（预期 3-5 个）

5. **testing-reality-checker** — UX 交互体验验收
   - 调出交互前后对比截图
   - 校验完整的交互流（导航、表单验证、弹窗遮挡等）
   - 输出：交互阻碍、流程断裂

**额外 Personas（已提升到 _shared/agents/）：**

6. **engineering-technical-writer** — 活文档同步（已有）
   - 在 Ship 阶段（Step 7）调用
   - 自动更新 `docs/prd/` 和 `docs/tech/project-structure.md`

---

## 提升决策

### Sub-Skills 提升决策

**三个 sub-skills 都应该被提升。**

**理由：**

1. **通用工程纪律** — 不仅限于 Loop 3
   - incremental-implementation、debugging-and-error-recovery、test-driven-development 都是通用的编码纪律
   - 适用于任何大型实现任务，而不仅是工单执行

2. **用户发现性** — 提升后可直接调用
   ```
   /skill incremental-implementation 我如何分解这个大型重构？
   /skill debugging-and-error-recovery 测试失败了，怎样找到根本原因？
   /skill test-driven-development 我如何写高覆盖率的测试？
   ```

3. **与 Loop 2 一致** — Loop 2 已有的 spec-driven-development 和 planning-and-task-breakdown 都是顶层独立 skills
   - Loop 3 的三个 sub-skills 应该享有同等地位

4. **双模态使用** — 提升后仍在 Loop 3 中使用，也支持独立调用
   - 不需要维护两个副本，提升后的 skill 既在 Loop 3 中引用，也可独立使用

---

### Review Personas 提升决策

**静态代码审查组（3 个）应该被提升到 `skills/_shared/agents/`。**

**理由：**

1. **专业审查能力** — code-reviewer、security-auditor、test-engineer 代表不同的审查维度
   - 这些可能在其他场景中也被用到（人工代码审查、安全审计、测试覆盖分析）
   - 用户可能想要在其他项目中复用这些审查 personas

2. **不仅限于 Loop 3** — 这些 personas 的专业判断可以应用到任何代码变更
   - 不是"工单执行特定"的 personas，而是"软件工程通用"的 personas

3. **与现有 Personas 平行** — 已有的 7 个 discovery personas 都在 `_shared/agents/`
   - 这 3 个 review personas 应该与其他 personas 并存，形成完整的审查体系

**动态 UI/UX Personas（2 个）保持为内部引用。**

**理由：**

1. **高度特化** — testing-evidence-collector 和 testing-reality-checker 设计用于读取本地截图文件
   - 这种机制（本地截图路径、工单隔离目录）非常特化于 Loop 3

2. **工单生命周期耦合** — 这两个 personas 只有在隔离 worktree 环境中有意义
   - 在其他独立场景中可能不适用

3. **可选功能** — 仅当 `ui_capture: true` 时调用
   - 用户通常不会直接编排这两个 personas

4. **可作为参考** — 用户可以查看这两个 personas 的定义，学习如何进行 UI/UX 验收
   - 但它们不需要作为独立的、可调用的 personas 暴露

---

## 提升方案

### 第一步：复制 Sub-Skills 到顶层

```bash
# 复制 3 个 sub-skills
cp -R skills/codoop-flow/references/skills/incremental-implementation/ skills/
cp -R skills/codoop-flow/references/skills/debugging-and-error-recovery/ skills/
cp -R skills/codoop-flow/references/skills/test-driven-development/ skills/
```

结果：
- `skills/incremental-implementation/SKILL.md` 及其关联文件
- `skills/debugging-and-error-recovery/SKILL.md` 及其关联文件
- `skills/test-driven-development/SKILL.md` 及其关联文件

### 第二步：复制 Review Personas 到 _shared/agents

```bash
# 复制 3 个 static review personas
cp skills/codoop-flow/references/agents/code-reviewer.md skills/_shared/agents/
cp skills/codoop-flow/references/agents/security-auditor.md skills/_shared/agents/
cp skills/codoop-flow/references/agents/test-engineer.md skills/_shared/agents/
```

结果：
- `skills/_shared/agents/code-reviewer.md`
- `skills/_shared/agents/security-auditor.md`
- `skills/_shared/agents/test-engineer.md`
- 与现有的 7 个 discovery personas 并存，共 10 个

### 第三步：删除 references/ 目录

```bash
# 删除 codoop-flow 的 references/ 目录
rm -rf skills/codoop-flow/references/
```

codoop-flow 直接引用顶层的 skills 和 _shared/agents，无需中间层。

### 第四步：注册到 Manifests

在 `.claude-plugin/marketplace.json` 和 `.agents/plugins/marketplace.json` 中注册：

```json
{
  "plugins": [
    // 现有的 6 个 Loop skills...
    
    // 新增：Loop 3 Sub-Skills
    {
      "name": "incremental-implementation",
      "displayName": "增量实现纪律",
      "description": "将大型代码变更分解为可验证的小垂直切片并逐步实现"
    },
    {
      "name": "debugging-and-error-recovery",
      "displayName": "调试和自愈",
      "description": "系统化的根本原因分析和自动修复流程"
    },
    {
      "name": "test-driven-development",
      "displayName": "测试驱动开发",
      "description": "坚持 Red-Green-Refactor 循环的 TDD 纪律"
    }
  ]
}
```

### 第五步：更新文档和配置

- **docs/install.md** — 列出新增的 3 个 skills
- **docs/loop-3-agent-centric.md** — 更新 Skills 小节，指出 incremental-implementation 等现已顶层可用
- **docs/loop-3-agent-centric.zh-CN.md** — 对应中文版更新
- **skills/codoop-flow/SKILL.md** — 在工作流描述中引用新的顶层 skills 路径

---

## 工作量评估

| 任务 | 工作量 |
|---|---|
| 复制 3 个 sub-skills | 3 分钟 |
| 复制 3 个 review personas | 2 分钟 |
| 删除 references/ 目录 | 1 分钟 |
| 更新 manifests | 5 分钟 |
| 更新文档 | 15 分钟 |
| 验证和测试 | 10 分钟 |
| **合计** | **~36 分钟** |

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 路径引用遗漏 | 中 | 中 | 脚本化搜索和替换所有引用，逐一检查 |
| Manifest 注册不完整 | 低 | 低 | 脚本生成 manifest，避免手动编辑 |
| 提升后 skills 被错误调用 | 低 | 低 | 在各 skill SKILL.md 中明确说明适用场景 |
| 用户混淆哪些是 Loop-specific | 低 | 低 | 文档清晰说明每个 skill 的适用范围 |

---

## 提升后的结构

```
skills/
├── _shared/
│   ├── agents/
│   │   ├── alignment-agent.md                      (Loop 1)
│   │   ├── design-ui-designer.md                   (Loop 1)
│   │   ├── design-ux-architect.md                  (Loop 1)
│   │   ├── engineering-backend-architect.md        (Loop 1)
│   │   ├── engineering-software-architect.md       (Loop 1)
│   │   ├── product-sprint-prioritizer.md           (Loop 1)
│   │   ├── sales-offer-lead-gen-strategist.md      (Loop 1)
│   │   ├── code-reviewer.md                        (Loop 3 审查 - 新增)
│   │   ├── security-auditor.md                     (Loop 3 审查 - 新增)
│   │   └── test-engineer.md                        (Loop 3 审查 - 新增)
│   └── ...
├── codoop-discover/                               (Loop 1)
├── codoop-ticket/                                 (Loop 2)
├── spec-driven-development/                       (Loop 2)
├── planning-and-task-breakdown/                   (Loop 2)
├── definition-of-done/                            (Loop 2)
├── codoop-flow/                                   (Loop 3 主编排)
├── incremental-implementation/                    (Loop 3 子 skill - 新增)
├── debugging-and-error-recovery/                  (Loop 3 子 skill - 新增)
├── test-driven-development/                       (Loop 3 子 skill - 新增)
└── ...
```

---

## 后续影响

### 文档变化

**docs/install.md** 新增：
```markdown
### Loop 3 Sub-Skills（工单执行管道中使用的工程纪律）

- **incremental-implementation** — 将大型变更分解为可验证的小垂直切片
- **debugging-and-error-recovery** — 系统化根本原因分析和自动修复
- **test-driven-development** — TDD 纪律和高覆盖率测试方法论

这三个 skills 既在 Loop 3 的工单执行中被自动应用，也可以独立调用。
```

### codoop-flow 的代码改动

- 删除 `skills/codoop-flow/references/` 整个目录
- 在 codoop-flow 的主脚本/配置中，直接引用：
  - `../../incremental-implementation/SKILL.md`
  - `../../debugging-and-error-recovery/SKILL.md`
  - `../../test-driven-development/SKILL.md`
  - `../../_shared/agents/code-reviewer.md` 等
- 第三环的工作流完全不变，功能完全兼容

### 用户使用体验改进

提升前：
```
/skill incremental-implementation 怎样分解这个大型重构？
→ Skill not found
```

提升后：
```
/skill incremental-implementation 怎样分解这个大型重构？
→ 调用成功，获得增量实现的指导
```

---

## 待讨论的问题

1. **时机** — 是否现在就提升，还是等待其他工作完成？
2. **其他 24 个 skills** — source/agent-skills-main/ 中的其他 24 个通用工程 skills 是否也应该提升到顶层？
3. **文档充实** — 新提升的 3 个 skills 是否需要新的 README.md 说明独立使用场景？

