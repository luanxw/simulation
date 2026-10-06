"""配置一致性：sensor_params ↔ test_thresholds ↔ spec.md 三方核验（NFR-3）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from simulation.thresholds import (
    degradation_envelope,
    load_sensor_params,
    load_thresholds,
    sampling,
    tc_gates,
)

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / ".trae/specs/0002-mower-sensor-sim-test-plan/spec.md"


@pytest.fixture(scope="module")
def spec_text() -> str:
    return SPEC.read_text(encoding="utf-8")


def test_threshold_yaml_loads():
    th = load_thresholds()
    assert th["version"] == 1
    assert set(th["suites"]) == {"L", "U", "C", "F"}


def test_all_46_tc_registered():
    th = load_thresholds()
    counts = {s: len(th["suites"][s]) for s in "LUCF"}
    assert counts == {"L": 11, "U": 12, "C": 10, "F": 13}
    assert sum(counts.values()) == 46


def test_all_tc_have_archetype():
    th = load_thresholds()
    for suite in "LUCF":
        for tc_id, gates in th["suites"][suite].items():
            assert gates["archetype"], f"{tc_id} 缺 archetype"


def test_sensor_envelope_matches_params():
    th, sp = load_thresholds(), load_sensor_params()
    env = th["sensor_envelope"]
    assert env["lidar"]["near_ground_min_m"] == pytest.approx(sp["lidar"]["near_ground_min_m"])
    assert env["ultrasonic"]["range_max_m"] == pytest.approx(sp["ultrasonic"]["range_max_m"])
    assert env["camera"]["zmax_m"] == pytest.approx(sp["camera"]["zmax_m"])


def test_spec_numbers_consistent(spec_text: str):
    # R1/I-1 整改口径：0.67/0.87m，禁止 0.76m 残留
    assert "0.76 m" not in spec_text
    assert "0.67 m" in spec_text and "0.87 m" in spec_text
    sp = load_sensor_params()
    assert sp["lidar"]["near_ground_min_m"] == pytest.approx(0.67)
    assert sp["lidar"]["ground_hit_min_m"] == pytest.approx(0.87)
    # 计数口径：46 条用例、50 项障碍物（I-5/I-6 整改）
    assert "46 条测试用例（LiDAR 11 / 超声 12 / 双目 10 / 融合 13）" in spec_text
    assert "全库 50 项（OB-B3a/b 计 2 项）" in spec_text
    assert "49 项" not in spec_text
    # 温漂口径（F-7）
    assert "约 1.7%" in spec_text and "1.9%" not in spec_text


def test_spec_sampling_matches_yaml(spec_text: str):
    smp = sampling()
    assert "静态类 ≥ 200 帧/条件" in spec_text and smp["static_frames_min"] == 200
    assert "动态类 ≥ 20 次遭遇/条件" in spec_text and smp["dynamic_encounters_min"] == 20
    assert "Wilson 95% 置信区间" in spec_text


def test_spec_classification_10(spec_text: str):
    cls = load_thresholds()["classification"]
    assert len(cls["classes"]) == 10
    assert cls["safety_class_count"] == 4
    assert "分类清单（10 类）" in spec_text


def test_degradation_envelope_seven_combos(spec_text: str):
    env = degradation_envelope()
    assert len(env) == 7
    combos = {e["combo"] for e in env}
    assert combos == {"disable_lidar", "disable_ultrasonic", "disable_camera",
                      "only_ultrasonic", "only_camera", "only_lidar", "single_side_camera"}
    assert "禁用组合（在位传感器）" in spec_text


def test_p1_mapping_declared(spec_text: str):
    th = load_thresholds()
    assert th["p1_to_matrix_mapping"] == {0.75: 0.8, 1.2: [1.0, 1.5]}  # YAML 数值键
    assert "以矩阵执行档为准" in spec_text


def test_tc_gates_lookup():
    assert tc_gates("TC-F-09")["collision_max"] == 0
    with pytest.raises(KeyError):
        tc_gates("TC-X-99")
