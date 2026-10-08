# 0003 独立评审报告（R1）

- **评审轮次**：R1（规格批准后首次独立终审）
- **评审日期**：2026-10-08
- **评审人**：独立上下文 agent（未参与本规格任何实施；仅阅读、运行与写本文件，未改动 `src/`、`tests/` 任何文件）
- **评审基线 commit**：`7c43e374f1f641ad7626a6bfa11920e54c382a0b`（分支 `spec/0003-batch-run-and-test-report`，工作区干净）
- **评审方法**：通读 spec.md / tasks.md / 全部实现与 8 个测试文件；独立重跑 pytest、ruff；在 `/tmp` 下真实生成全量、激光、多数据集、自定义、失败注入五类报告并直接阅读 HTML 原文；对 external 拦截、退出码、幂等、损坏容错、排序、可扩展性逐一构造场景实证（非照抄 tasks.md 数字）。

## 结论：fail

- rule 类 AC：**AC-4 fail**，其余 AC-1/2/3/5~14 共 13 条 pass。
- rubric：AC-15 = 5、AC-16 = 5、AC-17 = 5，均 ≥4。
- 按规则「所有 rule pass 且三条 rubric 均 ≥4 才给 pass」，因 AC-4（FR-4 选择防错）存在**非法命令行标签被静默执行为"假全绿"**的阻断性缺陷，本轮 **fail**。整改后可直接复审，缺陷定位与修复建议见 F1。

## rule 检查点（AC-1~AC-14）

| AC | 规格要求要点 | 证据（代码:行 / 测试 / 评审人实证） | 结果 |
|---|---|---|---|
| AC-1 | CLI 入口可用；无 `--batch` 全量 46；`--help` 列全参数；全绿退出 0 | [cli.py](file:///Users/allen/source/positec/simulation/src/simulation/cli.py#L56-L79) 参数定义；[__main__.py](file:///Users/allen/source/positec/simulation/src/simulation/__main__.py)；`test_help_all_levels`、`test_run_full_matrix_archives_and_prints_summary`、`test_module_invocation_as_subprocess`。实证：全量运行「46 次执行…总体 46/46」`EXIT=0`；`run --help` 九参数（--batch/--version/--suite/--tc/--tag/--exclude/--seed/--out/--dry-run）全部在位 | **pass** |
| AC-2 | suites∪include→tags→exclude；CLI 交集收窄、exclude 追加；五类情形测试；排序 L/U/C/F | [selection.py](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L233-L267)（`_select_side`/`select_tcs`/`_tc_sort_key`）；强断言测试 `test_world_tag_matches_combined_world_values`（含 W1/W2 组合、「任意」、与注册表全集合比对）、`test_override_intersects_suite_and_tcs`（精确断言仅 TC-L-01）、`test_override_exclude_is_additive`、`test_results_are_sorted`。实证：lidar∪跨专题→TC-L-01；safety-dynamic∩`--tag kind=safety`→恰好 F-09/F-10；`--suite U,C`→22；双 `--exclude` 后仅剩 TC-L-10 | **pass** |
| AC-3 | 数据集×用例矩阵；结果带数据集 id 与 seed 参数；seed 优先级 cli>dataset>sampling_default；external 仅解析不执行 | [execution.py](file:///Users/allen/source/positec/simulation/src/simulation/execution.py#L35-L64)；[selection.py](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L274-L295)（`resolve_datasets`）；[runner.py](file:///Users/allen/source/positec/simulation/src/simulation/runner.py#L77-L81)；`test_matrix_is_dataset_cross_tcs`、`test_dataset_seeds_recorded_in_record`、`test_seed_override_applies_to_all_datasets`、`test_external_dataset_rejected_at_execution`。实证：自定义双数据集批次 2×2=4、两组 seeds 分别为 `[11,22,33]/sampling_default` 与 `[42]/dataset` 且两组 verdict 确因 seed 不同而不同；`--seed 42` 实跑 manifest 记 `source: cli`；external 批次 dry-run 可预览、实跑退出 2 且无归档 | **pass** |
| AC-4 | 未知 TC/数据集/标签值/空选择必须非零退出、错误信息列可选值、**禁止静默执行空集合或忽略未知项** | 批次 YAML 路径合规：[selection.py](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L160-L178) 对标签键/值列合法值、未知 TC（[L204-L210](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L204-L210)）、未知数据集（[datasets.py](file:///Users/allen/source/positec/simulation/src/simulation/datasets.py#L127-L134)）。**但 CLI 覆盖路径完全不校验枚举值**：实证 `--tag world=W9`（不存在的标签值）静默命中 world=「任意」的 [TC-F-13](file:///Users/allen/source/positec/simulation/src/simulation/scenarios.py#L74)，实跑 1 条并 `EXIT=0`（假全绿）；`--tag kind=foo`、`--suite X` 仅得通用「选择结果为空」，不列合法值。根因：[cli.py `_tag`](file:///Users/allen/source/positec/simulation/src/simulation/cli.py#L41-L53) 只校验键名；[select_tcs](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L244-L260) 对 override 不走枚举校验；[_world_matches](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L215-L218) 的「任意」兜底使非法 world 不致空集。现有 `test_selection_errors_exit_2_without_archive` 只断言退出码与「错误：」前缀，漏掉该假绿路径 | **fail**（见 F1，blocker） |
| AC-5 | 归档五件套齐全可解析；同版本不覆盖 | [archive.py](file:///Users/allen/source/positec/simulation/src/simulation/archive.py#L134-L188)；`test_archive_writes_all_artifacts`、`test_same_version_creates_distinct_dirs`、`test_report_renderer_optional`。实证：`/tmp/sim-review/archive/*/` 两个目录均含 report.html/results.json/manifest.json/batch.snapshot.yaml/datasets.snapshot.yaml；同版本 `same` 连跑生成两个不同时间戳目录；同秒冲突序号 `-1` 有单测 | **pass** |
| AC-6 | manifest 字段齐全且与执行一致；非 git 环境 commit=unavailable 不致命 | [archive.py](file:///Users/allen/source/positec/simulation/src/simulation/archive.py#L104-L131)；`test_manifest_fields_complete_and_consistent`（逐字段）、`test_git_unavailable_outside_repo`（真实非 git 临时目录 + monkeypatch 双通道）。实证真实 manifest 含 version/created_at/git{commit,dirty}/python/backend/seed(含 source)/datasets(path/checksum 预留)/selection 快照/counts(总体+四专题)/files，commit 与评审基线一致；计数 46/46、127/127 | **pass** |
| AC-7 | 抬头版本/时间/commit/seed/数据集；四专题执行/通过/通过率+检查项统计；总体汇总；数字与 results.json 一致 | [report.py](file:///Users/allen/source/positec/simulation/src/simulation/report.py#L141-L231)；`test_report_has_four_suites_with_matching_stats`。实证真实 report.html：抬头八行元数据齐全（seeds 与来源在数据集行）、两张大数字卡片、四专题 h2 徽章 11/11、12/12、10/10、13/13 与检查项 36/26/24/41，与 manifest/results.json 完全一致 | **pass** |
| AC-8 | 展开用例见 name/status/value/op/threshold；检出率含 Wilson CI；路径≤2 次点击 | [report.py](file:///Users/allen/source/positec/simulation/src/simulation/report.py#L87-L138)；[runner.py](file:///Users/allen/source/positec/simulation/src/simulation/runner.py#L58-L64)（n/ci 随 check 落 verdict）；`test_every_check_evidence_rendered`（遍历每条 verdict 的每个 check 断言 name/value/threshold 入页）、`test_wilson_ci_rendered_for_detection_checks`（精确断言 `[lo, hi]` 与 n）、`test_details_live_inside_suite_section`、`test_multiple_datasets_rendered_as_groups`。实证全量报告 46 个 `<details class="tc">` 全部位于对应专题 h2 内；失败注入报告行原文 `OB-B1@L:0.5m｜失败｜0.0｜≥｜0.98｜n=600｜[0.0, 0.0064]`；专题锚点→展开用例即见证据，2 次点击内 | **pass** |
| AC-9 | report.html/index.html 零外链、无外链 script/link，断网可开 | `test_report_is_offline_self_contained`、`test_index_offline_self_contained`。评审人对真实三个 HTML 做 `grep -cE 'http://|https://|<script|<link '` 均为 0；内联 `<style>`、原生 `<details>` 无 JS；页内仅 `#suite-*` 锚点 | **pass** |
| AC-10 | index 列全部版本/时间/四专题与总体通过率，相对链接；可手动重建；损坏容错；幂等 | [history.py](file:///Users/allen/source/positec/simulation/src/simulation/history.py#L24-L147)；`test_index_lists_all_archives_with_rates_and_links`、`test_empty_root_renders_placeholder`、`test_corrupt_manifest_skipped_and_flagged`、`test_rebuild_idempotent_except_timestamp`、`test_rebuild_index_command`。实证：2 归档真实总览相对链接 `archive/<dir>/report.html` 正确、空专题显「—」；手工放入损坏目录后重建，损坏行红标 `⚠ manifest 无法解析：JSONDecodeError` 且正常行不受影响；固定生成时间两次渲染字节一致。**遗留**：按目录名字典序而非时间戳排序，版本标签字典序与时间反向时乱序（F2，minor），不影响 AC-10 明列功能 | **pass**（附 F2） |
| AC-11 | 同批次/同 seed/同 commit 两次 results.json 数值完全一致 | `test_reproducible_results_json_bytes`（逐字节）、`test_reproducible_same_input_same_verdicts`（逐 check value）。实证：safety-dynamic+`--seed 42` 两次独立归档 `diff results.json` 无差异（RESULTS-BYTES-IDENTICAL）；落盘用 `sort_keys`+固定缩进+尾换行 | **pass** |
| AC-12 | 失败退出非零但归档/报告完整；配置错误非零且无归档 | `test_failed_tc_exits_1_but_archive_complete`、`test_unknown_tc_exits_2_without_archive`、`test_missing_batch_file_exits_2`、`test_bad_tag_syntax_exits_2`、`test_selection_errors_exit_2_without_archive`。实证：注入 `lidar_blind` 跑 TC-L-05+TC-F-06 → verdict pass=False、7 检查失败，五件套+index.html 仍完整、报告红色可定位；未知 TC/未知标签值/缺失批次/交集为空四类均 `EXIT=2` 且 out 目录不存在 | **pass** |
| AC-13 | pytest 全绿、ruff 无告警、reports/ 入 .gitignore、新模块均有测试 | 评审人独立重跑（输出见下节）：**255 passed in 9.21s**、ruff **All checks passed!**；[.gitignore:21](file:///Users/allen/source/positec/simulation/.gitignore#L21) 含 `reports/`，`git ls-files` 确认零入库；0003 八个测试文件实测 21/25/10/10/9/5/12/7＝**99** 项，与模块一一对应（runtime 上下文由 execution/runner 测试间接覆盖） | **pass** |
| AC-14 | 用户指南新增完整章节（合并语义/退出码/归档结构）；≥1 个可直接运行示例批次；按文档原样执行成功 | [user_guide.md 第 5 章](file:///Users/allen/source/positec/simulation/src/simulation/docs/user_guide.md#L170-L252)（5.1~5.6 全覆盖）；[lidar-suite.yaml](file:///Users/allen/source/positec/simulation/src/simulation/config/batches/lidar-suite.yaml)、[safety-dynamic.yaml](file:///Users/allen/source/positec/simulation/src/simulation/config/batches/safety-dynamic.yaml)；`test_example_batches_load_and_select_expected_tcs`（断言精确命中集合）、`test_user_guide_has_batch_report_section`、`test_guide_lidar_command_runs_as_written`（提取指南原文命令并子进程原样执行，断言 report.html+index.html）。评审人实证 dry-run 激光=11、safety-dynamic=5（交集 safety=2），均与声明一致 | **pass** |

测试断言质量抽查（18 个函数，远超 8 个下限）：上述表中选择器 3 例、执行矩阵/复现/external 4 例、归档 3 例、报告 5 例、总览 3 例、CLI 负向与失败 5 例、文档 2 例均为**强断言**（精确集合/逐字段/逐字节/真实子进程），未发现假测试；唯一断言偏弱处为 `test_details_live_inside_suite_section`（`page.index("</details>")` 只定位首个闭合标签），但 DOM 归属另由 details 计数与多数据集分组测试补强，不构成问题；真正的覆盖缺口是 AC-4 缺「CLI 非法标签值」回归（见 F1）。

## rubric 评分

| AC | 分数 | 锚点理由 | 阈值判定 |
|---|---|---|---|
| AC-15 报告专业可读性 | **5** | 真实阅读 `/tmp/sim-review/.../report.html` 原文：首屏即两张大数字卡片（用例通过率/检查项通过率，全绿显绿、失败注入报告显红 `card fail`），其下抬头元数据（版本/UTC 时间/commit/seed/数据集）+ 四个中文专题分区，每分区徽章直接写「11/11 通过（100.0%）」与检查项 x/y；红绿同时配「通过/失败」中文文字而非仅靠颜色；专题锚点导航。非测试专业读者 30 秒内能回答「哪个版本、四专题各多少、总体红绿」，命中 5 分锚点 | ≥4，达标 |
| AC-16 证据可辩护性 | **5** | 实操点击路径：index.html 点版本名（第 1 跳）→ report.html 抬头即见 commit SHA/运行时间/seeds=[11,22,33]（含来源）/数据集/归档目录；点用例 `<details>`（第 2 跳）即见每条检查 value、中文判定符（≤/≥）、threshold、样本量 n、Wilson 95% CI 上下界（真实例：`0.0 ≥ 0.98，n=600，CI [0.0, 0.0064]`，失败红色加粗）。归档目录五件套（results.json 原始 verdict + manifest + 两份快照 + 报告）可整体压缩发走，index 为入口；信息无须翻页、不缺 CI/版本，命中 5 分锚点 | ≥4，达标 |
| AC-17 配置可扩展性 | **5** | 评审人仅按用户指南 5.1 节、在仓库外 `/tmp` 手写一个新批次（`include: [TC-U-10, TC-F-06]` + `tags.kind: [dynamic]`，未改任何代码），dry-run 立即正确列出 2 条用例标题与「1 数据集 × 2 用例」，正式执行成功并生成完整归档（总墙钟 1.76 s）。新增合成数据集确为纯 YAML（datasets.yaml 校验白名单）；external 的 path/checksum schema 可被装载、进 manifest 与 datasets.snapshot.yaml、误执行有明确报错并指向指南 5.2，标签键限定从 Scenario 字段派生；命中 5 分锚点 | ≥4，达标 |

## 真实命令输出摘录

```text
$ PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q
........................................................................ [ 28%]
........................................................................ [ 56%]
........................................................................ [ 84%]
.......................................                                  [100%]
255 passed in 9.21s

$ /usr/local/anaconda3/envs/simulation-py312/bin/ruff check .
All checks passed!

# 0003 八个测试文件分文件计数（评审人 --collect-only 实测）
test_datasets.py:21  test_selection.py:25  test_execution.py:10  test_archive.py:10
test_report.py:9     test_history.py:5    test_cli.py:12       test_docs.py:7   （合计 99）

$ python -m simulation.cli run --version review-demo --out /tmp/sim-review
执行完成：1 数据集 × 46 用例 = 46 次执行
  激光 LiDAR：11/11 通过（100.0%），检查项 36/36
  USS 超声：12/12 通过（100.0%），检查项 26/26
  相机：10/10 通过（100.0%），检查项 24/24
  融合：13/13 通过（100.0%），检查项 41/41
总体：46/46 用例通过，失败 0；检查项 127/127      → EXIT=0

$ python -m simulation.cli run --batch .../lidar-suite.yaml --version review-lidar --out /tmp/sim-review
执行完成：1 数据集 × 11 用例 = 11 次执行 …… EXIT=0
# 两次同批次同 seed（--seed 42）归档 results.json：diff 无输出 → RESULTS-BYTES-IDENTICAL
# grep -cE 'http://|https://|<script|<link ' index.html archive/*/report.html → 三个文件均 0

# AC-17 自定义批次（/tmp/review-batch-dynamic.yaml）
$ python -m simulation.cli run --batch /tmp/review-batch-dynamic.yaml --dry-run
用例（2）：
  TC-U-10  动态接近响应  [U]
  TC-F-06  动态跟踪  [F]
合计：1 数据集 × 2 用例 = 2 次执行                → DRYEXIT=0；正式执行 RUNEXIT=0（real 1.76s）

# F1 复现（AC-4 阻断性缺陷）
$ python -m simulation.cli run --tag world=W9
执行完成：1 数据集 × 1 用例 = 1 次执行
  融合：1/1 通过（100.0%），检查项 1/1
总体：1/1 用例通过，失败 0；检查项 1/1          → EXIT=0（非法标签值被静默当作有效过滤）
$ python -m simulation.cli run --tag kind=foo    → EXIT=2  错误：选择结果为空：…（未列合法值）
$ python -m simulation.cli run --suite X         → EXIT=2  错误：选择结果为空：…（未列合法值）
# 对照：批次 YAML 内 tags.kind:[foo] → 错误：标签 kind 含未知值 ['foo']；可选：['drive','dynamic','safety','static']
```

## Actionable Findings

### F1（blocker）：CLI 覆盖标签/专题不做枚举校验，非法 world 标签被静默执行并返回 0（违反 FR-4 / AC-4）

- **现象（评审人复现）**：
  - `run --tag world=W9`：`W9` 不是任何用例的 world 合法值（合法集合由 scenarios 派生：W0/W1/W2/W3），命令却选中 world 标注为「任意」的 TC-F-13 实跑 1 条、归档完整报告并 `EXIT=0`——命令行打错标签会得到**误导性的全绿归档**，正是 FR-4 明令禁止的「静默执行…忽略未知项」。
  - `run --tag kind=foo`、`run --suite X`：虽 `EXIT=2` 且无归档，但错误仅为通用「选择结果为空：没有任何用例同时满足批次与命令行条件」，**未按 FR-4 列出可选值**，用户无法区分是拼写错误还是真实空交集。
- **证据/根因**：
  1. [cli.py:41-53](file:///Users/allen/source/positec/simulation/src/simulation/cli.py#L41-L53) `_tag` 只校验等号格式与键名 ∈ {world, kind}，不校验取值；`--suite` 经 `_csv`（[cli.py:37-38](file:///Users/allen/source/positec/simulation/src/simulation/cli.py#L37-L38)）同样无枚举校验。
  2. [selection.py:244-260](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L244-L260) `select_tcs` 对 override 一侧直接 `_select_side`，绕过了批次侧的枚举校验 [_parse_tags](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L160-L178) 与 suites 校验（[selection.py:109-112](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L109-L112)）。
  3. [selection.py:215-218](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L215-L218) `_world_matches` 对「任意」用例一律放行（该兜底对**合法** world 是正确设计），叠加无校验后使非法 world 得到非空结果，绕过了末尾的空集保护。
  4. 测试缺口：`test_selection_errors_exit_2_without_archive` 仅含 `kind=foo` 且只断言「错误：」前缀，没有 `world=<非法值>` 用例，故假绿路径未被拦住。
- **修复建议**（不改判定语义，仅补防错层；批次 YAML 路径与「任意」对合法值的兜底保持不变）：
  1. 在 `_override_from_args`（或 `select_tcs` 入口）对 override 做枚举校验：`suites` 对照 `VALID_SUITE`，`tags` 各值对照 `selection._valid_tag_values(key)`；非法即抛 `SelectionError`，错误文本与批次侧同构并列出合法值（如「标签 world 含未知值 ['W9']；可选：['W0','W1','W2','W3']」「未知专题 'X'；可选：L, U, C, F」），CLI 自然走退出码 2、不归档。
  2. 在 `tests/test_cli.py` 增三类回归：`--tag world=W9`、`--tag kind=foo`、`--suite X` 均断言退出码 2、stderr 含「可选」与合法值、out 目录不存在；另加一条保证合法 `--tag world=W1` 仍能选中「任意」用例（防止误删兜底语义）。
  3. 顺手收紧现有 `test_selection_errors_exit_2_without_archive`：对负向错误断言「可选值」提示而非仅「错误：」前缀。

### F2（minor）：历史总览按归档目录名字典序排序，非严格时间序

- **现象**：spec 假设承诺「排序即时间序（目录名含 UTC 时间戳）」。[history.py:31](file:///Users/allen/source/positec/simulation/src/simulation/history.py#L31) 对目录名整体 `sorted()`，时间戳位置随版本标签长度/词法变化。评审人构造 `v2.0_2026-10-05`（早）与 `v10.0_2026-10-08`（晚）两个归档，页面中 v10.0 行排在 v2.0 之前（字典序 v10<v2），与时间反向；`dev-<stamp>` 与带标签前缀混排时同理。
- **影响**：单元格数值与链接均正确，仅行序可能误导「最新在最上/最下」的直觉。
- **修复建议**：排序键改为从目录名解析尾部 `YYYYMMDDTHHMMSSZ`（自动版本 `dev-<stamp>` 直接取整体），失败再回退 manifest `created_at`；补一条字典序与时间序相反的排序测试。

### F3（minor）：dry-run 对 external 数据集显示合成默认 seeds，略有误导

- **现象**：external 批次 dry-run 输出 `ext-real [external] … seeds=[11, 22, 33]（来源 sampling_default）`（[selection.py:274-314](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L274-L314) 未区分 kind）。external 本期不执行，预览仅用于展示矩阵，但把合成种子挂在外部数据包上易让读者误以为外部数据也用该种子复现。
- **修复建议**：external 条目在 `resolve_datasets/preview` 中 seeds 显示为 `—（external 不参与合成采样）`；不影响实跑拦截（已正确退出 2）。

### F4（minor）：未知精确用例编号的提示指向文件而非直接列可选值

- **现象**：FR-4 措辞为「错误信息需列出可选值」。未知精确编号当前报「全部 46 条编号见 scenarios.py」（[selection.py:209](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L209)），通配无命中才列前 5 个示例。文件指引用途可行，但严格按 FR-4 字面未在终端列出可选值。
- **修复建议**：错误信息附带全部 46 个编号（或至少分组列出 `TC-L-01..11、TC-U-01..12、…`）；可与 F1 的错误文本统一改造。

## 复核须知（必须整改项）

1. **阻断项（决定结论）**：完成 F1——CLI `--suite/--tag` 取值纳入与批次 YAML 同构的枚举校验，非法值退出码 2、错误信息列合法值、不产生归档；特别确认 `--tag world=<非法值>` 不再静默执行「任意」用例；补齐三类 CLI 回归测试与合法值不回归测试。修复后重跑 `pytest -q`（应仍 ≥255 且新增用例）与 `ruff check .` 全绿。
2. F2/F3/F4 为 minor，建议同分支一并修复；若延期请在 tasks.md 登记为后续任务并说明理由。
3. 复审方式：在 F1 修复后的新 commit 上，重点重放本报告 F1 的三条命令（`--tag world=W9` / `--tag kind=foo` / `--suite X`）并核对退出码、错误文本与零归档，其余 AC 可采信 R1 证据做回归确认。

## R2 复审（2026-10-08）

- **复审基线 commit**：`fc8d4f5717113bd7140bdeff3af42700bb41594d`（分支 `spec/0003-batch-run-and-test-report`，工作区干净；R1 基线 7c43e37，整改提交 fc8d4f5）
- **复审人**：全新独立上下文 agent，未参与实施与 R1 评审；仅阅读、运行与在本文件末尾追加，未改动 `src/`、`tests/` 任何文件（全部实证产物写入 `/tmp/sim-r2`，仓库 `reports/` 零写入，`git status` 干净）。
- **复审方法**：不照抄 tasks.md 数字——独立重放 F1 三命令并分离 stdout/stderr；自写 `/tmp` 脚本构造 F2/F3 场景（字典序/时间序相反、双类损坏条目、external 注册表注入 + 完整 `cli.main` 路径）；F4 三类编号实跑；全量 pytest/ruff 重跑；对 AC-2/3/4/10 相关语义另做 CLI 抽查。

### 复审结论：pass

F1 blocker 与 F2/F3/F4 三个 minor **全部闭环**；14 条 rule 全 pass，三条 rubric 维持 R1 的 5 分（均 ≥4），满足「所有 rule pass 且三条 rubric ≥4」。

### F1~F4 逐条核验表

| 项 | 复审人真实执行（PYTHONPATH=src，python3.12） | 退出码 | 关键 stderr / stdout | 归档 | 结论 |
|---|---|---|---|---|---|
| F1-a | `python -m simulation.cli run --tag world=W9 --out /tmp/sim-r2/f1a` | **2** | stderr：`错误：覆盖标签 world 含未知值 ['W9']；可选：W0, W1, W2, W3`（stdout 为空，错误确在 stderr） | `/tmp/sim-r2/f1a` 不存在 | **闭环** |
| F1-b | `python -m simulation.cli run --tag kind=foo --out /tmp/sim-r2/f1b` | **2** | stderr：`错误：覆盖标签 kind 含未知值 ['foo']；可选：drive, dynamic, safety, static` | 不存在 | **闭环** |
| F1-c | `python -m simulation.cli run --suite X --out /tmp/sim-r2/f1c` | **2** | stderr：`错误：覆盖条件含未知专题 ['X']；可选：L, U, C, F` | 不存在 | **闭环** |
| F1 防误伤 | `python -m simulation.cli run --suite F --tag world=W1 --out /tmp/sim-r2/ok` | **0** | `1 数据集 × 11 用例 = 11 次执行`，融合 11/11；归档 results.json 的 tcs 实测为 `TC-F-01..05、07..11、TC-F-13`，**TC-F-13（world="任意"）在列** | 五件套齐全 | **闭环**（「任意」兜底未被误伤） |
| F2 | `/tmp/sim-r2/f2_check.py`：write_archive 注入 v2.0@2026-10-05（早）/ v10.0@2026-10-08（晚），断言 `late.name < early.name`（字典序确实相反）；另放带时间戳损坏条目 v0.9@10-01、无时间戳正常条目（manifest created_at=10-03）、无时间戳损坏条目 | 脚本 0 | iter_archives 实测行序 = `v0.9(损坏,10-01) → zz-manual-nostamp(10-03) → v2.0(10-05) → v10.0(10-08) → zzz-no-timestamp-corrupt(最后)`，与期望完全一致；index 中 v2.0 位置先于 v10.0；损坏行红标「⚠ manifest 无法解析：JSONDecodeError」仍参与排序显示 | — | **闭环**（内嵌时间戳主键、同秒序号、created_at 回退、损坏排最后四条路径均独立实证，强于仓库内单测） |
| F3 | `/tmp/sim-r2/f3_check.py`：parse_datasets 注入 external 数据集 ext-real（path+checksum），monkeypatch `load_datasets` 后调 resolve_datasets/preview/execute_batch，并经 `cli.main` 走完整 CLI | resolve/preview 正常；实跑 **2** | resolve：`seeds=[]、seed_source=external`（`--seed 42` 覆盖下仍为 `[]`）；preview：`ext-real [external] … path=data/ext.zip（external 数据集本期不执行，不使用合成种子）`，无 `[11, 22, 33]`；execute_batch 抛 DatasetError；CLI 实跑 stderr 报 external 不执行、退出 2 | 实跑无归档；dry-run 退出 0 且无 out 目录 | **闭环** |
| F4 | `--tc TC-Q-01`、`--tc TC-L-99`、`--tc 'TC-Z-*' --dry-run` | 均 **2** | 精确编号：`错误：未知用例编号 'TC-Q-01'；可用编号：TC-L-01~TC-L-11、TC-U-01~TC-U-12、TC-C-01~TC-C-10、TC-F-01~TC-F-13（共 46 条）`；越界编号 TC-L-99 同文；通配无命中：`通配模式 'TC-Z-*' 未命中任何用例；可用编号区间：…（共 46 条）`（dry-run 同样拦截） | 三种均无归档 | **闭环**（终端直接分组列可选编号 + 总数） |

根因核对：修复位于 [selection.py `_validate_override`](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L256-L275)（select_tcs 应用覆盖前校验，[L282-L285](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L282-L285)），与批次 YAML 侧校验同构、未触碰 [`_world_matches`](file:///Users/allen/source/positec/simulation/src/simulation/selection.py#L227-L230) 对合法值的「任意」兜底——定位与 R1 修复建议一致，无绕过面（dry-run 与实跑共用 select_tcs，F4-c 已证 dry-run 同样生效）。

### 回归与全量验证

```text
$ PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python -m pytest -q
........................................................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 82%]
...............................................                          [100%]
263 passed in 9.78s

$ /usr/local/anaconda3/envs/simulation-py312/bin/ruff check .
All checks passed!
```

- 数字真实复现：**263 passed**（= R1 255 + 8 整改回归），ruff 零告警。
- 0003 八测试文件 `--collect-only` 实测：test_datasets 21 / **test_selection 31（+6）** / test_execution 10 / test_archive 10 / test_report 9 / **test_history 6（+1）** / **test_cli 13（+1）** / test_docs 7，合计 107（R1 为 99，+8 与声称一致）；8 项新测试单独点名执行 `8 passed`。
- **新增/收紧测试断言质量评价（逐条，均为强断言、无被绕过）**：
  1. `test_override_unknown_suite_rejected_with_options`：raises match「未知专题」且断言含「可选」与 L/F；
  2. `test_override_unknown_tag_values_rejected_with_options`：world=W9、kind=foo 双例，逐字断言 W0/W1/W2/W3 与 static/safety 全部出现在错误文本；
  3. `test_override_unknown_tag_key_rejected`：未知键 raises；
  4. `test_override_valid_world_still_matches_any_world_case`：既断言 TC-F-13 仍命中，又断言结果集**全部**为「任意」或含 W1——防「修校验顺手删兜底」的双向守护；
  5. `test_unknown_exact_tc_error_lists_available_ids`：精确断言四个分组区间字符串齐全；
  6. `test_external_dataset_preview_has_no_synthetic_seeds`：seeds==[]、source=external、提示语在、合成种子串不在；
  7. `test_sorted_by_embedded_timestamp_not_version_lexical`：先断言前置条件 `late.name < early.name`，再精确比对行序列表与页面位置；
  8. `test_valid_world_tag_runs_and_keeps_any_world_case`（CLI）：`cli.main` 真实退出 0 并读归档 results.json 断言 TC-F-13；
  收紧的 `test_selection_errors_exit_2_without_archive` 由「错误：」前缀升级为 5 类场景分别断言「可选」或「选择结果为空」并逐例断言 out 目录不存在。
  反证强度推演：若移除 `_validate_override`，用例 1/2 将分别失配「未知专题」/「DID NOT RAISE」（W9 会再次静默命中 TC-F-13）；回退旧排序/旧 F3/F4 文本，用例 5/6/7 必失败——测试对缺陷真实敏感。
- **既有语义抽查（整改未破坏）**：①合法 `--tag world=W1` 选中 11 条含 TC-F-13、`--tag kind=drive` 4 条；②交集收窄 lidar 批次 ∩ `--suite F` → 退出 2「选择结果为空」（值合法、仅空交集，文案区分正确）；③exclude 追加：`--suite L --exclude TC-L-11 --exclude 'TC-L-0[1-5]'` dry-run 恰剩 TC-L-06~10 共 5 条、退出 0、零产物；④多数据集批次（synthetic-default + synthetic-seed42 × TC-L-01/TC-U-03）实跑 2×2=4，manifest seed 分别为 `[11,22,33]/sampling_default` 与 `[42]/dataset`，同用例两数据集首检值因 seed 不同而不同（0.124274 vs 0.039273）；⑤external 实跑拦截退出 2（见 F3）。

### AC 状态

- **AC-2（独立复核 pass）**：CLI 实测交集收窄、exclude 追加（精确+通配双 `--exclude`）、合法 world/kind 标签、L 起始排序、dry-run 零产物均与规格语义一致；选择器测试 31 项全绿。
- **AC-3（独立复核 pass）**：多数据集矩阵条数=数据集数×用例数、每结果带数据集 id、seeds 与来源写入 manifest 且实际影响数值；external schema 可解析、不执行（F3 实证）。
- **AC-4（独立复核 pass，由 R1 fail 转 pass）**：未知标签值（world/kind，批次 YAML W7 与 CLI W9/foo 两路径均实测）、未知专题、未知用例编号/通配、未知数据集、空交集/空选择五类均退出 2、错误文本列可选值、不创建归档；F1 的假全绿路径已被枚举校验在选择前阻断，合法「任意」兜底保留。
- **AC-10（独立复核 pass）**：时间序排序（F2）、损坏条目标注且不致命、相对链接 `archive/<dir>/report.html`、版本/运行时间/总体单元格与 manifest 一致（sem3 真实归档实测）、零外链、固定生成时间渲染幂等均成立。
- **AC-1、AC-5~9、AC-11~14**：整改 diff 仅触及 selection.py（校验/错误文案/external 预览）、history.py（排序键）、user_guide.md 一行测试计数注释与 3 个测试文件；report.py、archive.py、runner.py、datasets.yaml、示例批次均未改动，R1 所依赖的产物/报告/复现证据不被影响，且 263 全量回归全绿——**采信 R1 pass 结论**。
- **rubric**：AC-15=5、AC-16=5 —— 报告渲染链路零改动，R1 的页面实测与下钻证据持续有效，维持 5 分；AC-17=5 —— 批次/合成数据集纯 YAML 扩展路径未变，external 预览文案由「误挂合成种子」改为明确 path 与「本期不执行」提示，可扩展性/防误导性只增不减，维持 5 分。

### 新发现

无。（附带观察，非缺陷：override 非法值文案以「覆盖标签/覆盖条件」前缀与批次侧区分，措辞不同构但同样列出可选值，满足 FR-4；lowercase 如 `--suite l` 现按未知值拦截并列合法值，属 FR-4 要求的收紧，规格定义专题本就为大写。）

### 最终判定

R2 复审 **pass**：R1 唯一 blocker（F1）与 F2/F3/F4 均已真实闭环并由 8 项强断言回归固化；14 条 rule 全 pass、三条 rubric 均 5 分，`263 passed`、`ruff All checks passed!` 独立复现，未发现新增问题。
