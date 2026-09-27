# 规格驱动开发工作流（Spec-Driven Workflow）

本目录是项目所有需求变更的**唯一事实来源**。用户只需说一句话（"我要……"或"帮我修复/优化……"），AI 代理按"第 0 步智能受理"自动开工，并在**项目常驻授权**下一路自动走完六阶段；除 `git push` 外不停顿等待确认。

## 目录组织：按特性隔离 + 类型双轨

```text
.trae/specs/
├── README.md                  # 本工作流指南（权威细则）
├── INDEX.md                   # 全部变更的状态索引（取号看这里）
├── _templates/
│   ├── feature/               # 新需求交付模板（完整规格）
│   │   ├── spec.md
│   │   ├── tasks.md
│   │   ├── review.md          # 模板；特性目录中仅 S5 才实例化
│   │   └── state.md           # 断点状态卡
│   └── fix/                   # 问题修复模板（轻量：复现/根因/回归）
│       ├── spec.md
│       ├── tasks.md
│       ├── review.md
│       └── state.md
└── NNNN-<slug>/               # 一条变更一个文件夹
    ├── spec.md                # 做什么
    ├── tasks.md               # 怎么做 + 完成证据
    ├── review.md              # 独立评审（仅 S5 创建/修改）
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
- **歧义处理**：一句话同时像优化又像新能力、或无法判断影响面时，只向用户**询问一次**，确认后继续。

### 0.2 受理四步（自动执行）

```bash
# 1. 取号：查 INDEX.md 已有最大编号 +1；从用户输入提炼英文 kebab-case slug

# 2. 复制对应类型的三件工作文件（review.md 留到 S5 才实例化）
mkdir -p .trae/specs/0002-your-slug
cp .trae/specs/_templates/fix/{spec,tasks,state}.md .trae/specs/0002-your-slug/

# 3. 一律从最新 develop 创建工作分支（不允许从别的工作分支拉；例外须用户明确批准并在 state.md 留痕）
git switch develop
git switch -c fix/0002-your-slug      # 新需求：feature/NNNN-<slug>

# 4. 初始化 state.md（含评审者指定字段），在 INDEX.md 登记新行，然后进入 S1
```

- `develop` 不存在时先由 main 基线创建 `git branch develop`。
- 受理完成标志：三件套就位、当前位于工作分支、state.md 与 INDEX 已登记。

---

## 常驻授权与唯一确认点

本仓库适用**项目级常驻授权**（用户 2026-09-27 授予，见 ADR-0003）：

| 动作 | 是否需要逐次确认 |
|---|---|
| 工作区内新建/修改/删除文件、跑测试、本地提交 commit、建本地分支、阶段推进 | **不需要**，直接执行并留证据 |
| 需求方向（S3 规格与计划批准） | **不需要停顿等待**：S3 自动批准，代理在对话中给出 spec/tasks 摘要即可继续 |
| `git push`、创建 MR/PR 等任何**远端写操作** | **必须**取得用户当次明确确认；未确认一律不执行 |
| force-push、`reset --hard`、删除分支、工作区外文件 | 始终禁止（即使用户措辞随意，也要二次确认命令本身） |

**用户的随时否决权**：自动推进不等于失去控制——用户可随时中断或否决；一旦否决，立即停止当前动作并**回退到对应阶段**（如否决需求方向回 S1/S2，否决评审结论则发起新一轮 S5），在 state.md 交接备注中记录否决内容。

---

## 六个阶段：严格串行门禁

```text
S1 Specify → S2 Plan → S3 Approve(自动) → S4 Implement → S5 Review → S6 Deliver → Done
```

**铁律：上一阶段 Exit 清单未全部勾选并写入 state.md，不得进入下一阶段。**（S3 在常驻授权下为自动批准，但勾选与留痕动作不能省。）

### S1 Specify 规格澄清
- **Entry**：Intake 已完成。
- **做什么**：调研代码、澄清歧义（歧义只问一次），只定义"做什么"，填写 `spec.md`（fix 版必须给出可复现步骤；根因允许留到 Implement Task 1 回填）。
- **Exit**：spec.md 存在；每条 AC 类型仅为 `rule`/`rubric` 且写明证据来源；待澄清问题清零或被显式接受为假设；state.md 推进。

### S2 Plan 计划
- **Entry**：S1 已勾选。
- **做什么**：把每条 AC 映射为原子、依赖有序的垂直切片任务，每任务至少一条 TR，填写 `tasks.md`。
- **Exit**：每条 AC 至少被一个任务覆盖；任务有优先级与 Depends On；fix 保持"定位→修复+回归→自证"主线；state.md 推进。

### S3 Approve 批准（常驻授权下自动）
- **Entry**：S2 已勾选。
- **做什么**：代理自检 spec/tasks 完整性（AC 合法、TR 齐全、无未决歧义），在**对话中输出规格与计划摘要**（标题、范围、任务数、关键取舍），然后**不停顿直接进入 S4**；在 state.md 记录"自动批准 + 授权依据 + 日期"。
- **用户控制方式**：看到摘要后可随时打断/否决 → 回 S1/S2 修订后重新自动通过；用户明确要求恢复人工批准时，在 ADR 中修订本授权。
- **Exit**：自检通过、摘要已呈现、state.md 已留痕。

### S4 Implement 实施
- **Entry**：S3 已勾选。
- **做什么**：一次只推进一个最高优先级的就绪任务：置 in_progress → 实施 → 自验全部 TR → 写 Completion Evidence → 置 completed；同步更新 state.md。阻塞写 `Blocked By`/`Unblock Condition` 并通知用户。实施期可随时做本地 commit。
- **Exit**：所有任务 ∈ {completed, cancelled}，无 pending/in_progress/blocked；completed 有 Completion Evidence（rubric 含得分/理由/证据）；cancelled 有用户批准；`pytest`、`ruff check .` 全绿；state.md 推进到 Review。

### S5 Review 独立评审（评审者可选）
- **Entry**：S4 已勾选，队列已清空。
- **评审者选择**：
  - 默认：派一个**未参与实施的全新上下文** general_purpose_task 子代理，只读、只出报告；
  - 用户可在受理时起至 S5 前**预先指定**评审 agent，写入 state.md 的"评审者指定"字段，例如：
    - `browser_use`：需求含页面交互/前端渲染，需要真实浏览器点按、截图验证；
    - `search`：改动跨多模块/依赖外部资料，需要大范围检索式核查；
    - 后续如接入安全审查等专门 agent 同理登记。
  - **独立性三不变**：无论哪种 agent，都必须满足 ①未参与本需求实施 ②评审期间只读不改 ③出具带 Result（pass/fail/blocked）的 R 轮次报告。
- **做什么**：按 review.md 检查点独立取证；pass 进 S6；fail 把每条 actionable 发现落成 tasks.md 的 pending Issue 回 S4；blocked 记录环境阻塞。整改/解阻后必须以**全新评审者**开启新一轮（R2、R3……），并沿用或重新指定 agent。
- **Exit**：最近一轮 Result = pass；每检查点通过、每条 AC 有独立证据、无 actionable 发现；state.md 推进到 Deliver。

### S6 Deliver 交付（自动提交，推送前确认）
- **Entry**：S5 最近一轮 pass。
- **做什么（全部自动，无需确认）**：
  1. 把评审与收尾产物（review.md、state.md、INDEX.md 终态、整改变更）全部提交：Conventional Commit，如 `docs(NNNN): record Rn pass and deliver`；
  2. 确认 `git status` 干净、state.md 当前阶段置 Done 且 S1-S6 全勾选、INDEX 登记 Done 与最终评审轮次；
  3. 输出交付摘要（提交链、评审结论、测试结果）。
- **确认点**：S6 **只做本地 commit，不 push**。需要推送/建 MR 时，代理明确询问并等待用户**当次**确认后才执行；合并到 develop/main 的时机同样由用户决定。
- **Exit（= 整个需求完成）**：S1-S6 全勾选；工作区干净；INDEX = Done；无遗留 actionable 发现。

### 文件所有权

| 文件 | 可写阶段 |
|---|---|
| `spec.md` | S1；需求变更经否决回退后修订 |
| `tasks.md` | S2、S4 |
| `review.md` | **仅 S5**，评审 agent 创建/修改；S4 及之前不存在（模板除外） |
| `state.md` | 任何阶段据实更新；不得用它跳过门禁 |
| `src/`、`tests/` | 仅 S4 |
| 本地 commit | S4 可随时；S6 强制收尾提交。push 永远需要当次确认 |

---

## 断点恢复协议（换会话/换 agent 无损续跑）

接手本仓库的任何 AI 代理，在继续任何未完成变更前**必须先执行**：

1. **查索引**：读 `INDEX.md`，找阶段不是 Done 的条目（多条按编号确认）。
2. **读状态卡**：打开 `state.md`，获取"当前阶段 / 下一动作 / 当前任务 / 评审者指定 / 交接备注"。
3. **一致性校验**：对照门禁记录检查实际产物；矛盾时**以产物与 git 提交为准**，修正 state.md 并在交接备注记录修正。
4. **从断点续跑**：严格按"下一动作"继续；禁止重走已勾选阶段、跳过未勾选阶段；进入 S5 前确认评审者指定字段。
5. **每次推进后写回**：任务/阶段变化立即更新 state.md 并尽快提交（未提交改动在会话边界可能丢失，真相以 git 为准）。

state.md 保持一屏以内；细节证据放 tasks.md / review.md。

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

## 完成定义（DoD）

```text
所有任务/问题 ∈ {completed, 用户批准的 cancelled}
S1-S6 门禁在 state.md 全部勾选且最近一轮 Review == pass
每条 rule 有通过证据；每条 rubric 达阈值并有理由和证据
pytest 全绿、ruff check . 无告警；S6 已收尾提交且 git status 干净
INDEX 登记 Done；无遗留 actionable 发现
push/合并由用户当次确认后另行执行
```

## 豁免

纯文档订正、依赖补丁、不改行为的格式化等琐碎变更可免六阶段，提交信息注明 `chore:`（仍自动提交、不 push）；拿不准时按需要规格处理。
