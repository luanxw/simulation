"""批次选择器测试（spec 0003 Task 2，TR-2.1~2.5）。"""

import pytest

from simulation.scenarios import SCENARIOS
from simulation.selection import (
    BatchConfig,
    SelectionError,
    SelectionOverride,
    default_batch,
    parse_batch,
    preview,
    resolve_datasets,
    select_tcs,
)

ALL_TCS = tuple(SCENARIOS)


def batch(**kw) -> BatchConfig:
    defaults = dict(
        name="t", version_label=None, datasets=("synthetic-default",),
        suites=(), include=(), exclude=(), tags={},
    )
    defaults.update(kw)
    return BatchConfig(**defaults)


# ---- TR-2.1：七类基本选择情形 ----

def test_empty_selection_is_all_46():
    assert select_tcs(batch()) == ALL_TCS
    assert len(ALL_TCS) == 46


def test_single_suite_expands_to_its_tcs():
    got = select_tcs(batch(suites=("L",)))
    assert got == tuple(tc for tc in ALL_TCS if tc.startswith("TC-L-"))
    assert len(got) == 11


def test_multiple_suites_union():
    got = select_tcs(batch(suites=("L", "U")))
    assert len(got) == 23
    assert set(got) == {tc for tc in ALL_TCS if tc.startswith(("TC-L-", "TC-U-"))}


def test_include_wildcard_and_exact_ids():
    got = select_tcs(batch(include=("TC-L-0[1-5]",)))
    assert got == ("TC-L-01", "TC-L-02", "TC-L-03", "TC-L-04", "TC-L-05")
    got_exact = select_tcs(batch(include=("TC-U-03", "TC-C-04")))
    # 排序按专题固定顺序 L/U/C/F，故 U 在 C 前
    assert got_exact == ("TC-U-03", "TC-C-04")


def test_exclude_removes_matches():
    got = select_tcs(batch(suites=("L",), exclude=("TC-L-11", "TC-L-0[1-9]")))
    assert got == ("TC-L-10",)


def test_world_tag_matches_combined_world_values():
    got = select_tcs(batch(tags={"world": ("W1",)}))
    # W1/W2 组合值的用例必须命中；W0-only 与 W2/W3 不命中；「任意」命中
    assert "TC-L-07" in got and "TC-F-13" in got
    assert "TC-L-01" not in got and "TC-C-05" not in got
    # 与注册表逐条核对
    expected = {tc for tc, sc in SCENARIOS.items()
                if sc.world == "任意" or "W1" in sc.world.split("/")}
    assert set(got) == expected


def test_kind_tag_exact_match():
    got = select_tcs(batch(tags={"kind": ("safety",)}))
    assert set(got) == {"TC-F-09", "TC-F-10"}


def test_results_are_sorted():
    from simulation.selection import VALID_SUITES

    def key(tc: str) -> tuple[int, int]:
        return VALID_SUITES.index(tc.split("-")[1]), int(tc.rsplit("-", 1)[1])

    got = select_tcs(batch(include=("TC-F-13", "TC-L-01", "TC-U-03")))
    assert got == ("TC-L-01", "TC-U-03", "TC-F-13")
    assert got == tuple(sorted(got, key=key))


# ---- TR-2.2：CLI 覆盖的交集收窄与排除追加 ----

def test_override_intersects_suite_and_tcs():
    # 批次选 L 专题，CLI 指定两条跨专题编号，交集只剩 TC-L-01
    got = select_tcs(batch(suites=("L",)),
                     SelectionOverride(tcs=("TC-L-01", "TC-U-03")))
    assert got == ("TC-L-01",)


def test_override_tags_narrow_batch():
    got = select_tcs(batch(suites=("F",)),
                     SelectionOverride(tags={"kind": ("safety",)}))
    assert set(got) == {"TC-F-09", "TC-F-10"}


def test_override_exclude_is_additive():
    got = select_tcs(batch(suites=("L",), exclude=("TC-L-01",)),
                     SelectionOverride(exclude=("TC-L-02",)))
    assert "TC-L-01" not in got and "TC-L-02" not in got
    assert "TC-L-03" in got


def test_disjoint_override_yields_empty_error():
    with pytest.raises(SelectionError, match="选择结果为空"):
        select_tcs(batch(suites=("L",)), SelectionOverride(suites=("C",)))


# ---- TR-2.3 / TR-2.4：五类显式错误 ----

def test_unknown_exact_tc_id_lists_hint():
    with pytest.raises(SelectionError, match="未知用例编号"):
        select_tcs(batch(include=("TC-X-99",)))


def test_wildcard_without_hits_rejected():
    with pytest.raises(SelectionError, match="未命中任何用例"):
        select_tcs(batch(include=("TC-Z-*",)))


def test_empty_final_selection_rejected():
    with pytest.raises(SelectionError, match="选择结果为空"):
        select_tcs(batch(include=("TC-L-01",), exclude=("TC-L-*",)))


def test_unknown_tag_key_and_value_rejected():
    with pytest.raises(SelectionError, match="未知标签键"):
        parse_batch({"name": "t", "tags": {"owner": ["a"]}})
    with pytest.raises(SelectionError, match="未知值"):
        parse_batch({"name": "t", "tags": {"world": ["W9"]}})


def test_invalid_suite_rejected():
    with pytest.raises(SelectionError, match="未知专题"):
        parse_batch({"name": "t", "suites": ["X"]})


def test_unknown_dataset_rejected():
    with pytest.raises(Exception, match="未知数据集 id"):
        parse_batch({"name": "t", "datasets": ["nope"]})


def test_unknown_top_level_key_rejected():
    with pytest.raises(SelectionError, match="未知字段"):
        parse_batch({"name": "t", "suites": ["L"], "author": "a"})


def test_malformed_field_types_rejected():
    with pytest.raises(SelectionError):
        parse_batch({"name": "t", "suites": "L"})
    with pytest.raises(SelectionError):
        parse_batch({"name": "t", "include": [1]})
    with pytest.raises(SelectionError):
        parse_batch({"datasets": []})


# ---- 装载、默认批次、preview ----

def test_load_batch_from_yaml(tmp_path):
    p = tmp_path / "lidar.yaml"
    p.write_text(
        "name: lidar-suite\n"
        "version_label: v9\n"
        "suites: [L]\n"
        "exclude: [TC-L-11]\n",
        encoding="utf-8",
    )
    from simulation.selection import load_batch

    b = load_batch(p)
    assert b.name == "lidar-suite"
    assert b.version_label == "v9"
    assert b.datasets == ("synthetic-default",)
    assert len(select_tcs(b)) == 10


def test_load_batch_missing_file():
    from simulation.selection import load_batch

    with pytest.raises(SelectionError, match="批次文件不存在"):
        load_batch("/nonexistent/batch.yaml")


def test_default_batch_runs_all():
    assert select_tcs(default_batch()) == ALL_TCS


def test_preview_lists_matrix_and_counts():
    text = preview(batch(suites=("L",), include=("TC-U-03",)))
    assert "数据集（1）" in text
    assert "用例（12）" in text
    assert "合计：1 数据集 × 12 用例 = 12 次执行" in text
    assert "TC-L-01" in text and "TC-U-03" in text


def test_resolve_datasets_seeds_and_override():
    ds = resolve_datasets(batch(datasets=("synthetic-seed42",)))
    assert ds[0]["seeds"] == [42]
    assert ds[0]["seed_source"] == "dataset"

    default_ds = resolve_datasets(batch())
    assert default_ds[0]["seeds"] == [11, 22, 33]
    assert default_ds[0]["seed_source"] == "sampling_default"

    overridden = resolve_datasets(batch(), seed_override=7)
    assert overridden[0]["seeds"] == [7]
    assert overridden[0]["seed_source"] == "cli"
