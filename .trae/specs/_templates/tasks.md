# [特性名称] - 实施计划

> 阶段：Plan / Implement。由 spec.md 派生：每条 AC 必须至少被一个任务覆盖。
> 任务按依赖排序、垂直切片（一个任务交付可验证的完整增量）。
> 标题中禁止写状态；状态只存在于 `Status` 字段。

## Task 1：[描述性标题]
- **Status**：`pending`
- **Priority**：high | medium | low
- **Depends On**：None
- **Description**：
  - [本任务要达成的实现结果]
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-1.1：[二值条件；通过判据；证据来源]
  - `rubric` TR-1.2：[维度]；scale 1-5；anchors 1 = / 3 = / 5 =；threshold >= 4；evidence [材料]
- **Notes**：[可选]

<!--
每个任务至少一条 TR，只保留适用的类型。
TR 类型默认继承父 AC；为 rubric AC 提供更窄的二值 rule 证据亦可。

完成后追加（Status 改为 completed）：
- **Completion Evidence**：
  - [rule：命令与结果 / 提交 SHA / 产物路径]
  - [rubric：得分 + 理由 + 证据]

阻塞时：
- **Status**：`blocked`
- **Blocked By**：[可观察的阻塞事实]
- **Unblock Condition**：[恢复条件]

取消时（必须有用户批准）：
- **Status**：`cancelled`
- **Cancellation Reason**：[原因]
- **Cancellation Approved By**：[批准证据]
-->

---

## 整改问题（Review fail 后使用）

> 评审的每条 actionable 发现，必须在重新选任务前在此落成 pending Issue。
> 优先新建 Issue，而非重开已完成任务（除非原完成证据无效）。

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
