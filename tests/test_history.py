"""跨版本历史总览测试（spec 0003 Task 6，TR-6.1~6.4）。"""

import json
from datetime import datetime, timezone

from simulation.archive import write_archive
from simulation.execution import execute_batch
from simulation.history import iter_archives, rebuild_index, render_index
from simulation.selection import BatchConfig

M1 = datetime(2026, 10, 1, 1, 0, 0, tzinfo=timezone.utc)
M2 = datetime(2026, 10, 2, 2, 0, 0, tzinfo=timezone.utc)
M3 = datetime(2026, 10, 3, 3, 0, 0, tzinfo=timezone.utc)


def batch(**kw) -> BatchConfig:
    defaults = dict(
        name="t", version_label=None, datasets=("synthetic-default",),
        suites=(), include=(), exclude=(), tags={},
    )
    defaults.update(kw)
    return BatchConfig(**defaults)


def _make_archive(root, version, moment, **batch_kw):
    rec = execute_batch(batch(**batch_kw))
    return write_archive(root, rec, version=version, moment=moment,
                         report_renderer=lambda r, m: "<!DOCTYPE html><html></html>")


def test_index_lists_all_archives_with_rates_and_links(tmp_path):
    root = tmp_path / "reports"
    p1 = _make_archive(root, "v1.0", M1, suites=("L",))
    p2 = _make_archive(root, "v1.1", M2, include=("TC-L-01", "TC-F-09"))
    p3 = _make_archive(root, "v2.0", M3, include=("TC-U-03",))

    items = iter_archives(root)
    assert [i["dir"] for i in items] == [p1.name, p2.name, p3.name]
    assert all(i["invalid"] is None and i["has_report"] for i in items)

    rebuild_index(root)
    page = (root / "index.html").read_text(encoding="utf-8")

    for version, path in (("v1.0", p1), ("v1.1", p2), ("v2.0", p3)):
        assert version in page
        assert f'archive/{path.name}/report.html' in page
    assert "2026-10-01" in page and "2026-10-03" in page

    # 单元格数字与各归档 manifest 一致
    m1 = json.loads((p1 / "manifest.json").read_text(encoding="utf-8"))
    l_rate = m1["counts"]["by_suite"]["L"]["tc_rate"]
    assert f"{l_rate * 100:.1f}%" in page
    overall = m1["counts"]["overall"]
    assert f'{overall["tc_passed"]}/{overall["tc_total"]}' in page
    # v1.0 只有 L 专题，U/C/F 单元格显示 —
    assert "激光 LiDAR" in page and "USS 超声" in page
    # 专题表头四列齐全
    for title in ("激光 LiDAR", "USS 超声", "相机", "融合", "总体通过率"):
        assert title in page


def test_empty_root_renders_placeholder(tmp_path):
    root = tmp_path / "reports"
    path = rebuild_index(root)
    page = path.read_text(encoding="utf-8")
    assert "暂无归档记录" in page
    assert "<table>" not in page


def test_corrupt_manifest_skipped_and_flagged(tmp_path):
    root = tmp_path / "reports"
    _make_archive(root, "v1.0", M1, include=("TC-L-01",))
    bad = root / "archive" / "v9.9_broken"
    bad.mkdir(parents=True)
    (bad / "manifest.json").write_text("{ not json", encoding="utf-8")

    rebuild_index(root)
    page = (root / "index.html").read_text(encoding="utf-8")
    assert "v9.9_broken" in page
    assert "manifest 无法解析" in page
    assert "v1.0" in page  # 正常归档不受影响


def test_index_offline_self_contained(tmp_path):
    root = tmp_path / "reports"
    _make_archive(root, "v1.0", M1, suites=("L",))
    rebuild_index(root)
    page = (root / "index.html").read_text(encoding="utf-8")
    assert "http://" not in page and "https://" not in page
    assert "<script src=" not in page and '<link rel="stylesheet"' not in page
    assert "<style>" in page


def test_rebuild_idempotent_except_timestamp(tmp_path):
    root = tmp_path / "reports"
    _make_archive(root, "v1.0", M1, include=("TC-L-01",))
    items = iter_archives(root)
    p1 = render_index(items, generated_at="2026-10-08T00:00:00Z")
    p2 = render_index(items, generated_at="2026-10-08T00:00:00Z")
    assert p1 == p2
    rebuild_index(root, now=M1)
    on_disk = (root / "index.html").read_text(encoding="utf-8")
    assert "2026-10-01T01:00:00Z" in on_disk  # 注入的生成时间
