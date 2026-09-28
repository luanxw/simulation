# 常驻授权、S6 自动交付与可选评审者 - 修复实施计划

## Task 1：Intake 台账与分支例外留痕
- **Completion Evidence**：0002 目录三件（spec/tasks/state；review 按新规 S5 才实例化）就绪；state.md 含评审者指定字段、S3 自动批准依据、分支例外留痕；INDEX 第 8 行登记 0002；intake 提交 7307aff。
- **Status**：`completed`
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 复制 fix 模板创建 0002 四件套；初始化 state.md（S1/S2 勾选、S3 常驻授权自动通过留痕、评审者指定=默认）；INDEX 登记 0002
  - 分支例外：经用户 2026-09-27 批准，0002 沿用 fix/0001-workflow-resume-and-intake 分支，不新建分支
- **Acceptance Criteria Addressed**：AC-6
- **Test Requirements**：
  - `rule` TR-1.1：0002 目录含四件套，state.md 字段完整且记录 S3 自动批准依据与分支例外，INDEX 含 0002 行；证据为 ls/grep

## Task 2：工作流 README 六阶段化
- **Completion Evidence**：`.trae/specs/README.md` 重写为六阶段版（常驻授权表/否决权/S3 自动/S6/push 当次确认/评审者可选 browser_use·search+三不变/恢复协议/DoD）；TR-2.1 grep 五要素全中、旧强制批准表述 CLEAN（见 Task 5 取证）。
- **Status**：`completed`
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
- **Completion Evidence**：两套 state.md 均加评审者指定字段与 S6 Deliver 门禁（grep 各 1 命中）；两套 review.md 加 Reviewer agent 类型行与三不变说明；fix/spec.md"五阶段"已改；`grep -rn 五阶段 _templates/` = TEMPLATE CLEAN。
- **Status**：`completed`
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
- **Completion Evidence**：AGENTS.md 七节重写（常驻授权/六阶段所有权/push 唯一确认点/评审者可选/DoD S1-S6）；根 README 六阶段流程图+常驻授权+S6+push 确认；ADR-0003 新建并登记 docs/adr/README.md（含 0001/0002 分支例外）；11 条相对链接 ALL LINKS OK。
- **Status**：`completed`
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

## Task 6：S7 建 MR 条款落地（2026-09-28 需求变更增补）
- **Completion Evidence**：工作流 README 改七阶段（流程图含 S7 Merge、S7 小节 Entry/动作/边界/Exit、文件所有权与 DoD 同步）；AGENTS.md 第 3 节补 S7 条款、DoD 七阶段；根 README 流程图七阶段+S7 说明；双轨 state.md 模板加 S7 Merge 门禁（含链接记录位）；ADR-0003 追加"补充：S7 Merge（2026-09-28）"段。提交 2691cdd。
- **Status**：`completed`
- **Priority**：high
- **Depends On**：Task 4
- **Description**：
  - 工作流 README：六阶段流程图改七阶段；新增 S7 Merge 小节（Entry=用户当次确认 push；动作=push → 成功后建 MR 并返回链接，`gh pr create` 优先 / compare 链接兜底，目标分支默认 develop；合并按钮由用户自行点击）；DoD/文件所有权同步
  - AGENTS.md：第 3 节补 S7 条款；DoD 六阶段→七阶段（S7 单独列，标注"需用户当次确认后执行"）
  - 根 README：流程图改七阶段，S6 条后补 S7 说明
  - 双轨 state.md 模板：门禁区 S1-S6 扩为 S1-S7（S7 Merge 勾选含 MR 链接）
  - ADR-0003 增补 S7 决策段落（正文体不改已 Accepted 的历史表述，追加"2026-09-28 补充"段）
- **Acceptance Criteria Addressed**：AC-2、AC-8
- **Test Requirements**：
  - `rule` TR-6.1：工作流 README/AGENTS.md/根 README 三处 grep 到 S7 与"返回.*链接"，双轨 state.md 模板各含 S7 勾选项；证据为 grep

## Task 5：S4 自证与提交
- **Completion Evidence**：`PYTHONPATH=src pytest -q` = 1 passed（1 warning 为 pytest6 对 pythonpath 配置的已知无害警告）；零 .py 改动，lint 面无变化（ruff>=0.6 已在 dev 依赖声明）；AC-1~5 grep 全通过、旧表述 CLEAN、链接无死链；主体提交 93c7c8d（intake 7307aff 之后）。
- **Status**：`completed`
- **Priority**：medium
- **Depends On**：Task 4
- **Description**：
  - 全量取证：pytest、Markdown 死链、AC-1~AC-5 的 grep 核验；更新 state.md（S4 勾选→Review）；在 fix/0001 分支提交（不 push）
- **Acceptance Criteria Addressed**：AC-1、AC-2、AC-3、AC-4、AC-5
- **Test Requirements**：
  - `rule` TR-5.1：pytest 1 passed、零 .py 改动、链接无 BROKEN、各 grep 项通过；证据为命令输出


---

# R1 评审整改（2026-09-28）

## Issue I-1：spec.md 修订补全
- **Status**：`completed`
- **Priority**：high
- **Completion Evidence**：spec.md 已含 AC-8；AC-2 改 S1→S7、AC-5 改七阶段；远端假设更正为 origin 已配置；AC-6 表述改为"0002 提交未推送（ahead）"。提交 ae69a56。

## Issue I-2：AGENTS.md 补 S7 条款
- **Status**：`completed`
- **Priority**：high
- **Completion Evidence**：§3 标题改"S6/S7"并新增 S7 Merge 条款（gh pr create 优先/compare 兜底/目标 develop/不代合并）；§7 DoD 改 S1-S7 并含 MR 链接返回项。提交 ae69a56。

## Issue I-3：工作区未提交修改处理
- **Status**：`completed`
- **Priority**：high
- **Completion Evidence**：根因为工具层回滚导致 59cc361 提交视图陈旧（spec.md 仅进 +1/-1 行）；非并发修改。已将工作区修改核实后纳入 ae69a56 正规提交，git status 恢复干净。流程教训已写入 review.md F-3 与 ADR 待办。

## Issue I-4：模板 S3 Exit 改自动批准语义
- **Status**：`completed`
- **Priority**：medium
- **Completion Evidence**：双轨 _templates/*/state.md S3 Exit 均改为"常驻授权下自动批准并留痕；用户可随时否决→回退对应阶段"。提交 ae69a56。

## Issue I-5：fix/spec.md 阶段计数
- **Status**：`completed`
- **Priority**：low
- **Completion Evidence**：_templates/fix/spec.md"六阶段"改"七阶段"。提交 ae69a56。
