"""合成后端：确定性、包络、故障注入、融合概率、环形扫描。"""

from __future__ import annotations

import pytest

from simulation.backends import SyntheticBackend, rng_for
from simulation.obstacles import LIBRARY, safety_items
from simulation.thresholds import load_sensor_params


def test_rng_stable_across_instances():
    a = [rng_for("k", 7).random() for _ in range(10)]
    b = [rng_for("k", 7).random() for _ in range(10)]
    c = [rng_for("k", 8).random() for _ in range(10)]
    assert a == b and a != c


def test_detection_prob_respects_ultrasonic_range():
    be = SyntheticBackend()
    assert be.detection_prob("U", "OB-A3", 1.4) > 0
    assert be.detection_prob("U", "OB-A3", 1.6) == 0.0
    assert be.detection_prob("U", "OB-A3", 0.04) == 0.0


def test_detection_prob_respects_camera_range():
    be = SyntheticBackend()
    assert be.detection_prob("C", "OB-C1", 3.9) > 0
    assert be.detection_prob("C", "OB-C1", 4.5) == 0.0


def test_lidar_near_ground_suppression():
    """近地目标（顶面<=80mm）在 0.67m 覆盖线内不得由 LiDAR 负责（I-1 口径）。"""
    be = SyntheticBackend()
    assert be.detection_prob("L", "OB-B8", 0.5) == 0.0
    assert be.detection_prob("L", "OB-B8", 0.67) > 0
    assert be.detection_prob("U", "OB-B8", 0.5) > 0  # 超声兜底


def test_no_rate_means_no_detection():
    be = SyntheticBackend()
    assert be.detection_prob("U", "OB-B12", 1.0) == 0.0  # B12 无 U 考核
    assert be.detection_prob("L", "OB-A5", 1.0) == 0.0


def test_fault_injection_zeroes_sensor():
    be = SyntheticBackend()
    be.faults.add("lidar_blind")
    assert be.detection_prob("L", "OB-A3", 2.0) == 0.0
    assert be.fusion_prob("OB-A3", 2.0) > 0  # 其余传感器兜底


def test_fusion_ge_best_single():
    be = SyntheticBackend()
    for code in ("OB-B1", "OB-B8", "OB-D2", "OB-C1"):
        singles = [be.detection_prob(s, code, 1.0) for s in "LUC"]
        assert be.fusion_prob(code, 1.0) >= max(singles) - 1e-9


def test_stop_distance_matches_spec():
    """急停包络：1.6 m/s、延迟 0.25s、减速度 2 m/s² → ≈1.04m。"""
    be = SyntheticBackend()
    d = be.stop_distance_m(1.6)
    assert d == pytest.approx(1.6 * 0.25 + 1.6**2 / 4, abs=1e-9)


def test_clearance_positive_for_safety_items():
    be = SyntheticBackend()
    for ob in safety_items():
        assert be.clearance_m(ob.code, 1.6) > 0, f"{ob.code} 安全间隙不足"


def test_ring_scan_spectrum():
    be = SyntheticBackend()
    rng = rng_for("ring", 11)
    big = be.ring_scan(75, 100, rng)
    assert sum(big.values()) >= 71  # TC-U-11 门禁
    small = be.ring_scan(25, 100, rng)
    assert sum(small.values()) < 72  # Φ25 存在盲区谱（特性数据）
    assert sum(small.values()) >= 50


def test_sample_hits_deterministic():
    be = SyntheticBackend()
    a = be.sample_hits("L", "OB-D1", 2.0, 100, rng_for("t", 3))
    b = be.sample_hits("L", "OB-D1", 2.0, 100, rng_for("t", 3))
    assert a == b


def test_all_library_codes_valid():
    assert len(LIBRARY) == 50
    sp = load_sensor_params()
    assert sp["fusion"]["rate_hz"] == 10
