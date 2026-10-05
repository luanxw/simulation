"""TC-F 门禁套件：13 条融合用例全部 pass；含安全 0 碰撞与故障注入负向测试。"""

from __future__ import annotations

import pytest

from simulation.backends import SyntheticBackend
from simulation.runner import run_suite, run_tc

VERDICTS = run_suite("F")


@pytest.mark.parametrize("tc_id", sorted(VERDICTS))
def test_fusion_gate_pass(tc_id: str):
    v = VERDICTS[tc_id]
    assert v["pass"], f"{tc_id} 未通过：{v['failed']}"
    assert v["n_pending_backend"] == 0


def test_f_suite_has_13_cases():
    assert len(VERDICTS) == 13


class TestSafetyNonNegotiable:
    """安全专项（不可豁免）：0 碰撞 + 间隙 + 触发一致性。"""

    def test_static_zero_collision(self):
        v = VERDICTS["TC-F-09"]
        collisions = next(c for c in v["checks"] if c["name"] == "collisions")
        assert collisions["value"] == 0 and collisions["status"] == "pass"

    def test_dynamic_zero_collision(self):
        v = VERDICTS["TC-F-10"]
        collisions = next(c for c in v["checks"] if c["name"] == "collisions")
        assert collisions["value"] == 0 and collisions["status"] == "pass"

    def test_clearance_by_speed(self):
        v = VERDICTS["TC-F-09"]
        worst = next(c for c in v["checks"] if c["name"] == "worst_clearance_m")
        assert worst["value"] >= 0.05  # >=50mm @0.8m/s 最严门限

    @pytest.mark.parametrize("speed", [0.3, 0.8, 1.6])
    def test_stop_envelope_covers_trigger(self, speed: float):
        be = SyntheticBackend()
        assert be.trigger_distance_m("OB-D2") > be.stop_distance_m(speed)


class TestFaultInjection:
    """故障注入负向测试：证明 rule 门禁真实生效（假绿检测）。"""

    def test_blind_lidar_fails_detection_gates(self):
        be = SyntheticBackend()
        be.faults.add("lidar_blind")
        v = run_tc("TC-L-05", be)
        assert not v["pass"] and v["failed"]

    def test_blind_camera_fails_camera_gates(self):
        be = SyntheticBackend()
        be.faults.add("camera_blind")
        v = run_tc("TC-C-04", be)
        assert not v["pass"]

    def test_degraded_ultrasonic_fails_accuracy(self):
        be = SyntheticBackend()
        be.faults.add("ultrasonic_degraded")
        v = run_tc("TC-U-03", be)
        assert not v["pass"]


def test_tc_f08_seven_combos_gated():
    v = VERDICTS["TC-F-08"]
    combo_checks = [c for c in v["checks"] if c["name"].endswith(("_overall", "_safety"))]
    assert len(combo_checks) == 10  # 5 组合双门限 + 2 组合仅安全门限；单侧双目无数值门限


def test_tc_f13_determinism_five_runs():
    v = VERDICTS["TC-F-13"]
    assert v["pass"]
    h = next(c for c in v["checks"] if c["name"] == "identical_hashes")
    assert h["value"] == 1
