"""场景注册表完整性：46 条、编号连续、NAMED 条件与库一致。"""

from __future__ import annotations

import pytest

from simulation.obstacles import LIBRARY
from simulation.scenarios import ALL_TC_IDS, NAMED, SCENARIOS, census_conditions

EXPECTED = {"L": 11, "U": 12, "C": 10, "F": 13}


def test_scenario_counts():
    counts = {s: 0 for s in "LUCF"}
    for sc in SCENARIOS.values():
        counts[sc.suite] += 1
    assert counts == EXPECTED
    assert len(ALL_TC_IDS) == 46


def test_tc_ids_contiguous():
    for suite, n in EXPECTED.items():
        ids = sorted(tc for tc in SCENARIOS if tc.startswith(f"TC-{suite}-"))
        assert ids == [f"TC-{suite}-{i:02d}" for i in range(1, n + 1)]


def test_named_conditions_reference_library():
    for tc_id, conds in NAMED.items():
        assert tc_id in SCENARIOS
        for c in conds:
            ob = LIBRARY[c["code"]]
            assert c["sensor"] in ob.tiers, f"{tc_id}: {c['code']} 无 {c['sensor']} 档"
            assert c["min_rate"] <= ob.rate[c["sensor"]], f"{tc_id}: 门限松于库门限"


def test_census_conditions_shape():
    for sensor in "LUC":
        conds = census_conditions(sensor)
        assert len(conds) >= 20
        for c in conds:
            assert c["sensor"] == sensor
            assert c["min_rate"] <= 0.99


def test_scenario_worlds_valid():
    valid = {"W0", "W1", "W2", "W3", "W1/W2", "W0/W1", "W0/W1/W2", "W2/W3", "任意"}
    for sc in SCENARIOS.values():
        assert sc.world in valid, f"{sc.tc_id} 世界标注异常：{sc.world}"


@pytest.mark.parametrize("tc_id", sorted(SCENARIOS))
def test_every_tc_has_gates(tc_id: str):
    from simulation.thresholds import tc_gates
    gates = tc_gates(tc_id)
    assert gates["archetype"]
