# 状态卡 · 0001-workflow-resume-and-intake

> 断点恢复的唯一权威。阶段切换或任务状态变化时立即更新本卡；保持一屏以内。

- 编号：0001
- 类型：fix
- Slug：workflow-resume-and-intake
- 分支：fix/0001-workflow-resume-and-intake（注：本需求创建于双轨机制落地前，经用户批准沿用该分支名，等价于新规则的 fix/0001）
- 当前阶段：Done
- 下一动作：None（0001 全部完成；后续由人工决定何时把 fix/0001 合入 develop/main，工作流不自动合并）
- 当前任务：None（Task 1-6 + Issue I-1 全部 completed）
- 更新时间：2026-09-27
- 交接备注：
  - 本需求为"犬食其言"：0001 目录在新机制建成前手动创建，无历史包袱；基线提交 f26031b 已在 main/develop/fix 三分支同点
  - Task 1-4 已完成并有真实命令证据（见 tasks.md）；Task 5 完成 ADR-0002、本状态卡与 INDEX 登记
  - 坑：对同一文件并行多处 Edit 会互相覆盖；且工具编辑层与磁盘曾出现瞬时不一致（R1 的 F-1 即由此误读），状态真相以 git 提交为准
  - 提交链：f26031b 基线 → 6ddd5c4 实施 → 6163f3a S4 台账 → 78fb747 R1 fail + I-1 登记 → 本次 I-1 整改

## 阶段门禁记录（严格按序；Exit 未全部勾选，禁止进入下一阶段）

- [x] **S1 Specify** ｜ 完成时间：2026-09-27
  - Exit：spec.md 存在；6 条 AC（AC-1~AC-5 rule，AC-6 rubric）类型合法且有证据来源；3 项假设经用户批准视为接受
- [x] **S2 Plan** ｜ 完成时间：2026-09-27
  - Exit：tasks.md 6 个任务依赖有序（Task 1→6），每条 AC 均有任务覆盖，每任务至少一条 TR
- [x] **S3 Approve** ｜ 完成时间：2026-09-27
  - Exit：用户通过 NotifyUser 明确批准 spec.md 与 tasks.md（含首次基线提交授权）
- [x] **S4 Implement** ｜ 完成时间：2026-09-27（R1 fail 后整改 I-1，二次满足）
  - Exit：Task 1-6 与 Issue I-1 全部 completed 且有 Completion Evidence；pytest 1 passed；零代码改动 ruff 面无变化；state/INDEX/tasks/git 四方一致；实施 6ddd5c4、整改见本次提交
- [x] **S5 Review** ｜ 完成时间：2026-09-27
  - Exit：review.md 最近一轮 R2 由全新上下文出具且 Result = pass；每条 AC 有独立证据；INDEX 已登记 Done / R2 pass
