# 常驻授权、S6 自动交付与可选评审者 - 修复实施计划

## Task 1：Intake 台账与分支例外留痕
- **Status**：`pending`
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 复制 fix 模板创建 0002 四件套；初始化 state.md（S1/S2 勾选、S3 常驻授权自动通过留痕、评审者指定=默认）；INDEX 登记 0002
  - 分支例外：经用户 2026-09-27 批准，0002 沿用 fix/0001-workflow-resume-and-intake 分支，不新建分支
- **Acceptance Criteria Addressed**：AC-6
- **Test Requirements**：
  - `rule` TR-1.1：0002 目录含四件套，state.md 字段完整且记录 S3 自动批准依据与分支例外，INDEX 含 0002 行；证据为 ls/grep

## Task 2：工作流 README 六阶段化
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 阶段链改 S1→S6：S3 改"自动批准"（进 Implement 前自检+对话摘要、不停顿；用户可随时否决回退）；新增 S6 Deliver（Entry=S5 最近一轮 pass；自动收尾 commit；state/INDEX 置 Done；git status 干净；不 push）
  - 新增"常驻授权与唯一确认点"小节：工作区内增改免逐次确认；push/建 MR 必须当次明确确认；force-push/reset --hard 禁止
  - S5 增加评审者指定规则：默认全新 general_purpose_task；可选 browser_use（界面交互验证）、search（跨模块/资料核查）等；指定时机（受理时起至 S5 前，写入 state.md）；独立性三不变
  - 文件所有权表、恢复协议、DoD 同步六阶段；清除"未经用户明确批准不得实施"类旧表述
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4
- **Test Requirements**：
  - `rule` TR-2.1：grep 命中 S6/自动批准/当次确认/评审者指定/否决回退，且无残留旧强制批准表述；证据为 grep

## Task 3：双轨模板升级六阶段
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - feature/fix 两套 state.md：新增"评审者指定（默认：全新 general_purpose_task 子代理）"字段；门禁区 S1-S5 扩展为 S1-S6（S6 Deliver 勾选含完成时间/提交 SHA）
  - 两套 review.md：评审者信息处支持记录被指定的 agent 类型
  - 模板正文阶段计数与"五阶段"字样同步改六阶段
- **Acceptance Criteria Addressed**：AC-5、AC-4
- **Test Requirements**：
  - `rule` TR-3.1：两套 state.md 均 grep 到 S6 与评审者指定字段；模板目录无残留冲突表述；证据为 find+grep

## Task 4：AGENTS.md、根 README、ADR-0003
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 3
- **Description**：
  - AGENTS.md：第 1 节改为常驻授权（增改免确认、S3 自动批准、用户随时否决）；第 2 节六阶段+文件所有权；第 3 节 push 唯一确认点、S6 自动提交；新增评审者可选条款；DoD 六阶段
  - 根 README：流程图改六阶段、"一句话开工"体验改为"全程自动、推送前确认"
  - 新建 docs/adr/0003-standing-authorization-s6-reviewer.md（常驻授权边界、S6、push 确认点、评审者可选、0001/0002 分支例外）并登记 ADR 索引
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-7
- **Test Requirements**：
  - `rule` TR-4.1：AGENTS/README/ADR 更新点全部落地且相对链接无死链；证据为内容检查
  - `rubric` TR-4.2：自主边界可理解性 1-5，anchors 见 AC-7，threshold >= 4，评审者评分

## Task 5：S4 自证与提交
- **Status**：`pending`
- **Priority**：medium
- **Depends On**：Task 4
- **Description**：
  - 全量取证：pytest、Markdown 死链、AC-1~AC-5 的 grep 核验；更新 state.md（S4 勾选→Review）；在 fix/0001 分支提交（不 push）
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**：
  - `rule` TR-5.1：pytest 1 passed、零 .py 改动、链接无 BROKEN、各 grep 项通过；证据为命令输出
