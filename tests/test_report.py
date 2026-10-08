"""单次 HTML 报告测试（spec 0003 Task 5，TR-5.1~5.5）。"""

import re

import pytest

from simulation.archive import build_manifest, write_archive
from simulation.backends import SyntheticBackend
from simulation.execution import execute_batch
from simulation.report import render_report
from simulation.selection import BatchConfig


def batch(**kw) -> BatchConfig:
    defaults = dict(
        name="t", version_label=None, datasets=("synthetic-default",),
        suites=(), include=(), exclude=(), tags={},
    )
    defaults.update(kw)
    return BatchConfig(**defaults)


@pytest.fixture()
def manifest_kwargs():
    return dict(version="v1.0", archive_name="v1.0_20261008T033005Z",
                created_at="2026-10-08T03:30:05Z",
                git_info={"commit": "abc123def", "dirty": False},
                backend_name="SyntheticBackend")


def test_report_has_four_suites_with_matching_stats(manifest_kwargs):
    rec = execute_batch(batch())
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))

    for title in ("激光 LiDAR", "USS 超声", "相机", "融合"):
        assert title in page
    overall = rec["summary"]["overall"]
    assert f"{overall['tc_passed']}/{overall['tc_total']}" in page
    for stats in rec["summary"]["by_suite"].values():
        assert f'{stats["tc_passed"]}/{stats["tc_total"]} 通过' in page
    # 抬头元数据
    for token in ("v1.0", "abc123def", "SyntheticBackend", "synthetic-default",
                  "2026-10-08T03:30:05Z"):
        assert token in page


def test_every_check_evidence_rendered(manifest_kwargs):
    rec = execute_batch(batch())
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))

    for group in rec["results"]:
        assert group["dataset"] in page
        for tc, verdict in group["runs"].items():
            assert tc in page
            for check in verdict["checks"]:
                assert str(check["name"]) in page
                assert str(check["value"]) in page
                assert str(check["threshold"]) in page
                assert check["status"] in ("pass", "fail", "pending_backend")


def test_wilson_ci_rendered_for_detection_checks(manifest_kwargs):
    rec = execute_batch(batch(include=("TC-L-05",)))
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))
    ci = rec["results"][0]["runs"]["TC-L-05"]["checks"][0]["ci"]
    assert f"[{ci[0]}, {ci[1]}]" in page
    n = rec["results"][0]["runs"]["TC-L-05"]["checks"][0]["n"]
    assert str(n) in page


def test_report_is_offline_self_contained(manifest_kwargs):
    rec = execute_batch(batch())
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))
    assert "http://" not in page and "https://" not in page
    assert "<script src=" not in page
    assert '<link rel="stylesheet"' not in page
    assert "<style>" in page  # 样式内联
    assert "<details" in page  # 原生折叠，无 JS 依赖


def test_failed_case_is_locatable_and_red(manifest_kwargs):
    be = SyntheticBackend()
    be.faults.add("lidar_blind")
    rec = execute_batch(batch(include=("TC-L-05",)), backend=be)
    assert rec["results"][0]["runs"]["TC-L-05"]["pass"] is False
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))
    assert 'class="badge fail"' in page
    assert "失败" in page
    # 失败检查项行带 fail 类
    failed_name = rec["results"][0]["runs"]["TC-L-05"]["failed"][0]
    assert failed_name in page


def test_multiple_datasets_rendered_as_groups(manifest_kwargs):
    rec = execute_batch(batch(
        datasets=("synthetic-default", "synthetic-seed42"),
        include=("TC-L-01", "TC-U-03"),
    ))
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))
    assert "synthetic-default" in page and "synthetic-seed42" in page
    assert page.count('class="dataset-note"') >= 2
    # 每个用例一个 details（内含两个数据集的检查表），点击一次即见全部检查项
    assert page.count("<details") == 2


def test_details_live_inside_suite_section(manifest_kwargs):
    rec = execute_batch(batch(suites=("L",)))
    page = render_report(rec, build_manifest(rec, **manifest_kwargs))
    l_start = page.index('<h2 id="suite-L">')
    l_end = page.index("</details>")
    assert l_start < l_end
    assert "<details" in page[l_start:]


def test_dynamic_content_is_html_escaped(manifest_kwargs):
    rec = execute_batch(batch(include=("TC-L-01",)))
    kwargs = {**manifest_kwargs, "version": "<script>alert(1)</script>"}
    page = render_report(rec, build_manifest(rec, **kwargs))
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_report_written_end_to_end_in_archive(tmp_path, manifest_kwargs):
    rec = execute_batch(batch(suites=("L",)))
    html_text = render_report(rec, build_manifest(rec, **manifest_kwargs))
    path = write_archive(tmp_path / "reports", rec,
                         report_renderer=lambda r, m: html_text)
    written = (path / "report.html").read_text(encoding="utf-8")
    assert written == html_text
    assert re.search(r"<!DOCTYPE html>", written)
