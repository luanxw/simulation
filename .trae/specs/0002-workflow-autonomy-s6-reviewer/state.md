# 状态卡 · 0002-workflow-autonomy-s6-reviewer

> 断点恢复的唯一权威。阶段切换或任务状态变化时立即更新本卡；保持一屏以内。

- 编号：0002
- 类型：fix
- Slug：workflow-autonomy-s6-reviewer
- 分支：fix/0001-workflow-resume-and-intake（**例外**：用户 2026-09-27 明确批准沿用，不新建分支；正常规则仍为一律从 develop 切 fix/feature 分支）
- 评审者指定：默认（全新 general_purpose_task 子代理，只读）；用户未指定其他 agent
- 当前阶段：Implement
- 下一动作：执行 Task 6（S7 建 MR 条款落地），完成后进入新 R1 评审
- 当前任务：Task 6（in_progress）
- 更新时间：2026-09-27
- 交接备注：
  - 2026-09-28 需求变更：新增 push 成功后创建 MR 并返回链接（原 S6 Deliver 不 push；新增 S7 Merge 等待用户确认）
  - 用户已授予项目级常驻授权：工作区内增改免逐次确认，S3 自动批准；唯一强制确认点是 push
  - 受理时四个边界已一次问清（免确认含 S3／分支例外／S6 自动提交不 push／评审者可预先指定）
  - 0002 改的是工作流自身文件，全部为 Markdown；与 0001 同分支连续落地，提交 scope 用 docs(0002)

## 阶段门禁记录（严格按序；Exit 未全部勾选，禁止进入下一阶段）

- [x] **S1 Specify** ｜ 完成时间：2026-09-27
  - Exit：spec.md 含复现步骤/影响范围/根因；7 条 AC（AC-1~AC-6 rule，AC-7 rubric）类型合法；四个待澄清问题已清零
- [x] **S2 Plan** ｜ 完成时间：2026-09-27
  - Exit：tasks.md 含 5 个任务，定位（已在 spec 根因）→ 修复（Task 2-4）→ 自证（Task 5）主线；每条 AC 有任务覆盖
- [x] **S3 Approve** ｜ 完成时间：2026-09-27（**自动批准**）
  - Exit：依据用户常驻授权（"增改不需要确认，连 S3 也免"，2026-09-27）自动通过；spec/tasks 已在对话中呈现，用户保留随时否决权
- [ ] **S4 Implement（修订中）** ｜ 完成时间：—
  - Exit：Task 1-6 全部 completed 且有 Completion Evidence；pytest 全绿；七阶段改造 grep 项通过
- [x] **S3 Approve（修订重批）** ｜ 完成时间：2026-09-28（自动批准）
  - Exit：用户常驻授权下自动通过；spec/tasks 已修订补充 AC-8/S7/远端信息
- [ ] **S4 Implement（修订）** ｜ 完成时间：—
  - Exit：Task 1-6 全部 completed 且有 Completion Evidence；pytest 全绿；七阶段改造 grep 项通过
- [ ] **S5 Review（新 R1）** ｜ 完成时间：—
  - Exit：review.md 由全新上下文出具，按新 CP-1~CP-8 检查 AC-1~8；最近一轮 Result = pass
- [ ] **S6 Deliver** ｜ 完成时间：—
  - Exit：全部收尾变更自动 commit、git status 干净、state/INDEX 置 Done；**不 push**（等待用户当次确认）
- [ ] **S7 Merge** ｜ 完成时间：—
  - Exit：用户当次确认后 push；成功后创建 Merge 请求并把链接返回给用户；MR 合并按钮由用户自行点击
