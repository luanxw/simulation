# 状态卡 · NNNN-<slug>

> 断点恢复的唯一权威。阶段切换或任务状态变化时**立即**更新本卡；中断后新 agent 按工作流 README 的"恢复协议"读本卡续跑。保持一屏以内。

- 编号：NNNN
- 类型：feature
- Slug：<slug>
- 分支：feature/NNNN-<slug>
- 当前阶段：Specify            <!-- Specify | Plan | Approve | Implement | Review | Done -->
- 下一动作：[谁在什么时候做什么，如"等待用户批准 spec.md 与 tasks.md"]
- 当前任务：Task 1（pending）   <!-- 无则写 None -->
- 更新时间：YYYY-MM-DD
- 交接备注：
  - [给下一位 agent 的关键上下文：已做决策、坑、未决问题；没有写"无"]

## 阶段门禁记录（严格按序；Exit 未全部勾选，禁止进入下一阶段）

- [ ] **S1 Specify** ｜ 完成时间：—
  - Exit：spec.md 存在；每条 AC 类型仅为 rule/rubric 且有证据来源；待澄清问题清零或被显式接受
- [ ] **S2 Plan** ｜ 完成时间：—
  - Exit：tasks.md 存在；每条 AC 至少映射一个任务；任务原子、依赖有序、每任务至少一条 TR
- [ ] **S3 Approve** ｜ 完成时间：—
  - Exit：用户对 spec.md + tasks.md 明确批准（在此记录批准方式与日期）
- [ ] **S4 Implement** ｜ 完成时间：—
  - Exit：所有任务 ∈ completed/cancelled；completed 均有 Completion Evidence；blocked 为 0；pytest 与 ruff 全绿
- [ ] **S5 Review** ｜ 完成时间：—
  - Exit：review.md 最近一轮 Result = pass；每条 AC 有独立证据；INDEX 已登记最终状态
