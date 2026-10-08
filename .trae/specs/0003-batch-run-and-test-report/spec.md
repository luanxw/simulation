# 运行时批次选择与可视化测试报告 - 需求规格说明书

> 阶段：Specify。本文件只定义"做什么"，不写任务分解与实现方案。

## 概述
- **摘要**：为现有 46 条传感器仿真测试用例（TC-L/U/C/F）新增"运行时按批次配置选择用例与数据批次执行"能力，并在每次执行后生成自包含可视化 HTML 报告，连同测试数据定义、原始结果与环境元数据统一归档，同时维护跨版本历史总览页用于对外发布。
- **目的**：
  1. 测试执行不再依赖 pytest 过滤或手写 Python 脚本，使用者可通过可命名、可复用、可留痕的批次配置选择"跑哪些用例、用哪批数据"。
  2. 每次执行产出标准化、可对外发布的可视化报告：按激光 / USS（超声）/ 相机 / 融合四专题展示执行条数与通过率，并可下钻到每条用例、每条检查项的实测数值与门限证据，使结论在被质疑时可快速自证。
  3. 测试数据（批次配置、数据集定义、种子等）与测试结果（verdict、报告、环境元数据）归档到同一不可变目录，按版本累积，支持跨版本追溯与趋势查看。
- **目标用户**：感知/测试工程师（配置批次、执行、归因）、测试负责人与部门评审方（看通过率与证据）、外部/上级质疑方（离线打开报告核验证据）。

## 目标
- 一条命令按 YAML 批次执行选定用例 × 选定数据批次，选择条件可临时由命令行覆盖。
- 每次运行生成归档目录，内含：自包含 `report.html`、机器可读 `results.json`、元数据 `manifest.json`、批次配置快照、数据集定义快照。
- 报告首页按四专题（激光 / USS / 相机 / 融合）汇总执行用例数、通过数、通过率；两次点击内可下钻到任意检查项的实测值、判定运算符、门限、Wilson 置信区间。
- 归档根目录维护 `index.html` 历史总览：列出所有已归档版本、各专题通过率与总体通过率，并可进入任一历史版本的单次报告。
- 相同批次 + 相同 seed + 相同代码版本重跑，结果数值完全一致（可复现）。

## 非目标
- 不接入真实仿真引擎或真实采集数据集（沿用 spec 0002 的后端替换路线）；外部数据集（external）本期只预留注册 schema，不实际执行。
- 不实现自动上传服务器、邮件分发、用户权限或在线服务（"对外发布"指产出可整体拷贝/挂载任意静态 Web 服务的自包含目录）。
- 不产出 PDF 版报告。
- 不提供用例/阈值的图形化编辑能力，不引入数据库。
- 不改变任何现有用例的判定逻辑、阈值与 46 条用例集合。

## 背景与上下文
- 现有执行入口只有 Python API：[runner.py](file:///Users/allen/source/positec/simulation/src/simulation/runner.py) 的 `run_tc / run_suite / run_all`，返回可 JSON 序列化的 verdict dict（含每条 check 的 `name/status/value/op/threshold`，检出率条件另含 Wilson CI）；日常运行依赖 pytest 过滤，无独立 CLI、无落盘、无报告。
- 用例注册在 [scenarios.py](file:///Users/allen/source/positec/simulation/src/simulation/scenarios.py)：`Scenario(tc_id, suite, title, world, kind)`，suite ∈ {L, U, C, F}，world ∈ W0/W1/W2/W3/组合，kind ∈ static/dynamic/drive/safety；46 条编号固定。
- 配置集中在 [config/](file:///Users/allen/source/positec/simulation/src/simulation/config)（YAML），装载器 [thresholds.py](file:///Users/allen/source/positec/simulation/src/simulation/thresholds.py)；采样种子在 `test_thresholds.yaml` 的 `sampling.default_seeds`，全部随机量经 `rng_for(key, seed)` 派生，已具备跨进程可复现性。
- [user_guide.md](file:///Users/allen/source/positec/simulation/src/simulation/docs/user_guide.md) Q5 已建议调用方把 verdict 归档到 `reports/`，但从未实现；`.gitignore` 当前未忽略 `reports/`。
- 运行环境为 conda `simulation-py312`（Python 3.12，已装 pyyaml）；`pyproject.toml` 的 `dependencies` 目前为空（PyYAML 已被代码实际使用但未声明）。

## 功能需求
- **FR-1（批次配置选择用例）**：提供 YAML 批次定义，支持按专题（L/U/C/F）、用例编号通配（如 `TC-L-*`、`TC-U-03`）、白名单（include）、黑名单（exclude）、场景标签（world、kind）选择用例；空选择条件等于全量 46 条。
- **FR-2（命令行覆盖与预览）**：提供命令行入口执行批次；命令行可对专题/用例/标签/排除项做临时收窄覆盖；支持 dry-run 预览"本次将执行哪些用例 × 哪些数据集"而不实际执行。
- **FR-3（数据批次维度）**：引入数据集注册表（配置文件），批次可声明引用一个或多个数据集；执行矩阵为"数据集 × 用例"，每条结果记录所属数据集 id。首个数据集为合成数据集（synthetic，沿用默认种子，可携带如 seeds 的参数组表达多批数据）；同时为外部数据集（external：path + checksum 等字段）预留 schema，未来接入不改选择与归档模型。
- **FR-4（选择防错）**：选择结果为空、引用不存在的用例编号/数据集/标签时，必须报错并以非零退出码终止，错误信息需列出可选值，禁止静默执行空集合或忽略未知项。
- **FR-5（归档产物）**：每次执行在归档根目录（默认 `reports/`）下创建独立归档目录 `<版本标识>_<UTC时间戳>/`，写入 `results.json`（全部 verdict 原始数据）、`manifest.json`（元数据）、`report.html`、批次配置快照、数据集定义快照；同一版本重复执行不覆盖既有归档。
- **FR-6（元数据与证据链）**：`manifest.json` 至少包含：版本标识、运行时间戳、git commit SHA 与工作区是否脏、Python 版本、后端名称、seed、数据集清单与参数、批次选择条件快照、用例总数/通过数、检查项总数/通过数。
- **FR-7（单次可视化报告）**：`report.html` 为单文件自包含页面（CSS/JS 全部内联，不引用任何外部网络资源，断网双击可开）：抬头展示版本、时间、commit、seed、数据集；主体按四专区分组展示用例执行数、通过数、通过率与检查项统计；可展开查看每条用例每个检查项的 status/value/op/threshold，检出率类条件同时展示 Wilson CI。
- **FR-8（跨版本历史总览）**：归档根目录生成/刷新 `index.html`：以版本为行列出运行时间、各专题通过率、总体通过率，并链接到对应单次报告；提供命令手动重建总览。
- **FR-9（退出码语义）**：全部选用例通过退出码 0；有用例失败时退出码非零但报告与归档仍完整生成；选择/配置错误以非零退出码终止且不产生归档。
- **FR-10（文档与示例）**：用户指南补充"批次配置 → 执行 → 阅读报告 → 归档发布"完整章节；仓库内提供至少一个可直接运行的示例批次文件（如激光专项批次）。

## 非功能需求
- **NFR-1（依赖克制）**：报告生成仅使用 Python 标准库（字符串模板），运行期依赖维持 PyYAML 一个第三方库；不引入 Jinja2、pandas、图表库等。
- **NFR-2（可复现）**：沿用 `rng_for` 种子体系；数据集 seeds 参数生效路径唯一且被记录；同输入重跑数值结果逐字节一致。
- **NFR-3（性能）**：在默认数据集 × 全量 46 条用例规模下，报告与总览页生成耗时 < 5 秒（不含用例执行本身）。
- **NFR-4（可移植）**：兼容 Python ≥ 3.10（开发/运行环境 3.12）；路径处理跨平台；归档目录可整体拷贝、压缩后在任意机器离线打开。
- **NFR-5（仓库洁净）**：`reports/` 归档产物不入库（加入 `.gitignore`）；示例批次与数据集注册表等模板配置入库。
- **NFR-6（向后兼容）**：`run_tc / run_suite / run_all` 现有调用方式与 verdict 结构不变；新能力以新增模块与可选参数承载。

## 约束
- **技术**：src-layout，包代码在 `src/simulation/`，测试镜像于 `tests/`；配置集中于 YAML；提交前 `ruff check .` 与 `pytest` 必须全绿，新增行为必须伴随测试；规格与用户指南使用中文，代码标识符使用英文。
- **业务**：四专题命名固定——激光（LiDAR，L）、USS/超声（U）、相机（C）、融合（F）；报告面向外部评审，证据必须为数值型，禁止截图充当证据。
- **依赖**：无需外部服务或凭据；git 元数据通过本地 `git` 命令获取（非 git 环境下该字段标记为 unavailable，不致命）。

## 假设
- 版本标识来源优先级：命令行 `--version` > 批次 YAML 中版本字段 > 自动生成 `dev-<YYYYMMDDHHmmss>`；归档目录名对版本标识做文件名安全化处理。
- 归档根目录默认 `reports/`，可由命令行 `--out` 覆盖；历史总览固定位于归档根的 `index.html`，排序即时间序（目录名含 UTC 时间戳），不依赖文件系统软链接。
- 首个合成数据集 id 为 `synthetic-default`，未显式声明数据集的批次默认使用它；数据集可通过参数覆盖采样种子（沿用 `sampling` 其余配置），用于表达"多批数据"；verdict 按数据集分别记录。
- "测试数据归档到一起"在合成阶段指：批次配置、数据集定义、seed、git commit 等可复现输入全部快照入归档；external 数据集未来以"路径 + sha256 校验和 + 元数据快照"方式归档引用，本期只定义字段不实现执行。
- 选择合并语义：命令行提供的筛选项与批次配置按交集收窄，命令行排除项为追加排除；确切规则在用户指南写明并由测试固化。

## 验收标准

> 每条 AC 有且仅有一种 Type：`rule`（客观二值）或 `rubric`（质量评分）。

### AC-1：命令行运行入口存在且可用
- **Type**：`rule`
- **Given**：已安装依赖的 Python 3.10+ 环境
- **When**：执行 `python -m simulation.cli run --batch <批次文件>`
- **Then**：命令按批次完成执行并在终端打印汇总（四专题用例数/通过率）
- **Pass Condition**：不带 `--batch` 时默认全量执行 46 条；`--help` 列出全部参数；命令以退出码 0 结束（全绿基线）
- **Evidence**：终端命令与输出；`tests/` 中 CLI 测试用例

### AC-2：批次 YAML 支持完整用例选择维度
- **Type**：`rule`
- **Given**：一份批次 YAML，含 suites、include（通配）、exclude、tags（world/kind）选择段
- **When**：解析并执行该批次；同时分别用命令行 `--suite/--tc/--tag/--exclude` 覆盖
- **Then**：实际执行集合与选择语义一致（suites/include 并集 → 标签过滤 → 排除；命令行交集收窄、排除追加）
- **Pass Condition**：通配（`TC-L-*`）、多专题、world/kind 标签、白/黑名单、命令行覆盖五类情形各有测试断言解析出的用例集合
- **Evidence**：`tests/` 选择器单测；dry-run 实际输出

### AC-3：数据批次维度端到端生效
- **Type**：`rule`
- **Given**：数据集注册表含 `synthetic-default`，批次声明一个或多个数据集
- **When**：执行批次
- **Then**：执行矩阵为数据集 × 用例；`results.json` 中每条结果带数据集 id 与数据集参数（含 seed）；注册表为 external（path、checksum 字段）预留 schema
- **Pass Condition**：多数据集批次的结果条数 = 数据集数 × 用例数；数据集 seeds 覆盖实际影响随机结果且写入 manifest；external 字段可被装载器解析（不执行）
- **Evidence**：`tests/` 数据集装载与执行矩阵单测；归档 `results.json` / `manifest.json`

### AC-4：选择错误必须显式失败
- **Type**：`rule`
- **Given**：批次引用未知用例编号（如 `TC-X-99`）、未知数据集、未知标签值，或选择结果为空
- **When**：执行（含 dry-run）
- **Then**：命令打印包含可选值提示的错误信息，以非零退出码终止，且不创建归档目录
- **Pass Condition**：四类错误各有测试断言退出码非零与错误文本；归档目录不存在
- **Evidence**：`tests/` CLI/选择器负向测试

### AC-5：每次执行产生完整自包含归档
- **Type**：`rule`
- **Given**：一次成功执行
- **When**：检查归档根目录
- **Then**：生成 `archive/<版本标识>_<UTC时间戳>/`，含 `report.html`、`results.json`、`manifest.json`、批次配置快照、数据集定义快照；同版本重复执行生成新目录、不覆盖
- **Pass Condition**：测试以临时目录为归档根执行后断言上述文件齐全、JSON 可解析、两次同版本运行产生两个目录
- **Evidence**：`tests/` 归档单测；实际产物路径

### AC-6：manifest 元数据完整
- **Type**：`rule`
- **Given**：一次归档执行
- **When**：解析 `manifest.json`
- **Then**：含版本标识、时间戳、git commit SHA、工作区脏标记、Python 版本、后端名称、seed、数据集清单及参数、选择条件快照、用例总数与通过数、检查项总数与通过数
- **Pass Condition**：逐字段断言存在且与本次执行一致；非 git 环境下 commit 字段为 `unavailable` 且不报错
- **Evidence**：`tests/` manifest 单测

### AC-7：报告首页四专题汇总
- **Type**：`rule`
- **Given**：一次执行生成的 `report.html`
- **When**：在浏览器（file://）打开
- **Then**：抬头显示版本/时间/commit/seed/数据集；主体出现激光、USS、相机、融合四个分区，各显示用例执行数、通过数、通过率与检查项统计；另含总体汇总
- **Pass Condition**：测试断言 HTML 含四专题名称及与 `results.json` 一致的统计数字
- **Evidence**：`tests/` 报告内容断言；浏览器打开截图（人工核验留档）

### AC-8：报告可下钻至检查项证据
- **Type**：`rule`
- **Given**：报告中任一用例条目
- **When**：展开该用例
- **Then**：显示用例标题、pass/fail 状态及全部检查项，每项含 name、status、value、op、threshold；检出率类条件显示 Wilson CI 上下界
- **Pass Condition**：测试断言每条 verdict 的每个 check 字段都出现在 HTML 数据中；从首页到任一检查项详情的交互路径 ≤ 2 次点击（专题分区→用例展开）
- **Evidence**：`tests/` 报告内容断言；浏览器人工核验

### AC-9：HTML 报告完全离线自包含
- **Type**：`rule`
- **Given**：`report.html` 与 `index.html`
- **When**：断网后以 file:// 直接打开
- **Then**：样式、折叠交互、专题展示全部正常
- **Pass Condition**：自动化扫描两个 HTML 文件不含 `http://` / `https://` 外部引用（链接到本地归档的相对路径除外），无外链 `<script src>` / `<link href>`
- **Evidence**：`tests/` 静态扫描用例；断网浏览器核验

### AC-10：跨版本历史总览自动维护
- **Type**：`rule`
- **Given**：归档根下存在多个历史归档
- **When**：完成一次新执行，或手动执行重建命令
- **Then**：`reports/index.html` 列出全部归档版本、运行时间、各专题通过率与总体通过率，版本名链接到对应 `archive/.../report.html`（相对路径）
- **Pass Condition**：测试构造多个归档后断言总览行数、各单元格数值与链接路径；重建命令幂等
- **Evidence**：`tests/` 总览页单测；实际 index.html

### AC-11：相同输入重跑结果可复现
- **Type**：`rule`
- **Given**：同一份批次、同一数据集、同一 seed、同一代码提交
- **When**：连续执行两次
- **Then**：两次 `results.json` 中所有 verdict 数值完全一致
- **Pass Condition**：测试比对两次结果的 `checks[].value` 与 pass 状态完全相同（时间戳/manifest 运行时间字段除外）
- **Evidence**：`tests/` 复现单测

### AC-12：退出码与失败语义
- **Type**：`rule`
- **Given**：存在失败用例的执行（如经故障注入后端或放宽门限的批次）与配置错误场景
- **When**：分别执行
- **Then**：有用例失败时退出码非零但归档与报告完整（失败用例在报告中红色可查）；选择/配置错误退出码非零且无归档产生
- **Pass Condition**：测试分别断言两类场景的退出码与产物存在性
- **Evidence**：`tests/` CLI 退出码测试

### AC-13：测试、静态检查与仓库洁净
- **Type**：`rule`
- **Given**：全部实现完成
- **When**：运行 `pytest -q` 与 `ruff check .`
- **Then**：pytest 全绿、ruff 无告警；`reports/` 已加入 `.gitignore`；新增模块（选择/数据集/归档/报告/CLI）均有对应测试文件
- **Pass Condition**：两条命令退出码 0；测试清单覆盖选择器、数据集、执行矩阵、归档、manifest、HTML 内容与自包含、总览、退出码
- **Evidence**：命令真实输出；`.gitignore` diff

### AC-14：文档与示例齐备
- **Type**：`rule`
- **Given**：实现完成
- **When**：审查用户指南与配置目录
- **Then**：用户指南新增"批次配置 → 命令执行 → 报告阅读 → 归档对外发布"章节（含合并语义、退出码、归档结构说明）；配置目录至少有一个可直接运行的示例批次（如激光专项）
- **Pass Condition**：按文档命令原样执行可成功生成归档与报告；示例批次 dry-run 输出与其声明一致
- **Evidence**：用户指南章节；示例文件；按文档执行的终端输出

### AC-15：报告的专业可读性
- **Type**：`rubric`
- **Dimension**：非测试专业读者能否快速准确读懂报告结论
- **Scale**：1-5
- **Anchors**：1 = 版面混乱、看不懂通过率口径；3 = 信息齐全但需要测试人员讲解；5 = 首次阅读者 30 秒内从首页看懂四专题与总体通过率、明确红绿含义与版本时间
- **Pass Threshold**：>= 4
- **Evidence**：实际 report.html/index.html 页面；评审人独立阅读记录

### AC-16：证据可辩护性
- **Type**：`rubric`
- **Dimension**：被外部质疑某条用例结论时，报告提供原始数值证据的能力
- **Scale**：1-5
- **Anchors**：1 = 只有红绿结论、无数值；3 = 能找到 value/threshold 但需翻多页或无 CI/版本信息；5 = 3 次点击内看到该检查项 value/op/threshold/Wilson CI/seed/版本/commit，且归档目录自包含可整体发走
- **Pass Threshold**：>= 4
- **Evidence**：下钻路径实操；归档目录结构与 manifest

### AC-17：批次与数据集配置的可扩展性
- **Type**：`rubric`
- **Dimension**：后续新增批次、数据集、标签维度及接入 external 数据集的成本
- **Scale**：1-5
- **Anchors**：1 = 新增批次/数据集需改代码；3 = 加配置即可但 external 接入路径不清；5 = 新增批次与合成数据集仅改 YAML，标签派生自用例字段，external schema 字段与归档预留清晰、有文档指引
- **Pass Threshold**：>= 4
- **Evidence**：配置文件 schema、用户指南扩展章节、评审人按文档试新增一个批次

## 待澄清问题
- 无。2026-10-08 已通过交互确认四项关键决策：①选择维度同时覆盖用例与数据批次，external 数据集预留；②YAML 批次 + CLI 覆盖；③自包含 HTML + 机器可读 JSON；④归档 + 跨版本历史总览，发布形态为静态目录。其余默认见"假设"，随 Approve 一并确认。
