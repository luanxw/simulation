"""障碍物规格库完整性：50 项、五要素、四组分布、量程自洽、3.8 矩阵一致。"""

from __future__ import annotations

from simulation.obstacles import OBSTACLES, by_group, census_items, safety_items
from simulation.thresholds import load_sensor_params

EXPECTED_COUNTS = {"A": 7, "B": 21, "C": 14, "D": 8}  # B3a/b 计 2 项，全库 50
SAFETY_CODES = {"OB-B11", "OB-B15", "OB-C9", "OB-C14", "OB-D1", "OB-D2"}
FIELDS = ("geometry", "material", "optical", "acoustic", "difficulty")


def test_library_size_and_groups():
    assert len(OBSTACLES) == 50
    for group, n in EXPECTED_COUNTS.items():
        assert len(by_group(group)) == n


def test_all_obstacles_have_five_fields():
    for ob in OBSTACLES:
        for f in FIELDS:
            assert getattr(ob, f), f"{ob.code} 缺字段 {f}"


def test_safety_items_match_spec():
    assert {ob.code for ob in safety_items()} == SAFETY_CODES


def test_tiers_within_sensor_envelopes():
    sp = load_sensor_params()
    u_max = sp["ultrasonic"]["range_max_m"]
    c_max = sp["camera"]["zmax_m"]
    l_min = sp["lidar"]["range_min_m"]
    for ob in OBSTACLES:
        for d in ob.tiers.get("U", ()):
            assert 0 < d <= u_max, f"{ob.code} U 档 {d} 超量程"
        for d in ob.tiers.get("C", ()):
            assert 0 < d <= c_max, f"{ob.code} C 档 {d} 超量程"
        for d in ob.tiers.get("L", ()):
            assert l_min <= d <= sp["lidar"]["range_max_m_80pct"], f"{ob.code} L 档 {d} 越界"


def test_rate_keys_subset_of_tiers_and_bounds():
    for ob in OBSTACLES:
        for sensor, rate in ob.rate.items():
            assert sensor in ob.tiers, f"{ob.code} rate[{sensor}] 无对应距离档"
            if rate is not None:
                assert 0.80 <= rate <= 1.0, f"{ob.code} rate[{sensor}]={rate} 越界"


def test_near_ground_items_are_low_obstacles():
    codes = {ob.code for ob in OBSTACLES if ob.near_ground}
    assert codes == {"OB-B5", "OB-B8", "OB-B17", "OB-C10", "OB-D3"}


def test_census_covers_all_gated_items():
    """普查条件必须覆盖该传感器全部设门限项（I-2 整改：承载闭环）。"""
    for sensor in "LUC":
        gated = {ob.code for ob in OBSTACLES
                 if ob.rate.get(sensor) is not None}
        covered = {ob.code for ob in census_items(sensor)}
        assert covered == gated


def test_matrix_rows_carry_tc_refs():
    """3.8 矩阵中凡标注考核传感器的行，关联列须含对应普查用例（R1/I-2 回归）。"""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[1]
    spec = repo / ".trae/specs/0002-mower-sensor-sim-test-plan/spec.md"
    matrix = spec.read_text("utf-8").split("### 3.8")[1].split("## 4.")[0]
    checked = 0
    for line in matrix.split("\n"):
        if not (line.startswith("| OB-") or line.startswith("| **OB-")):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        sensor_col, tc_col = cells[1], cells[-1]
        for g in "LUC":
            if f"{g}:" in sensor_col:
                assert f"TC-{g}" in tc_col, f"{cells[0]} 缺 TC-{g} 承载"
                checked += 1
    assert checked >= 50
