"""归档与 manifest 测试（spec 0003 Task 4，TR-4.1~4.5）。"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from simulation.archive import (
    detect_git,
    safe_slug,
    utc_stamp,
    write_archive,
)
from simulation.execution import execute_batch
from simulation.selection import BatchConfig

FIXED_MOMENT = datetime(2026, 10, 8, 3, 30, 5, tzinfo=timezone.utc)


def batch() -> BatchConfig:
    return BatchConfig(
        name="t", version_label=None, datasets=("synthetic-default",),
        suites=("L",), include=(), exclude=(), tags={},
    )


@pytest.fixture()
def record():
    return execute_batch(batch())


def test_archive_writes_all_artifacts(tmp_path, record):
    path = write_archive(tmp_path / "reports", record, moment=FIXED_MOMENT)
    assert path.name == "dev-20261008T033005Z"
    names = {p.name for p in path.iterdir()}
    assert {"results.json", "manifest.json",
            "batch.snapshot.yaml", "datasets.snapshot.yaml"} <= names

    restored = json.loads((path / "results.json").read_text(encoding="utf-8"))
    assert restored["tcs"] == record["tcs"]
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "dev-20261008T033005Z"

    batch_snap = yaml.safe_load((path / "batch.snapshot.yaml").read_text(encoding="utf-8"))
    assert batch_snap["name"] == "t"
    ds_snap = yaml.safe_load((path / "datasets.snapshot.yaml").read_text(encoding="utf-8"))
    assert ds_snap["datasets"][0]["id"] == "synthetic-default"


def test_manifest_fields_complete_and_consistent(tmp_path, record):
    path = write_archive(tmp_path / "reports", record, version="v1.0",
                         backend_name="SyntheticBackend", moment=FIXED_MOMENT)
    m = json.loads((path / "manifest.json").read_text(encoding="utf-8"))

    assert m["schema_version"] == 1
    assert m["version"] == "v1.0"
    assert m["archive"] == path.name
    assert m["created_at"].endswith("Z")
    assert set(m["git"]) == {"commit", "dirty"}
    assert m["python"].count(".") == 2
    assert m["backend"] == "SyntheticBackend"
    assert m["seed"][0]["dataset"] == "synthetic-default"
    assert m["seed"][0]["seeds"] == [11, 22, 33]
    assert m["datasets"][0]["kind"] == "synthetic"
    assert m["selection"]["suites"] == ["L"]
    counts = m["counts"]["overall"]
    assert counts["tc_total"] == 11
    assert counts["tc_passed"] + counts["tc_failed"] == 11
    assert set(m["counts"]["by_suite"]) == {"L", "U", "C", "F"}
    assert "results.json" in m["files"]


def test_git_unavailable_outside_repo(tmp_path, monkeypatch):
    # 非 git 目录直接探测：返回 unavailable 且不抛异常
    info = detect_git(cwd=tmp_path)
    assert info["commit"] == "unavailable"

    # 模拟 git 不可用（非 git 环境/命令失败）：归档仍完整生成
    class _FakeProc:
        returncode = 128
        stdout = ""
        stderr = "fatal: not a git repository"

    monkeypatch.setattr(
        "simulation.archive.subprocess.run",
        lambda *a, **k: _FakeProc())
    rec = execute_batch(batch())
    path = write_archive(tmp_path / "out", rec, moment=FIXED_MOMENT)
    m = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    assert m["git"]["commit"] == "unavailable"
    assert m["git"]["dirty"] is None


def test_same_version_creates_distinct_dirs(tmp_path, record):
    root = tmp_path / "reports"
    p1 = write_archive(root, record, version="v1.0", moment=FIXED_MOMENT)
    p2 = write_archive(root, record, version="v1.0", moment=FIXED_MOMENT)
    assert p1 != p2 and p1.exists() and p2.exists()
    assert p2.name.endswith("-1")


def test_version_label_slugified(tmp_path, record):
    path = write_archive(tmp_path / "reports", record,
                         version="v 1.0/候选", moment=FIXED_MOMENT)
    assert "/" not in path.name and " " not in path.name
    assert path.name.startswith("v-1.0-候选_")


def test_batch_version_label_used_when_no_explicit(tmp_path):
    b = BatchConfig(name="t", version_label="v2.3", datasets=("synthetic-default",),
                    suites=(), include=("TC-L-01",), exclude=(), tags={})
    rec = execute_batch(b)
    path = write_archive(tmp_path / "reports", rec, moment=FIXED_MOMENT)
    assert path.name.startswith("v2.3_")
    m = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    assert m["version"] == "v2.3"


def test_report_renderer_optional(tmp_path, record):
    path = write_archive(tmp_path / "reports", record,
                         report_renderer=lambda r, m: "<html></html>",
                         moment=FIXED_MOMENT)
    assert (path / "report.html").read_text(encoding="utf-8") == "<html></html>"


def test_reproducible_results_json_bytes(tmp_path):
    from simulation.selection import SelectionOverride

    b = batch()
    r1 = execute_batch(b)
    r2 = execute_batch(b, SelectionOverride())
    p1 = write_archive(tmp_path / "a", r1, moment=FIXED_MOMENT)
    p2 = write_archive(tmp_path / "b", r2, moment=FIXED_MOMENT)
    assert ((p1 / "results.json").read_bytes()
            == (p2 / "results.json").read_bytes())


def test_safe_slug_and_stamp_helpers():
    assert safe_slug(" v/1 2 ") == "v-1-2"
    assert safe_slug("v1.0/候选") == "v1.0-候选"
    assert safe_slug("///") == "unnamed"
    assert utc_stamp(FIXED_MOMENT) == "20261008T033005Z"


def test_reports_gitignored():
    ignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "reports/" in ignore
