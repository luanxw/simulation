# simulation

规格驱动（Spec-Driven）的 Python 仿真项目骨架。**先有规格、后有代码；独立评审通过，需求才算完成。**

## 目录结构

```text
simulation/
├── .trae/specs/               # 【规格层】需求的唯一事实来源
│   ├── README.md              #   工作流权威说明（规则细节以此为准）
│   ├── INDEX.md               #   需求状态看板
│   ├── _templates/            #   spec / tasks / review 三件套模板
│   └── NNNN-<slug>/           #   按特性隔离：一个需求一个文件夹
│       ├── spec.md            #     做什么：需求与验收标准
│       ├── tasks.md           #     怎么做：任务队列、整改 Issue、完成证据
│       └── review.md          #     独立评审（仅 Review 阶段可写）
├── src/simulation/            # 【代码层】业务代码（src-layout）
├── tests/                     # 【测试层】与 src 模块镜像
├── docs/adr/                  # 【决策层】架构决策记录，只追加
├── AGENTS.md                  # 人与 AI 的协作铁律
└── pyproject.toml             # 构建、pytest、ruff 配置
```

分层原则：**规格 → 决策 → 代码 → 测试** 各居其位；规格产物描述"做什么、为什么验收通过"，不污染业务代码目录。

## 快速开始

```bash
python3.10 -m venv .venv          # 需要 Python >= 3.10
source .venv/bin/activate
pip install -e ".[dev]"

pytest                            # 运行测试
ruff check .                      # 静态检查
```

---

## 规格驱动工作流

每个非平凡的功能、重构或跨模块变更，都对应 `.trae/specs/` 下的一个特性文件夹，端到端走完五个阶段。

### 五个阶段与门禁

| 阶段 | 做什么 | 产出/写入 | 退出条件 |
|---|---|---|---|
| 1. Specify 规格澄清 | 调研代码、澄清需求，定义"做什么" | `spec.md` | 验收标准无歧义，待澄清问题清零或被显式接受 |
| 2. Plan 计划 | 把每条验收标准拆成原子、有序的任务 | `tasks.md` | 每条 AC 都映射到任务，依赖关系清晰 |
| 3. Approve 批准 | 用户审阅规格与计划 | — | **用户明确批准** |
| 4. Implement 实施 | 逐任务写代码+测试并自证 | `src/`、`tests/`、`tasks.md` | 任务队列清空，completed 项均有完成证据 |
| 5. Review 评审 | **未参与实施的全新上下文**独立验证 | `review.md` | 评审结果 `pass`（唯一成功出口） |

硬门禁：

1. 未批准不得实施；批准若改变需求，回到 Specify 重新计划后再批准。
2. `review.md` 只能在 Review 阶段创建/修改，实施期间一律只读。
3. 评审 `fail`：每条可执行发现必须先落成 `tasks.md` 中的 `pending` 整改 Issue，整改清空后由全新评审者开启新一轮（R2、R3……）。
4. 拿不准变更是否需要规格时，按"需要规格"处理；纯文档订正、依赖升级、格式化等零行为变更可豁免，提交信息用 `chore:`。

### 两个核心概念

**验收类型只有两种**（AC 与 TR 通用）：

- `rule`：客观二值条件，写清可观察的通过判据与证据来源（命令输出、产物、日志）。
- `rubric`：质量维度评分，写清维度、1-5 量表、1/3/5 锚点、通过阈值（通常 ≥ 4）；验证时必须记录得分、理由、证据。验证顺序先 rule 后 rubric。

**任务状态机**（状态只写在 `Status` 字段，标题不嵌状态）：

```text
pending ──▶ in_progress ──▶ completed
                ├──▶ blocked（须写 Blocked By / Unblock Condition）
                └──▶ cancelled（须有用户批准记录）
```

没有 failed 状态：自验不通过保持 `in_progress`。

## 使用方法（新需求六步）

```bash
# 1. 取号：打开 .trae/specs/INDEX.md 确认下一个编号，复制模板建目录
cp -R .trae/specs/_templates .trae/specs/0001-your-feature-slug

# 2. Specify：填写 0001-your-feature-slug/spec.md（背景、FR/NFR、rule/rubric 验收标准）

# 3. Plan：填写同目录 tasks.md，逐条映射 AC；然后请用户批准，等待明确同意

# 4. Implement：批准后建分支，一次只推进一个最高优先级任务
git switch -c spec/0001-your-feature-slug
#    每完成一个任务：跑 pytest / ruff 自验 → 在 tasks.md 补 Completion Evidence → 置 completed

# 5. Review：队列清空后，由未参与实施的全新上下文按模板创建 review.md 独立评审
#    pass → 收尾；fail → 把发现落成 Issue 回第 4 步整改

# 6. 登记：在 .trae/specs/INDEX.md 更新阶段（Done）与评审结果（如 R1 pass）
```

命名约定：

- 特性目录：`NNNN-<英文-kebab-case-slug>`，编号四位、递增、永不复用/重命名（供分支、提交、ADR 引用）。
- 分支：`spec/NNNN-<slug>`；紧急修复用 `fix/<简述>`。
- 提交：[Conventional Commits](https://www.conventionalcommits.org/)，scope 带规格编号，如 `feat(0001): add collision solver`。

### 完成定义（DoD 自查清单）

- [ ] 最近一轮独立 Review 为 `pass`，每个检查点都有证据；
- [ ] 每条 rule 有通过证据，每条 rubric 达阈值且有得分与理由；
- [ ] `pytest` 全绿、`ruff check .` 无告警，新增行为有测试覆盖；
- [ ] `tasks.md` 无 pending / in_progress / blocked；
- [ ] `INDEX.md` 已登记最终状态；产生难逆转决策时已在 `docs/adr/` 新建 ADR。

## 参考文档

- [`.trae/specs/README.md`](.trae/specs/README.md)：工作流权威细则（阶段门禁、验证词汇、评审结果契约）
- [`AGENTS.md`](AGENTS.md)：人与 AI 协作铁律（文件所有权、分支提交、代码约定）
- [`docs/adr/README.md`](docs/adr/README.md)：如何写架构决策记录
