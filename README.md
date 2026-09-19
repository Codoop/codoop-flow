# codoop-flow

**English** · [简体中文](./README.zh-CN.md)

**Turn ideas into actionable requirements, then let AI build, verify, and review the code.**

codoop-flow is a development workflow plugin for Codex, Claude Code, and Cursor. Describe what you want in plain language; it helps clarify requirements, break down tasks, and implement them. Use it to plan a new product, add features, or fix bugs in an existing project.

## Install

Requires Git and Python 3.11+. Use it inside a local Git project.

**Codex (Desktop / CLI)** — run in your terminal, then reopen Codex:

```bash
codex plugin marketplace add Codoop/codoop-flow
codex plugin add codoop-flow@codoop-flow
```

**Claude Code** — run in your session:

```text
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

**Using Cursor, another agent, or having trouble?** See the [full installation guide](./docs/install.md).

## Get started

Open your project and send these three prompts to your coding agent, one step at a time.

**1. Set up your project (once)**

```text
Use codoop-init to inspect this project and set up codoop-flow.
```

The agent checks your project structure, creates the configuration, and asks for your language and role preferences.

**2. Describe a feature**

```text
Use codoop-ticket to design a ticket for letting users search and filter orders.
```

Replace the example with your requirement. The agent clarifies key questions and creates requirements, an implementation plan, and a task list, with a viewable UI preview when needed. After your confirmation, the ticket enters the queue. You don't need to write ticket files yourself.

**3. Let the agent implement it**

```text
Use codoop-execute to run the next ticket in this project.
```

The agent implements the ticket on a separate branch, runs verification and reviews, then commits the code and archives the ticket. If verification or review fails, it attempts fixes within a retry budget; if it cannot finish, it leaves a report for you. You decide whether to merge and when to push.

For each subsequent feature, repeat steps 2 and 3.

## Other common tasks

| What you want | What to tell the agent |
| --- | --- |
| Explore a product idea before building | Use codoop-discover to plan an order management tool for small teams. |
| Fix an existing bug | Use codoop-ticket to create a fix ticket for search filters being lost when changing pages. |
| Implement a ticket already in the queue | Use codoop-execute to run the next ticket in this project. |
| Check the experience from a user's perspective | Use codoop-ux-walkthrough to try order search as a first-time operations manager. |

Use these capabilities independently; you don't need to start with product planning every time.

## Documentation

- [Installation and configuration](./docs/install.md): agent setup, language and role preferences, and UI snapshots.
- [Product planning](./docs/loop-1-venture-discovery.md): from idea to product proposal.
- [Ticket design](./docs/loop-2-human-centric.md): requirements, UI previews, ticket formats, and design modes.
- [Execution mechanics](./docs/loop-3-agent-centric.md): isolated development, verification, reviews, failure recovery, and CLI.
- [Design blueprint](./docs/engineering-design.md): architecture and design rationale.
- [Changelog](./CHANGELOG.md)

[MIT License](./LICENSE)
