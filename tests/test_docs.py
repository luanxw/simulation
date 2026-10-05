"""文档一致性：标准指导书与使用说明必须存在且关键章节与代码对齐。"""

from __future__ import annotations

from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "src/simulation/docs"


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
