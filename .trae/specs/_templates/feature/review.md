# [特性名称] - 独立评审

> 仅当 tasks.md 队列清空（S4 Exit 全满足）后创建本文件；只在 Review 阶段修改。
> 评审者必须是未参与实施的全新上下文。每条 AC/TR 都必须被某个检查点覆盖。

- [ ] CP-R1：[二值产品结果]
  - **Type**：`rule`
  - **Covers**：AC-1 / TR-1.1
  - **Evidence**：Pending

- [ ] CP-U1：[评估型产品结果]
  - **Type**：`rubric`
  - **Covers**：AC-2 / TR-1.2
  - **Scale**：1-5
  - **Anchors**：1 = [最差]；3 = [可接受]；5 = [理想]
  - **Pass Threshold**：>= 4
  - **Evidence**：Pending

<!--
检查点编号约定：CP-Rn 为 rule，CP-Un 为 rubric。
相关联的多个 AC/TR 可用一个连贯、可观察的检查点合并覆盖。
-->

## Review History

### Review R1
- **Result**：`pass` | `fail` | `blocked`
- **Checks Performed**：
  - [执行的检查与命令/动作]
- **Evidence**：
  - [观察到的结果]
- **Checkpoint Results**：
  - CP-R1 (`rule`)：`pass` | `fail` | `blocked`
  - CP-U1 (`rubric`)：`pass` | `fail` | `blocked`；得分 [1-5]；理由 [...]
- **Findings**：
  - [F-1]：`actionable` | `advisory`；严重度；复现方式；预期结果
- **Blocked By**：[仅 blocked：缺失的环境/权限/依赖]
- **Resume When**：[仅 blocked：恢复条件]

<!--
结果判定不变量：
- pass：所有检查点通过 + 每条 AC 有独立证据 + 无 actionable 发现与 blocked 检查。
- fail：至少一条 actionable 发现；每个失败检查点映射一条发现，
        每条发现回到 tasks.md 落成 pending Issue。
- blocked：因环境/权限/依赖无法取证（不是实现缺陷）；解除后用全新评审者重启一轮。
整改或解阻后，复制上方 R1 块新增 R2，禁止覆盖历史。
-->
