# [问题标题] - 独立评审

> 仅当 tasks.md 队列清空（S4 Exit 全满足）后创建本文件；只在 Review 阶段修改。
> 评审者必须是未参与修复的全新上下文。每条 AC/TR 都必须被某个检查点覆盖。

- [ ] CP-R1：原问题在修复后不可复现
  - **Type**：`rule`
  - **Covers**：AC-1 / TR-1.1 / TR-2.1
  - **Evidence**：Pending

- [ ] CP-R2：回归测试红绿成立且测试套件全绿
  - **Type**：`rule`
  - **Covers**：AC-2 / TR-2.2 / TR-2.3
  - **Evidence**：Pending

<!--
修复涉及质量维度时增补 CP-Un（rubric）。评审结果契约与轮次记录写法同 feature 模板：
pass = 全部检查点通过 + 每条 AC 有独立证据 + 无 actionable 发现；
fail = 每条 actionable 发现回 tasks.md 落成 pending Issue；
blocked = 环境/权限/依赖导致无法取证。每轮新增 R2、R3，禁止覆盖历史。
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
  - CP-R2 (`rule`)：`pass` | `fail` | `blocked`
- **Findings**：
  - [F-1]：`actionable` | `advisory`；严重度；复现方式；预期结果
- **Blocked By**：[仅 blocked]
- **Resume When**：[仅 blocked]
