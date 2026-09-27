# AGENTS.md —— 人与 AI 协作约定

本文件是本仓库的协作铁律，人类开发者与 AI 编码代理共同遵守。AI 代理在动手改代码前必须先读完本文件与 [`.trae/specs/README.md`](.trae/specs/README.md)。

## 1. 智能受理与规格先行（Intake + Spec-First Gate）

- 用户只需给一句话需求；代理**自动受理**，不要求用户手动取号/复制/建分支：
  1. **分类**：输入含"修复、优化、bug、报错、错误、异常、崩溃、挂了、故障、不工作、不行、失败、缺陷、慢、卡、超时、回归"（含英文 bug/fix/error/regression/refactor）判为 **fix（问题修复）**，否则判为 **feature（新需求交付）**；拿不准只询问用户一次；
  2. **取号**：查 `.trae/specs/INDEX.md` 取全局下一个四位编号（feature/fix 共用），从输入提炼英文 kebab-case slug；
  3. **复制模板**：fix 复制 `_templates/fix/`，feature 复制 `_templates/feature/`（各含 spec/tasks/review/state 四件套）；
  4. **建分支**：一律先 `git switch develop`，再建 `feature/NNNN-<slug>` 或 `fix/NNNN-<slug>`；
  5. 初始化 `state.md` 并在 INDEX 登记，然后进入 S1 Specify。
- 任何非平凡变更**先有规格后有代码**：走完 S1 Specify → S2 Plan → S3 Approve，未经用户明确批准不得进入 Implement。
- 拿不准是否琐碎时，按"需要规格"处理。纯文档订正、依赖升级、格式化等零行为变更可豁免，提交信息使用 `chore:`。

## 2. 阶段门禁与文件所有权

五个阶段严格串行：**S1 Specify → S2 Plan → S3 Approve → S4 Implement → S5 Review**；上一阶段 Exit 清单未在 `state.md` 全部勾选，不得进入下一阶段。

| 文件/目录 | 谁能改、什么时候改 |
|---|---|
| `.trae/specs/<id>/spec.md` | S1 Specify；批准后的需求变更需重走 S3 Approve |
| `.trae/specs/<id>/tasks.md` | S2 Plan 与 S4 Implement；记录状态与 Completion Evidence |
| `.trae/specs/<id>/review.md` | **仅 S5 Review**，由未参与实施的全新上下文创建/修改；S4 期间只读 |
| `.trae/specs/<id>/state.md` | 任何阶段可写，但仅限阶段切换/任务状态变化时据实更新；**不得用它跳过门禁** |
| `src/`、`tests/` | 仅 S4 Implement，按 tasks.md 逐项推进 |
| `docs/adr/` | 只追加；出现难逆转的技术决策时新建 ADR |

- 任务状态只写在 `Status` 字段：`pending / in_progress / blocked / completed / cancelled`，标题不嵌状态。
- 每次只推进一个最高优先级的就绪任务；阻塞必须写 `Blocked By` 与 `Unblock Condition`。
- 评审 fail 后，先把 actionable 发现全部落成 `tasks.md` 中的 pending Issue，再选任务。
- **断点恢复**：中断或换 agent 后，先读 INDEX → 该条 `state.md` → 校验产物一致性（矛盾以产物为准并修正状态卡）→ 按"下一动作"续跑；禁止重走已勾选阶段、禁止跳阶段。
- 每次阶段切换或任务状态变化，立即更新 state.md 与更新时间。

## 3. 分支与提交

- **所有工作分支一律从最新 `develop` 创建**，不得从其他工作分支拉取：
  - 新需求：`feature/NNNN-<slug>`；问题修复：`fix/NNNN-<slug>`；评审整改沿用同一分支。
  - 纯本地仓库无需 pull；`develop` 不存在时先从 main 基线创建。
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)：
  `feat|fix|refactor|test|docs|chore(scope): 简述`，scope 建议带编号，如 `feat(0002): add pause button`。
- 一个提交只解决一件事；不得在未要求时执行 push、force-push、reset --hard。

## 4. 代码与测试约定

- Python ≥ 3.10；src-layout，包代码只放 `src/simulation/`，测试镜像模块结构放 `tests/`。
- 提交前自验：`ruff check .` 与 `pytest` 必须全绿；新增行为必须伴随测试；fix 必须有"红绿成立"的回归测试。
- 验证词汇只有 `rule`（二值）与 `rubric`（评分）；自证必须给出可复现命令与真实输出，禁止编造结果。
- 仿真相关代码注意：随机数需可播种（seedable），数值参数集中配置，保证实验可复现。

## 5. 语言与命名

- 规格、ADR、评审等文档：**中文**；代码标识符、文件名、提交 type、分支名：**英文**。
- 规格目录 slug 使用英文 kebab-case，编号四位、feature/fix 共用、永不复用。

## 6. 完成定义（DoD）

- [ ] `state.md` 中 S1-S5 门禁全部勾选，与 INDEX、tasks.md、review.md 实际内容一致；
- [ ] 最近一轮独立 Review 结果为 `pass`，所有检查点有证据；
- [ ] 每条 rule 有通过证据，每条 rubric 达阈值（含得分与理由）；
- [ ] `pytest` 全绿、`ruff check .` 无告警；
- [ ] tasks.md 中无 pending/in_progress/blocked，completed 项均有 Completion Evidence；
- [ ] `INDEX.md` 已登记 Done 与评审结果；产生难逆转决策时已写 ADR。
