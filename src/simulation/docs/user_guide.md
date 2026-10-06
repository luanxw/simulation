# 传感器仿真测试代码——详细使用说明

> 面向使用者的一步步操作指南。读完本篇你可以：跑通全部 46 条测试、读懂判定结果、修改阈值、新增障碍物与用例、接入真实仿真引擎、排查常见问题。
> 方法学背景见 [sensor_test_standard.md](sensor_test_standard.md)；需求依据见 `.trae/specs/0002-mower-sensor-sim-test-plan/spec.md`。

---

## 1. 环境准备（一次性）

本项目使用 conda 独立环境 **Python 3.12**（环境名 `simulation-py312`）：

```bash
# 若环境尚未创建（本机已创建过可跳过）
/usr/local/anaconda3/bin/conda create -y -n simulation-py312 --override-channels -c conda-forge python=3.12
/usr/local/anaconda3/envs/simulation-py312/bin/pip install pytest ruff pyyaml
```

> 本机 `conda` shell 函数有权限问题（`permission denied`），请直接用完整路径
> `/usr/local/anaconda3/bin/conda` 或 `/usr/local/anaconda3/envs/simulation-py312/bin/python`。
> 注意系统默认 `python3` 是 3.8，不要用它跑本项目。

设个别名省事（可加入 `~/.zshrc`）：

```bash
alias simp='PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python'
alias simtest='PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest'
```

## 2. 三分钟跑通

```bash
cd /Users/allen/source/positec/simulation

# ① 全部测试（156 项，含 46 条用例门禁 + 一致性 + 统计函数 + 安全负向测试）
PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q
# 预期输出：156 passed

# ② 代码风格检查（提交前必做）
/usr/local/anaconda3/envs/simulation-py312/bin/ruff check .
# 预期输出：All checks passed!
```

就这两条命令。测试全绿 = 46 条用例门禁全过 + 配置与规格一致 + 安全负向测试证明门禁真实生效。

### 只跑某一组

```bash
PYTHONPATH=src py312python -m pytest tests/test_gates_l.py -q      # 只跑 LiDAR 11 条
PYTHONPATH=src py312python -m pytest tests/test_gates_f.py -q      # 只跑融合 13 条
PYTHONPATH=src py312python -m pytest tests/test_gates_f.py::TestSafetyNonNegotiable -q  # 安全专项
PYTHONPATH=src py312python -m pytest -k "TC-U-03" -q               # 按用例号过滤
```

## 3. 代码地图（每个文件干什么）

```
src/simulation/
├── config/
│   ├── sensor_params.yaml      # 传感器标称参数（量程/安装/帧率…）——改选型只动这里
│   └── test_thresholds.yaml    # 全部 46 条用例的判定阈值——改门禁只动这里
├── obstacles.py                # 障碍物规格库：50 项，每项五要素+各传感器距离档与门限
├── scenarios.py                # 场景注册表：46 条用例定义 + 专项检出条件表 NAMED
├── thresholds.py               # 配置装载器：tc_gates("TC-L-01") 取某条用例阈值
├── verdict.py                  # 判定器：检出率/Wilson 区间/稳定窗/误差统计/门禁判定
├── backends.py                 # 合成后端：确定性传感器模型（种子驱动，可注入故障）
├── runner.py                   # 执行器：run_tc("TC-L-01") → verdict 字典
└── docs/                       # 本文档 + 标准指导书
tests/                          # 测试镜像：test_gates_l/u/c/f.py 即四套门禁
```

**数据流**：`thresholds.yaml（阈值）+ obstacles.py（目标）+ scenarios.py（条件）`
→ `backends.py（产生带种子的仿真观测）` → `runner.py（按用例逻辑判定）`
→ `verdict 字典（pass/fail + 每条检查的数值与 CI）`。

## 4. 核心用法

### 4.1 执行一条用例并读取结果

```python
from simulation.runner import run_tc
import json

v = run_tc("TC-L-05")            # 旗杆/码数桩/警戒带细长障碍检出
print(json.dumps(v, ensure_ascii=False, indent=2))
```

输出结构（每个 verdict 都长这样）：

```json
{
  "tc": "TC-L-05",
  "pass": true,                      ← 放行看这里
  "n_checks": 7, "n_live": 7, "n_pending_backend": 0,
  "failed": [],                      ← 失败的检查名
  "checks": [
    {"name": "OB-B1@L:0.5m", "status": "pass",
     "value": 1.0, "op": "ge", "threshold": 0.98},   ← 每条 rule 的数值证据
    ...
  ]
}
```

要点：
- `pass` 为 false 时先看 `failed` 列表，再到 `checks` 里找同名项对比 `value` 与 `threshold`。
- `n_pending_backend > 0` 表示该用例有检查项需要真实仿真引擎才有意义（当前 46 条全部为 0）。
- verdict 是纯 dict，可直接 `json.dump` 落盘归档（建议路径 `reports/0002-*/<TC-ID>/verdict.json`）。

### 4.2 批量执行与汇总

```python
from simulation.runner import run_suite, run_all

suite_l = run_suite("L")     # {"TC-L-01": {...}, ...} 共 11 条
allv = run_all()             # 46 条
bad = {tc: v["failed"] for tc, v in allv.items() if not v["pass"]}
print(bad or "全部通过")
```

### 4.3 复现实验（seed）

所有随机量都从 `rng_for(场景键, seed)` 派生，**同 seed 同结果**，跨进程跨平台一致：

```python
from simulation.backends import SyntheticBackend, rng_for

be = SyntheticBackend()
a = be.sample_hits("L", "OB-D1", 2.0, 100, rng_for("my-exp", 42))
b = be.sample_hits("L", "OB-D1", 2.0, 100, rng_for("my-exp", 42))
assert a == b                   # 永远成立
```

seed 与样本量下限配置在 `test_thresholds.yaml` 的 `sampling:` 段（默认种子 11/22/33，静态 ≥200 帧，动态 ≥20 遭遇）。

### 4.4 故障注入（负向测试 / 门禁有效性验证）

```python
from simulation.backends import SyntheticBackend
from simulation.runner import run_tc

be = SyntheticBackend()
be.faults.add("lidar_blind")            # 可选：lidar_blind / camera_blind / ultrasonic_degraded
v = run_tc("TC-L-05", be)
assert not v["pass"]                    # LiDAR 致盲后门禁必须变红——证明测试不是假绿
```

`tests/test_gates_f.py::TestFaultInjection` 就是三个这样的负向测试。**新增 rule 时建议配一条负向测试**，防止门禁永远为真。

### 4.5 降级组合（TC-F-08）

```python
be = SyntheticBackend()
be.combo = "only_ultrasonic"            # 7 种：disable_lidar / disable_ultrasonic / disable_camera
                                        # / only_ultrasonic / only_camera / only_lidar / single_side_camera
p = be.fusion_prob("OB-D2", 0.5)        # 仅超声在位时对俯卧儿童的融合检出概率
be.combo = None                         # 用完记得复位
```

包线数值在 `test_thresholds.yaml` 的 `degradation_envelope:` 段，7 组合与 spec 5 章 TC-F-08 表一一对应。

## 5. 修改与扩展（怎么做才不破坏一致性）

### 5.1 调整某个门禁阈值

例：把旗杆 @3 m 的门限从 98% 收紧到 99%：

1. 改 `config/test_thresholds.yaml` → `suites.L.TC-L-05` 里对应键（当前该用例门限经 `NAMED` 条件表引用障碍物库门限，实际改 `obstacles.py` 中 `OB-B1` 的 `rate["L"]`）。
2. 同步修改 `.trae/specs/0002-.../spec.md` 中对应数字（一致性测试会 grep 规格）。
3. 跑 `simtest tests/test_config_consistency.py -q` 与对应门禁测试确认全绿。

> 铁律：**阈值只存在于两处**（yaml + obstacles.py），绝不散落在测试或业务代码里；文档与配置不一致时测试会直接失败。

### 5.2 新增一个障碍物

在 `obstacles.py` 的 `OBSTACLES` 元组中加一项：

```python
_o("OB-B21", "球道标识牌", "B", "400×600 mm 板 + Φ30 立柱", "金属+反光膜", "高反板面",
   "大板+细柱", "近地细柱+高反板",
   tiers={"L": (1.0, 2.0, 3.0), "U": (0.5,), "C": (1.0, 2.0)},
   rate={"L": 0.95, "U": 0.95, "C": 0.95}),
```

规则：
- `rate` 的每个键必须出现在 `tiers` 里（`test_rate_keys_subset_of_tiers_and_bounds` 强制）；
- 距离档不得超出传感器量程（U ≤1.5 m、C ≤4.0 m，越界测试直接失败）；
- 安全品类加 `safety=True`（会自动进入 TC-F-09/10 零碰撞清单）；
- 近地目标（顶面 ≤80 mm）加 `near_ground=True`（LiDAR 在 0.67 m 内自动不负责，超声兜底）；
- 特性记录目标（不设门限）写 `rate={"L": None}`，普查会记录但不断言。

### 5.3 新增一条测试用例（四步）

以新增"TC-L-12 泥浆飞溅致盲"为例：

1. **场景**：`scenarios.py` 加 `SCENARIOS["TC-L-12"] = S("TC-L-12", "L", "泥浆飞溅致盲", "W3", "static")`。
2. **阈值**：`test_thresholds.yaml` 的 `suites.L` 加 `TC-L-12: {archetype: detection}`；若是全新判定类型则自拟 archetype 并在 `runner.py` 的 `_simple_model_case` 加分支。
3. **条件表**：专项检出类在 `scenarios.py` 的 `NAMED` 加 `_c("OB-B21", "L", 1.0, 0.95)` 形式的条件；并确认 `test_scenarios.py` 的编号连续性测试（TC-L 必须连续到 12）。
4. **测试**：`tests/test_gates_l.py` 的参数化会自动覆盖新用例；若属安全类，在 `test_gates_f.py` 补零碰撞断言。

### 5.4 接入真实仿真引擎（Isaac Sim / Gazebo / 自研）

唯一需要实现的是替换 `backends.SyntheticBackend`：

```python
class IsaacBackend:                       # 鸭子类型：实现同名方法即可
    name = "isaac"
    def detection_prob(self, sensor, code, distance): ...
    def fusion_prob(self, code, distance): ...
    def sample_hits(self, sensor, code, distance, n, rng): ...
    def range_error_mm(self, sensor, rng): ...
    def depth_error_mm(self, distance, rng): ...
    def latency_ms(self, kind, rng): ...
    def stop_distance_m(self, speed): ...
    def trigger_distance_m(self, code, rate_floor=0.8): ...
    def clearance_m(self, code, speed): ...
    def ring_scan(self, diameter_mm, frames, rng): ...

v = run_tc("TC-L-05", IsaacBackend())     # 门禁与阈值一字不改
```

`run_tc` 第二个参数就是后端。选型决策按仓库约定写 ADR（`docs/adr/0003-*.md`，对应 tasks.md Task 1）。真值（GT）对齐：引擎侧须输出 ≥100 Hz 全局真值快照，检出判定用 spec 2.4 的定义（`verdict.py` 已实现统计部分）。

## 6. 结果解读与放行

| 现象 | 含义 | 处置 |
|---|---|---|
| `pass: true` | 全部 live rule 通过 | 可放行；verdict 归档作证据 |
| `failed` 含 `_overall/_safety`（TC-F-08） | 某降级组合低于包线 | 查 `degradation_envelope` 对应组合，定位弱传感器 |
| `failed` 含 `collisions` | **安全项失败，不可豁免** | 立即冻结放行，转感知团队归因 |
| 大量检出率恰在门限边缘 | 传感器模型或安装参数与门限不匹配 | 查 `sensor_params.yaml` 与覆盖预算（0.67 m 线、超声 1.5 m 量程） |
| `KeyError: 未在 test_thresholds.yaml 登记` | 用例号没配阈值 | 补 yaml（见 5.3） |

**放行清单**（对应 spec DoD）：46 条 verdict 全 pass → 安全类碰撞 =0 → `pytest` 全绿 → `ruff check .` 无告警 → verdict JSON 归档 → INDEX 登记。

## 7. 常见问题（FAQ）

**Q1：为什么不叫 oracle.py / 和 Oracle 数据库有关系吗？**
没有关系。test oracle 是测试工程术语（判定器），为避免误会已更名 `verdict.py`。本项目无任何数据库依赖；若需把 verdict 落 MySQL 供部门查询，属新需求，需另立规格。

**Q2：为什么系统 python3（3.8）跑不了？**
pyproject 声明 ≥3.10，代码用了 3.10+ 语法（`zip(strict=)`、match 无、dataclass slots 未用但按 3.12 风格编写）。请始终用 conda 环境的完整路径解释器。

**Q3：合成后端的结果可信吗？**
SyntheticBackend 是**判定链路的打通工具**：它按"标称门限 + 名义机台裕量"产生确定性观测，验证的是门禁逻辑、统计方法、条件覆盖的正确性，**不是**传感器性能结论。性能结论必须来自真实引擎后端（Task 1 选型后接入）。这正是 `n_pending_backend` 字段存在的原因。

**Q4：怎么只重跑一次失败的用例？**
`PYTHONPATH=src py312python -m pytest tests/test_gates_l.py::test_lidar_gate_pass[TC-L-05] -q`（注意方括号参数在 zsh 里要加引号）。

**Q5：verdict 存哪里？**
`run_tc` 只返回不落盘。建议在调用方按 `reports/0002-mower-sensor-sim-test-plan/<TC-ID>/verdict.json` 归档（spec 2.2 约定的证据路径），CI 中可加一步 `json.dump`。

**Q6：阈值改了但测试没反应？**
`thresholds.py` 用了 `lru_cache`。同进程内改 yaml 后需 `load_thresholds.cache_clear()`；跨进程（重新跑 pytest）无此问题。

**Q7：中文文档在哪？**
标准指导书（部门展示用）：`src/simulation/docs/sensor_test_standard.md`；需求与评审：`.trae/specs/0002-mower-sensor-sim-test-plan/`（spec.md / tasks.md / review.md）。

## 8. 设计图索引（配合标准指导书）

七张设计图在 `src/simulation/docs/diagrams/`（由 `scripts/make_diagrams.py` 生成，改图请改脚本后重跑），按四类编目：架构类 `01`/`03`、流程类 `02`/`05`、数据类 `06`、模块交互类 `07`、障碍物介绍 `04`。部门展示直接用 `docs/sensor_test_standard.md` + 七图，或使用配套 PPT。

## 9. 提交前自检（对照 AGENTS.md）

```bash
PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q   # 必须全绿
/usr/local/anaconda3/envs/simulation-py312/bin/ruff check .                          # 必须无告警
```

提交信息遵循 Conventional Commits 并带规格编号，例如 `feat(0002): add sensor test gates baseline`。一个提交只解决一件事。
