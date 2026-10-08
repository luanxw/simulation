# 运行时批次选择与可视化测试报告 - 实施计划

> 阶段：Plan / Implement。由 spec.md 派生：每条 AC 必须至少被一个任务覆盖。
> 任务按依赖排序、垂直切片（一个任务交付可验证的完整增量）。
> 标题中禁止写状态；状态只存在于 `Status` 字段。
>
> AC 覆盖矩阵：AC-1→T7；AC-2→T2；AC-3→T1/T3；AC-4→T2/T7；AC-5→T4；AC-6→T4；
> AC-7→T5；AC-8→T5；AC-9→T5/T6；AC-10→T6；AC-11→T3；AC-12→T7；AC-13→T1~T9；
> AC-14→T8；AC-15→T5；AC-16→T4/T5；AC-17→T1/T2/T8。
> 分支：`spec/0003-batch-run-and-test-report`（批准后从 develop 创建）。

## Task 1：数据集注册表、装载器与依赖声明
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [datasets.yaml](file:///Users/allen/source/positec/simulation/src/simulation/config/datasets.yaml)（synthetic-default / synthetic-seed42，external schema 注释）、[datasets.py](file:///Users/allen/source/positec/simulation/src/simulation/datasets.py)（Dataset/dataclass、parse_datasets、load_datasets、get_dataset、DatasetError）、[test_datasets.py](file:///Users/allen/source/positec/simulation/tests/test_datasets.py)。
  - pyproject.toml `dependencies = ["pyyaml>=6.0"]`。
  - TR-1.1~1.4：`pytest tests/test_datasets.py -q` → 21 passed；`ruff check` → All checks passed!（2026-10-08，分支 spec/0003）。
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 新增 `src/simulation/config/datasets.yaml`：数据集注册表 v1。
    - 内置 `synthetic-default`（kind: synthetic；title/description；params 默认沿用 sampling，不重复写 seeds）。
    - 内置一个参数组示例 `synthetic-seed42`（params.seeds: [42]），演示"多批数据"如何用 seeds 参数组表达。
    - 注释中写明 external 数据集预留 schema（kind: external；path、checksum.sha256、title、description），本期不执行。
  - 新增 `src/simulation/datasets.py`：`load_datasets()`（带缓存，仿 thresholds.py 风格）、`get_dataset(dataset_id)`（未知 id 抛 `DatasetError` 并列出可用 id）、数据集结构校验（id/kind 必填、kind ∈ {synthetic, external}、synthetic 参数白名单仅含 seeds 且为正整数列表；external 必须含 path）。
  - 在 `pyproject.toml` 的 `dependencies` 补声明 `pyyaml>=6.0`（代码早已实际依赖，本需求 CLI 全新环境安装的前提）。
  - 新增 `tests/test_datasets.py`。
- **Acceptance Criteria Addressed**：AC-3、AC-13、AC-17
- **Test Requirements**：
  - `rule` TR-1.1：装载注册表返回两个内置合成数据集，字段齐全；`get_dataset("synthetic-default")` 成功，未知 id 抛 DatasetError 且错误文本含全部可用 id。
  - `rule` TR-1.2：external 示例条目（测试内构造或注册表注释样例经解析函数校验）可通过 schema 校验，缺 path 的 external 条目报错。
  - `rule` TR-1.3：seeds 非法（0/负数/非整数/空列表）时校验报错。
  - `rule` TR-1.4：`pytest tests/test_datasets.py -q` 全绿，`ruff check src/simulation/datasets.py tests/test_datasets.py` 无告警。
- **Notes**：不修改任何现有用例与阈值文件。

## Task 2：批次 YAML 与用例选择器
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [selection.py](file:///Users/allen/source/positec/simulation/src/simulation/selection.py)（BatchConfig/SelectionOverride、load_batch/parse_batch、select_tcs 交集收窄、resolve_datasets、preview、SelectionError）与 [test_selection.py](file:///Users/allen/source/positec/simulation/tests/test_selection.py)。
  - 实施中修复两处真实缺陷：空 tuple 默认值被 list 校验拒绝；排序改为专题 L/U/C/F 固定顺序+编号数字（与注册顺序一致），并由测试固化。
  - TR-2.1~2.5：新增 25 项选择器测试全绿；全套 `pytest -q` → 206 passed（无回归）；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 新增 `src/simulation/selection.py`：
    - `BatchSelection`/`BatchConfig` 数据类：name、version_label（可空）、datasets（默认 `[synthetic-default]`）、suites、include、exclude、tags（仅允许派生自 Scenario 现有字段的标签键：world、kind）。
    - `load_batch(path)`：装载 YAML、基础校验（未知顶层键/未知标签键报错并提示可用值）。
    - `select_tcs(batch, override=None) -> tuple[str, ...]`：选择语义 =（suites 展开 ∪ include 通配（fnmatch，如 `TC-L-*`、`TC-U-03`））→ 按 tags 过滤（world 支持包含匹配，兼容 `W1/W2` 组合值；kind 精确匹配）→ 减去 exclude；suites/include 均空 = 全量 46 条。
    - `SelectionOverride`（CLI 覆盖）：suites / tcs / tags / exclude；覆盖与批次条件取**交集收窄**，override.exclude 与 batch.exclude **并集追加**。
    - `SelectionError`：未知 TC 编号、通配无命中、未知数据集 id、未知标签键/值、最终结果为空，五类错误各自错误信息列出合法可选值。
    - `preview(batch, override) -> str`：dry-run 文本（数据集 × 用例清单与计数）。
  - 新增 `tests/test_selection.py`。
- **Acceptance Criteria Addressed**：AC-2、AC-4、AC-17
- **Test Requirements**：
  - `rule` TR-2.1：通配/多专题/白名单/黑名单/world 组合标签（W1/W2）/kind 标签/空条件全量，七类情形的解析集合逐一断言与预期 TC 集合相等且结果按编号排序。
  - `rule` TR-2.2：override 交集收窄与排除追加语义各一例断言；override 指定 `--tc` 时忽略批次 suites/include 的收窄结果符合"交集"定义（即只保留同时满足者），并在测试注释写明语义。
  - `rule` TR-2.3：五类 SelectionError 各有测试，错误文本包含合法值提示；空结果拒绝执行。
  - `rule` TR-2.4：批次引用未知数据集 id 报错（与 datasets.py 校验联动）。
  - `rule` TR-2.5：pytest/ruff 对新增文件全绿无告警。
- **Notes**：标签键刻意限定 world/kind，不引入自由 tags 字段，避免与用例注册脱节。

## Task 3：批次执行编排（数据集 × 用例矩阵）与可复现
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [runtime.py](file:///Users/allen/source/positec/simulation/src/simulation/runtime.py)（ContextVar seeds 上下文）、[execution.py](file:///Users/allen/source/positec/simulation/src/simulation/execution.py)（execute_batch / summarize / SUITE_TITLES，RunRecord 可 JSON 序列化）；微调 [runner.py](file:///Users/allen/source/positec/simulation/src/simulation/runner.py)（`_seeds()` 读上下文、`run_tc(..., seeds=None)` 可选参数，默认行为不变）；新增 [test_execution.py](file:///Users/allen/source/positec/simulation/tests/test_execution.py)。
  - TR-3.1~3.6：矩阵条数、数据集 seeds、`--seed` 覆盖、同输入两次执行 verdict 全等、无参调用与历史行为一致、summary 手工核对、故障注入失败计数、JSON 可序列化共 9 项测试全绿；全套 `pytest -q` → 215 passed；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：high
- **Depends On**：Task 1、Task 2
- **Description**：
  - 新增 `src/simulation/runtime.py`：基于 contextvars 的执行上下文（当前数据集 id、seeds 覆盖），提供 `run_context(dataset)` 上下文管理器。
  - 微调 `src/simulation/runner.py`：`_seeds()` 优先读 runtime 上下文中的 seeds 覆盖，回退 `sampling()["default_seeds"]`；`run_tc` 增加可选参数 `seeds: list[int] | None = None`（默认 None 时行为完全不变，经上下文透传，保证向后兼容 NFR-6）。
  - 新增 `src/simulation/execution.py`：
    - `execute_batch(batch, override=None, backend=None, seed_override=None) -> RunRecord`：对每个选中数据集 × 每条选中用例执行 `run_tc`，记录 dataset_id、数据集参数、verdict；同后端实例在数据集间复用（注意数据集只改 seeds，不改 backend 状态；故障/降级状态不跨用例残留，沿用现有 runner 的 try/finally 约定）。
    - `summarize(record) -> dict`：总体 + 四专题（L/U/C/F）的用例执行数、通过数、通过率、检查项总数/通过数。
    - RunRecord 为纯 dict/可 JSON 序列化结构，含 schema_version、batch 归一化快照、datasets 解析结果、results（按 dataset 分组）、summary。
  - 新增 `tests/test_execution.py`。
- **Acceptance Criteria Addressed**：AC-3、AC-11、AC-13
- **Test Requirements**：
  - `rule` TR-3.1：双数据集 × 多用例批次的结果条数 = 数据集数 × 用例数，每条结果带正确 dataset_id。
  - `rule` TR-3.2：数据集 seeds 覆盖实际生效：`synthetic-seed42` 与默认数据集的 manifest/record 中 seeds 字段不同；同一数据集两次执行 verdict 逐字段一致（可复现）。
  - `rule` TR-3.3：相同批次/seed 连续两次 `execute_batch` 产生的 results 中所有 `checks[].value` 与 pass 完全相等（AC-11 直接证据）。
  - `rule` TR-3.4：`run_tc("TC-L-01")` 无参调用结果与改动前基线一致（现有 156 项测试全绿即回归证据）。
  - `rule` TR-3.5：summarize 四专题计数与手工从 RunRecord 统计一致；不存在的专题计数为 0 而不报错。
  - `rule` TR-3.6：新增文件 pytest/ruff 全绿；全套 pytest 不因 runner 改动回归。
- **Notes**：runner 微调仅限 `_seeds()` 取值来源与可选参数，判定逻辑零改动。

## Task 4：归档目录与 manifest 证据链
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [archive.py](file:///Users/allen/source/positec/simulation/src/simulation/archive.py)（safe_slug 保留中文、utc_stamp/iso_now、detect_git 默认锚定包源码目录、resolve_version、build_manifest、write_archive 含同秒冲突序号）、[test_archive.py](file:///Users/allen/source/positec/simulation/tests/test_archive.py)；[.gitignore](file:///Users/allen/source/positec/simulation/.gitignore) 增加 `reports/`。
  - 实施修正：自动版本 dev-<stamp> 不再重复拼接时间戳；git 探测锚点改为包源码目录（输出目录在仓库外时仍记录被测代码版本）。
  - TR-4.1~4.5：10 项测试全绿（产物齐全可解析、manifest 字段、git unavailable 不致命（monkeypatch）、同版本双目录、slug 安全化、results.json 逐字节可复现、reports/ 已忽略）；全套 `pytest -q` → 225 passed；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：high
- **Depends On**：Task 3
- **Description**：
  - 新增 `src/simulation/archive.py`：
    - `make_archive(root, version_label, run_record) -> Path`：目录名 `<safe(version)>_<UTC紧凑时间戳>`；同版本重复执行产生不同目录（时间戳冲突时追加序号），不覆盖。
    - 写入 `results.json`（RunRecord，UTF-8、缩进、ensure_ascii=False、键排序稳定）。
    - 写入批次快照 `batch.snapshot.yaml`（归一化后的批次定义）与 `datasets.snapshot.yaml`（本次引用到的数据集定义）。
    - 写入 `manifest.json`：schema_version、version、created_at(UTC ISO8601)、git.commit、git.dirty、python、backend、seed（含来源：dataset/--seed）、datasets 清单及参数、selection 条件快照、counts（用例/检查项，总体与四专题）、归档内文件清单。
    - git 探测：`git rev-parse HEAD` 与 `git status --porcelain`（超时/非 git 环境 → `"unavailable"`，不致命）。
  - 根 `.gitignore` 增加 `reports/`。
  - 新增 `tests/test_archive.py`（tmp_path 隔离）。
- **Acceptance Criteria Addressed**：AC-5、AC-6、AC-13、AC-16
- **Test Requirements**：
  - `rule` TR-4.1：执行后归档目录含 report 之外的全部四个文件（report.html 在 Task 5 接入；本任务先断言 results.json、manifest.json、两个快照存在且可解析）。
  - `rule` TR-4.2：manifest 逐字段断言：version/created_at/commit/dirty/python/backend/seed/datasets/selection/counts 均存在且与本次 RunRecord、批次一致。
  - `rule` TR-4.3：monkeypatch git 探测为失败时 commit == "unavailable" 且不抛异常。
  - `rule` TR-4.4：同版本连续两次归档生成两个不同目录、内容独立；版本标识中的路径分隔符/空格被安全化。
  - `rule` TR-4.5：`.gitignore` 含 `reports/`；新增测试与 ruff 全绿。
- **Notes**：时间戳/manifest 运行时间字段是 AC-11 复现比对时唯一允许的差异。

## Task 5：自包含单次 HTML 报告
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [report.py](file:///Users/allen/source/positec/simulation/src/simulation/report.py)（render_report：内联 CSS、原生 details 折叠、四专题分区、用例多数据集分组、check 表含 value/op/threshold/n/Wilson CI、动态内容 HTML 转义）与 [test_report.py](file:///Users/allen/source/positec/simulation/tests/test_report.py)。
  - 微调 [runner.py](file:///Users/allen/source/positec/simulation/src/simulation/runner.py)：专项检出类（TC-L-05/06/07、TC-U-03/04、TC-C-04）的每条 check 附加样本量 `n` 与 Wilson 95% `ci`（原计算结果此前被丢弃），门禁判定不变、既有测试无回归。
  - TR-5.1~5.5：9 项测试全绿（四专题统计一致、全部 check 证据入页、CI 渲染、零外链自包含、失败红色可定位、多数据集分组、details 位于专题内、XSS 转义、归档端到端写入）；rubric TR-5.6/5.7 留独立评审在浏览器评分；全套 `pytest -q` → 234 passed；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：high
- **Depends On**：Task 4
- **Description**：
  - 新增 `src/simulation/report.py`：`render_report(run_record, manifest) -> str`（纯标准库字符串拼接/`string.Template`，不引第三方）。
    - 抬头：版本、运行时间、commit（含 dirty 标记）、seed、数据集清单、后端。
    - 总览条：总体用例通过率、检查项通过率。
    - 四专题分区（激光 LiDAR / USS 超声 / 相机 / 融合）：用例执行数、通过数、通过率、检查项统计；红/绿/灰配色（pass/fail/pending_backend）。
    - 用例下钻：每专题下用例行可就地展开（原生 `<details>` 或内联 JS），展示用例标题与全部 check：name、status、value、op、threshold；检出率条件（数据来自 runner 的 cond 统计，含 ci 字段时）展示 Wilson CI 上下界；多数据集结果分组展示。
    - CSS/JS 全部内联；页面注明报告生成时间与归档目录名。
  - 归档流程接入：Task 4 的归档目录写入 `report.html`（由 archive 调用 report 渲染，或 CLI 串联；保持 archive 单测可注入假 HTML）。
  - 新增 `tests/test_report.py`。
- **Acceptance Criteria Addressed**：AC-7、AC-8、AC-9、AC-13、AC-15、AC-16
- **Test Requirements**：
  - `rule` TR-5.1：渲染结果含四专题中文名（激光、USS、相机、融合）与每专题统计，数值与 summarize() 输出一致。
  - `rule` TR-5.2：RunRecord 中每条 verdict 的每个 check 的 name/status/value/op/threshold 均出现在 HTML；含 ci 的条件其上下界数值出现。
  - `rule` TR-5.3：静态扫描输出不含 `http://`、`https://`、外链 `<script src=`、`<link rel="stylesheet"`；file:// 打开所需资源全部内联。
  - `rule` TR-5.4：构造含 fail 用例与多数据集的 RunRecord，报告中失败用例与失败 check 可被字符串断言定位；下钻交互路径 ≤ 2 次点击（用例详情在专题分区内的 `<details>` 中，断言 DOM 层级结构）。
  - `rule` TR-5.5：report.html 经归档端到端写入并存在；pytest/ruff 全绿。
  - `rubric` TR-5.6：报告专业可读性；scale 1-5；anchors 1=版面混乱看不懂口径 / 3=信息齐但需讲解 / 5=首次阅读 30 秒看懂四专题与红绿；threshold >= 4；evidence：评审人在浏览器独立阅读 report.html 的记录。
  - `rubric` TR-5.7：证据可辩护性；scale 1-5；anchors 1=只有红绿 / 3=有 value/threshold 但难找或缺 CI / 5=3 次点击内看到 value/op/threshold/CI/seed/版本/commit；threshold >= 4；evidence：下钻实操与归档结构。
- **Notes**：rubric 由独立评审打分；实施期先以 rule TR-5.1~5.5 固化客观部分。

## Task 6：跨版本历史总览页
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [history.py](file:///Users/allen/source/positec/simulation/src/simulation/history.py)（iter_archives 扫描容错、render_index 自包含表格、rebuild_index 幂等写 root/index.html，相对链接 archive/<dir>/report.html）与 [test_history.py](file:///Users/allen/source/positec/simulation/tests/test_history.py)。
  - TR-6.1~6.4：5 项测试全绿（3 归档版本/时间/四专题通过率/相对链接、空根占位、损坏 manifest 跳过标注、零外链、固定生成时间幂等）；全套 `pytest -q` → 239 passed；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：medium
- **Depends On**：Task 5
- **Description**：
  - 新增 `src/simulation/history.py`：
    - `iter_archives(root) -> list[ArchiveMeta]`：扫描 `root/archive/*/manifest.json`，按目录名时间序解析。
    - `rebuild_index(root) -> Path`：聚合每个归档的版本、时间、四专题与总体通过率，生成根下 `index.html`（自包含内联样式；版本列为指向 `archive/<dir>/report.html` 的相对链接；含生成时间与归档总数）；幂等（重复生成内容除生成时间外一致）。
  - 每次 CLI run 完成后自动调用 rebuild_index。
  - 新增 `tests/test_history.py`。
- **Acceptance Criteria Addressed**：AC-9、AC-10、AC-13
- **Test Requirements**：
  - `rule` TR-6.1：构造 3 个归档（写 manifest.json + 占位 report.html）后重建，index.html 含 3 行版本、各专题通过率单元格与正确相对链接。
  - `rule` TR-6.2：空归档根生成"暂无记录"总览且不报错；损坏 manifest 的目录被跳过并在页内标注（不致命）。
  - `rule` TR-6.3：index.html 同样无任何外部 http(s) 引用。
  - `rule` TR-6.4：重复 rebuild 幂等（除生成时间戳外字节一致）；pytest/ruff 全绿。
- **Notes**：不做软链接；"latest" 入口通过总览页第一行天然实现。

## Task 7：CLI 装配与退出码
- **Status**：`completed`
- **Completion Evidence**：
  - 新增 [cli.py](file:///Users/allen/source/positec/simulation/src/simulation/cli.py)（argparse：run / rebuild-index 子命令；--batch/--version/--suite/--tc/--tag/--exclude/--seed/--out/--dry-run；退出码 0/1/2；串联 execute_batch→write_archive(render_report)→rebuild_index）、[__main__.py](file:///Users/allen/source/positec/simulation/src/simulation/__main__.py)（支持 `python -m simulation`）与 [test_cli.py](file:///Users/allen/source/positec/simulation/tests/test_cli.py)。
  - 配套重构 [archive.py](file:///Users/allen/source/positec/simulation/src/simulation/archive.py)：write_archive 以 report_renderer(record, manifest) 回调在归档内部 manifest 构建后渲染 report.html，保证报告抬头版本/时间与 manifest 一致（test_archive/test_report/test_history 同步更新）。
  - TR-7.1~7.5：11 项测试全绿（三级 --help、全量归档+终端四专题汇总、dry-run 零产物、未知 TC/缺失批次/坏标签→2、注入失败→1 且归档完整、--seed 写入 manifest、批次文件 suite+tag、rebuild-index 含空根、`python -m simulation.cli` 子进程实跑）；全套 `pytest -q` → 250 passed；`ruff check .` → All checks passed!（2026-10-08）。
- **Priority**：high
- **Depends On**：Task 5、Task 6
- **Description**：
  - 新增 `src/simulation/cli.py`（argparse、`main(argv=None) -> int`）：
    - `run`：`--batch PATH`（可空=全量默认批次）、`--version LABEL`、`--suite L,U`、`--tc TC-L-01`（可重复）、`--tag world=W1`（可重复）、`--exclude PAT`（可重复）、`--seed N`（覆盖数据集 seeds 为 [N] 并记录来源）、`--out DIR`（默认 reports）、`--dry-run`（只打印 preview，不执行不归档）。
    - `rebuild-index`：`--out DIR`。
    - 终端输出：执行矩阵计数、四专题用例通过率汇总、归档目录路径、总览页路径。
    - 错误处理：SelectionError/DatasetError/批次文件缺失 → stderr 明确信息 + 退出码 2，且不产生归档；用例失败 → 退出码 1，归档与报告完整生成；成功 → 0。
  - 新增 `src/simulation/__main__.py`，支持 `python -m simulation` 与 `python -m simulation.cli` 两种调用。
  - 新增 `tests/test_cli.py`。
- **Acceptance Criteria Addressed**：AC-1、AC-4、AC-12、AC-13
- **Test Requirements**：
  - `rule` TR-7.1：`python -m simulation.cli --help`、`run --help`、`rebuild-index --help` 退出码 0 且列出全部参数（subprocess 真实调用）。
  - `rule` TR-7.2：无 --batch 在 tmp out 下全量执行 46 条，退出码 0，产物含 report.html/results.json/manifest.json/index.html，终端汇总含四专题。
  - `rule` TR-7.3：`--dry-run` 输出用例与数据集清单、计数正确，且 out 目录下无 archive 产物。
  - `rule` TR-7.4：未知 TC（`--tc TC-X-99`）退出码 2、错误文本含合法值提示、无归档；不存在的 --batch 文件退出码 2。
  - `rule` TR-7.5：用例失败场景（同进程 main + monkeypatch 使一个 verdict 失败）退出码 1 但归档与报告完整；选择错误退出码 2 且无归档。
  - `rule` TR-7.6：`--seed 42` 生效：manifest seed 记录 42 与来源 `--seed`；同 seed 重跑结果一致。
  - `rule` TR-7.7：CLI 新测试全绿；ruff 全绿。
- **Notes**：测试以 `main([...])` 同进程注入 tmp out 为主，--help 用 subprocess 验真实入口。

## Task 8：示例批次与用户指南
- **Status**：`completed`
- **Completion Evidence**：
  - 新增示例批次 [lidar-suite.yaml](file:///Users/allen/source/positec/simulation/src/simulation/config/batches/lidar-suite.yaml)（激光 11 条、含字段中文注释）与 [safety-dynamic.yaml](file:///Users/allen/source/positec/simulation/src/simulation/config/batches/safety-dynamic.yaml)（F 专题 world W1/W2 × kind safety/dynamic，命中 F-06/07/09/10/11 共 5 条）。
  - [user_guide.md](file:///Users/allen/source/positec/simulation/src/simulation/docs/user_guide.md) 新增第 5 章「批次执行与可视化报告」（批次字段与交集/追加语义、数据集注册表与 external 预留、CLI 全参数与退出码 0/1/2、归档五件套与复现方法、报告取证路径、静态目录发布），后续章节顺延为 6-10，代码地图补入 0003 全部模块。
  - 补漏（spec 非目标合规）：[execution.py](file:///Users/allen/source/positec/simulation/src/simulation/execution.py) 在 execute_batch 拦截 external 数据集实际执行（抛 DatasetError → CLI 退出码 2、不归档），dry-run 纯解析仍可预览；新增对应负向测试，修复"external 被静默按合成跑"的缺口。
  - TR-8.1~8.3：dry-run 实测激光=11、安全/动态=5；[test_docs.py](file:///Users/allen/source/positec/simulation/tests/test_docs.py) 新增 3 项（示例批次装载与命中集合/交集收窄、指南章节关键锚点与章节重编号、指南激光命令解析后子进程原样执行并生成 report.html+index.html）；全套 `pytest -q` → 254 passed；`ruff check .` → All checks passed!（2026-10-08）。rubric TR-8.4 留独立评审打分。
- **Priority**：medium
- **Depends On**：Task 7
- **Description**：
  - 新增 `src/simulation/config/batches/lidar-suite.yaml`（激光 11 条专题批次，含中文注释说明各字段）。
  - 新增 `src/simulation/config/batches/safety-dynamic.yaml`（融合安全/动态标签批次，演示 tags 与多条件组合）。
  - 更新 `src/simulation/docs/user_guide.md`：新增章节"批次执行与可视化报告"，覆盖：
    - 批次 YAML 字段与选择/合并语义（交集收窄、排除追加）、数据集字段与 external 预留；
    - CLI 全部参数与退出码；
    - 归档目录结构、manifest 字段、复现方法；
    - 报告阅读路径（首页四专题 → 用例 → check 证据/CI）；
    - 对外发布方式（整体拷贝/压缩归档目录或挂载 reports/ 到静态 Web 服务；index.html 为入口）。
- **Acceptance Criteria Addressed**：AC-14、AC-17
- **Test Requirements**：
  - `rule` TR-8.1：两个示例批次经 `run --batch ... --dry-run` 输出清单与其声明一致（激光=11 条）。
  - `rule` TR-8.2：按用户指南新增章节中的命令原样执行（临时 out），成功生成归档并退出码 0。
  - `rule` TR-8.3：现有 `tests/test_docs.py` 风格下新增对示例批次可装载、指南章节存在关键命令的一致性测试；pytest/ruff 全绿。
  - `rubric` TR-8.4：配置可扩展性；scale 1-5；anchors 1=加批次要改代码 / 3=加 YAML 可但 external 路径不清 / 5=批次与合成数据集仅改 YAML、external 预留有文档；threshold >= 4；evidence：评审人按指南 5 分钟内新建一个自定义批次并 dry-run 成功。
- **Notes**：遵循既有"文档-配置一致性由测试守护"的约定。

## Task 9：端到端自验、证据归档与规格收尾
- **Status**：`completed`
- **Completion Evidence**（2026-10-08，conda simulation-py312，分支 spec/0003-batch-run-and-test-report）：
  - **TR-9.1 全量自验**：`ruff check .` → `All checks passed!`；`PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q` → `255 passed in 9.22s`。
  - **TR-9.2 端到端真实输出**：
    - 全量默认批次 `run --version e2e-full`：`1 数据集 × 46 用例 = 46 次执行`；激光 11/11（check 36/36）、USS 12/12（26/26）、相机 10/10（24/24）、融合 13/13（41/41）；总体 46/46、check 127/127；归档 `reports/archive/e2e-full_20261008T132839Z/`（五件套齐全）并生成 `reports/index.html`。
    - 激光示例批次 `--batch config/batches/lidar-suite.yaml --version e2e-lidar`：11/11 通过；safety-dynamic 批次 `--tag kind=safety --seed 42 --version e2e-safety42`：交集收窄为 2/2（check 5/5），manifest seed=`[{dataset: synthetic-default, seeds: [42], source: cli}]`。
    - dry-run `--suite U,C`：`合计：1 数据集 × 22 用例 = 22 次执行`，零产物；错误场景 `--tc TC-X-99`：stderr `错误：未知用例编号 'TC-X-99'；全部 46 条编号见 scenarios.py`，退出码 2。
    - **复现性**：相同批次+seed 42 两次执行（reports 与 /tmp 两个独立归档）`results.json` `diff` 字节一致（RESULTS-BYTES-IDENTICAL）。
    - **幂等**：连续两次 `rebuild-index`，index.html 去除生成时间戳后 `diff` 一致（INDEX-IDEMPOTENT）。
    - **失败语义（AC-12）**：注入 `lidar_blind` 故障跑 TC-L-05：verdict pass=False、7 项检查失败，归档五件套与 report.html 仍完整写出，报告含失败标记；CLI 退出码 1 路径由 test_cli::test_failed_tc_exits_1_but_archive_complete 固化。
    - **报告证据行实例**：`OB-B1@L:0.5m | 通过 | 实测值 1.0 | ≥ | 门限 0.98 | 样本量 n=600 | Wilson 95% CI [0.9906, 0.9997]`；报告与总览均无 http(s) 外链、无 script。
    - 端到端产物在已 gitignore 的 `reports/` 与 /tmp 下；`reports/` 未入库（删除操作需用户授权，保留待用户自行清理）。
  - **AC 覆盖核对**：rule 类 AC-1~AC-14 全部有自动化测试与真实产物证据（选择器 25、数据集 21、执行矩阵 10、归档 10、报告 9、总览 5、CLI 12、文档 7）；AC-4 补齐未知数据集/未知标签值/交集为空三类 CLI 退出码 2 测试（test_selection_errors_exit_2_without_archive）；rubric AC-15/16/17 留独立 Review 打分。
  - 指南测试总数同步为 255。
- **Priority**：medium
- **Depends On**：Task 8
- **Description**：
  - 真实环境（conda simulation-py312）端到端执行：全量默认批次、lidar-suite 示例、--dry-run、一次失败语义验证（临时批次收窄后用测试注入方式或记录为测试证据）、rebuild-index 幂等。
  - 全量 `pytest -q` 与 `ruff check .` 留证；清理本次产生的 reports/（已 gitignore，不入库）。
  - 回填本文件各任务 Completion Evidence；确认 AC 全覆盖；准备独立评审输入清单（spec/tasks 路径、运行命令、关键产物路径）。
- **Acceptance Criteria Addressed**：AC-13（DoD 总验收）
- **Test Requirements**：
  - `rule` TR-9.1：`PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q` 全绿，附真实输出数字；`ruff check .` 为 All checks passed。
  - `rule` TR-9.2：端到端命令真实输出（含归档路径、index.html、四专题汇总）粘贴入 Completion Evidence。
  - `rule` TR-9.3：tasks.md 无 pending/in_progress/blocked（评审 Issue 除外），每条 AC 至少有一个 completed 任务与其证据对应。
- **Notes**：本任务不写业务代码；发现缺口回开对应任务而非在此修补。

---

## 整改问题（Review fail 后使用）

> 评审的每条 actionable 发现，必须在重新选任务前在此落成 pending Issue。

### Issue-1（blocker，源自 R1 F1 / AC-4）：CLI 覆盖标签/专题缺枚举校验，非法 world 静默假全绿
- **Status**：`completed`（2026-10-08，待 R2 复核）
- **Blocked By**：—
- **Unblock Condition**：—
- **Completion Evidence**：selection.py 新增 `_validate_override`（select_tcs 应用覆盖前校验：suites∈VALID_SUITES、tags 键∈TAG_KEYS、值∈_valid_tag_values，错误文本与批次侧同构并列可选值）；tests/test_selection.py 增 4 项（非法专题/world/kind/标签键、合法 world=W1 仍含 TC-F-13 防回归）；test_cli.py 负向矩阵扩为 5 类并断言 stderr 含"可选"/"选择结果为空"，新增合法 world CLI 回归。真实重放：`--tag world=W9`→`错误：覆盖标签 world 含未知值 ['W9']；可选：W0, W1, W2, W3` 退出 2；`--tag kind=foo`、`--suite X` 同样退出 2；三种均无归档产生（NO-ARCHIVE）；合法 `--suite F --tag world=W1` 退出 0 且归档含 TC-F-13。

### Issue-2（minor，源自 R1 F2）：历史总览按目录名字典序而非时间戳排序
- **Status**：`completed`（2026-10-08，待 R2 复核）
- **Blocked By**：—
- **Unblock Condition**：—
- **Completion Evidence**：history.py 新增 `_archive_sort_key`（解析目录名内嵌 `YYYYMMDDTHHMMSSZ`+同秒序号；缺时间戳回退 manifest.created_at；再缺排最后），iter_archives 改按该键排序；test_history.py 增 `test_sorted_by_embedded_timestamp_not_version_lexical`（v2.0@10-05 早 / v10.0@10-08 晚，字典序 v10 在前但总览 v2.0 在前）。

### Issue-3（minor，源自 R1 F3）：external 数据集 dry-run 误显示合成 seeds
- **Status**：`completed`（2026-10-08，待 R2 复核）
- **Blocked By**：—
- **Unblock Condition**：—
- **Completion Evidence**：selection.py resolve_datasets 对 kind=external 给出 seeds=[]、seed_source="external"（即使 --seed 也不挂合成种子）；preview 对 external 显示 `path=...（external 数据集本期不执行，不使用合成种子）`；test_selection.py 增 `test_external_dataset_preview_has_no_synthetic_seeds`；execute_batch 拦截行为不变（test_external_dataset_rejected_at_execution 仍绿）。

### Issue-4（minor，源自 R1 F4）：未知精确用例编号错误未在终端列可选值
- **Status**：`completed`（2026-10-08，待 R2 复核）
- **Blocked By**：—
- **Unblock Condition**：—
- **Completion Evidence**：selection.py 新增 `_available_id_hint`（按专题分组 TC-L-01~TC-L-11、TC-U-01~TC-U-12、TC-C-01~TC-C-10、TC-F-01~TC-F-13 + 总条数），精确编号与通配无命中错误均直接在终端列出；test_selection.py 增 `test_unknown_exact_tc_error_lists_available_ids`。

### 整改后总验
- `ruff check .` → All checks passed!；`pytest -q` → **263 passed in 10.02s**（255 + 8 项整改回归）。指南测试总数同步 263。
