"""判定器统计函数：检出率、Wilson 区间、稳定窗、误差统计、R²、门禁判定。"""

from __future__ import annotations

import pytest

from simulation.verdict import (
    detection_rate,
    error_stats,
    gate_check,
    linear_r2,
    make_verdict,
    percentile,
    stable_rate,
    wilson_interval,
)


def test_detection_rate_basic():
    assert detection_rate([True] * 8 + [False] * 2) == pytest.approx(0.8)
    with pytest.raises(ValueError):
        detection_rate([])


def test_wilson_interval():
    lo, hi = wilson_interval(95, 100)
    assert lo < 0.95 < hi and lo > 0.88 and hi < 1.0
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_stable_rate_window():
    # 90 帧全检出 + 10 帧全漏：通过窗 = i=0..82（83 个），总窗 91
    hits = [True] * 90 + [False] * 10
    assert stable_rate(hits) == pytest.approx(83 / 91)
    with pytest.raises(ValueError):
        stable_rate([True] * 5)


def test_error_stats():
    st = error_stats([10.0, 12.0, 8.0, 10.0])
    assert st["systematic_mm"] == pytest.approx(10.0)
    assert st["sigma_mm"] == pytest.approx(1.633, abs=1e-2)
    with pytest.raises(ValueError):
        error_stats([1.0])


def test_linear_r2_perfect():
    pairs = [(0.5, 0.5), (1.0, 1.0), (2.0, 2.0), (5.0, 5.0)]
    assert linear_r2(pairs) == pytest.approx(1.0)


def test_percentile_nearest():
    assert percentile(list(range(1, 101)), 95) == 95
    assert percentile([5.0], 99) == 5.0


def test_gate_check_ops():
    assert gate_check("a", 1.0, "le", 2.0)["status"] == "pass"
    assert gate_check("a", 3.0, "le", 2.0)["status"] == "fail"
    assert gate_check("b", 0.99, "ge", 0.98)["status"] == "pass"
    with pytest.raises(KeyError):
        gate_check("c", 1.0, "eq", 1.0)


def test_make_verdict_pending_not_blocking():
    checks = [gate_check("ok", 1.0, "le", 2.0),
              {"name": "needs_engine", "status": "pending_backend", "reason": "x"}]
    v = make_verdict("TC-TEST", checks)
    assert v["pass"] is True and v["n_pending_backend"] == 1
    v2 = make_verdict("TC-TEST", [gate_check("bad", 5.0, "le", 2.0)])
    assert v2["pass"] is False and v2["failed"] == ["bad"]
