# 规格驱动开发工作流（Spec-Driven Workflow）

本目录是项目所有需求变更的**唯一事实来源**。用户只需说一句话（"我要……"或"帮我修复/优化……"），AI 代理按"第 0 步智能受理"自动开工；任何非平凡变更都必须走完五阶段门禁才允许交付。

## 目录组织：按特性隔离 + 类型双轨

```text
.trae/specs/
├── README.md                  # 本工作流指南（权威细则）
├── INDEX.md                   # 全部变更的状态索引（取号看这里）
├── _templates/
│   ├── feature/               # 新需求交付模板（完整规格）
│   │   ├── spec.md
│   │   ├── tasks.md
│   │   ├── review.md
│   │   └── state.md           # 断点状态卡
│   └── fix/                   # 问题修复模板（轻量：复现/根因/回归）
│       ├── spec.md
│       ├── tasks.md
│       ├── review.md
│       └── state.md
└── NNNN-<slug>/               # 一条变更一个文件夹
    ├── spec.md                # 做什么
    ├── tasks.md               # 怎么做 + 完成证据
    ├── review.md              # 独立评审（仅 Review 阶段可写）
    └── state.md               # 断点状态卡（进度的唯一权威）
```

- `NNNN` 四位递增、feature/fix 共用、永不复用；slug 用英文 kebab-case。
- 文件夹一旦创建不重命名；编号供分支名、提交信息、ADR 长期引用。

---

## 第 0 步：智能受理（Intake）

用户给出一句话需求时，AI 代理**自动**完成分类、取号、复制模板、建分支，不要求用户手动操作。

### 0.1 分类规则

| 判定 | 触发条件 |
|---|---|
| **fix（问题修复）** | 输入命中修复类关键词：修复、优化、bug、报错、错误、异常、崩溃、挂了、故障、不工作、不行、失败、缺陷、慢、卡、超时、回归（含英文 bug/fix/error/regression/refactor） |
| **feature（新需求交付）** | 不命中上述关键词的一切新增能力、新模块、行为增强 |

判定样例：

- "修复碰撞检测穿模的问题" → fix
- "优化一下仿真主循环的帧率" → fix
- "给仿真器加一个暂停按钮"（无修复类关键词）→ feature
- **歧义处理**：一句话同时像优化又像新能力、或无法判断影响面时，只向用户**询问一次**（"这是问题修复还是新功能？"），确认后继续，不反复追问。

### 0.2 受理四步（自动执行）

```bash
# 1. 取号：查 INDEX.md 已有最大编号 +1；从用户输入提炼英文 kebab-case slug
#    例："修复碰撞检测穿模" → 编号 0002，slug collision-penetration-fix

# 2. 复制对应类型模板四件套
cp -R .trae/specs/_templates/fix .trae/specs/0002-collision-penetration-fix
#   feature 同理：cp -R .trae/specs/_templates/feature .trae/specs/0003-xxx

# 3. 一律从最新 develop 创建工作分支（不允许从别的工作分支拉）
git switch develop
git pull --ff-only            # 有远端且需要同步时；纯本地仓库跳过
git switch -c fix/0002-collision-penetration-fix
#   新需求分支名：feature/NNNN-<slug>；修复分支名：fix/NNNN-<slug>

# 4. 初始化 state.md（编号/类型/slug/分支/更新时间），在 INDEX.md 登记新行
#    然后进入 S1 Specify
```

- `develop` 分支不存在时（仅仓库初始化当天可能发生）：先由 main 基线创建 `git branch develop`，再执行第 3 步。
- 受理完成的标志：特性目录四件套就位、当前位于对应工作分支、state.md 与 INDEX 已登记。

---

## 五个阶段：严格串行门禁

```text
S1 Specify → S2 Plan → S3 Approve → S4 Implement → S5 Review → Done
```

**铁律：上一阶段 Exit 清单未全部勾选并写入 state.md，不得进入下一阶段。** 每个阶段的进入条件不满足时，回到应处的阶段。

### S1 Specify 规格澄清
- **Entry**：Intake 已完成（四件套在、分支对、INDEX 已登记）。
- **做什么**：调研代码、澄清歧义，只定义"做什么"，填写 `spec.md`（fix 版必须给出可复现步骤；根因允许留到 Implement Task 1 回填）。
- **Exit（全部满足才能勾 S1）**：
  - spec.md 存在；每条 AC 类型仅为 `rule` 或 `rubric` 且写明证据来源；
  - 待澄清问题清零，或被用户显式接受为假设；
  - state.md 更新：当前阶段→Plan，下一动作、当前任务、更新时间、交接备注已填。

### S2 Plan 计划
- **Entry**：state.md 中 S1 已勾选。
- **做什么**：把每条 AC 映射为原子、依赖有序的垂直切片任务，每任务至少一条 TR，填写 `tasks.md`。
- **Exit**：每条 AC 至少被一个任务覆盖；任务有优先级与 Depends On；fix 类保持"定位→修复+回归→自证"主线；state.md 推进到 Approve。

### S3 Approve 批准
- **Entry**：S2 已勾选。
- **做什么**：把 spec.md 与 tasks.md 一并提交用户审阅，**等待明确批准**；不批准或要求改需求时回到 S1/S2 修订，重新提请批准。
- **Exit**：用户明确批准；在 state.md 的 S3 记录批准方式与日期；推进到 Implement。

### S4 Implement 实施
- **Entry**：S3 已勾选（未批准不得动 `src/`、`tests/`）。
- **做什么**：一次只推进一个最高优先级的就绪任务：置 in_progress → 实施 → 自验全部 TR → 写 Completion Evidence → 置 completed；同步更新 state.md 的当前任务/交接备注。阻塞写 `Blocked By` / `Unblock Condition` 并通知用户。
- **Exit**：所有任务 ∈ {completed, cancelled}，无 pending/in_progress/blocked；每个 completed 有 Completion Evidence（rubric 含得分、理由、证据）；每个 cancelled 有用户批准；`pytest`、`ruff check .` 全绿；state.md 推进到 Review。

### S5 Review 独立评审
- **Entry**：S4 已勾选，队列已清空。
- **做什么**：由**未参与实施的全新上下文**按 review.md 检查点独立取证；pass 收尾，fail 把每条 actionable 发现落成 tasks.md 的 pending Issue 并回到 S4，blocked 记录环境阻塞并请求解决。整改/解阻后必须以**全新评审者**开启新一轮（R2、R3……）。
- **Exit（= 整个需求完成）**：最近一轮 Result = pass；每个检查点通过、每条 AC 有独立证据、无 actionable 发现；INDEX 登记 Done 与评审结果；state.md 当前阶段→Done。

### 文件所有权

| 文件 | 可写阶段 |
|---|---|
| `spec.md` | S1；批准后的需求变更需重走 S3 |
| `tasks.md` | S2、S4 |
| `review.md` | **仅 S5**，全新评审上下文；S4 期间只读 |
| `state.md` | 任何阶段，但只能在阶段切换/任务状态变化时据实更新，不得用它跳过门禁 |
| `src/`、`tests/` | 仅 S4 |

---

## 断点恢复协议（换会话/换 agent 无损续跑）

接手本仓库的任何 AI 代理，在继续任何未完成变更前**必须先执行**：

1. **查索引**：读 `INDEX.md`，找到阶段不是 Done 的条目（多条时按编号从小到大确认）。
2. **读状态卡**：打开该目录 `state.md`，获取"当前阶段 / 下一动作 / 当前任务 / 交接备注"。
3. **一致性校验**：对照门禁记录检查实际产物（如 S1 勾选则 spec.md 必须存在且 AC 合法；S4 进行中则 tasks.md 状态与 state.md 当前任务一致）。
   - 发现矛盾时：**以产物为准**，修正 state.md 后继续，并在交接备注中记录修正。
4. **从断点续跑**：严格按"下一动作"继续；禁止重走已勾选阶段，禁止跳过未勾选阶段。
5. **每次推进后写回**：任务状态变化或阶段切换时，立即更新 state.md（含更新时间），保证下次可恢复。

state.md 保持一屏以内；细节证据放 tasks.md / review.md，状态卡只放指针与结论。

---

## 验证词汇：rule 与 rubric

每条 AC/TR 有且仅有一种类型；先验 rule 后验 rubric。

| 类型 | 含义 | 必填形态 |
|---|---|---|
| `rule` | 客观二值条件 | 可观察通过条件 + 证据来源（命令输出、产物、日志） |
| `rubric` | 质量维度评分 | 维度、1-5 量表、1/3/5 锚点、阈值（通常 ≥4）、证据来源；须记录得分+理由+证据 |

## 任务状态机

```text
pending ──▶ in_progress ──▶ completed
                ├──▶ blocked   （须写 Blocked By / Unblock Condition）
                └──▶ cancelled （须写用户批准证据）
```

状态只写在 `Status` 字段，标题不嵌状态；自验不通过保持 `in_progress`，没有 failed 状态。

## 队列清空与完成定义（DoD）

```text
所有任务/问题 ∈ {completed, 用户批准的 cancelled}
S1-S5 门禁在 state.md 全部勾选且最近一轮 Review == pass
每条 rule 有通过证据；每条 rubric 达阈值并有理由和证据
pytest 全绿、ruff check . 无告警；INDEX 已登记 Done
无遗留 actionable 发现
```

## 豁免

纯文档订正、依赖补丁、不改行为的格式化等琐碎变更可免五阶段，提交信息注明 `chore:`；拿不准时按需要规格处理。
