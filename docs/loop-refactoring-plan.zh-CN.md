# 三环改造完整计划

## 核心愿景

**三个环（Loop）通过文件系统协作，代码上完全独立。**

```
Loop 1 (codoop-discover)
  ↓ 输出文档
docs/backlog/ {product/, interface/, architecture/, ...}
  ↑ 
Loop 2 (codoop-ticket) ← 读 backlog，设计工单
  ↓ 输出文档
docs/tickets/pending/ {ticket_001/, ticket_002/, ...}
  ↑
Loop 3 (codoop-flow) ← 读 pending，执行工单
  ↓ 输出代码 + 文档
docs/tickets/done/ {ticket_001/, ticket_002/, ...}
```

**好处：**
- 每个环完全独立运行（不需要其他环的代码）
- 三个环可以组合使用（通过文件系统协作）
- 用户可以选择只使用某个环，或使用完整流程

---

## 改造分为两部分

### Part A：架构重构（CLI 和库分离）

**目标：** Loop 2 和 Loop 3 各自独立的 CLI 和库

**现状问题：**
- Loop 2 的 CLI（codoop.py）混在 codoop-flow 中
- Loop 3 的 CLI（codoop_tools.py）和 Loop 2 共享同一个 codoop_flow/ 库
- 用户无法单独使用某个环

**解决方案：**

```
改造前：
skills/codoop-flow/
├── agents/               (6 个 internal personas)
├── scripts/
│   ├── codoop.py         (Loop 2 + 3 混合)
│   ├── codoop_tools.py   (Loop 3)
│   └── codoop_flow/      (Loop 2 + 3 + 共享)
└── references/           (3 skills + 6 personas)

改造后：
skills/codoop-ticket/scripts/
├── codoop-ticket.py      ← 新增（Loop 2 专用 CLI）
└── codoop_lib_v1/        ← 新增（独立库，含 Loop 2 + 共享）

skills/codoop-flow/scripts/
├── codoop_tools.py       (Loop 3 CLI)
├── codoop.py             (保留 setup/install 全局命令)
└── codoop_lib_v1/        ← 改名自 codoop_flow/（独立库，含 Loop 3 + 共享）

skills/_shared/agents/
├── (原有 7 个 personas)
├── code-reviewer.md      ← 新增
├── security-auditor.md   ← 新增
├── test-engineer.md      ← 新增
├── testing-evidence-collector.md      ← 新增
├── testing-reality-checker.md         ← 新增
└── engineering-technical-writer.md    ← 新增
```

**关键：** 两个 `codoop_lib_v1/` 必须是独立副本，不能有任何 import 依赖

#### Part A 工作量

| 任务 | 工作量 |
|---|---|
| 复制 5 个模块到 codoop-ticket/scripts/codoop_lib_v1/ | 5 分钟 |
| 创建 codoop-ticket.py（从 codoop.py 派生） | 10 分钟 |
| 修改所有导入语句（config.py, ticket.py） | 5 分钟 |
| 更新 codoop-ticket SKILL.md 添加 CLI 文档 | 10 分钟 |
| 重命名 codoop-flow/scripts/codoop_flow/ → codoop_lib_v1/ | 5 分钟 |
| 更新 codoop_tools.py 和 codoop.py 导入 | 10 分钟 |
| 更新 codoop-flow SKILL.md | 5 分钟 |
| 验证两环独立运行 | 10 分钟 |
| **合计** | **~60 分钟** |

---

### Part B：Loop 3 能力提升（Sub-Skills + All Personas）

**目标：** 提升 Loop 3 内部的 sub-skills 和所有 personas 到顶层

**三个子 Skills（从 references/skills/ 提升）：**
- incremental-implementation（增量实现纪律）
- debugging-and-error-recovery（调试自愈纪律）
- test-driven-development（TDD 纪律）

**六个 Personas（从 references/agents/ 全部提升）：**

*Review Personas（审查类）：*
- code-reviewer（代码审查）
- security-auditor（安全审计）
- test-engineer（测试工程）

*UI/UX Personas（验收类）：*
- testing-evidence-collector（UI 视觉规范验收）
- testing-reality-checker（UX 交互体验验收）

*Documentation Persona（文档类）：*
- engineering-technical-writer（活文档同步）

**codoop-flow 中不再包含任何 agents 目录。**

#### Part B 步骤

1. 复制 3 个 sub-skills 到 `skills/` 顶层
2. 复制 6 个 personas（全部）到 `skills/_shared/agents/`
3. 删除 `skills/codoop-flow/references/` 目录
4. 删除 `skills/codoop-flow/agents/` 目录
5. 更新 codoop-flow SKILL.md 中的路径引用（指向 `../../_shared/agents/`）
6. 更新 manifests（.claude-plugin/marketplace.json）

#### Part B 工作量

| 任务 | 工作量 |
|---|---|
| 复制 3 个 sub-skills | 3 分钟 |
| 复制 6 个 personas | 2 分钟 |
| 删除 references/ 目录 | 1 分钟 |
| 删除 agents/ 目录 | 1 分钟 |
| 更新 codoop-flow SKILL.md 路径 | 10 分钟 |
| 更新 manifests | 5 分钟 |
| 更新文档（docs/install.md） | 5 分钟 |
| 验证功能无破损 | 10 分钟 |
| **合计** | **~37 分钟** |

---

## 完整改造路线

### 并行进行（推荐）

**时间：** ~97 分钟（60 + 37）

同时进行 Part A 和 Part B，最后一起提交：

```
Phase 1（并行）：
├─ Part A：分离 Loop 2/3 CLI 和库 (~60 min)
├─ Part B：提升 Loop 3 sub-skills 和所有 personas (~37 min)
└─ 最后：验证整体一致性，单个提交

产出：
├── codoop-ticket/scripts/{codoop-ticket.py, codoop_lib_v1/}
├── codoop-flow/scripts/{codoop_lib_v1/ (改名), SKILL.md 更新}
│   (删除 agents/ 目录)
├── skills/{incremental-implementation/, debugging-and-error-recovery/, test-driven-development/}
├── skills/_shared/agents/
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   ├── test-engineer.md
│   ├── testing-evidence-collector.md
│   ├── testing-reality-checker.md
│   └── engineering-technical-writer.md
└── docs/{install.md, loop-2-human-centric.md, loop-3-agent-centric.md} 更新
```

### 或顺序进行

先 Part B（独立于 Part A），再 Part A（依赖但不冲突）

---

## 改造完成后的架构

### 文件系统

```
docs/
├── backlog/              ← Loop 1 输出
│   ├── design-draft.md
│   ├── product/
│   ├── interface/
│   └── architecture/
├── tickets/
│   ├── drafts/           ← Loop 2 设计中
│   ├── pending/          ← Loop 3 待执行
│   ├── in_progress/      ← Loop 3 执行中
│   ├── done/             ← Loop 3 完成
│   └── failed/
├── prd/                  ← 业务常青文档
└── tech/                 ← 技术常青文档
```

### Skills 结构

```
skills/
├── codoop-discover/                         (Loop 1 - 已独立)
├── codoop-ticket/                           (Loop 2 - 改造后独立)
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── codoop-ticket.py                 ← CLI
│   │   └── codoop_lib_v1/                   ← 独立库
├── codoop-flow/                             (Loop 3 - 改造后独立 + 能力提升)
│   ├── SKILL.md (更新)
│   └── scripts/
│       ├── codoop_tools.py
│       ├── codoop.py                        (setup/install)
│       └── codoop_lib_v1/                   ← 独立库（改名，删除 agents/）
├── spec-driven-development/                 (Loop 2 支持 skill)
├── planning-and-task-breakdown/             (Loop 2 支持 skill)
├── definition-of-done/                      (Loop 2 支持 skill)
├── incremental-implementation/              (Loop 3 sub-skill - 新增)
├── debugging-and-error-recovery/            (Loop 3 sub-skill - 新增)
├── test-driven-development/                 (Loop 3 sub-skill - 新增)
└── _shared/agents/                          (所有 personas 集中)
    ├── alignment-agent.md                   (Loop 1)
    ├── design-ux-architect.md               (Loop 1)
    ├── ... (原有 7 个)
    ├── code-reviewer.md                     (Loop 3 - 新增)
    ├── security-auditor.md                  (Loop 3 - 新增)
    ├── test-engineer.md                     (Loop 3 - 新增)
    ├── testing-evidence-collector.md        (Loop 3 - 新增)
    ├── testing-reality-checker.md           (Loop 3 - 新增)
    └── engineering-technical-writer.md      (Loop 3 - 新增)
```

---

## 改造后的用户体验

### 场景 1：只用 Loop 2（工单设计）

```bash
# 用户有一个 codoop_flow.toml，想设计工单

python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket init ticket_001 --config codoop_flow.toml --title "Add search"

# 编辑 docs/tickets/drafts/ticket_001/ 的文件

python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket validate ticket_001 --config codoop_flow.toml

python skills/codoop-ticket/scripts/codoop-ticket.py \
  ticket promote ticket_001 --config codoop_flow.toml
# 完成！工单在 docs/tickets/pending/ 中
```

或在 AI 编码工具中：
```
/skill codoop-ticket 设计一个用户搜索功能
```

### 场景 2：只用 Loop 3（工单执行）

```bash
# 用户有工单在 docs/tickets/pending/，想执行

python skills/codoop-flow/scripts/codoop_tools.py \
  --config codoop_flow.toml pick

# AI 代理在会话内执行工单
/skill codoop-flow 针对 codoop_flow.toml 运行工单
```

### 场景 3：完整流程（Loop 1 → 2 → 3）

```bash
# 初始化
python skills/codoop-flow/scripts/codoop_tools.py \
  setup /path/to/project --config codoop_flow.toml

# Loop 1：产品探索（AI 编码工具中）
/skill codoop-discover "我想做一个 SaaS 项目管理工具"
# → 输出 docs/backlog/

# Loop 2：工单设计（AI 编码工具中 或 CLI）
/skill codoop-ticket 基于 backlog 设计第一张工单
# 或
python skills/codoop-ticket/scripts/codoop-ticket.py ticket init ticket_001 ...
# → 输出 docs/tickets/pending/

# Loop 3：工单执行（AI 编码工具中 或 CLI）
/skill codoop-flow 执行 pending 工单
# 或
python skills/codoop-flow/scripts/codoop_tools.py --config ... pick
# → 输出 docs/tickets/done/ + 代码
```

---

## 检查清单

### Part A（架构重构）

- [ ] 在 codoop-ticket/scripts/ 中创建 codoop_lib_v1/
- [ ] 复制 5 个模块（config, ticket, gitutil, ignore, tickets_cli）
- [ ] 创建 codoop-ticket.py（从 codoop.py 派生）
- [ ] 删除 codoop.py 中的 setup 和 install 命令
- [ ] 更新所有导入语句（改为 `from codoop_lib_v1...`）
- [ ] 重命名 codoop-flow/scripts/codoop_flow/ → codoop_lib_v1/
- [ ] 更新 codoop_tools.py 的导入
- [ ] 更新 codoop-flow SKILL.md 和 codoop-ticket SKILL.md
- [ ] 测试 codoop-ticket.py 独立运行
- [ ] 测试 codoop_tools.py 独立运行

### Part B（能力提升）

- [ ] 复制 3 个 sub-skills 到 skills/
- [ ] 复制 6 个 personas 到 skills/_shared/agents/
- [ ] 删除 skills/codoop-flow/references/
- [ ] 删除 skills/codoop-flow/agents/
- [ ] 更新 codoop-flow SKILL.md 中的路径引用
  - 第 77 行（incremental-implementation）→ `../../incremental-implementation/SKILL.md`
  - 第 92 行（debugging-and-error-recovery）→ `../../debugging-and-error-recovery/SKILL.md`
  - 第 100-114 行（所有 personas）→ `../../_shared/agents/xxx.md`
- [ ] 更新 manifests（.claude-plugin/marketplace.json）- 添加 3 个新 skills
- [ ] 更新 docs/install.md 列出新增 3 个 skills
- [ ] 更新 docs/loop-3-agent-centric.md 更新 agents 说明
- [ ] 更新 docs/loop-3-agent-centric.md（如有说明）

### 最后验证

- [ ] 无任何文件被 git 意外忽略
- [ ] 所有 Python 文件 import 正确（模拟运行 `python -m py_compile`）
- [ ] README 或文档被正确更新
- [ ] 提交消息清晰准确

---

## 后续可选优化

1. **共享库版本检查脚本** — 检测两个 codoop_lib_v1/ 的一致性
2. **Loop 1 + 2 集成** — codoop-ticket 中添加读 backlog 的参考文档功能
3. **部署脚本** — 为每个环生成独立的可安装包

---

## 待讨论

1. **执行顺序** — Part A 和 Part B 同步还是顺序？（推荐同步）
2. **测试策略** — 完成后如何验证三个环仍能协作？
3. **文档** — 需要新增"三环协作指南"文档吗？

