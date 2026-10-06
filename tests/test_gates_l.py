"""TC-L 门禁套件：11 条 LiDAR 用例全部 pass（SyntheticBackend 名义机台）。"""

from __future__ import annotations

import pytest

from simulation.runner import run_suite

VERDICTS = run_suite("L")


@pytest.mark.parametrize("tc_id", sorted(VERDICTS))
def test_lidar_gate_pass(tc_id: str):
    v = VERDICTS[tc_id]
    assert v["pass"], f"{tc_id} 未通过：{v['failed']}"
    assert v["n_pending_backend"] == 0


def test_l_suite_has_11_cases():
    assert len(VERDICTS) == 11


def test_tc_l01_accuracy_evidence():
    v = VERDICTS["TC-L-01"]
    names = {c["name"] for c in v["checks"]}
    assert {"systematic", "sigma", "r2"} <= names
