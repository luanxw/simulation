# 架构决策记录（Architecture Decision Records）

ADR 用于记录项目中**有后果的、难以逆转的**决策：技术选型、目录结构、关键依赖、架构模式取舍。

## 规则

- 文件名：`NNNN-kebab-case-title.md`，编号递增、**永不复用**。
- 状态取值：`Proposed` → `Accepted` →（`Deprecated` | `Superseded by NNNN`）。
- ADR **只追加、不删改历史**；决策被推翻时新建 ADR 并把旧记录标为 Superseded。
- 与规格的关系：ADR 记录"为什么这样定"的跨需求约束；`.trae/specs/` 记录单个需求做什么。

## 索引

| 编号 | 标题 | 状态 | 日期 |
|---|---|---|---|
| [0001](0001-adopt-spec-driven-workflow.md) | 采用规格驱动工作流与分层目录架构 | Accepted（模板四件套与分支命名部分被 [0002](0002-workflow-checkpoints-and-intake.md) 更新） | 2026-09-27 |
| [0002](0002-workflow-checkpoints-and-intake.md) | 断点状态卡、严格阶段门禁与智能受理、develop 基线 | Accepted | 2026-09-27 |
| [0003](0003-sim-engine-selection.md) | 仿真引擎选型：gz-sim 主引擎 + 分层传感器建模 | Proposed | 2026-10-05 |

## 模板

```markdown
# NNNN. 标题

- 状态：Proposed | Accepted | Deprecated | Superseded by NNNN
- 日期：YYYY-MM-DD

## 背景（Context）

[面对的问题、约束、被考虑的方案]

## 决策（Decision）

[最终选择，以及为什么]

## 后果（Consequences）

- 正面：[...]
- 负面/代价：[...]
- 后续行动：[...]
```
