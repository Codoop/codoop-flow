# 第三环 Sub-Skills 提升计划

## 问题陈述

第三环（Loop 3: AI 编排）目前包含三个强大的 sub-skills，但被埋在内部参考中：

- `incremental-implementation` — 增量构建代码变更（一个小改变 → 测试 → 验证 → 提交 → 重复）
- `debugging-and-error-recovery` — 系统根本原因调试和恢复
- `test-driven-development` — TDD 纪律（红 → 绿 → 重构）

这些 skills 目前放在 `skills/codoop-flow/references/skills/` 中，仅由第三环编排内部引用。然而，它们代表了**通用的工程纪律**，适用于任何代码开发，不仅仅是第三环工单。

**问题：** 这些应该被提升到顶层 skills，像第二环的四个 skills（codoop-ticket、spec-driven-development、planning-and-task-breakdown、definition-of-done）那样吗？

---

## 现状架构

### 第三环 Sub-Skills（内部参考）

位置：`skills/codoop-flow/references/skills/`

```
references/skills/
├── incremental-implementation/SKILL.md
├── debugging-and-error-recovery/SKILL.md
└── test-driven-development/SKILL.md
```

**在第三环工作流中的使用：**

| 步骤 | Skill | 调用者 | 目的 |
|---|---|---|---|
| 2. 构建 | incremental-implementation | 代理（你写代码） | 用薄垂直切片实现功能、每个切片后测试、验证、提交、重复 |
| 4. 自愈 | debugging-and-error-recovery | 代理（验证失败时） | 把失败分类到根本原因；用最小改变修复根本原因；在预算内重试 |
| （可选） | test-driven-development | 代理（可选参考） | TDD 纪律用于测试优先开发 |

### 第三环审查 Personas（也是内部）

位置：`skills/codoop-flow/references/agents/`

```
references/agents/
├── code-reviewer.md                    （总是运行）
├── security-auditor.md                 （总是运行）
├── test-engineer.md                    （总是运行）
├── testing-evidence-collector.md       （如果 ui_capture=true 运行）
├── testing-reality-checker.md          （如果 ui_capture=true 运行）
└── engineering-technical-writer.md     （发布活文档阶段）
```

**状态：** 这些是代理 personas（作为系统提示读取），不是 skills。它们不需要提升 — 已经在第三环审查管道中使用。

---

## 与第二环的对比

第二环把四个相关的 skills 提升到顶层：

```
skills/
├── codoop-ticket/                 ← 编排器
├── spec-driven-development/       ← sub-skill，也可独立使用
├── planning-and-task-breakdown/   ← sub-skill，也可独立使用
└── definition-of-done/            ← 参考 skill
```

所有这些都注册到 marketplace.json 并有文档。用户可以：
```
/skill spec-driven-development 独立设计技术规格
/skill planning-and-task-breakdown 独立把规格分解为任务
/skill codoop-ticket 编排所有三个阶段
```

第三环的 sub-skills 有类似的独立使用潜力。

---

## 为什么提升是有意义的

### 1. 通用价值

- **incremental-implementation**：任何多文件代码变更都能从这个纪律受益。不是第三环专有的。
- **debugging-and-error-recovery**：每个开发者都会遇到测试失败、编译中断、运行时错误。这是通用调试框架。
- **test-driven-development**：TDD 是通用开发方法论，适用于第三环之外。

### 2. 发现性和重用

- 在非 codoop-flow 代码上工作的用户可能想要：`/skill incremental-implementation 我如何把这个大型重构分解为安全的步骤？`
- 被调试卡住的用户：`/skill debugging-and-error-recovery 我的测试失败，我找不到原因`
- 采用 TDD 的团队：`/skill test-driven-development 我如何用 TDD 写这个功能？`

### 3. 一致性

- 第二环已经确立了模式：sub-skills 被提升到顶层，README.md 描述独立和集成使用。
- 提升第三环的 sub-skills 遵循相同模式。

### 4. 降低耦合

- 目前，sub-skills 仅在第三环的 SKILL.md 中被文档化。
- 提升它们使它们成为一等公民，降低与第三环的耦合。
- 第一环或第二环或独立工作流的用户可以受益。

---

## 为什么不提升

### 1. 上下文依赖

- 这些 skills 与第三环管道步骤紧密耦合。
- 在第三环外，它们可能需要不同的入口点或适配。

### 2. 成熟度

- 它们是第三环的内部实现细节。
- 提升它们表示它们是稳定的公开 API。

### 3. 命名空间污染

- 三个新的顶层 skills 增加了 skills 列表的噪音。
- 如果用户很少需要独立使用它们，可能过度设计。

---

## 推荐方案：完全提升

**决定：** 把所有三个 sub-skills 提升到顶层的 `skills/`。

**理由：**
1. 这些是通用工程纪律，不是第三环专有制品。
2. 与第二环提升模型一致。
3. 最大化为需要增量开发、调试框架或 TDD 的用户发现性。
4. 清楚表示这些*也*在第三环中有用，但*不仅*在第三环中有用。

---

## 实施路线图

### 阶段 1：文件结构

```
skills/
├── incremental-implementation/
│   ├── SKILL.md                   （从 references/skills/... 复制）
│   ├── README.md                  （新增：独立 + 第三环上下文）
│   └── examples/                  （可选：详细示例）
├── debugging-and-error-recovery/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
└── test-driven-development/
    ├── SKILL.md
    ├── README.md
    └── examples/
```

### 阶段 2：README 文档

每个 README.md 应该描述：

1. **是什么** — 单句总结
2. **何时使用** — 独立场景
3. **如何调用** — `/skill incremental-implementation ...`
4. **工作流** — 分步纪律
5. **在第三环上下文中** — 如何在 AI 编排循环中使用
6. **示例** — 具体场景和输出

### 阶段 3：Manifest 注册

更新 `.claude-plugin/marketplace.json` 和 `.agents/plugins/marketplace.json`：

```json
{
  "name": "incremental-implementation",
  "description": "增量构建代码变更：实现一个切片、测试、验证、提交、重复。用于大型重构、多文件功能，或任何你想要在没有测试的情况下写超过 100 行代码时。",
  "source": "local:skills/incremental-implementation"
},
{
  "name": "debugging-and-error-recovery",
  "description": "系统根本原因调试。停止一切、保留证据、应用结构化分类、修复根本原因。用于测试失败、编译中断或行为不符合期望时。",
  "source": "local:skills/debugging-and-error-recovery"
},
{
  "name": "test-driven-development",
  "description": "测试驱动开发纪律：先写测试，再写代码（红 → 绿 → 重构）。用于启动新功能或测试将在编码前澄清需求时。",
  "source": "local:skills/test-driven-development"
}
```

### 阶段 4：文档更新

1. **docs/install.md** — 添加说明这三个也可作为独立 skills 使用（除了在第三环中被使用）
2. **docs/loop-3-agent-centric.md** — 添加部分："第三环中使用的 Sub-Skills"，指向它们的独立文档
3. **README.md** — 更新"三环 + 六 skills"部分以提到这三个作为*额外*通用 skills
4. **skills/*/README.md** — 每个 sub-skill README 交叉引用它在第三环的使用处

### 阶段 5：CLI 集成（可选）

确保 `codoop install` 和安装文档提到所有九个 skills：
- 6 个顶层循环 skills（discover、ticket、spec、planning、dod、codoop-flow）
- 3 个现在被提升的 sub-skills（incremental-implementation、debugging-and-error-recovery、test-driven-development）

---

## 范围和工作量

| 任务 | 工作量 | 备注 |
|---|---|---|
| 复制三个 skills 到顶层 | 10 分钟 | 简单文件复制；无内容变更 |
| 写三个 README.md 文件 | 1-2 小时 | 为每个描述独立 + 第三环上下文 |
| 更新 manifests | 15 分钟 | 向 .claude-plugin/ 和 .agents/plugins/ 添加三个条目 |
| 更新 docs/install.md | 30 分钟 | 添加关于额外 skills 的说明 |
| 更新 docs/loop-3-agent-centric.md | 30 分钟 | 添加部分链接到被提升的 skills |
| 更新 README.md | 20 分钟 | 提到九个 skills（6+3） |
| （可选）创建 docs/skill-incremental-implementation.md 等 | 1-2 小时 | 详细用户指南（如需要） |
| **合计** | **~3-5 小时** | 大部分时间在文档 |

---

## 风险和缓解

| 风险 | 缓解 |
|---|---|
| 重复文件（references/ + skills/） | 决定：保留两者，但文档说明 skills/ 是权威版本。references/ 保留为内部备份。将来考虑从 references/ 到 skills/ 的符号链接。 |
| 不清楚哪个版本要更新 | 在 SKILL.md 标题中添加注释："权威位置：skills/incremental-implementation/。此 skill 也由第三环在 references/skills/incremental-implementation/ 内部引用" |
| 用户对 9 个 skills vs 6 个 skills 困惑 | 在文档中澄清："每个循环的六个核心 skills（discover、4× human-centric、codoop-flow）。三个额外通用 skills（incremental、debugging、tdd）也可用。" |
| Skills 过度增殖 | 设定门栏：仅提升真正通用的（适用于 codoop-flow 之外）。不要提升第三环专有的 agents（五个审查 personas）。 |

---

## 后续步骤

1. **获得批准** — 这个计划是否符合方向？
2. **创建任务** — 实施上面的阶段 1-4
3. **测试** — 验证 /skill incremental-implementation 独立工作
4. **提交** — 单个提交，包含所有三个 skills、manifests 和文档
5. **宣布** — 更新 CHANGELOG / 发布说明

---

## 开放问题

1. 复制后我们应该保留 references/ 中的文件，还是删除它们？
   - **推荐：** 保留两者。references/ 是内部参考库；skills/ 是公开 API。
   
2. 我们应该创建单独的 docs/skill-incremental-implementation.md 文件，还是只更新 docs/loop-3-agent-centric.md？
   - **推荐：** 在 docs/loop-3-agent-centric.md 中添加"使用的 Skills"部分，带链接到顶层 skills。如果需要详细指南，创建单独文档。

3. 这三个 skills 应该在安装指南中标记为"额外"或"高级"吗？
   - **推荐：** 不。把它们与六个核心 skills 平等对待。只是澄清它们的目的："通用工程纪律，在和超出 codoop-flow 中都有用。"

