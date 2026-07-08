# 设计文档：工单类型（需求单 / 修复单）

> 状态：设计（仅设计，未实现）
> 日期：2026-07-07
> 范围：Loop 2（工单生产）；Loop 3 仅调整 commit message 前缀。

---

## 1. 背景

工单分为两种类型，各自的性质和所需信息不同：

| 维度 | 需求单 (feature) | 修复单 (fix) |
|---|---|---|
| 出发点 | 业务需求、用户故事 | 一个已存在的 bug / 缺陷 |
| 是否需要 PRD | 需要——定义"要做什么" | 不需要——"要做什么"已明确：让它别再错 |
| 是否需要 spec | 需要——设计新接口 / 数据模型 | 通常不需要——改动局限、契约不变 |
| 核心信息 | 业务大图 + 验收标准 | 复现步骤 + 根因 + 预期行为 |
| 编辑范围 | 可能跨多端多模块 | 通常很窄、集中 |
| 典型体量 | 中大 | 小 |

Loop 2 的工单生产流程（`codoop-ticket`）以需求单为模型设计：三阶段强制流转 `module_prd.md`（纯业务 PRD）→ `spec.md`（技术契约）→ `plan.md` + `todo.md`（任务拆解），且 `validate` 把 `module_prd.md` 和 `spec.md` 列为硬必需。修复单套用这套重流程时，会被迫为一个小 bug 编造 PRD 和 spec，否则无法通过 `validate` 并 promote。

因此系统区分两类工单，并让"必需文档集合"随工单类型变化：feature 保持完整流程，fix 采用贴合缺陷排查的轻量流程。核心原则是**减法**——fix 只是放宽 feature 强加的必需项，不引入新的强制流程或门禁。

---

## 2. 设计

### 2.1 metadata 字段 `ticket_type`

`metadata.json` 包含一个可选字段 `ticket_type`：

```json
{
  "ticket_id": "ticket_042",
  "title": "修复搜索结果分页越界",
  "ticket_type": "fix",          // "feature" | "fix"，缺省 = "feature"
  "modules": ["backend"],
  "test_command": { "backend": "bash script/test-backend.sh" },
  "files_to_edit": ["backend/**"],  // 可选、仅作编辑范围提示，verify 不强制
  "max_healing_attempts": 3,
  "ui_capture": false
}
```

- 类型：`str`，取值 `"feature"` | `"fix"`。
- 缺省 `"feature"`：未写该字段的工单按需求单处理（后向兼容）。
- 落点：`skills/_shared/codoop_lib_v1/ticket.py` 的 `Ticket` dataclass 增加 `ticket_type: str = "feature"`，`load()` 中 `raw.get("ticket_type", "feature")` 并校验取值合法。
- 枚举天然可扩展：未来新增类型只需加枚举值 + 一行查表。

类型用显式字段承载（而非仅靠描述推断），使确定性工具层（`validate` 的必需项分支）能可靠地选择规则，不依赖 LLM 判断。

### 2.2 必需文档按类型区分

`validate` 先读 `metadata.json` 拿到 `ticket_type`，再按下表选择必需 / 推荐文档集合：

| 类型 | 必需文档 | 推荐文档 |
|---|---|---|
| `feature` | `module_prd.md`, `spec.md` | `plan.md`, `todo.md` |
| `fix` | `bug_report.md` | `plan.md`, `todo.md` |

- feature 规则与现状一致。
- fix 只要求 `bug_report.md`，不强制 PRD 与 spec。
- `plan.md` / `todo.md` 对两类工单同等对待——均为推荐文档：`init` 都会生成脚手架，`validate` 缺失时以 advisory warning 提醒但不阻塞 promote。fix 单同样用它们落实修复步骤与原子任务。

对应 `tickets_cli.py` 中当前的全局常量：

```python
REQUIRED_DOCS = ("module_prd.md", "spec.md")
RECOMMENDED_DOCS = ("plan.md", "todo.md")
```

改为按 `ticket_type` 查表。

### 2.3 fix 的模板 `bug_report.md`

`init_draft` 在 `ticket_type == "fix"` 时生成 bug 报告模板（中 / 英双语，沿用现有语言检测逻辑）：

```markdown
# <title> — Bug 修复单

## 现象 (Symptom)
> 用户/系统观察到的错误表现，附截图或日志。

## 复现步骤 (Reproduction)
> 1. ... 2. ... 3. → 出现 X（期望 Y）

## 根因 (Root Cause)
> 定位到的原因（可在修复中补充）。

## 预期行为 (Expected Behavior)
> 修好之后应该是什么样。

## 影响范围 (Scope)
> 受影响的模块 / 文件（对应 metadata 里可选的 files_to_edit 编辑范围提示）。
```

`spec.md` 对 fix 为可选：当修复确实涉及契约 / 数据模型变更（例如改 API 返回结构）时，作者可自愿补一份 spec；简单 bug 不强制。

### 2.4 `codoop-ticket` 的流程分支

`codoop-ticket` skill（`SKILL.md`）在开场根据用户描述推断类型：

- 出现"修复 / fix / bug / 报错 / 异常 / 坏了 / 回归 / 修复"等信号 → 倾向 `fix`。
- 否则倾向 `feature`。

**类型确认策略：总是确认。** `codoop-ticket` 把推断结果明示给用户并请其确认，不静默选型，用户一句话即可纠正。原因：

- `ticket_type` 是分流开关——它决定走哪条流程、哪些文档是必需项（feature 强制 PRD + spec，fix 用 bug_report.md 轻量流程）。判错必然返工：把 feature 判成 fix 会让设计过薄流向 Loop 3；把 fix 判成 feature 会为一个小 bug 强制 PRD / spec，正是本设计要消除的摩擦。
- 类型边界本就模糊（"改善报错文案"是改进还是缺陷修复？"加重试机制"既像修 bug 又像加功能），而确认成本极低——对话里问一句、用户通常一个词即可。
- Loop 2 本就在每个阶段之间插入人工确认（PRD OK → 进 spec 等）。"类型确认"作为流程的第一个确认步骤，与既有对话节奏一致。

示例对话：

```
User: 搜索结果分页有时候会越界报错，帮我处理一下
codoop-ticket: 这看起来是「修复单 (fix)」——已存在的 bug，我会用 bug_report.md
              轻量流程（跳过 PRD/Spec）。确认吗？还是当作需求单 (feature) 走完整流程？
User: 对，修 bug
codoop-ticket: 好，创建 fix 类型草稿…
```

确认后分支：

- **feature 分支**：三阶段流程（PRD → Spec → Tasks），与现状一致。
- **fix 分支**：填 `bug_report.md`（现象 / 复现 / 根因 / 预期），拆出 `plan.md` + `todo.md`（修复步骤与原子任务），然后 `update-metadata` → `validate` → `promote`。

`init` 命令支持 `--type feature|fix`（缺省 `feature`），写入 metadata 并选对应脚手架。用 `--type` 显式指定时不涉及推断；确认策略只作用于 skill 的自然语言入口。

### 2.5 Loop 3 的 commit message 前缀

Loop 3 按 `ticket_type` 区分 `finish` 生成的默认 commit message 前缀：

- `feature` → `feat(<module>): <title> [<id>]`
- `fix` → `fix(<module>): <title> [<id>]`

落点：`skills/codoop-execute/scripts/codoop_tools.py` 的 `cmd_finish`（当前硬编码 `feat(...)`），改为读取 `ticket.ticket_type` 选前缀。`Ticket.load` 天然可读到该字段。仅影响未显式传入 `--message` 的默认模板；用户显式指定的 message 不受影响。

Loop 3 其余逻辑不变：`verify` 仍只有两道硬门（测试 + UI 截图，见 [[loop-3-agent-centric]]），不新增门禁。pick 时可将 `ticket_type` 一并透出，供编码代理调整策略（例如 fix 单更聚焦最小改动、优先补一个能复现的测试），但这是建议而非强制。

---

## 3. 后向兼容性

- `ticket_type` 缺省 `"feature"`：所有现存工单、以及外部工具生成的旧 metadata 都按需求单处理，行为不变。
- `validate` 的 feature 分支等于当前逻辑，行为零变化。
- `bug_report.md` 只在 fix 类型下出现，不影响 feature 的文件集合。
- Loop 3 仅 `cmd_finish` 的默认 commit 前缀按 `ticket_type` 区分（缺省 feature → 仍是 `feat(...)`）；verify / pick / fail 逻辑不变。

---

## 4. 影响到的文件（实现时参考）

| 文件 | 改动 |
|---|---|
| `skills/_shared/codoop_lib_v1/ticket.py` | `Ticket` 增加 `ticket_type` 字段 + 取值校验 |
| `skills/_shared/codoop_lib_v1/tickets_cli.py` | `REQUIRED_DOCS` / `RECOMMENDED_DOCS` 改为按类型查表；`init_draft` 增加 fix 脚手架；`validate_draft` 按类型选规则 |
| `skills/codoop-ticket/scripts/codoop-ticket.py` | `init` 子命令增加 `--type` 参数 |
| `skills/codoop-execute/scripts/codoop_tools.py` | `cmd_finish` 默认 commit 前缀按 `ticket_type` 选 `feat` / `fix` |
| `skills/codoop-ticket/SKILL.md` | 增加"类型判断 + fix 分支流程"说明 |
| `docs/loop-2-human-centric.md`（+ zh-CN） | 文档化两类工单与各自必需项 |
| `tests/test_skeleton.py` | 增加 fix 类型的 init / validate / promote 生命周期测试 |
