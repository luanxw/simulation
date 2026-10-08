"""文档一致性：标准指导书与使用说明必须存在且关键章节与代码对齐。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from simulation.selection import SelectionOverride, load_batch, select_tcs

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "src/simulation/docs"
BATCHES = ROOT / "src/simulation/config/batches"


def test_standard_doc_exists_with_sections():
    text = (DOCS / "sensor_test_standard.md").read_text(encoding="utf-8")
    for section in ("## 1. 目的与范围", "## 2. 被测对象与标称假设", "## 4. 障碍物规格库（50 项）",
                    "## 5. 测试用例体系（46 条）", "## 6. 统计判定规则", "## 8. 门禁汇总与放行"):
        assert section in text, f"标准指导书缺章节：{section}"
    assert "0.67 m" in text and "46 条" in text and "50 项" in text


def test_user_guide_matches_code():
    text = (DOCS / "user_guide.md").read_text(encoding="utf-8")
    # 文中提到的运行方式与真实文件/命令对齐
    for anchor in ("simulation-py312", "test_thresholds.yaml", "obstacles.py",
                   "run_tc(\"TC-L-05\")", "SyntheticBackend", "degradation_envelope",
                   "user_guide.md" if False else "sensor_test_standard.md"):
        assert anchor in text, f"使用说明缺关键内容：{anchor}"
    assert "oracle" in text  # 更名说明必须在


def test_design_diagrams_exist():
    diagrams = DOCS / "diagrams"
    expected = ["01_framework_flow.png", "02_execution_swimlane.png",
                "03_sensor_architecture.png", "04_obstacle_library.png",
                "05_execution_strategy.png", "06_data_flow.png",
                "07_module_sequence.png"]
    for name in expected:
        assert (diagrams / name).exists(), f"缺设计图：{name}"
    # 标准指导书须包含设计图章节
    text = (DOCS / "sensor_test_standard.md").read_text(encoding="utf-8")
    assert "## 10. 设计图" in text


def test_package_doc_linked():
    init = Path(__file__).resolve().parents[1] / "src/simulation/__init__.py"
    assert init.exists()


# ---- spec 0003 Task 8：示例批次与指南新章节的一致性 ----

def test_example_batches_load_and_select_expected_tcs():
    lidar = load_batch(BATCHES / "lidar-suite.yaml")
    assert select_tcs(lidar) == tuple(f"TC-L-{i:02d}" for i in range(1, 12))

    safety = load_batch(BATCHES / "safety-dynamic.yaml")
    assert set(select_tcs(safety)) == {
        "TC-F-06", "TC-F-07", "TC-F-09", "TC-F-10", "TC-F-11"}

    # 指南承诺：--tag kind=safety 在该批次上交集收窄为安全两条
    narrowed = select_tcs(
        safety, SelectionOverride(tags={"kind": ("safety",)}))
    assert set(narrowed) == {"TC-F-09", "TC-F-10"}


def test_user_guide_has_batch_report_section():
    text = (DOCS / "user_guide.md").read_text(encoding="utf-8")
    for anchor in (
            "## 5. 批次执行与可视化报告（spec 0003）",
            "python -m simulation.cli run",
            "src/simulation/config/batches/lidar-suite.yaml",
            "src/simulation/config/batches/safety-dynamic.yaml",
            "--dry-run", "rebuild-index", "index.html",
            "manifest.json", "Wilson", "退出码"):
        assert anchor in text, f"用户指南第 5 章缺关键内容：{anchor}"
    # 章节重编号后不得残留旧编号的大标题
    for stale in ("## 9. 提交前自检", "## 8. 设计图索引"):
        assert stale not in text


def _bash_commands(markdown: str) -> list[str]:
    """提取全部 bash 围栏里的命令；同一围栏内以空行/注释分隔多条命令，反斜杠续行合并。"""
    commands: list[str] = []
    for block in re.findall(r"```bash\n(.*?)```", markdown, flags=re.S):
        pending: list[str] = []
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                if pending:
                    commands.append(re.sub(r"\s+", " ", " ".join(pending)))
                    pending = []
                continue
            if line.endswith("\\"):
                line = line[:-1].rstrip()
            pending.append(line)
            if not raw_line.rstrip().endswith("\\"):
                commands.append(re.sub(r"\s+", " ", " ".join(pending)))
                pending = []
        if pending:
            commands.append(re.sub(r"\s+", " ", " ".join(pending)))
    return commands


def test_guide_lidar_command_runs_as_written(tmp_path):
    """TR-8.2：指南中激光批次的正式执行命令原样可跑通并生成归档（仅重定向 --out）。"""
    text = (DOCS / "user_guide.md").read_text(encoding="utf-8")
    candidates = [
        cmd for cmd in _bash_commands(text)
        if ("simulation.cli run" in cmd
            and "batches/lidar-suite.yaml" in cmd
            and "--dry-run" not in cmd)
    ]
    assert candidates, "指南中未找到激光批次的正式执行命令"

    argv = candidates[0].split()
    env = {"PYTHONPATH": str(ROOT / "src"), "PATH": ""}
    # bash 的 VAR=value 前缀不经 shell 时需剥离（PYTHONPATH 已在 env 中给绝对值）
    if re.match(r"^[A-Z_]+=", argv[0]):
        argv.pop(0)
    # 文档写死本机解释器完整路径；执行时用当前 pytest 解释器，保证 CI 可复现
    argv[0] = sys.executable
    out_idx = argv.index("--out") + 1
    argv[out_idx] = str(tmp_path / "guide-run")

    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          env=env, check=False)
    assert proc.returncode == 0, proc.stderr
    archives = list((tmp_path / "guide-run" / "archive").iterdir())
    assert len(archives) == 1
    assert (archives[0] / "report.html").is_file()
    assert (tmp_path / "guide-run" / "index.html").is_file()
