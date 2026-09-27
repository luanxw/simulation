# 常驻授权、S6 自动交付与可选评审者 - 修复规格说明书

> 阶段：S1（fix 模板；本需求犬食新规则——用户已授予项目级常驻授权，S3 自动通过不阻断）。

## 问题概述
- **报告人/环境**：仓库所有者；0001 工作流落地后的首次实战反馈
- **现象**：① 每次文件增改与规格批准都要用户确认，链路频繁停等人；② 全部流程结束后没有明确的"收尾提交"步骤，提交动作散落在实施期，评审通过后产物与台账的最后变更可能未提交；③ Review 固定由同类全新子代理执行，视角单一，无法按需选择具备特定能力的 agent（如浏览器验证、跨模块检索、安全审查）
- **影响范围**：`.trae/specs/README.md`、`AGENTS.md`、根 `README.md`、`_templates/{feature,fix}/state.md`（及模板内阶段引用）、`docs/adr/`

## 复现步骤
1. 走完 0001 流程：S3 必须等 NotifyUser 批准、编辑文件可能触发逐次确认 → 链路中断等待；
2. R2 pass 后检查清单：没有专门步骤保证"评审产物、state、INDEX 的收尾变更"已提交；
3. 想让 browser_use 类 agent 验证带界面的需求：工作流没有指定评审者的入口。

## 期望行为 vs 实际行为
- **期望**：本仓库内 AI 对文件的增/改及阶段推进**默认无需逐次确认**，受理后一路自动跑到 S5 评审；评审通过后自动进入 S6 完成收尾提交；仅在 `git push` 前停下取得用户当次确认；S5 评审者可由用户预先指定。
- **实际**：S3 为人工强制门禁；无 S6；评审者不可选。

## 根因分析
- **Root Cause**：ADR-0002 的门禁设计把"需求方向校准"与"逐次操作授权"耦合在人工确认上，且流程在 Review pass 处戛然而止（只定义了完成判据，未定义交付动作）；评审委派只规定了独立性，未暴露 agent 类型选择面。

## 修复方案概述
- 引入**项目级常驻授权**：本仓库内文件增改免逐次确认；S3 由"人工强制批准"改为"自动批准"——代理在进 Implement 前自检 spec/tasks 完整性并在对话中给出摘要、不停顿；用户保留随时中断/否决权（否决即回退对应阶段）。
- 新增 **S6 Deliver 交付**：Entry 为 S5 最近一轮 pass；动作是自动完成全部收尾 commit（含 review.md/state.md/INDEX.md 终态）并保证 `git status` 干净；**不 push**。
- **push 成为唯一强制确认点**：任何远端写操作（push、建 MR/PR）必须取得用户当次明确确认；force-push、reset --hard 仍禁止。
- **评审者可选**：state.md 增加"评审者指定"字段；用户可在受理时或 S5 前指定 agent（默认全新 general_purpose_task；如 browser_use 做前端交互验证、search 做跨模块核查）；独立性三不变（未参与实施、只读、出具 R 轮次报告）。

## 约束与假设
- 常驻授权仅限**本项目工作区内**的文件增改与本地 git 操作；不延伸到 push/远端写、工作区外文件、不可逆破坏操作。
- 0002 沿用 fix/0001-workflow-resume-and-intake 分支（用户 2026-09-27 明确批准的例外，等价于"先在集成分支上连续落地两条工作流修复"）；在 state.md 与 ADR-0003 留痕。
- 已完成的 0001 不重走流程；六阶段与新字段只对新受理变更强制（0001 保持 Done 原状）。
- 当前仓库无远端；push 门禁先成文，配置远端后自动生效。

## 验收标准（以回归 rule 为主）

### AC-1：常驻授权与 S3 自动批准成文且无旧门禁冲突
- **Type**：`rule`
- **Given（给定）**：AGENTS.md 与工作流 README
- **When（当）**：检视门禁条款
- **Then（则）**：明确写出本项目内文件增改免逐次确认、S3 自动批准不停顿、用户可随时中断/否决（否决回退对应阶段）；且不存在与该规则冲突的"未经批准不得实施"旧强制表述
- **Pass Condition（通过条件）**：grep 命中免确认/S3 自动批准/否决回退三要素；旧表述已改写为自动批准语义
- **Evidence（证据来源）**：两文档 grep 输出

### AC-2：S6 交付阶段在三处成文
- **Type**：`rule`
- **Given（给定）**：工作流 README、AGENTS.md、双轨 state.md 模板
- **When（当）**：检视阶段定义
- **Then（则）**：流程为 S1→S6；S6 Entry=S5 最近一轮 pass，动作=自动收尾 commit + state/INDEX 置 Done 且 git status 干净，明确不 push
- **Pass Condition（通过条件）**：三处均含 S6 门禁/条款；模板状态卡含 S6 勾选项
- **Evidence（证据来源）**：文档与模板 grep

### AC-3：push 是唯一强制确认点
- **Type**：`rule`
- **Given（给定）**：AGENTS.md、工作流 README、根 README
- **When（当）**：检视远端操作条款
- **Then（则）**：push/建 MR 等远端写必须经用户当次明确确认；未确认不执行；force-push、reset --hard 保持禁止
- **Pass Condition（通过条件）**：三处文档均有当次确认条款；禁力推送/硬重置条款仍在
- **Evidence（证据来源）**：grep 输出

### AC-4：评审者可预先指定且独立性不变
- **Type**：`rule`
- **Given（给定）**：工作流 README 与 state.md 模板
- **When（当）**：检视 S5 委派规则
- **Then（则）**：state.md 含"评审者指定"字段（含默认值）；README 说明可选 agent 类型、适用场景、指定时机，并保留"未参与实施/只读/出 R 报告"三不变
- **Pass Condition（通过条件）**：字段存在；README 列默认值+至少 2 类可选 agent 场景+三不变
- **Evidence（证据来源）**：state 模板与 README 内容

### AC-5：双轨模板一致升级为六阶段
- **Type**：`rule`
- **Given（给定）**：_templates/feature 与 _templates/fix
- **When（当）**：检查四件套
- **Then（则）**：两套 state.md 均含 S1-S6 六个门禁勾选与评审者指定字段；模板正文无残留"S5 即最终/五阶段完成"与新六阶段冲突的表述
- **Pass Condition（通过条件）**：grep 两套 state 各含 S6；模板中阶段计数表述一致
- **Evidence（证据来源）**：find + grep

### AC-6：0002 自身按新规闭环且无未授权远端操作
- **Type**：`rule`
- **Given（给定）**：0002 执行全过程
- **When（当）**：S6 完成后
- **Then（则）**：实施期无阻断式批准等待（S3 以常驻授权自动通过并留痕）；全部变更已提交、`git status` 干净；未执行任何 push（无 upstream/无远端调用）；state.md 与 INDEX 为 Done + 最终 R 轮次
- **Pass Condition（通过条件）**：git status 空输出；`git log` 可见各阶段提交；无 push 证据（无远端跟踪分支）；state/INDEX 一致
- **Evidence（证据来源）**：git 命令输出、state.md、INDEX.md

### AC-7：自主边界的可理解性
- **Type**：`rubric`
- **Dimension（维度）**：新 agent 只读 AGENTS.md 即可明确"什么不用问 / 什么必须问 / 用户如何纠偏"
- **Scale（量表）**：1-5
- **Anchors（锚点）**：1 = 边界模糊不敢动手或可能越权 push；3 = 知道大原则但例外场景需多处拼凑；5 = 三类边界（免确认/必须确认 push/随时否决）一目了然且有阶段位置
- **Pass Threshold（通过阈值）**：>= 4
- **Evidence（证据来源）**：AGENTS.md，由 S5 评审者按新 agent 视角评分

## 待澄清问题
- 无（四个边界问题已在受理时一次问清：免确认含 S3、分支例外、S6 自动提交不 push、评审者预先指定）。
