# AGENTS.md —— 人与 AI 协作约定

本文件是本仓库的协作铁律，人类开发者与 AI 编码代理共同遵守。AI 代理在动手改代码前必须先读完本文件与 [`.trae/specs/README.md`](.trae/specs/README.md)。

## 1. 智能受理、常驻授权与规格先行

### 1.1 一句话智能受理
用户只需给一句话需求，代理自动完成，不要求用户手动操作：
1. **分类**：输入含"修复、优化、bug、报错、错误、异常、崩溃、挂了、故障、不工作、不行、失败、缺陷、慢、卡、超时、回归"（含英文 bug/fix/error/regression/refactor）判为 **fix**，否则判为 **feature**；拿不准只询问一次；
2. **取号**：查 INDEX.md 取全局下一个四位编号（feature/fix 共用），提炼英文 kebab-case slug；
3. **复制模板**：复制 `_templates/fix/` 或 `_templates/feature/` 的 spec/tasks/state 三件（review.md 留到 S5 实例化）；
4. **建分支**：一律先 `git switch develop`，再建 `feature/NNNN-<slug>` 或 `fix/NNNN-<slug>`（例外须用户明确批准并在 state.md 留痕）；
5. 初始化 state.md（含评审者指定字段）、登记 INDEX，进入 S1。

### 1.2 项目级常驻授权（2026-09-27 起，见 ADR-0003）
- **本项目工作区内的文件增/改/删、跑测试、本地 commit、建本地分支、阶段推进：均无需逐次确认**，直接执行并留证据。
- **S3 批准默认自动**：自检 spec/tasks 完整后在对话中给出摘要即继续，不停顿等待；但必须在 state.md 留授权痕迹。
- **用户随时可否决**：收到否决立即停手并回退到对应阶段（需求问题回 S1/S2；评审问题发起新一轮 S5），在交接备注记录。
- 纯文档订正、依赖升级、格式化等零行为变更可豁免流程，提交信息用 `chore:`。

## 2. 七阶段门禁与文件所有权

严格串行：**S1 Specify → S2 Plan → S3 Approve(自动) → S4 Implement → S5 Review → S6 Deliver → S7 Merge**。上一阶段 Exit 未在 state.md 全部勾选，不得进入下一阶段。

| 文件/目录 | 谁能改、什么时候改 |
|---|---|
| `spec.md` | S1；否决回退后修订 |
| `tasks.md` | S2 与 S4；记录状态与 Completion Evidence |
| `review.md` | **仅 S5**，由评审 agent 创建/修改；S4 及之前不得存在（模板除外） |
| `state.md` | 任何阶段据实更新；不得用它跳过门禁 |
| `src/`、`tests/` | 仅 S4 |
| `docs/adr/` | 只追加；难逆转的技术决策新建 ADR |

- 任务状态只写在 `Status` 字段：`pending / in_progress / blocked / completed / cancelled`，标题不嵌状态。
- 一次只推进一个最高优先级就绪任务；阻塞写 `Blocked By` / `Unblock Condition`。
- 评审 fail：先把 actionable 发现落成 tasks.md 的 pending Issue 再选活。
- **断点恢复**：先读 INDEX → state.md → 校验产物（矛盾以产物与 git 提交为准）→ 按"下一动作"续跑；不重走、不跳阶段。
- 任务/阶段一变化立即更新 state.md 并尽快提交。

## 3. 提交、S6/S7 交付与唯一确认点（push）

- **S4 期间可随时做本地 commit；S6 必须自动完成收尾提交**（review/state/INDEX 终态全部入库，`git status` 干净），无需用户确认。
- **S7 Merge**：用户确认 push 后，推送成功即**自动创建 Merge 请求并把链接返回用户**——优先 `gh pr create --base develop`（gh 缺失/未登录时输出预填 compare 链接兜底）；目标分支默认 develop；**代理不代点合并按钮**。
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)：`feat|fix|refactor|test|docs|chore(scope): 简述`，scope 带编号，如 `feat(0003): add pause button`。一个提交只解决一件事。
- **唯一强制确认点：`git push`、创建 MR/PR 等远端写操作**——必须取得用户**当次**明确确认才执行；S6 只本地提交、不 push。
- **始终禁止**：未经确认的 push、任何 force-push、`reset --hard`、删除分支、改动工作区外文件（用户措辞随意时也要二次确认命令本身）。
- 分支一律从最新 develop 创建；合并到 develop/main 的时机由用户决定。

## 4. 评审者可选（S5）

- 默认派**未参与实施的全新上下文** general_purpose_task 子代理，只读、只出报告。
- 用户可在受理时起至 S5 前指定评审 agent，写入 state.md"评审者指定"：如 `browser_use`（页面交互/渲染实测）、`search`（跨模块/资料核查）；后续专门 agent 同理。
- **独立性三不变**：未参与实施、评审期只读、出具带 pass/fail/blocked 的 R 轮次报告。整改后轮次递增（R2、R3），且每轮换全新评审者。

## 5. 代码与测试约定

- Python ≥ 3.10；src-layout，包代码只放 `src/simulation/`，测试镜像模块结构放 `tests/`。
- 提交前自验：`ruff check .` 与 `pytest` 必须全绿；新增行为必须伴随测试；fix 必须有"红绿成立"的回归测试。
- 验证词汇只有 `rule`（二值）与 `rubric`（评分）；自证必须给出可复现命令与真实输出，禁止编造结果。
- 仿真代码注意：随机数可播种（seedable），数值参数集中配置，保证实验可复现。

## 6. 语言与命名

- 规格、ADR、评审等文档：**中文**；代码标识符、文件名、提交 type、分支名：**英文**。
- slug 用英文 kebab-case；编号四位、feature/fix 共用、永不复用。

## 7. 完成定义（DoD）

- [ ] state.md 中 S1-S7 全部勾选（S7 在用户当次确认 push 后执行），与 INDEX、tasks.md、review.md 实际内容一致；
- [ ] 最近一轮独立 Review 为 `pass`，每条 rule 有通过证据、每条 rubric 达阈值（含得分与理由）；
- [ ] `pytest` 全绿、`ruff check .` 无告警；
- [ ] 无 pending/in_progress/blocked，completed 均有 Completion Evidence；
- [ ] S6 收尾提交完成、`git status` 干净、INDEX 登记 Done；
- [ ] 难逆转决策已写 ADR；push/合并已取得用户当次确认或明确暂缓；若已 push，MR 链接已返回用户。
