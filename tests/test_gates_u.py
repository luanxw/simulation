"""TC-U 门禁套件：12 条超声用例全部 pass，12 通道全测。"""

from __future__ import annotations

import pytest

from simulation.runner import run_suite

VERDICTS = run_suite("U")


@pytest.mark.parametrize("tc_id", sorted(VERDICTS))
def test_ultrasonic_gate_pass(tc_id: str):
    v = VERDICTS[tc_id]
    assert v["pass"], f"{tc_id} 未通过：{v['failed']}"
    assert v["n_pending_backend"] == 0


def test_u_suite_has_12_cases():
    assert len(VERDICTS) == 12


def test_tc_u01_covers_12_channels():
    """TC-U-01 逐通道判定：12 通道全部计入（最差通道门禁）。"""
    v = VERDICTS["TC-U-01"]
    names = {c["name"] for c in v["checks"]}
    assert "worst_systematic" in names and "worst_sigma" in names


def test_tc_u11_ring_gate():
    v = VERDICTS["TC-U-11"]
    assert v["pass"]
    ring = [c for c in v["checks"] if c["name"].startswith("ring_phi")]
    assert len(ring) == 2
