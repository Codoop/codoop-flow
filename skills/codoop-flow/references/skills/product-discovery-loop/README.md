# Product Discovery & Design Loop (产品探索与设计循环)

本技能（Skill）指导 AI 扮演**主编排代理（Orchestrator）**，运行一个去中心化、多角色协同的流水线，用于探索、验证并架构产品或新功能。它通过严格的上下文隔离、多视角辩论和独立的一致性审计，确保产出生产级的 BDD 规格说明书和系统架构。

---

## 1. 工作流生命周期流程图 (Workflow Lifecycle Flowchart)

以下流程图详细展示了从用户提出初始想法，到多角色协同起草、规格固化、独立一致性审计（Alignment Loop）、人类导演评审锁定，直至最终归档清理的完整闭环生命周期：

```mermaid
flowchart TD
    %% 1. Initiation Stage
    subgraph initStage [1. 启动阶段 (Initiation)]
        UserIdea["用户提出初始想法 (User Idea)"] -->|1.1 触发| Orchestrator["主编排代理 (Product Architect)"]
        Orchestrator -->|1.2 初始化草稿| CreateDraft["创建临时设计草稿<br>docs/backlog/design-draft.md"]
    end

    %% 2. Collaborative Drafting Stage
    subgraph draftStage [2. 协同起草与辩论阶段 (Collaborative Drafting)]
        CreateDraft -->|2.1 调度子代理| DispatchSubAgents["调度 PM, GTM, UI/UX, Architect"]
        DispatchSubAgents -->|2.2 协同起草| CoEdit["在 design-draft.md 中协同编辑与辩论"]
        
        %% Challenge Loop
        CoEdit -->|2.3 提出质疑| Challenge["[CHALLENGE: Role A -> Role B]"]
        Challenge -->|2.4 讨论与妥协| Resolve["[RESOLVED: Role B]"]
        Resolve -->|2.5 达成共识| Approve["[APPROVED: Role]"]
        Approve -->|循环辩论| CoEdit

        %% Human Directive
        UserDirective["人类导演介入<br>[HUMAN DIRECTIVE]"] -.->|无条件服从并调整设计| CoEdit
    end

    %% 3. Hardening Stage
    subgraph hardeningStage [3. 规格固化阶段 (Hardening)]
        CoEdit -->|3.1 达成初步共识| Hardening["固化为结构化规格说明书"]
        Hardening -->|3.2 生成文件| Specs["requirements.md / monetization-plan.md<br>design-system.md / ui-mockups.md<br>architecture.md / database-schema.sql<br>openapi.yaml / modules/ (BDD)"]
    end

    %% 4. Alignment Audit Stage (The Alignment Loop)
    subgraph alignmentStage [4. 一致性审计与对齐循环 (Alignment Loop)]
        Specs -->|4.1 触发审计| DispatchAlignment["Orchestrator 调度 Alignment Agent"]
        DispatchAlignment -->|4.2 交叉比对| CrossAudit["读取所有产出文档进行交叉比对与审计"]
        CrossAudit -->|4.3 生成报告| GenReport["生成 docs/backlog/alignment-report.md"]
        
        GenReport -->|4.4 发现不一致?| CheckInconsistency{"是否存在不一致?"}
        
        CheckInconsistency -->|是 (Yes)| AlignmentChallenge["在 design-draft.md 中写入<br>[ALIGNMENT CHALLENGE: Alignment -> Role]"]
        AlignmentChallenge -->|4.5 重新调度修正| ReDispatch["重新调度 PM/GTM/UI-UX/Architect 修正文件"]
        ReDispatch -->|4.6 更新规格文件| Specs
        
        CheckInconsistency -->|否 (No)| AlignmentApproved["在 design-draft.md 中追加<br>[ALIGNMENT APPROVED: Alignment]"]
    end

    %% 5. Human Review & Locking Stage
    subgraph reviewStage [5. 人工评审与锁定阶段 (Human Review & Lock)]
        AlignmentApproved -->|5.1 提请评审| WaitingReview["PM 追加 [WAITING FOR HUMAN REVIEW]<br>主代理暂停，等待人类导演评审"]
        WaitingReview -->|5.2 评审通过| HumanLock["人类导演确认并标记为 Locked"]
    end

    %% 6. Archiving & Purge Stage
    subgraph archiveStage [6. 归档与清理阶段 (Archiving & Purge)]
        HumanLock -->|6.1 归档验证| DispatchArchitect["Orchestrator 调度 Architect Agent"]
        DispatchArchitect -->|6.2 验证规格完整性| VerifySpecs["验证所有规格文件完整无缺"]
        VerifySpecs -->|6.3 清理临时文件| PurgeDraft["彻底删除临时草稿 design-draft.md<br>保持代码库整洁"]
        PurgeDraft -->|6.4 交付开发| DevReady["交付开发阶段 (Actual Coding)"]
    end
```

---

## 2. 依赖与第三方 Skill 集成 (Sibling Skills Overview)

为了保持 Token 效率，主 `SKILL.md` 中不重复视觉、动画或商业分析的具体标准。相反，它动态导入并路由执行到工作区中预装的兄弟 Skill 资产：

```text
product-discovery-loop/ (核心编排方法论)
   ├── SKILL.md
   └── README.md (本文件 - 依赖与流程目录)
        │
        ├──► ui-ux-pro-max/ (视觉 Token 与布局网格规则)
        │
        ├──► gsap-skills/ (60fps 动画时间线与曲线)
        │
        └──► pm-skills/ (OST、商业化与红队 CLI 工具)
```

---

## 3. 兄弟 Skill 路径配置 (Integration Mapping)

主编排代理（`@product-architect`）及各专业子代理利用以下路径和标准来加载并执行兄弟 Skill：

### 3.1 UI/UX 设计系统标准 (`ui-ux-pro-max`)
- **类型**：项目/用户级 Skill
- **默认路径**：`.cursor/skills/ui-ux-pro-max/SKILL.md`
- **作用域**：由 `@ui-ux-agent` 和 `@pm-agent` 加载，用以确立符合人体工程学、无障碍且直观的网格布局、间距比例、色彩 Token 和字体规范。

### 3.2 GSAP 流体交互动画 (`gsap-skills`)
- **类型**：插件/缓存级 Skill
- **默认路径**：`.cursor/plugins/cache/cursor-public/gsap-skills/aed9cfd3277740755f6bfc1155c7aa645403b760/skills/`
- **子模块**：
  - `gsap-core/SKILL.md` — 核心动画规则。
  - `gsap-timeline/SKILL.md` — 序列时间表。
  - `gsap-react/SKILL.md` — React 绑定优化。
- **作用域**：由 `@ui-ux-agent` 加载，用以精确调度界面交互、过渡路径和基于时间线的动画参数（如 60fps 淡入淡出、卡片折叠等）。

### 3.3 商业分析与红队工具 (`pm-skills`)
- **类型**：外部 CLI 与命令市场
- **作用域**：在终端上下文或 CLI 集成中全局可用。
- **常用命令**：
  - **PM**：`/discover`（假设映射）与 `/write-stories`（用户故事拆解）。
  - **GTM**：`/pricing`（定价弹性与商业化策略设计）。
  - **Architect**：`/red-team-prd`（PRD 压力测试）与 `/derive-tests`（BDD 测试映射）。

---

## 4. 移植与自定义路径 (Customizing Sibling Paths)

如果您将此设计循环移植到新项目或非 Cursor 工作区：
1. 将 `.cursor/skills/product-discovery-loop/` 复制到新项目的 `.cursor/skills/` 中。
2. 确保同时复制 `.cursor/skills/ui-ux-pro-max/` 目录，以保留视觉 Token 逻辑。
3. 主编排代理将自动根据标准相对路径（`../ui-ux-pro-max/SKILL.md`）查找并利用这些文件。
