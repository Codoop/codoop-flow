# codoop-flow

[English](./README.md) · **简体中文**

**把想法变成可执行的需求，让 AI 按需求写代码、验证和评审。**

codoop-flow 是用于 Codex、Claude Code 和 Cursor 的开发流程插件。你用自然语言描述要做什么，它帮你理清需求、拆分任务，再逐项实现。适合从零规划产品，也适合给已有项目加功能、修问题。

## 安装

需要 Git 和 Python 3.11+，并在本地 Git 项目中使用。

**Codex（Desktop / CLI）** — 在终端运行，安装后重新打开 Codex：

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

**Claude Code** — 在会话中运行：

```text
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

**Cursor、其他 Agent 或安装遇到问题？** 查看[完整安装说明](./docs/install.zh-CN.md)。

## 开始使用

打开你的项目，依次把下面三句话发给 AI。每一步完成后，再开始下一步。

**1. 初始化项目（首次使用时）**

```text
使用 codoop-init，分析当前项目并初始化 codoop-flow。
```

AI 会检查项目结构、设置配置，并询问你的语言和角色偏好。

**2. 描述一个要做的功能**

```text
使用 codoop-ticket，帮我设计“用户可以搜索并筛选订单”这个功能的工单。
```

把示例换成你的需求。AI 会澄清关键问题，生成需求、实现方案和任务清单；涉及界面时，按需提供可查看的预览。你确认后，工单进入待执行队列，无需手写工单文件。

**3. 让 AI 实现**

```text
使用 codoop-execute，执行当前项目的下一张工单。
```

AI 会在独立分支中实现，运行验证并进行评审，通过后提交代码、归档工单。验证或评审失败时，会在重试预算内修复；无法完成时留下报告，交给你处理。是否合并、何时推送，由你决定。

之后每做一个功能，重复第 2、3 步即可。

## 其他常用场景

| 你想做什么 | 可以直接对 AI 说 |
| --- | --- |
| 只有一个产品想法，先想清楚做什么 | 使用 codoop-discover，帮我梳理一个面向小团队的订单管理工具。 |
| 修复已有问题 | 使用 codoop-ticket，为“搜索后翻页丢失筛选条件”创建修复工单。 |
| 已有待执行工单，直接开始开发 | 使用 codoop-execute，执行当前项目的下一张工单。 |
| 从用户角度检查体验 | 使用 codoop-ux-walkthrough，以首次使用的运营人员身份体验订单搜索。 |

这些能力可以单独使用，不必每次从产品规划开始。

## 详细文档

- [安装与项目配置](./docs/install.zh-CN.md)：各 Agent 安装、语言和角色设置、页面快照。
- [产品规划](./docs/loop-1-venture-discovery.zh-CN.md)：从想法到产品方案。
- [工单设计](./docs/loop-2-human-centric.zh-CN.md)：需求确认、界面预览、工单格式和设计模式。
- [执行机制](./docs/loop-3-agent-centric.zh-CN.md)：隔离开发、验证评审、失败恢复和 CLI。
- [设计蓝图](./docs/engineering-design.zh-CN.md)：底层架构与设计思路。
- [更新记录](./CHANGELOG.md)

[MIT License](./LICENSE)
