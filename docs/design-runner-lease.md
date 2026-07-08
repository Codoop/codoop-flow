# 设计文档：工单钥匙（Ticket Lease）——防止两个执行者同时写一个 worktree

> 状态：已实现（见 `skills/_shared/codoop_lib_v1/lease.py`、`skills/codoop-execute/scripts/codoop_tools.py`、`tests/test_skeleton.py`）
> 日期：2026-07-08
> 范围：Loop 3（`codoop-execute` / `codoop_tools.py`）；附带 SKILL.md 文档修订。
> 背景：实际使用中发现 `pick` 能防止重复认领**新**工单，但不能防止两个执行者同时“恢复”同一个 `in_progress` 工单，导致同一个 worktree 被两边并发改写、互相覆盖。

---

## 1. 问题（大白话 + 代码定位）

一个工单 = 一个房间（worktree），一次只该有一个工人进去干活。

现在的门卫（`pick`）只检查“房间是不是空的”：

- 房间空 → 放新工人进去。✅
- **房间已经有人 → 门卫嘴上说“已经有人在干了”，但还是把钥匙递给第二个人，甚至房间没了还帮忙重建。** ❌

代码定位：`cmd_pick`（`skills/codoop-execute/scripts/codoop_tools.py:72`）在 `in_progress/` 非空时返回 `picked:false`，
却仍然回传 `worktree` 路径，并在 worktree 缺失时 `wt.create()`（第 84–85 行）。它把“已被占用”当成“可安全恢复”，**没有任何归属（谁的房间）概念**。而 `SKILL.md:70-72` 又把这个返回解释成“去 resume”，于是两个执行者拿到同一个 live worktree 各自施工、互相拆墙。

**另有一个潜在竞态**：`cmd_pick` 里“检查 in_progress 为空 → `_move(pending)`”不是原子操作。两个**首次** pick 若同时进来，都能通过空检查，第二个 `shutil.move` 会抛未捕获异常。完整修复应一并处理（见 §5）。

---

## 2. 决策：只做最简单的两件事

经过讨论，明确**不由机器去猜“工人是不是跑路了”**。理由：工单目录会留下记录，人（工头）每次验收时自然会发现“这间活没干完”，届时手动喊人接着干即可。既然判活交给人，机器侧就砍掉一切超时/心跳/自动接管逻辑。

于是方案缩成三件事：

1. **发钥匙，防撞车**：第一个工人进门时，门卫当场发一把钥匙（一串随机 token）。之后凡是对这个房间办事都要亮钥匙。没钥匙的第二个人——**一律挡在门外，让它干净地停下**。
2. **手动换人**：钥匙**永不自动过期**。万一工人真断了，房间就一直锁着；由**人**用一个显式命令“换人”，门卫作废旧钥匙、发新钥匙给接手的工人。
3. **让工头一眼看清房间进度**：既然判活交给人，就得给人一个明显、可靠的地方去判——增强 `status`，把每个 `in_progress` 工单的“干到哪了”摊出来（见 §4.5）。

### 明确不做（相对上一版砍掉的）

- ❌ 不做 TTL / 超时判活
- ❌ 不做心跳 / heartbeat 子命令
- ❌ 不做后台打卡进程
- ❌ 不做“租约过期自动接管”

“干得慢”因此**根本不构成问题**：钥匙不会因为干得久而失效，只有活干完（finish/fail）或人工换人（takeover）才会换钥匙。

---

## 3. 目标 / 非目标

**目标**
- 同一时刻，最多一个执行者对某个 `in_progress` 工单持有钥匙。
- 没拿钥匙的自动循环碰到别人的房间 → 干净停下并报告，不硬闯、不乱动。
- 合法的“同一执行者恢复自己被中断的工单”仍然顺畅（它带着钥匙回来即可）。
- 人可以用一条命令把房间交给新工人。
- 关闭 §1 的两个竞态。

**非目标**
- 不做机器自动判活 / 自动接管（交给人）。
- 不做跨机器强一致锁（单机 / 本地 worktree 场景）。

---

## 4. 钥匙（lease）设计

### 4.1 钥匙文件位置

放在**运行时目录**，不进 target repo 的 `docs/tickets/`（那里可能被人 `git add`，不该混入运行态）：

```
<worktree_root>/.codoop-leases/<ticket_id>.json
```

内容（极简）：

```json
{
  "ticket_id": "phase-26-visual-concept-alignment",
  "token": "9f3c…",     // 门卫铸造的随机凭证 = 谁持有这个房间
  "worktree": "/…/worktrees/phase-26-visual-concept-alignment",
  "acquired_at": "2026-07-08T10:00:00Z",   // 仅供人排障，不参与任何判活
  "note": "codoop-pending-ticket-executor"  // 可选，来自 --runner-note，仅排障
}
```

- `token` 是唯一权威凭证。没有 `heartbeat_at`、没有 TTL——因为不判活。
- `acquired_at` / `note` 只给人看，程序逻辑不依赖。

> **为什么是“门卫发钥匙让调用方回传”，而不是“调用方自报 runner_id”？**
> 干活的是 LLM 会话，记性不牢：若要求它每次迭代**稳定**报同一个 id，它可能这次“张三”下次“李四”，把自己判成他人而自锁。而门卫打印的 token 天然活在会话上下文里，后续步骤顺手带着走，无需它记住“我是谁”。`--runner-note` 仅作排障标注，不参与归属判定。

### 4.2 `pick` 的新决策表

`pick` 先取一个**短生命周期的流水线锁**（§5）串行化临界区，然后：

| 情形 | 行为 | 返回 |
|---|---|---|
| 无 `in_progress` | 认领最旧 pending，铸造新钥匙 | 退出码 0；`picked:true`，附 `lease_token` |
| 有 `in_progress`，无钥匙文件（历史遗留 / 首次升级） | 视为可接管：补建钥匙并恢复 | 退出码 0；`picked:false, reason:"resumed"`，附新 `lease_token` |
| 有 `in_progress`，调用方带的 `--lease` **匹配** | 恢复（同一执行者带钥匙回来） | 退出码 0；`picked:false, reason:"resumed"`，回传同一 `lease_token` |
| 有 `in_progress`，调用方**未带 / 带错**钥匙 | **拒绝**，且**不碰 worktree**（不再 `wt.create()`） | 退出码 ≠ 0；`picked:false, reason:"blocked_by_active_runner"`，附 `held_by`（note）、`acquired_at` |

关键点：**只有 `blocked_by_active_runner` 退出码非 0**，SKILL 据此干净停下。

> 注意与旧行为的区别：现在“有人占着且你没钥匙”时，`pick` **绝不再回传 worktree、绝不再重建 worktree**——这正是当前 bug 的源头。

### 4.3 手动换人：`takeover`

新增子命令，**由人显式触发**（不是机器自动）：

```
python3 $SKILL/scripts/codoop_tools.py --config <toml> takeover <ticket_id>
```

行为：作废该工单的旧钥匙 → 铸造新钥匙并打印 → 返回 `worktree` 供接手者继续。旧钥匙从此失效（就算原执行者“诈尸”回来带着旧 token，也会被 §4.4 挡下）。

> 语义上等价于“工头拍板：这间房换人”。因为不判活，这是**唯一**能在原钥匙还在时抢到房间的途径，且必须人工执行——符合“判活交给人”的决策。

### 4.4 后续命令的归属校验

`verify / finish / fail` 增加可选 `--lease <token>`：

- 带且匹配：正常执行。
- 带但不匹配现有有效钥匙：**拒绝**（退出码非 0）——说明已被 `takeover` 换人。
- **未带**（老调用方 / agent 忘了）：**放行 + 打印 warning**（向后兼容，见 §6）。真正的并发闸门在 `pick`；这里是加固，不做硬门禁以免升级期打挂现有自动化。

`finish / fail` 成功后**删除钥匙文件**（房间腾空，钥匙收回）。

### 4.5 让工头一眼看清进度：增强 `status`

**先厘清一件事**：一个工单只要还在 `in_progress/` 里，按定义就是“没干完”——干完了 `finish` 会把它移去 `done/`，失败了 `fail` 会移去 `failed/`。所以“有没有干完”不用判断，`in_progress/` 里的**每一个都是没干完的**。工头真正需要的是**“干到哪了、要不要我插手”**。

原则：**机器不下结论，只把现成的事实摊出来给人看**——全是确定性信息，不涉及 AI。

`status` 对每个 `in_progress` 工单增加一块明细：

| 字段 | 含义 | 来源（确定性） |
|---|---|---|
| `held_by` | 房间有没有主、是谁 | 钥匙文件的 `note`（无钥匙则显示“无主，可接管”） |
| `acquired_at` | 什么时候进的门 | 钥匙文件 |
| `todo` | 施工进度，如 `3/8` | 数 `todo.md` 里 `- [x]` / `- [ ]` 的条数 |
| `worktree_dirty` | worktree 里有没有未提交改动 | `git status --porcelain`（有输出=在动） |
| `dev_commits` | dev/<id> 分支上已提交几个 | `git rev-list --count` |
| `worktree_exists` | 房间还在不在 | 路径是否存在 |

示例输出：

```json
{
  "pending": ["ticket_042"],
  "in_progress": [
    {
      "ticket_id": "phase-26-visual-concept-alignment",
      "held_by": "codoop-pending-ticket-executor",
      "acquired_at": "2026-07-08T10:00:00Z",
      "todo": "3/8",
      "worktree_dirty": true,
      "dev_commits": 0,
      "worktree_exists": true
    }
  ],
  "done": [...],
  "failed": [...]
}
```

工头扫一眼就能判断：
- `todo 3/8` + `worktree_dirty` → 有人在干且干了一半，八成是被打断了 → `takeover` 让新工人接着干。
- `todo 0/8` + `worktree_dirty:false` + `held_by` 有值 → 认领了但一直没动 → 可能真跑路了，接管。
- `held_by: 无主` → 历史遗留，直接 pick 就能恢复。

> **兼容性**：`in_progress` 从“字符串数组”变成“对象数组”，是 `status` 输出的破坏性变更。当前只有 SKILL 和测试消费它，同步改即可；`pending/done/failed` 维持字符串数组不变。

---

## 5. 关闭“双重首次 pick”竞态（流水线锁）

`pick` 的临界区（读 in_progress + 移动 pending + 写钥匙）用 `os.open(lockpath, O_CREAT|O_EXCL)` 或 `os.mkdir`（均为原子）实现一把**短持有**互斥锁：

```
<worktree_root>/.codoop-leases/.pipeline.<target_repo_hash>.lock
```

- 只在 `pick` 的簿记期间持有（毫秒级），**不覆盖整个施工过程**。
- 按 `target_repo` 路径 hash 分键，避免多个 target 共享同一 `worktree_root` 时互相串。
- 因为持有极短，pick 进程被 kill 残留死锁的概率极低；实现时对锁文件做一次“进程已不存在则清理”的保底即可（这是 pick 内部毫秒级的锁，**不是** §2 砍掉的工单级判活）。

这样两个并发首次 pick 被串行化，第二个进来时已能看到 `in_progress`，走 §4.2 的“已占用”分支而非抛异常。

---

## 6. 接口变更清单

### 6.1 CLI
- `pick`：新增可选 `--lease <token>`、`--runner-note <str>`。
- `verify / finish / fail`：新增可选 `--lease <token>`。
- 新增子命令：`takeover <ticket_id>`（人工换人）。
- 可选（便于排障）：`lease status` / `lease release <ticket_id>`。

### 6.2 JSON 字段
- `pick` 成功 / 恢复：新增 `lease_token`。
- 被拦：`reason:"blocked_by_active_runner"`，附 `held_by`（note）、`acquired_at`，让 SKILL 能给人看清“被谁占着”。
- `status`：`in_progress` 由字符串数组改为对象数组，每项含 §4.5 的进度明细（破坏性变更，同步改 SKILL + 测试）。

### 6.3 退出码
- `0`：pick 成功 / 可恢复（含带对钥匙的 resume、历史遗留补建）。
- 非 0：`blocked_by_active_runner`（以及 verify 失败等既有非 0 语义）。

### 6.4 配置
- **无新增必需配置。** 钥匙目录默认 `<worktree_root>/.codoop-leases/`。（因为不判活，不需要 `lease_ttl_seconds` 之类。）

---

## 7. 向后兼容 / 迁移

- **历史遗留 `in_progress` 无钥匙**：`pick` 视为可接管并补建钥匙（§4.2 第 2 行），不卡住现有工单。
- **老调用方不带 `--lease`**：`verify/finish/fail` 放行 + warning；`pick` 在有他人有效钥匙时仍会拦（这正是要的）。升级不会把现有 `/loop` 自动化直接打挂。
- 钥匙文件在运行时目录、不进 git，删掉即“忘记归属”，安全降级。

---

## 8. SKILL.md 需要改的地方

1. **Pick 步骤**：
   - 记录 `pick` 返回的 `lease_token`，本次运行的**每个**后续 CLI 调用都带 `--lease <token>`。
   - 若 `reason == "blocked_by_active_runner"`（退出码非 0）：**立即干净停止**，把 `held_by` / `acquired_at` 告诉用户，**不要进 worktree**。
   - 若 `reason` 是 `resumed`：正常恢复。
2. **改写 §Running periodically**：从“The guardrail CLI only lets one in_progress ticket run at a time”改成——“…且对工单持有一把钥匙。只有当前执行者带着钥匙、或人工执行了 `takeover` 时才会恢复；否则自动循环干净停下并报告，等人处理。”
3. **新增“换人”说明**：告诉用户——若某工单卡住（活没干完、又锁着别人的钥匙），先用 `status` 看进度（`held_by` / `todo` / `worktree_dirty`），再决定是否用 `takeover <ticket_id>` 把它交给新执行者。
4. **Guardrails recap 表**：把“钥匙 / 归属仲裁”明确列入“Deterministic → CLI”一侧。

> **一个要接受的副作用**：自动循环碰到一个“锁着、又不是自己”的房间时，会停在那儿报告，**不会自动跳过它去干后面的工单**——必须等人 `takeover` 或清理。这符合“工头定期验收”的工作方式；若日后希望“卡住就自动跳过下一个”，需另议。

---

## 9. 测试计划（扩展 `tests/test_skeleton.py`，无需 AI）

1. `pick` 首次 → 返回 `lease_token`；钥匙文件存在。
2. **双重恢复被拦**：pick A 拿 token；不带 token 再 pick → `blocked_by_active_runner`，退出码非 0，**worktree 未被重建 / 触碰**。
3. **同执行者恢复**：带正确 token 再 pick → `resumed`，同一 token。
4. **手动换人**：`takeover` 后铸造新 token；旧 token 从此在 verify/finish 被拒。
5. **finish/fail 释放**：成功后钥匙文件被删除；之后 `pick` 能认领下一个 pending。
6. **首次 pick 竞态**：并发两个 `pick` 子进程，只有一个 `picked:true`，另一个走“已占用”分支且**不抛异常**。
7. **历史遗留 in_progress 无钥匙**：pick 能补建钥匙并恢复。
8. **verify/finish 带错 token 被拒；不带 token 放行 + warning**（兼容性）。
9. **status 进度明细**：造一个 `in_progress` 工单、`todo.md` 勾若干项、worktree 改一个文件，断言 `status` 回传的对象含正确的 `todo`（如 `2/5`）、`worktree_dirty:true`、`held_by`。

---

## 10. 实现顺序建议

1. **先做 §4.2 的 pick 归属闸门 + §4.3 takeover**：直接解决当前“两个执行者同写一个 worktree”的痛点。
2. 再补 §5 流水线锁，关闭首次 pick 竞态。
3. 最后补 §4.4 后续命令的 `--lease` 加固 + SKILL.md 文档修订。
