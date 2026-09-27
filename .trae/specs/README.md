# 规格驱动开发工作流（Spec-Driven Workflow）

本目录是项目所有需求变更的**唯一事实来源**。任何非平凡的功能开发、重构或跨模块变更，都必须先在本目录走完规格流程，再动业务代码。

## 目录组织：按特性隔离

每个特性/需求一个独立文件夹，端到端内聚三件套：

```text
.trae/specs/
├── README.md                 # 本工作流指南
├── INDEX.md                  # 全部需求的状态索引
├── _templates/               # 三件套模板（新需求从这里复制）
│   ├── spec.md
│   ├── tasks.md
│   └── review.md
└── NNNN-<kebab-case-slug>/    # 一个需求一个文件夹，例如 0001-collision-detection/
    ├── spec.md               # 做什么（需求与验收标准）
    ├── tasks.md              # 怎么做（任务队列、整改问题、完成证据）
    └── review.md             # 独立评审结论（仅 Review 阶段创建/修改）
```

- 编号 `NNNN` 四位递增、全局唯一，名称用英文短横线 slug。
- 一个文件夹 = 一条可独立交付、可独立评审的变更线。
- 文件夹一旦创建不重命名（编号稳定，供分支名、提交信息、ADR 引用）。

## 五个阶段（严格按序）

| 阶段 | 产出 | 写入的文件 | 退出条件 |
|---|---|---|---|
| 1. 规格澄清 Specify | 需求共识 | `spec.md` | 验收标准无歧义，待澄清问题清零或被显式接受 |
| 2. 计划 Plan | 实施队列 | `tasks.md` | 每条 AC 都映射到任务，任务原子、依赖有序 |
| 3. 批准 Approve | 用户明确批准 | — | 用户对 `spec.md` + `tasks.md` 显式同意 |
| 4. 实施 Implement | 可运行代码 + 自证 | `tasks.md`（业务代码在 `src/`） | 队列清空且每个任务有 Completion Evidence |
| 5. 评审 Review | 独立评审结论 | `review.md` | 独立评审 `pass`（唯一成功出口） |

### 阶段门禁（硬规则）

1. `spec.md`、`tasks.md` 必须先于批准和实施存在。
2. 未获明确批准，不得开始实施。批准若改变需求，回到 Specify 并重生成受影响的计划。
3. `review.md` **只能在 Review 阶段创建或修改**；Implement 阶段它只读，即使已存在。
4. 评审失败（fail）必须把每条可执行发现落成 `tasks.md` 中的 `pending` 整改 Issue，然后才允许选任务干活。
5. 整改清空后，必须用**全新上下文**启动新一轮评审，不允许实施者自验充当终审。

## 验收词汇：rule 与 rubric

每条验收标准（AC）和测试需求（TR）有且仅有一种类型：

| 类型 | 含义 | 必填形态 |
|---|---|---|
| `rule` | 客观二值条件（过/不过） | 可观察的通过条件 + 证据来源（命令、输出、产物） |
| `rubric` | 质量维度评分 | 维度、1-5 量表、1/3/5 锚点、通过阈值（通常 >= 4）、证据来源 |

- 验证时**先 rule 后 rubric**。
- rubric 必须记录：得分、理由、证据，三者缺一不可。

## 任务状态机

状态只记录在任务的 `Status` 字段中，标题里禁止出现状态标记。

```text
pending ──▶ in_progress ──▶ completed
                │              ▲
                ├──▶ blocked ──┘（解除后回 in_progress）
                └──▶ cancelled（必须有用户批准记录）
```

| 状态 | 附加字段 |
|---|---|
| `pending` | 无 |
| `in_progress` | 无（恢复时清除陈旧的阻塞字段） |
| `blocked` | `Blocked By` + `Unblock Condition` |
| `completed` | `Completion Evidence`（rule 结果；rubric 得分/理由/证据） |
| `cancelled` | `Cancellation Reason` + `Cancellation Approved By` |

本地自验不通过时保持 `in_progress`，**没有 failed 状态**。

## 队列清空与完成定义（DoD）

队列清空 = 全部任务/问题 ∈ {completed, cancelled}，且无 pending/in_progress/blocked，且每个 cancelled 有用户批准且不损害 AC 覆盖。

整个需求完成还必须满足：

```text
所有必需评审检查点已检查
每条 rule 有通过证据
每条 rubric 达阈值并有理由和证据
最近一轮 Review 结果 == pass
不存在遗留的 actionable 发现
```

## 新需求开工步骤

```bash
# 1. 取号（查 INDEX.md 下一个编号），创建特性目录并复制模板
cp -R .trae/specs/_templates .trae/specs/0001-your-slug
# 2. 填写 spec.md（Specify）
# 3. 填写 tasks.md（Plan），通知用户批准（Approve）
# 4. 批准后建分支实施：git switch -c spec/0001-your-slug
# 5. 队列清空后进入 Review，由全新上下文生成 review.md
# 6. 在 INDEX.md 登记结果
```

## 豁免

纯文案订正、依赖补丁、不改行为的格式化等琐碎变更可免规格流程，但需在提交信息中注明 `chore: ...`；拿不准时按有规格处理。
