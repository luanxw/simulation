"""数据集注册表测试（spec 0003 Task 1，TR-1.1~1.4）。"""

import pytest

from simulation.datasets import (
    Dataset,
    DatasetError,
    get_dataset,
    load_datasets,
    parse_datasets,
)


def test_builtin_registry_loads_two_synthetic_datasets():
    table = load_datasets()
    assert {"synthetic-default", "synthetic-seed42"} <= set(table)
    default = table["synthetic-default"]
    assert default.kind == "synthetic"
    assert default.title and default.description
    assert isinstance(default, Dataset)
    seed42 = table["synthetic-seed42"]
    assert seed42.params["seeds"] == [42]
    assert seed42.effective_seeds([11, 22, 33]) == [42]
    assert default.effective_seeds([11, 22, 33]) == [11, 22, 33]


def test_get_unknown_dataset_lists_available_ids():
    with pytest.raises(DatasetError, match="未知数据集 id") as exc_info:
        get_dataset("does-not-exist")
    assert "synthetic-default" in str(exc_info.value)
    assert "synthetic-seed42" in str(exc_info.value)


def test_external_dataset_schema_accepted_with_path_and_checksum():
    parsed = parse_datasets({
        "datasets": [{
            "id": "ext-bag1",
            "kind": "external",
            "title": "外景采集包",
            "description": "2026 秋测",
            "path": "data/bags/field-2026-10.zip",
            "checksum": {"alg": "sha256", "value": "abc123"},
        }],
    })
    ds = parsed["ext-bag1"]
    assert ds.kind == "external"
    assert ds.path == "data/bags/field-2026-10.zip"
    assert ds.checksum == {"alg": "sha256", "value": "abc123"}


def test_external_dataset_without_path_rejected():
    with pytest.raises(DatasetError, match="必须含非空 path"):
        parse_datasets({"datasets": [{"id": "ext-x", "kind": "external"}]})


def test_external_checksum_must_be_alg_value_pair():
    base = {"id": "ext-x", "kind": "external", "path": "a.zip"}
    with pytest.raises(DatasetError):
        parse_datasets({"datasets": [{**base, "checksum": {"alg": "sha256"}}]})
    with pytest.raises(DatasetError):
        parse_datasets({"datasets": [{**base, "checksum": "sha256:xx"}]})


@pytest.mark.parametrize("bad_seeds", [[], [0], [-1], [1.5], ["7"], [True], [1, 0]])
def test_synthetic_seeds_must_be_nonempty_positive_ints(bad_seeds):
    with pytest.raises(DatasetError, match="seeds 必须是非空正整数列表"):
        parse_datasets({"datasets": [
            {"id": "bad", "kind": "synthetic", "params": {"seeds": bad_seeds}},
        ]})


def test_unknown_synthetic_param_rejected():
    with pytest.raises(DatasetError, match="未知 synthetic 参数"):
        parse_datasets({"datasets": [
            {"id": "bad", "kind": "synthetic", "params": {"frames": 200}},
        ]})


def test_synthetic_dataset_cannot_carry_path():
    with pytest.raises(DatasetError, match="不允许 path"):
        parse_datasets({"datasets": [
            {"id": "bad", "kind": "synthetic", "path": "x.zip"},
        ]})


def test_duplicate_id_rejected():
    with pytest.raises(DatasetError, match="id 重复"):
        parse_datasets({"datasets": [
            {"id": "dup", "kind": "synthetic"},
            {"id": "dup", "kind": "synthetic"},
        ]})


@pytest.mark.parametrize("bad_raw", [
    None,
    {},
    {"datasets": "x"},
    {"datasets": ["not-a-dict"]},
    {"datasets": [{"kind": "synthetic"}]},
    {"datasets": [{"id": "x", "kind": "alien"}]},
])
def test_malformed_registry_rejected(bad_raw):
    with pytest.raises(DatasetError):
        parse_datasets(bad_raw)
