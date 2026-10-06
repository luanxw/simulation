# 状态卡 · NNNN-<slug>

> 断点恢复的唯一权威。阶段切换或任务状态变化时**立即**更新本卡；中断后新 agent 按工作流 README 的"恢复协议"读本卡续跑。保持一屏以内。

- 编号：NNNN
- 类型：fix
- Slug：<slug>
- 分支：fix/NNNN-<slug>
- 评审者指定：默认（全新 general_purpose_task 子代理，只读）；用户指定其他 agent 时改写本行（如 browser_use / search）
- 当前阶段：Specify            <!-- Specify | Plan | Approve | Implement | Review | Done -->
- 下一动作：[谁在什么时候做什么，如"进入 S4（S3 已在常驻授权下自动批准）"]
- 当前任务：Task 1（pending）   <!-- 无则写 None -->
- 更新时间：YYYY-MM-DD
- 交接备注：
  - [给下一位 agent 的关键上下文：复现要点、已试方案、坑；没有写"无"]

## 阶段门禁记录（严格按序；Exit 未全部勾选，禁止进入下一阶段）

- [ ] **S1 Specify** ｜ 完成时间：—
  - Exit：spec.md 存在且含复现步骤与影响范围；AC 以回归 rule 为主、类型合法；待澄清问题清零（根因允许 Task 1 回填，但复现路径必须成立）
- [ ] **S2 Plan** ｜ 完成时间：—
  - Exit：tasks.md 含"定位 → 修复+回归 → 自证"主线；每条 AC 至少映射一个任务；每任务至少一条 TR
- [ ] **S3 Approve** ｜ 完成时间：—
  - Exit：常驻授权下自动批准并留痕（记录授权依据与日期）；用户可随时否决→回退对应阶段
- [ ] **S4 Implement** ｜ 完成时间：—
  - Exit：根因已回填；所有任务 ∈ completed/cancelled 且有 Completion Evidence；回归测试红绿成立；pytest 与 ruff 全绿
- [ ] **S5 Review** ｜ 完成时间：—
  - Exit：review.md 最近一轮 Result = pass；每条 AC 有独立证据；INDEX 已登记最终状态
- [ ] **S6 Deliver** ｜ 完成时间：—
  - Exit：S5 最近一轮 pass；review/state/INDEX 终态已自动收尾提交、git status 干净；未 push（等待用户当次确认）
- [ ] **S7 Merge** ｜ 完成时间：—
  - Exit：用户当次确认后 push 成功；Merge 请求已创建（gh 优先 / compare 链接兜底）并把链接返回用户、记录于此：____；合并按钮由用户自行点击
