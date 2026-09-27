# [问题标题] - 修复实施计划

> 阶段：Plan / Implement。修复类任务保持"定位 → 修复+回归 → 自证"主线。
> 状态只写在 `Status` 字段；阶段进度记录在 `state.md`。

## Task 1：根因定位与稳定复现
- **Status**：`pending`
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 构造最小复现路径，稳定触发问题；定位根因并回填 spec.md 的"根因分析"
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-1.1：存在一条可重复执行的复现命令/脚本，在当前代码上必然失败；根因已写入 spec.md；证据为命令输出与 spec.md 回填内容
- **Notes**：[若无法稳定复现，置 blocked 并写明 Blocked By / Unblock Condition]

## Task 2：实施修复并新增回归测试
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 按 spec.md 修复方案改动最小必要代码；修复与回归测试在同一任务内完成
- **Acceptance Criteria Addressed**：AC-1、AC-2
- **Test Requirements**：
  - `rule` TR-2.1：复现命令在修复后通过；证据为命令输出
  - `rule` TR-2.2：新增回归测试在不含修复的代码上失败、含修复后通过（红绿均有输出）；证据为两次 pytest 输出
  - `rule` TR-2.3：`pytest` 全绿、`ruff check .` 无告警；证据为命令输出

<!--
阻塞/取消/完成字段写法同 feature 模板：
completed 必须附 Completion Evidence（rule 结果；如有 rubric 附得分+理由+证据）。
-->

---

## 整改问题（Review fail 后使用）

## Issue I-1：[发现标题]
- **Status**：`pending`
- **Priority**：high | medium | low
- **Depends On**：None
- **Discovered By**：Review R1
- **Description**：
  - [可观察的差距与复现方式]
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-I-1.1：[回归条件；通过判据；证据]
- **Notes**：[可选]
