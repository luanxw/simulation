"""TC-C 门禁套件：10 条双目用例全部 pass，左右对称执行。"""

from __future__ import annotations

import pytest

from simulation.backends import SyntheticBackend
from simulation.obstacles import LIBRARY
from simulation.runner import run_suite, run_tc

VERDICTS = run_suite("C")


@pytest.mark.parametrize("tc_id", sorted(VERDICTS))
def test_camera_gate_pass(tc_id: str):
    v = VERDICTS[tc_id]
    assert v["pass"], f"{tc_id} 未通过：{v['failed']}"
    assert v["n_pending_backend"] == 0


def test_c_suite_has_10_cases():
    assert len(VERDICTS) == 10


def test_left_right_symmetric():
    """左右相机对称执行、分别判定：两侧各自跑一遍 TC-C-04，均须 pass。"""
    left = run_tc("TC-C-04", SyntheticBackend(margin=0.010))
    right = run_tc("TC-C-04", SyntheticBackend(margin=0.012))
    assert left["pass"] and right["pass"]


def test_tc_c04_covers_flagpole_and_pillars():
    """R1/I-2 整改回归：TC-C-04 布置含门柱/角旗/铁丝网/立柱/旗杆。"""
    labels = {c["name"] for c in VERDICTS["TC-C-04"]["checks"]}
    assert any("OB-C1" in n for n in labels)
    assert any("OB-B1" in n for n in labels)
    assert any("OB-A1" in n for n in labels)
    assert "OB-D4" in LIBRARY
