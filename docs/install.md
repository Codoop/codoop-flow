# 安装 codoop-flow skill 到各 coding agent

codoop-flow 是一个**自包含 skill**:`skills/codoop-flow/` 下同时带了编排说明书
(`SKILL.md`)、确定性护栏 CLI(`scripts/`)和它依赖的评审 persona / 子技能
(`references/`)。所以无论装到哪个 agent,只要那个目录能被读到、且能跑 `python3`,
流程就能跑起来。

> 前提:目标机器有 `python3`(标准库即可,无第三方依赖);目标工程是一个 git 仓库,
> 且有 `docs/tickets/{pending,in_progress,done,failed}/`。准备一份 `codoop_flow.toml`
> 指向目标工程(见 `codoop_flow.toml.example`)。

---

## Claude Code(推荐:插件市场)

```
/plugin marketplace add Codoop/codoop-flow
/plugin install codoop-flow@codoop-flow
```

> SSH 报错?市场默认用 SSH 克隆。没配 SSH key 就用完整 HTTPS:
> ```
> /plugin marketplace add https://github.com/Codoop/codoop-flow.git
> /plugin install codoop-flow@codoop-flow
> ```

**本地 / 开发**:
```bash
git clone https://github.com/Codoop/codoop-flow.git
claude --plugin-dir /path/to/codoop-flow
```

装好后,直接对 Claude 说:「读 codoop-flow skill,针对 <codoop_flow.toml> 跑一轮工单」,
或用 `/loop 5m run the codoop-flow skill against <toml>` 定时跑。

---

## 通用拷贝(Cursor / Codex / Gemini / 其他)

skill 是自包含目录,任何 agent 都可以直接把它拷进自己的技能/规则目录:

```bash
git clone https://github.com/Codoop/codoop-flow.git
# 拷这一个目录即可,它自带 scripts/ 和 references/
cp -R codoop-flow/skills/codoop-flow  <目标 agent 的技能目录>/
```

各 agent 的落脚点(参考各自文档,可能随版本变化):

| Agent | 放哪 | 怎么触发 |
|---|---|---|
| Cursor | 把 `SKILL.md` 放进 `.cursor/rules/`,或让 agent 引用整个 `skills/codoop-flow/` | 在对话里引用规则 |
| Codex / 其他 | skill 是纯 Markdown,把 `SKILL.md` 内容作为 system prompt / instructions 喂进去 | 直接对话 |
| Gemini CLI | 放进其 skills 目录 | 自动发现 |

**关键**:拷完后确保 `skills/codoop-flow/scripts/` 和 `references/` 跟 `SKILL.md`
保持在同一父目录下——SKILL.md 里所有路径都是相对自己(`$SKILL/scripts/...`、
`$SKILL/references/...`),拆开就找不到 CLI 和评审 persona 了。

---

## 验证装好了

```bash
python3 <skill路径>/scripts/codoop_tools.py --config <toml> status
```
能打印出各阶段工单计数(JSON)就说明护栏 CLI 就位、config 正确。

> 注意:非 Claude 的 agent 若没有等价于 Claude Code **Task 工具(派 subagent)** 的能力,
> skill 的「并行多重评审」这一段可能需要改写(改成串行评审或别的机制)。详见
> `docs/VERIFICATION_TODO.md` V4。
