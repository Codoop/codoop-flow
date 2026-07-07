# 第一环：创业探索（产品设计）

## 概述

**第一环**是 codoop-flow 三环系统中的第一个环。是一套结构化的、在会话内进行的协作式产品探索流程，用于 **0→1 阶段的产品设计** — 在写一行代码前进行。

**解决的问题：** 开发团队（尤其是 AI 协助的团队）经常跳过产品设计，直接开始开发，导致错误的假设被固化到代码里、业务/技术决策不对齐、规格不一致，最后付出昂贵的代价重做。第一环在聊天会话内运行一个分布式的多角色专家管道，生成锁定的、一致的规格文档集合，成为**唯一的真理来源**，在动笔写第一张工单前。

**在管道中的位置：** 生成 `docs/backlog/` → 供第二环（人工工单设计）和第三环（自动化实现）使用。

---

## 快速开始

在任何 AI 编码工具里（Claude Code、Codex、Cursor、Gemini CLI），只需说：

```
/skill codoop-discover 我想做一个 SaaS 项目管理工具，面向远程团队
```

这个 skill 会提问澄清问题、运行多角色专家会话并由你指挥，在一个会话内生成完整的设计规格到 `docs/backlog/`。

---

## 工作流程

### 第 1 步 — 澄清（SNAP：严格不做假设原则）

当编排器遇到任何模糊的需求（定价模式、平台范围、技术栈、功能边界）时，它会停下来并呈现结构化的选项：

```
[代理询问]：应该只支持网页还是也支持移动端？
- 选项 A：只支持网页，快速上市 [优势：范围聚焦、更快；劣势：限制用户体验]
- 选项 B：网页+稍后支持移动端 [优势：面向未来；劣势：初期复杂]
- 推荐：选项 A，然后把移动端作为第二环的工单 #2
```

你选择。会话不会跳过任何模糊的地方继续进行。

### 第 2 步 — 共享设计工作区

创建一个临时的协作文件：`docs/backlog/design-draft.md`。这是所有专家代理合作、浮出冲突和记录解决方案的"共享房间"。

### 第 3 步 — 多角色协作起草

七个专家代理依次被调用（或者如果你的 host 支持 subagent，就并行调用）。他们在 design-draft.md 中使用结构化协议工作：

- `[异议: <角色 A> → <角色 B>] <反对理由>` — 提出跨角色冲突
- `[已解决: <角色>] <解决方案>` — 记录达成的共识
- `[批准: <角色>]` — 角色对共识的签字

如果你需要推翻某个代理，直接在 `design-draft.md` 里放一个 `[人工指令]` 块。所有 sub-agent 下次调用时无条件遵从。

### 第 4 步 — 产品策略（PM 代理）

**产品-敏捷-优先级化** 代理起草：
- `module_prd.md` — 业务概览、用户故事、状态转移、Gherkin BDD 验收标准
- `user-journey.md` — 端到端的用户旅程和人物角色

**硬约束：** 100% 的纯业务语言。没有数据库表、没有 API 字段、没有代码。

### 第 5 步 — GTM 策略（GTM 代理）

**销售-推广-生成领导线索-策略家** 代理生产：
- `monetization-plan.md` — 订阅级别、通过价值方程式的定价、功能权限、领导磁铁和 GTM 渠道排序

### 第 6 步 — UX/UI 设计（设计代理）

**设计-UX-架构师** 和 **设计-UI-设计师** 合作生产：
- `design-system.md` — 信息架构、CSS 基础、响应式断点、无障碍组件模式
- `ui-mockups.md` — ASCII 线框图、设计令牌（颜色、排版、间距）、响应式框架和动画参数

### 第 7 步 — 技术架构（架构师代理）

**工程-后端-架构师** 和 **工程-软件-架构师** 联合生产：
- `architecture.md` — 系统架构模式、数据流、部署策略、缓存层、安全架构
- `database-schema.sql` — 完整的 DDL，包括索引和约束
- `openapi.yaml` — 生产级 OpenAPI 3.0 规格

### 第 8 步 — 模块级 BDD 规格

对每个功能单元，创建一个 `modules/module-<名称>.md` 文件，包含 Gherkin Given-When-Then 测试用例，覆盖主流程、边界情况和错误流程。

### 第 9 步 — 桥接文档

`bridge/` 下的三个文件：
- `human-preparation.md` — 非技术外部设置检查清单（注册账户、获取 API 密钥、设置支付网关、注册域名）
- `ai-co-dev-guide.md` — 非技术路线图，说明规格角色、逻辑编码序列和 AI 协作原则
- `scaffolding-blueprint.md` — 技术蓝图，目录布局、样板配置文件和核心代码结构

### 第 10 步 — 一致性审计（对齐代理）

**对齐代理** 在所有规格生成后独立运行。它：

1. 读取所有目录下的所有文件
2. 写入 `alignment-report.md`，包含严重级别、负责角色和解决状态
3. 在 `design-draft.md` 中为每个发现的冲突提出 `[对齐异议]` 块
4. 负责角色重新起草修复，并标记为 `[已解决]`
5. 对齐代理重新审计；如果 100% 对齐，向 `design-draft.md` 追加 `[对齐已批准]`

### 第 11 步 — 人工审查和锁定

只有在收到 `[对齐已批准]` 后，PM 才会向 `design-draft.md` 追加 `[等待人工审查]`。你审查整个 backlog 并批准。

### 第 12 步 — 归档

一旦锁定，架构师代理验证所有规格完整，然后删除 `design-draft.md` 以保持 repo 整洁。

---

## 输出

所有输出放在 `docs/backlog/` 下，结构如下：

```
docs/backlog/
├── design-draft.md              # 临时工作区（批准后删除）
├── alignment-report.md          # 一致性审计结果
├── product/
│   ├── requirements.md          # PRD：范围、状态转移、Gherkin BDD 场景
│   ├── user-journey.md          # 用户旅程和人物
│   └── monetization-plan.md     # 价格层级、功能权限、GTM 计划
├── interface/
│   ├── design-system.md         # 视觉令牌、响应式断点、组件
│   └── ui-mockups.md            # ASCII 线框图、动画参数
├── architecture/
│   ├── architecture.md          # 技术栈、数据流、部署、缓存
│   ├── database-schema.sql      # 完整 DDL，包括索引和约束
│   └── openapi.yaml             # 生产级 OpenAPI 3.0 契约
├── modules/
│   └── module-<名称>.md         # 单模块 Gherkin BDD 测试用例
└── bridge/
    ├── human-preparation.md     # 外部设置检查清单（非技术）
    ├── ai-co-dev-guide.md       # 如何继续使用 AI 编码工具
    └── scaffolding-blueprint.md # 物理目录结构+样板规格
```

所有文件都**按设计锁定** — 没有文件放在 `docs/backlog/` 根目录（除了两个根文件）。从不创建 `specs/` 目录。这些约束由对齐代理的目录审计强制。

---

## 涉及的 Skills

### 七个专家代理

所有代理定义在 `/skills/_shared/agents/` 中，由 `codoop-discover` skill 编排：

| 代理 | 文件 | 角色 |
|---|---|---|
| **PM / 产品策略** | `product-sprint-prioritizer.md` | 定义产品范围、用户旅程、BDD 场景；应用 RICE/MoSCoW 优先级化 |
| **GTM & 定价** | `sales-offer-lead-gen-strategist.md` | 设计价格层级、变现、GTM 渠道 |
| **UX 架构师** | `design-ux-architect.md` | 建立 IA、CSS 基础、响应式断点、无障碍基线 |
| **UI 设计师** | `design-ui-designer.md` | 视觉设计系统、组件库、WCAG AA 合规、设计令牌 |
| **后端架构师** | `engineering-backend-architect.md` | 系统架构、数据库模式、API 契约、安全优先设计 |
| **软件架构师** | `engineering-software-architect.md` | 域建模、ADR、架构模式、样板蓝图 |
| **对齐审计员** | `alignment-agent.md` | 交叉引用所有规格查找不一致，运行最终一致性审计 |

---

## CLI 参考

第一环**没有专用 CLI 命令**。它完全通过 `codoop-discover` skill 的在会话内调用进行。

`codoop.py` 文档中提到了一个 `discover` 子命令，但当前实现完全委托给了在会话内的 skill。CLI 工具链（`codoop.py setup`、`codoop.py install`、`codoop.py ticket`）是为第二环和第三环准备的。

---

## 配置

第一环不需要配置文件。它只在存在 `codoop_flow.toml` 时读取，以确定 `target_repo`，从而把输出写到正确的 `docs/backlog/` 目录。

**第一环不使用 `metadata.json`** — 所有输出都是人类可读的 markdown 和 YAML 规格。

---

## 集成

### 输入（第一环前）

第一环接收一个自由格式的产品想法作为输入：
```
我想做一个 SaaS 项目管理工具，面向远程团队
```

就这样。所有进一步的输入在会话内通过 SNAP 澄清问题交互收集。

### 输出（供第二环使用）

第一环批准后，人工工程师审查 `docs/backlog/` 并决定工单分解。第二环开始于：

1. 把 `docs/backlog/` 的核心内容提升到永恒文档树（`docs/prd/` 和 `docs/tech/`）
2. 在设计个别功能工单时，把 backlog 文件作为上下文阅读
3. 对每个模块调用 `/skill codoop-ticket <功能描述>`

**示例转移：** 第一环的 `docs/backlog/architecture/database-schema.sql` 直接流入第二环工单的 `spec.md` 文件的 `## 数据模式` 部分。

### 输出（供第三环使用）

第一环的 `docs/backlog/bridge/scaffolding-blueprint.md` 成为第一个第三环工单的直接输入：`ticket_001_project_scaffolding`。

所有 backlog 规格（架构、模式、API 契约）被第二环工单引用，然后由第三环通过 `codoop-execute` 执行。

---

## 轻量级 Beta 就绪完成定义（BR-DoD）

第一环对所有生成的设计应用四个条件质量要求：

1. **UX 连接优于控制台日志**（总是）— 所有异步状态必须有 UI 表现；没有无声失败；加载状态、错误提示和设置面板（如果产品有可配置设置）
2. **凭据持久化和会话恢复**（如果涉及认证）— 必须设计注册、登录、令牌刷新、DB 初始化
3. **外部服务和沙箱完整性**（如果有外部集成）— 所有服务必须支持完整沙箱/mock 模式；支付测试卡；通知双轨模式
4. **无摩擦分发**（条件取决于平台）— 未签名的桌面/移动构建脚本；web 后端的 docker-compose 或 PaaS

---

## 关键设计原则

- **人类作指导者，AI 作编排器** — 用户不被绕过。每个模糊的决策都通过结构化的代理询问块提交给你。
- **文档驱动，非代码驱动** — 第一环生成零代码。`scaffolding-blueprint.md` 是架构图，不是可执行样板。
- **分散起草前的集中审计** — 所有角色独立起草并提出 `[异议]` 标志。对齐代理最后运行作为独立审计员。
- **SNAP 作为不可协商** — skill 明确拒绝做假设。第一环解决的每个模糊性都能避免实现中 10 倍的代价。
- **输出语言自适应** — 如果你的会话是中文，输出就是中文。没有强制语言。

