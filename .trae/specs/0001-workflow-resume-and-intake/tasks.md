# 工作流断点恢复、严格门禁与智能受理 - 实施计划

## Task 1：建立 git 基线并从 develop 建工作分支
- **Status**：`completed`
- **Completion Evidence**：
  - TR-1.1（rule）通过：基线提交 f26031b 在 main；`git branch` 含 develop、fix/0001-workflow-resume-and-intake、main；`git log --decorate` 显示三者同指 f26031b，工作分支父提交与 develop 一致；未 push
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 将现有骨架（含本规格）首次提交到 main（master）：`chore: bootstrap spec-driven workflow scaffold`
  - 从基线创建并推送本地 `develop` 分支（不 push 远端）
  - 从 develop 创建本需求工作分支 `fix/0001-workflow-resume-and-intake`（本需求按新规则含"优化"属修复类，犬食其言）
- **Acceptance Criteria Addressed**：AC-5
- **Test Requirements**：
  - `rule` TR-1.1：`git branch` 输出同时包含 main（或 master）、develop、fix/0001 三个分支，且 fix/0001 的父提交与 develop 一致；证据为 `git branch` 与 `git log --oneline` 输出
- **Notes**：首次提交为搭建工作流基础设施所必需，批准本计划即视为批准该提交；不会执行任何 push

## Task 2：重组模板为 feature/fix 双轨，四件套含状态卡
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 删除旧扁平模板 `.trae/specs/_templates/{spec,tasks,review}.md`
  - 新建 `.trae/specs/_templates/feature/` 与 `.trae/specs/_templates/fix/`，各含 `spec.md`、`tasks.md`、`review.md`、`state.md`
  - feature 三件套沿用现有完整模板并加入状态卡引用；fix 版轻量：spec 含问题现象/复现步骤/期望vs实际/影响范围/根因/修复方案，AC 以回归 rule 为主；tasks 含根因定位→修复→回归测试
  - `state.md` 为断点状态卡：编号、类型、slug、当前阶段、下一动作、当前任务、更新时间、交接备注、S1-S5 门禁勾选区（每项含完成时间与证据）
- **Acceptance Criteria Addressed**：AC-1、AC-4
- **Test Requirements**：
  - `rule` TR-2.1：两套模板目录均存在且各含 4 个文件；证据为 `find .trae/specs/_templates -type f | sort`
  - `rule` TR-2.2：两个 state.md 均含 FR-1 全部必填字段（编号/类型/slug/当前阶段/下一动作/当前任务/更新时间/交接备注/S1-S5 勾选区）；证据为 grep 字段清单
  - `rule` TR-2.3：fix/spec.md 含复现步骤与根因章节，fix/tasks.md 含回归测试任务；证据为文件内容

## Task 3：更新工作流指南（智能受理 + 严格门禁 + 恢复协议）
- **Status**：`completed`
- **Completion Evidence**：
  - TR-3.1（rule）通过：逐项 grep 命中智能受理/关键词/判定样例/受理四步/git switch develop/S1-S5/Entry(5)/Exit(6)/断点恢复协议/feature|fix 新前缀/询问一次/下一动作，全部 ≥1
  - TR-3.2（rule）通过：grep 旧扁平模板路径与旧前缀 spec/NNNN 均无输出，无残留引用
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - 更新 `.trae/specs/README.md`：
    - 新增"第 0 步 智能受理 Intake"：关键词集合（修复/优化/bug/报错/异常/崩溃/故障/不工作/失败/缺陷/慢/卡/回归等）、默认规则（命中→fix，否则 feature）、歧义只问一次、每类至少一个样例
    - 受理四步命令序列：查 INDEX 取号 → 生成英文 slug → 复制对应模板 → `git switch develop`（必要时先同步）→ `git switch -c feature|fix/NNNN-slug`
    - 五阶段各自的 Entry/Exit 门禁清单，明示"Exit 未全部勾选不得进入下一阶段"
    - 断点恢复协议：查 INDEX → 读 state.md → 校验产物/门禁一致性（矛盾以产物为准并修正状态）→ 从"下一动作"续跑，禁止重走已完成阶段；更新状态卡的时机（每次阶段切换与任务状态变化）
    - 更新目录结构、模板路径、分支前缀（spec/ 改 feature|fix/）
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**：
  - `rule` TR-3.1：README 含 Intake、关键词集合、三类判定样例、四步命令、五阶段 Entry/Exit、恢复协议、新分支前缀；证据为逐项 grep 章节标题与关键词
  - `rule` TR-3.2：全文无残留旧路径 `_templates/spec.md` 式引用与旧前缀 `spec/NNNN`（本规格目录名除外的历史不可变引用说明）；证据为 grep

## Task 4：更新 INDEX、AGENTS.md、根 README
- **Status**：`completed`
- **Completion Evidence**：
  - TR-4.1（rule）通过：6 个被引用路径全部存在；AGENTS.md 含智能受理/feature|fix 前缀/develop(3)/state.md(6)/断点恢复/一次询问；INDEX 含"类型"列（feature / fix）；根 README 已重写为一句话受理+五阶段+断点续跑
  - TR-4.2（rubric）自评 4 分：根 README 提供一句话受理、3 条分类样例、自动四步、续跑四步，无需手动操作；未达 5 因首次用户仍需阅读约半屏规则才能信任分类结果。最终分以独立 Review 为准
- **Priority**：high
- **Depends On**：Task 3
- **Description**：
  - `INDEX.md`：表头增加"类型"列（feature/fix），示例行同步；阶段取值不变
  - `AGENTS.md`：第 1 节加入智能受理路由（含关键词与歧义一次询问）；第 2 节文件所有权表加入 `state.md`（任何阶段可更新，阶段切换时必须更新）；第 3 节分支改为 feature/fix 且一律从 develop 建；第 6 节 DoD 增加状态卡与 INDEX 一致性
  - 根 `README.md`：新需求六步改为"一句话受理（自动分类/取号/模板/分支）+ 五阶段 + 断点续跑"；目录结构同步双模板与 state.md
- **Acceptance Criteria Addressed**：AC-3、AC-5、AC-6
- **Test Requirements**：
  - `rule` TR-4.1：三处文件更新点全部落地且无死链；证据为文件内容与链接路径存在性检查
  - `rubric` TR-4.2：首次使用顺畅度；scale 1-5；anchors 1=仍需多文件/手动操作，3=可照做但有歧义，5=一句话受理且步骤无歧义含样例与续跑；threshold >= 4；evidence 为评审者按根 README 模拟从一句话到分支建成的全过程

## Task 5：ADR-0002 与规格自登记
- **Status**：`completed`
- **Completion Evidence**：
  - TR-5.1（rule）通过：docs/adr/0002-workflow-checkpoints-and-intake.md 存在且状态 Accepted；ADR README 索引含 0002 行
  - TR-5.2（rule）通过：0001/state.md 存在（字段与真实进度一致：S1-S3 勾选、S4/S5 未勾），INDEX 含 0001 fix 行；review.md 按文件所有权规则在 S5 前不存在，符合预期
- **Priority**：medium
- **Depends On**：Task 4
- **Description**：
  - 新建 `docs/adr/0002-workflow-checkpoints-and-intake.md`：记录状态卡断点机制、严格门禁、Intake 分类规则、develop 基线与 feature/fix 分支命名四项决策及后果；ADR 索引登记
  - 为 0001 自身补一份 `state.md`（从 fix 模板复制并填到 Implement 真实状态），INDEX 登记 0001（fix，Implement→最终 Review/Done）
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-5.1：ADR-0002 文件存在、状态 Accepted、ADR README 索引含 0002；证据为文件与目录清单
  - `rule` TR-5.2：0001/state.md 存在且字段与实际进度一致，INDEX 含 0001 行；证据为文件内容

## Task 6：自证与提交
- **Status**：`pending`
- **Priority**：medium
- **Depends On**：Task 5
- **Description**：
  - 全量自证：逐条执行 TR-1~TR-5 的取证命令；`pytest` 与 `ruff check .` 保持全绿（本次不改代码，确认无回归）
  - 检查 README/AGENTS/ADR 中所有相对链接指向的文件存在
  - 在 fix/0001 分支以 `docs(0001): ...`  Conventional Commit 提交（不 push）
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4、AC-5、AC-6
- **Test Requirements**：
  - `rule` TR-6.1：全部 rule TR 有真实命令输出证据，pytest 全绿；证据为命令输出记录到各任务 Completion Evidence
  - `rubric` TR-6.2：TR-4.2 同维度自评分并给出理由与证据，threshold >= 4；最终分数以独立 Review 为准
