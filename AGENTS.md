# AGENTS.md —— 人与 AI 协作约定

本文件是本仓库的协作铁律，人类开发者与 AI 编码代理共同遵守。AI 代理在动手改代码前必须先读完本文件与 [`.trae/specs/README.md`](.trae/specs/README.md)。

## 1. 规格先行（Spec-First Gate）

- 任何新功能、跨模块重构、行为变更，**先有规格后有代码**：在 `.trae/specs/NNNN-<slug>/` 走完 Specify → Plan → Approve，未经用户明确批准不得实施。
- 拿不准是否琐碎时，按"需要规格"处理。
- 纯文档订正、依赖升级、格式化等零行为变更可豁免，提交信息使用 `chore:`。

## 2. 阶段门禁与文件所有权

| 文件/目录 | 谁能改、什么时候改 |
|---|---|
| `.trae/specs/<id>/spec.md` | Specify 阶段；批准后的需求变更需重新走批准 |
| `.trae/specs/<id>/tasks.md` | Plan 与 Implement 阶段；记录状态与 Completion Evidence |
| `.trae/specs/<id>/review.md` | **仅 Review 阶段**，由未参与实施的全新上下文创建/修改 |
| `src/`、`tests/` | Implement 阶段，按 tasks.md 逐项推进 |
| `docs/adr/` | 只追加；出现难逆转的技术决策时新建 ADR |

- 任务状态只写在 `Status` 字段：`pending / in_progress / blocked / completed / cancelled`，标题不嵌状态。
- 每次只推进一个最高优先级的就绪任务；阻塞必须写 `Blocked By` 与 `Unblock Condition`。
- 评审 fail 后，先把 actionable 发现全部落成 `tasks.md` 中的 pending Issue，再选任务。

## 3. 分支与提交

- 分支：特性用 `spec/NNNN-<slug>`；评审整改用同一分支；紧急修复用 `fix/<简述>`。
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)：
  `feat|fix|refactor|test|docs|chore(scope): 简述`，scope 建议带规格编号，如 `feat(0001): add collision solver`。
- 一个提交只解决一件事；不得在未要求时执行 push、force-push、reset --hard。

## 4. 代码与测试约定

- Python ≥ 3.10；src-layout，包代码只放 `src/simulation/`，测试镜像模块结构放 `tests/`。
- 提交前自验：`ruff check .` 与 `pytest` 必须全绿；新增行为必须伴随测试。
- 验证词汇只有 `rule`（二值）与 `rubric`（评分）；自证必须给出可复现命令与真实输出，禁止编造结果。
- 仿真相关代码注意：随机数需可播种（seedable），数值参数集中配置，保证实验可复现。

## 5. 语言与命名

- 规格、ADR、评审等文档：**中文**；代码标识符、文件名、提交 type：**英文**。
- 规格目录 slug 使用英文 kebab-case，编号四位、永不复用。

## 6. 完成定义（DoD）

- [ ] 最近一轮独立 Review 结果为 `pass`，所有检查点有证据；
- [ ] 每条 rule 有通过证据，每条 rubric 达阈值（含得分与理由）；
- [ ] `pytest` 全绿、`ruff check .` 无告警；
- [ ] tasks.md 中无 pending/in_progress/blocked，completed 项均有 Completion Evidence；
- [ ] `.trae/specs/INDEX.md` 已登记最终状态；产生难逆转决策时已写 ADR。
