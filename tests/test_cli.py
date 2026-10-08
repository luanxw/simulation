"""CLI 装配测试（spec 0003 Task 7，TR-7.1~7.5）。"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from simulation import cli

ROOT = Path(__file__).resolve().parents[1]
LIDAR_BATCH = ROOT / "src/simulation/config/batches/lidar-suite.yaml"


def test_help_all_levels(capsys):
    for argv in (["--help"], ["run", "--help"], ["rebuild-index", "--help"]):
        with pytest.raises(SystemExit) as exc:
            cli.main(argv)
        assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--batch" in out and "--dry-run" in out


def test_run_full_matrix_archives_and_prints_summary(tmp_path, capsys):
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--out", str(out_dir)])
    assert code == 0
    captured = capsys.readouterr().out

    archives = sorted((out_dir / "archive").iterdir())
    assert len(archives) == 1
    archive_dir = archives[0]
    for name in ("results.json", "batch.snapshot.yaml", "datasets.snapshot.yaml",
                 "manifest.json", "report.html"):
        assert (archive_dir / name).is_file()
    assert (out_dir / "index.html").is_file()

    for title in ("激光 LiDAR", "USS 超声", "相机", "融合"):
        assert title in captured
    assert "总体：46/46 用例通过" in captured
    assert "归档目录：" in captured

    manifest = json.loads((archive_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["overall"]["tc_total"] == 46
    assert manifest["counts"]["overall"]["tc_failed"] == 0
    assert "report.html" in manifest["files"]


def test_dry_run_executes_nothing(tmp_path, capsys):
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--suite", "L", "--dry-run", "--out", str(out_dir)])
    assert code == 0
    captured = capsys.readouterr().out
    assert "合计：1 数据集 × 11 用例 = 11 次执行" in captured
    assert not out_dir.exists()


def test_unknown_tc_exits_2_without_archive(tmp_path, capsys):
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--tc", "TC-X-99", "--out", str(out_dir)])
    assert code == 2
    assert "错误：" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()


def test_missing_batch_file_exits_2(tmp_path, capsys):
    code = cli.main(["run", "--batch", str(tmp_path / "nope.yaml")])
    assert code == 2
    assert "错误：" in capsys.readouterr().err


def test_bad_tag_syntax_exits_2(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["run", "--tag", "world"])
    assert exc.value.code == 2


def test_selection_errors_exit_2_without_archive(tmp_path, capsys):
    """AC-4：未知数据集 / 未知标签值 / 交集为空 三类错误都退出 2 且无归档。"""
    out_dir = tmp_path / "reports"
    bad_dataset = tmp_path / "bad-ds.yaml"
    bad_dataset.write_text("name: bad-ds\ndatasets: [nope-dataset]\n", encoding="utf-8")
    cases = [
        ["run", "--batch", str(bad_dataset), "--out", str(out_dir)],
        ["run", "--tag", "kind=foo", "--out", str(out_dir)],
        # 激光批次与命令行 --suite F 交集为空
        ["run", "--batch", str(LIDAR_BATCH), "--suite", "F", "--out", str(out_dir)],
    ]
    for argv in cases:
        assert cli.main(argv) == 2, argv
        assert "错误：" in capsys.readouterr().err, argv
        assert not out_dir.exists(), argv


def test_failed_tc_exits_1_but_archive_complete(tmp_path, capsys, monkeypatch):
    real = cli.execute_batch

    def fake_failed(batch, override=None, seed_override=None, **kw):
        record = real(batch, override, seed_override=seed_override, **kw)
        first_runs = record["results"][0]["runs"]
        tc_id = next(iter(first_runs))
        first_runs[tc_id]["pass"] = False
        first_runs[tc_id]["failed"] = ["注入失败"]
        overall = record["summary"]["overall"]
        overall["tc_passed"] -= 1
        overall["tc_failed"] += 1
        return record

    monkeypatch.setattr(cli, "execute_batch", fake_failed)
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--tc", "TC-L-01", "--out", str(out_dir)])
    assert code == 1
    archive_dir = next((out_dir / "archive").iterdir())
    assert (archive_dir / "report.html").is_file()
    assert (out_dir / "index.html").is_file()
    assert "失败 1" in capsys.readouterr().out


def test_seed_override_recorded_in_manifest(tmp_path):
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--tc", "TC-L-01", "--seed", "42", "--out", str(out_dir)])
    assert code == 0
    manifest = json.loads(
        next((out_dir / "archive").iterdir()).joinpath("manifest.json").read_text("utf-8"))
    assert manifest["seed"] == [
        {"dataset": "synthetic-default", "seeds": [42], "source": "cli"}]


def test_batch_file_with_suite_and_tag(tmp_path):
    batch_yaml = tmp_path / "mini.yaml"
    batch_yaml.write_text(
        "name: mini\nsuites: [L]\ntags:\n  world: [W1]\n", encoding="utf-8")
    out_dir = tmp_path / "reports"
    code = cli.main(["run", "--batch", str(batch_yaml), "--out", str(out_dir)])
    assert code == 0
    record = json.loads(
        next((out_dir / "archive").iterdir()).joinpath("results.json").read_text("utf-8"))
    assert record["tcs"]  # 非空且均为 L 专题
    assert all(tc.startswith("TC-L-") for tc in record["tcs"])


def test_rebuild_index_command(tmp_path, capsys):
    out_dir = tmp_path / "reports"
    cli.main(["run", "--tc", "TC-L-01", "--version", "v1.0", "--out", str(out_dir)])
    code = cli.main(["rebuild-index", "--out", str(out_dir)])
    assert code == 0
    assert (out_dir / "index.html").is_file()
    assert "v1.0" in (out_dir / "index.html").read_text(encoding="utf-8")
    assert "历史总览已重建" in capsys.readouterr().out

    # 空根也能重建（占位页）
    empty = tmp_path / "empty"
    assert cli.main(["rebuild-index", "--out", str(empty)]) == 0
    assert "暂无归档记录" in (empty / "index.html").read_text(encoding="utf-8")


def test_module_invocation_as_subprocess():
    repo_root = Path(__file__).resolve().parents[1]
    env = {"PYTHONPATH": str(repo_root / "src")}
    proc = subprocess.run(
        [sys.executable, "-m", "simulation.cli", "run", "--help"],
        cwd=repo_root, capture_output=True, text=True, env=env, check=False)
    assert proc.returncode == 0
    assert "--batch" in proc.stdout
