# 割草机器人传感器套件仿真测试方案 - 实施计划

> 阶段：**Approve 已通过**（2026-10-05 用户批准："提交代码批准批准，全部完成后提交代码"）。实施按任务队列推进；先行代码基线（合成后端）见"实施进展备注"。
> 本计划交付执行 spec.md 测试方案所需的仿真测试平台与全部取证。
> 任务按依赖排序；TR 引用 spec.md 中的 TC/FR/AC 编号。
> AC 覆盖说明：AC-1~AC-5 为方案文档级 rule，由 spec.md 内容与独立评审检查点 CP-R1~CP-R5 覆盖（见 review.md）；AC-6/AC-7 为文档级 rubric，由 CP-U6/CP-U7 覆盖；Task 1~12 覆盖 FR-1~FR-7 与 NFR-1~NFR-4，实施完成后的终审将对照全部 AC 复核。

## Task 1：仿真平台选型 PoC
- **Status**：`pending`
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 候选平台 ≥2（如 Isaac Sim / Gazebo / 自研光线追踪栈）对比：LiDAR/超声/双目建模能力、渲染 BRDF 与夜场光照、确定性回放、Python API、CI 可运行性
  - 产出 `docs/adr/0003-*.md` 记录选型决策；PoC 场景跑通 LiDAR + 1×超声 + 1×双目数据流 30 分钟无崩溃
- **Acceptance Criteria Addressed**：FR-1
- **Test Requirements**：
  - `rule` TR-1.1：ADR 存在且状态 Accepted，含 ≥2 候选对比；PoC 运行日志含三传感器数据流与时间戳；证据为文件与日志
- **Notes**：选型属难逆转决策，必须走 ADR（AGENTS.md §2）

## Task 2：GT 取证框架与 seed/配置中心
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - ≥100 Hz 全局真值快照（障碍物 ID/位姿/尺寸/材质、机器人位姿、仿真时钟）
  - 场景文件格式（YAML + seed）；`src/simulation/config/{sensor_params,test_thresholds}.yaml` 建立并录入 spec.md 全部数值阈值（含 10 类分类清单与 7 组合降级包线数值）
  - oracle 判定器骨架（检出/虚警/误差统计，Wilson CI）
- **Acceptance Criteria Addressed**：FR-1、NFR-1、NFR-2、NFR-3
- **Test Requirements**：
  - `rule` TR-2.1：`pytest tests/test_gtruth.py` 全绿（快照频率、字段齐全）；证据为命令输出
  - `rule` TR-2.2：同 seed 跑 5 次，规范化输出哈希一致；证据为哈希清单
  - `rule` TR-2.3：文档-配置一致性脚本（阈值逐项比对 spec.md）通过；证据为脚本输出

## Task 3：障碍物资产库（50 项）
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 按 spec.md 第 3 章逐项建模：几何、材质（BRDF/反射率、声学属性）、动态变体（摆动/滚动/行走）
  - 元数据 schema 含：编码、几何、材质、光学特性、声学特性、感知难点
- **Acceptance Criteria Addressed**：FR-2
- **Test Requirements**：
  - `rule` TR-3.1：资产 ≥50 项且与 spec.md OB-A/B/C/D 四表逐项对齐（对齐清单 diff 为空）；证据为对齐脚本输出

## Task 4：W0 校准场与 W3 环境注入场
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - W0：50×50 m 平面、AprilTag 阵列、可编程漫射光
  - W3：ENV-1~9 全档注入（光照/雨/雾/风/温度/草被/地形/喷灌/露水）
- **Acceptance Criteria Addressed**：FR-1
- **Test Requirements**：
  - `rule` TR-4.1：环境档实测值（lux、能见度、雨强、风速、温度）与 spec.md 偏差 ≤10%；证据为场内探针读数日志

## Task 5：W1 商用高尔夫球场世界
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2、Task 3
- **Description**：
  - 球道/果岭/发球台/长草/沙坑×2/水塘/维修沟/乔木×8/灌木/护栏/球车道/喷头×8/旗杆洞杯/码数桩 + 动元素（球车、行人、雁群、喷灌）
- **Acceptance Criteria Addressed**：FR-1、FR-2
- **Test Requirements**：
  - `rule` TR-5.1：要素清单与 spec.md 2.1 W1 行逐项核验在位，尺寸偏差 ≤5%；证据为清单核验输出

## Task 6：W2 足球场世界
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2、Task 3
- **Description**：
  - 105×68 m 草坪与白线、球门×2（柱梁+带网）、角旗×4、广告围挡、训练区器具、排水箅子、动元素（运动员×3、足球×3、对向机器人）+ 夜场泛光预设
- **Acceptance Criteria Addressed**：FR-1、FR-2
- **Test Requirements**：
  - `rule` TR-6.1：要素清单核验同 TR-5.1；夜场泛光场内垂直照度 1800 lux ±10%（多点位）；证据为清单与照度日志

## Task 7：传感器模型接入与标定
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - LiDAR（点云+噪声模型）、超声 ×12（波束/时序轮询/温补）、双目 ×2（左右渲染+视差/深度）按 `sensor_params.yaml` 接入；时间戳统一
- **Acceptance Criteria Addressed**：FR-3、FR-4、FR-5
- **Test Requirements**：
  - `rule` TR-7.1：三类传感器输出时间戳与仿真时钟偏差 ≤5 ms、左右相机 ≤1 ms；标称噪声参数与配置一致；证据为时间戳统计输出

## Task 8：TC-L 组执行与取证
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 4、Task 5、Task 7
- **Description**：执行 TC-L-01~11（含 TC-L-11 全库普查），产出 verdict.json/report.md；未达阈值非安全项转"能力边界报告"
- **Acceptance Criteria Addressed**：FR-3
- **Test Requirements**：
  - `rule` TR-8.1：TC-L-01~11 全部 rule 通过且证据齐全；不通过项均已转能力边界报告且无安全项；证据为 `reports/0002-*/TC-L-*/verdict.json`

## Task 9：TC-U 组执行与取证
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 4、Task 5、Task 7
- **Description**：执行 TC-U-01~12（12 通道全测），含 Φ25 盲区角谱图与 TC-U-12 全库普查输出
- **Acceptance Criteria Addressed**：FR-4
- **Test Requirements**：
  - `rule` TR-9.1：TC-U-01~12 全部 rule 通过且证据齐全；证据为 verdict.json 集合

## Task 10：TC-C 组执行与取证
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 4、Task 6、Task 7
- **Description**：执行 TC-C-01~10（左右对称、分别判定，含 TC-C-10 全库普查）
- **Acceptance Criteria Addressed**：FR-5
- **Test Requirements**：
  - `rule` TR-10.1：TC-C-01~10 全部 rule 通过（左、右各一套证据）；证据为 verdict.json 集合

## Task 11：TC-F 组执行与取证（含安全专项）
- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 8、Task 9、Task 10
- **Description**：执行 TC-F-01~13；TC-F-09/10（0 碰撞）最后执行且不可豁免
- **Acceptance Criteria Addressed**：FR-6
- **Test Requirements**：
  - `rule` TR-11.1：TC-F-01~13 全部 rule 通过；TC-F-09/F-10 碰撞计数 = 0；证据为 verdict.json 与碰撞事件清单

## Task 12：汇总报告与 CI 回归
- **Status**：`pending`
- **Priority**：medium
- **Depends On**：Task 11
- **Description**：
  - 全量门禁汇总报告（6.1 表逐项）；CI 冒烟子集（TC-L-01/U-01/C-01/F-01，≤30 min）；`ruff check .` 与 `pytest` 全绿
- **Acceptance Criteria Addressed**：FR-7、NFR-2
- **Test Requirements**：
  - `rule` TR-12.1：冒烟子集纳入 CI 且单次运行 ≤30 min；汇总报告命令可复现；证据为 CI 配置与运行日志

---

## 整改问题（Review fail 后使用）

> 评审的每条 actionable 发现，必须在重新选任务前在此落成 pending Issue。

**Issue I-1：LiDAR 近地覆盖推导口径错误**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] 0.76m 清除/0.67·0.87 就位；复算 (0.350−0.080)/tan22°=0.668 m、0.350/tan22°=0.866 m 与文档一致；TC-L-06、TC-C-09 已同步。
- **Priority**：high
- **Depends On**：None
- **Discovered By**：Review R1（F-1）
- **Description**：
  - 1.2 节"≥0.76 m"与实算（(0.350−0.080)/tan22°=0.668 m、0.350/tan22°=0.866 m）均不符；TC-L-06 豁免线、TC-C-09 交接带引用同值。
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-I-1.1：1.2 覆盖预算、TC-L-06、TC-C-09 三处改为可复现口径（0.67/0.87 m）；证据为文档与 python 复算一致

**Issue I-2：3.8 矩阵考核项缺承载用例**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] 矩阵考核↔承载用例闭合（0 断链）；新增 TC-L-11/TC-U-12/TC-C-10 普查用例；31 行矩阵关联列显式补齐普查引用；TC-C-04 布置已含 OB-A1/OB-B1。
- **Priority**：high
- **Depends On**：None
- **Discovered By**：Review R1（F-2）
- **Description**：
  - OB-B2/B6/B9/B10、OB-C2/C5、OB-D1/D2/D6/D7/D8 有超声档但无 TC-U 承载；OB-B3a/b、OB-B4 有双目档但无 TC-C 承载；OB-A1/B1 关联 TC-C-04 但其布置不含这些目标；单传感器基线数据无采集载体。
- **Acceptance Criteria Addressed**：AC-1、AC-2
- **Test Requirements**：
  - `rule` TR-I-2.1：新增 TC-L-11/TC-U-12/TC-C-10 全库普查用例，矩阵关联列与 TC 布置互相对齐；证据为文档交叉核对输出

**Issue I-3：TC-F-01 分类清单未枚举**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] TC-F-01 含分类清单（10 类）①~⑩且安全类=①~④，声明录入 test_thresholds.yaml。
- **Priority**：high
- **Depends On**：None
- **Discovered By**：Review R1（F-3）
- **Description**：
  - "10 类分类混淆矩阵"的类别全文未枚举，判定脚本无法实现。
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-I-3.1：TC-F-01 枚举 10 类清单并标注安全类边界，同步声明录入 test_thresholds.yaml；证据为文档

**Issue I-4：TC-F-08 降级包线无数值**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] 包线表 7 行数值齐全（全库平均/安全品类/补充约束），依据声明为 1.2 覆盖预算与普查实测。
- **Priority**：high
- **Depends On**：None
- **Discovered By**：Review R1（F-4）
- **Description**：
  - 7 组合降级包线引用"配置中声明"但文档与配置均无数值或推导规则。
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-I-4.1：TC-F-08 给出 7 组合包线数值表及依据；证据为文档

**Issue I-5：方法字段缺失与 TC-F-02 无布置**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] 方法行=46=TC 总数；每条 TC 均含布置行（含 TC-F-02）。
- **Priority**：high
- **Depends On**：None
- **Discovered By**：Review R1（F-5）
- **Description**：
  - 显式"方法"行仅 1/43 条；TC-F-02 无布置行，与 AC-1 及 4 章头部声明不符。
- **Acceptance Criteria Addressed**：AC-1
- **Test Requirements**：
  - `rule` TR-I-5.1：全部 TC 含显式方法行；TC-F-02 补布置；证据为 grep 计数 = TC 总数

**Issue I-6：障碍物计数口径不一致**
- **Status**：`completed`
- **Completion Evidence**：自验脚本 [PASS] '49 项' 全文清除；3.1/3.3/3.8/FR-2/概述/Task 3 统一 50 项口径（B3a/b 计 2 项）。
- **Priority**：medium
- **Depends On**：None
- **Discovered By**：Review R1（F-6）
- **Description**：
  - 3.1/FR-2 称 49 项，库表 50 行（B 组 21 行），TR-3.1 对齐将歧义。
- **Acceptance Criteria Addressed**：AC-2
- **Test Requirements**：
  - `rule` TR-I-6.1：全库统一为 50 项（B3a/b 计 2 项），3.1/3.3/FR-2/概述/TR-3.1 同步；证据为 grep 一致


---

## 实施进展备注

- **2026-10-05 代码基线落地**（用户批准后先行）：在 `src/simulation/` 建立 pytest 测试代码基线——集中配置（`config/sensor_params.yaml` + `config/test_thresholds.yaml`，阈值与 spec 4/5 章逐条对齐）、50 项障碍物库（`obstacles.py`）、46 条用例场景注册与执行器（`scenarios.py` + `runner.py`）、判定器（`verdict.py`，含 Wilson CI/稳定窗/门禁判定）、合成后端（`backends.py`，种子驱动确定性模型，支持 3 类故障注入与 7 种降级组合）；pytest 159 项全绿（含 TC-L/U/C/F 四套门禁、配置-规格一致性、安全 0 碰撞、故障注入负向测试）、`ruff check .` 无告警；文档两份（`docs/sensor_test_standard.md` 标准指导书 + `docs/user_guide.md` 使用说明）。
- **口径**：该基线对应 Task 2 的配置/判定器骨架部分与 Task 8~12 的判定逻辑先行实现；传感器观测暂由合成后端产生（`n_pending_backend` 机制保留），**不构成** Task 1（引擎选型 PoC/ADR）与 GT 取证框架的完成，Task 1~12 状态维持 pending，待引擎选型后接入真实后端并按 2.4 采样计划全量取证。
- **2026-10-05 补充交付（设计图 + 演示 PPT）**：按四类补齐程序设计图共 7 张（架构类：01 框架分层 / 03 传感器架构；流程类：02 执行泳道 / 05 执行策略；数据类：06 数据流图；模块交互类：07 模块交互时序图；另含 04 障碍物介绍图），由 `scripts/make_diagrams.py` 图即代码生成至 `src/simulation/docs/diagrams/`，标准指导书与使用说明已按四类编目，test_docs 强制存在性。演示 PPT `src/simulation/docs/sensor_test_overview.pptx`（12 页，深浅三明治版式，嵌入全部 7 图）由 `scripts/make_deck.js` 生成，经 python-pptx 越界检查（0 问题）与 LibreOffice 渲染逐页目检（修复泳道箭头压字、图内测试计数 159→160、封底标签孤字三处）后交付。
