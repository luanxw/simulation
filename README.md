# simulation

规格驱动（Spec-Driven）的 Python 仿真项目骨架。**一句话提需求，AI 自动受理；阶段不跳级，中断可续跑，独立评审通过才算完成。**

## 目录结构

```text
simulation/
├── .trae/specs/               # 【规格层】需求的唯一事实来源
│   ├── README.md              #   工作流权威细则（受理/门禁/恢复协议）
│   ├── INDEX.md               #   需求看板（取号、阶段、评审结果）
│   ├── _templates/
│   │   ├── feature/           #   新需求模板：spec/tasks/review/state 四件套
│   │   └── fix/               #   修复模板：复现/根因/回归 四件套
│   └── NNNN-<slug>/           #   一条变更一个文件夹
│       ├── spec.md            #     做什么：需求与验收标准
│       ├── tasks.md           #     怎么做：任务队列、整改 Issue、完成证据
│       ├── review.md          #     独立评审（仅 Review 阶段可写）
│       └── state.md           #     断点状态卡：当前阶段/下一动作/门禁记录
├── src/simulation/            # 【代码层】业务代码（src-layout）
├── tests/                     # 【测试层】与 src 模块镜像
├── docs/adr/                  # 【决策层】架构决策记录，只追加
├── AGENTS.md                  # 人与 AI 的协作铁律
└── pyproject.toml             # 构建、pytest、ruff 配置
```

## 快速开始

```bash
python3.10 -m venv .venv          # 需要 Python >= 3.10
source .venv/bin/activate
pip install -e ".[dev]"

pytest                            # 运行测试
ruff check .                      # 静态检查
```

---

## 怎么用：一句话开工

直接对 AI 说出你的需求，无需手动取号、复制模板、建分支。AI 会自动：

1. **判定类型**：话里有"**修复、优化、bug、报错、异常、崩溃、故障、失败、缺陷、慢、卡、回归**"等字眼 → 问题修复（`fix`，走轻量模板，验收以回归测试为主）；否则 → 新需求交付（`feature`，走完整规格）。拿不准时只问你一次。
2. **自动取号**：在 INDEX 分配下一个四位编号（feature/fix 共用序号），生成英文 slug。
3. **自动复制模板**：从 `_templates/fix/` 或 `_templates/feature/` 复制四件套到 `.trae/specs/NNNN-<slug>/`。
4. **自动建分支**：**每次都从最新 `develop` 拉取**，创建 `fix/NNNN-<slug>` 或 `feature/NNNN-<slug>`。

示例：

| 你说 | 类型 | 自动产出 |
|---|---|---|
| "修复碰撞检测穿模的问题" | fix | `fix/0002-collision-penetration` + fix 四件套 |
| "优化仿真主循环帧率" | fix | `fix/0003-...` + fix 四件套 |
| "给仿真器加暂停按钮" | feature | `feature/0004-...` + feature 四件套 |

## 五个阶段：完成一个才能进下一个

```text
S1 Specify → S2 Plan → S3 Approve → S4 Implement → S5 Review → Done
  澄清需求     拆解任务     你批准       写代码自证      全新上下文独立评审
```

- 每个阶段有明确的 Entry 前置条件和 Exit 退出清单（见 [`.trae/specs/README.md`](.trae/specs/README.md)）；**上一阶段 Exit 未在 `state.md` 全部勾选，不得进入下一阶段**。
- **S3 必须等你明确批准**才动代码；**S5 由没参与写代码的全新上下文评审**，`pass` 是唯一完成出口；评审 fail 的问题会自动落成整改任务回炉。

## 中断了怎么办：断点续跑

换会话、换 agent、隔天继续都不丢进度。新 agent 按固定协议接手：

1. 读 `INDEX.md` 找到未 Done 的条目；
2. 读该条 `state.md`，看"当前阶段 / 下一动作 / 当前任务 / 交接备注"；
3. 对照实际产物校验（发现对不上时以产物为准修正状态卡）；
4. 严格从"下一动作"续跑——不重做已完成阶段，也不跳过未完成阶段。

进度细节都在 `state.md`（保持一屏），证据明细在 tasks.md / review.md。

## 完成定义（DoD 自查）

- [ ] state.md 中 S1-S5 全部勾选且与 INDEX、tasks.md、review.md 一致；
- [ ] 最近一轮独立 Review 为 `pass`，每条 rule 有通过证据、每条 rubric 达阈值；
- [ ] `pytest` 全绿、`ruff check .` 无告警，新增行为（含修复）有测试；
- [ ] INDEX 已登记 Done；难逆转的决策已记入 `docs/adr/`。

## 参考文档

- [`.trae/specs/README.md`](.trae/specs/README.md)：工作流权威细则（受理规则、五阶段 Entry/Exit、恢复协议、评审契约）
- [`AGENTS.md`](AGENTS.md)：人与 AI 协作铁律（文件所有权、分支提交、代码约定）
- [`docs/adr/README.md`](docs/adr/README.md)：如何写架构决策记录
