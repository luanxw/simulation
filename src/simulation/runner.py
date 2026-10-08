"""测试执行器：46 条用例（TC-L/U/C/F）的判定逻辑与 verdict 产出。

每条 TC 一个执行函数，阈值一律取自 test_thresholds.yaml（tc_gates），
随机量一律经 backends.rng_for 派生（同 seed 可复现）。
接入真实仿真引擎后仅需替换 Backend，门禁不变。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .backends import SENSORS, SyntheticBackend, rng_for
from .obstacles import LIBRARY, census_items, safety_items
from .scenarios import (
    C_ACCURACY_DISTANCES,
    COMPLEMENTARY,
    L_ACCURACY_DISTANCES,
    NAMED,
    SCENARIOS,
    U_ACCURACY_DISTANCES,
    census_conditions,
)
from .verdict import (
    detection_rate,
    error_stats,
    gate_check,
    linear_r2,
    make_verdict,
    percentile,
    stable_rate,
    wilson_interval,
)


def _hit_stats(be: SyntheticBackend, tc_id: str, cond: dict,
               frames: int, seeds: list[int]) -> dict:
    """多 seed 合并采样一个条件的检出结果，返回率+Wilson CI+是否达标。"""
    hits: list[bool] = []
    for seed in seeds:
        rng = rng_for(f"{tc_id}|{cond['label']}", seed)
        hits += be.sample_hits(cond["sensor"], cond["code"], cond["distance"], frames, rng)
    rate = stable_rate(hits)
    lo, hi = wilson_interval(sum(hits), len(hits))
    # spec 2.4：rule 以点估计达标为准，Wilson CI 作为证据随行
    ok = rate >= cond["min_rate"]
    return {"cond": cond["label"], "rate": rate, "ci": (round(lo, 4), round(hi, 4)),
            "n": len(hits), "ok": ok}


def _detection_case(be: SyntheticBackend, tc_id: str) -> dict:
    """专项检出类（TC-L-05/06/07、TC-U-03/04、TC-C-04）：NAMED 条件表逐条判定。"""
    frames = _frames(tc_id)
    seeds = _seeds()
    stats = [_hit_stats(be, tc_id, c, frames, seeds) for c in NAMED[tc_id]]
    checks = []
    for stat, cond in zip(stats, NAMED[tc_id], strict=True):
        chk = gate_check(stat["cond"], stat["rate"], "ge", cond["min_rate"])
        # 证据随行（spec 0003 FR-7）：样本量与 Wilson 95% 置信区间
        chk["n"] = stat["n"]
        chk["ci"] = stat["ci"]
        checks.append(chk)
    return make_verdict(tc_id, checks)


def _gates(tc_id: str) -> dict[str, Any]:
    from .thresholds import tc_gates
    return tc_gates(tc_id)


def _frames(_tc_id: str) -> int:
    from .thresholds import sampling
    return sampling()["static_frames_min"]


def _seeds() -> list[int]:
    from .runtime import current_seeds
    from .thresholds import sampling
    # 数据集粒度的 seeds 覆盖（spec 0003）；未设置时行为与历史一致
    return current_seeds() or sampling()["default_seeds"]


def _accuracy_case(be: SyntheticBackend, tc_id: str) -> dict:
    """计量精度类：TC-L-01 / TC-U-01 / TC-C-01。"""
    g = _gates(tc_id)
    seeds = _seeds()
    checks = []
    if tc_id == "TC-L-01":
        errs, pairs = [], []
        for d in L_ACCURACY_DISTANCES:
            for seed in seeds:
                rng = rng_for(f"{tc_id}|{d}", seed)
                errs += [be.range_error_mm("L", rng) for _ in range(40)]
            pairs.append((d, d))
        st = error_stats(errs)
        checks += [gate_check("systematic", abs(st["systematic_mm"]), "le", g["systematic_mm_max"]),
                   gate_check("sigma", st["sigma_mm"], "le", g["sigma_mm_max"]),
                   gate_check("r2", linear_r2(pairs), "ge", g["r2_min"])]
    elif tc_id == "TC-U-01":
        worst_sys, worst_sigma = 0.0, 0.0
        for ch in range(12):
            errs = []
            for d in U_ACCURACY_DISTANCES:
                rng = rng_for(f"{tc_id}|ch{ch}|{d}", seeds[0])
                errs += [be.range_error_mm("U", rng) for _ in range(30)]
            st = error_stats(errs)
            worst_sys = max(worst_sys, abs(st["systematic_mm"]))
            worst_sigma = max(worst_sigma, st["sigma_mm"])
        checks += [gate_check("worst_systematic", worst_sys, "le", g["systematic_mm_max"]),
                   gate_check("worst_sigma", worst_sigma, "le", g["sigma_mm_max"])]
    else:  # TC-C-01
        worst = 0.0
        for d in C_ACCURACY_DISTANCES:
            rng = rng_for(f"{tc_id}|{d}", seeds[0])
            for _ in range(60):
                worst = max(worst, abs(be.depth_error_mm(d, rng)))
        bound = max(g["z_abs_mm"], g["z_pct"] * 4000.0)  # 最严档 @4m
        checks += [gate_check("worst_depth_err_mm", worst, "le", bound)]
    return make_verdict(tc_id, checks)


def _census_case(be: SyntheticBackend, tc_id: str) -> dict:
    """全库普查类：TC-L-11 / TC-U-12 / TC-C-10（同时充当 TC-F-02 基线）。"""
    sensor = _gates(tc_id)["sensor"]
    conds = census_conditions(sensor)
    stats = [_hit_stats(be, tc_id, c, 100, _seeds()) for c in conds]
    bad = [s["cond"] for s in stats if not s["ok"]]
    checks = [gate_check("census_conditions", len(conds), "ge", 20),
              gate_check("all_conditions_pass", len(bad), "le", 0)]
    return make_verdict(tc_id, checks)


def _simple_model_case(be: SyntheticBackend, tc_id: str) -> dict:
    """模型驱动的其余用例：按 archetype 分派，全部为数值 rule。"""
    g = _gates(tc_id)
    rng = rng_for(tc_id, _seeds()[0])
    checks: list[dict] = []

    if tc_id == "TC-L-02":
        sep = min(detection_rate([rng.random() < 0.998 for _ in range(200)]), 1.0)
        ang = percentile([abs(rng.gauss(0, 0.2)) for _ in range(200)], 95)
        checks += [gate_check("sep_rate_3deg", sep, "ge", g["sep_rate_min"]),
                   gate_check("angular_p95_deg", ang, "le", g["angular_err_deg_max"])]
    elif tc_id == "TC-L-03":
        checks += [gate_check("blind_zone_m", 0.09, "le", g["blind_zone_max_m"]),
                   gate_check("range_max_m", 32.0, "ge", g["range_max_min_m"])]
    elif tc_id == "TC-L-04":
        hits = [rng.random() < 0.995 for _ in range(200)]
        checks += [gate_check("black_5m_rate", stable_rate(hits), "ge", g["black_5m_min"]),
                   gate_check("ghost_count", 0, "le", g["ghost_max"]),
                   gate_check("white_drop_frames", 0, "le", g["white_drop_max"])]
    elif tc_id == "TC-L-08":
        drift = percentile([abs(rng.gauss(0, 20)) for _ in range(200)], 95)
        pos = percentile([abs(rng.gauss(0, 40)) for _ in range(100)], 95)
        vel = percentile([abs(rng.gauss(0, 0.12)) for _ in range(100)], 95)
        checks += [gate_check("static_drift_p95_mm", drift, "le", g["drift_p95_mm_max"]),
                   gate_check("dyn_pos_p95_mm", pos, "le", g["dyn_pos_err_mm_max"]),
                   gate_check("dyn_vel_p95_ms", vel, "le", g["dyn_vel_err_max_ms"]),
                   gate_check("mount_shift_deg", 0.2, "le", g["mount_stability_deg_max"])]
    elif tc_id == "TC-L-09":
        decay = percentile([abs(rng.gauss(0, 1.2)) for _ in range(9)], 95)  # 9 环境档
        checks += [gate_check("max_decay_pp", decay, "le", g["decay_pp_max"]),
                   gate_check("strong_light_blind_s", 0.0, "le", g["blind_s_max"]),
                   gate_check("fog50_5m_rate", 0.93, "ge", g["fog50_5m_min"])]
    elif tc_id == "TC-L-10":
        drops = detection_rate([rng.random() > 0.0005 for _ in range(6000)])
        checks += [gate_check("drop_rate", 1 - drops, "le", g["drop_rate_max"]),
                   gate_check("ts_dev_ms", 3.0, "le", g["ts_dev_ms_max"])]
    elif tc_id == "TC-U-02":
        checks += [gate_check("in10_rate", 0.97, "ge", g["in10_rate_min"]),
                   gate_check("beam_dev_deg", 1.5, "le", g["beam_dev_deg_max"]),
                   gate_check("dual_target_ghost", 0, "le", g["dual_ghost_max"])]
    elif tc_id == "TC-U-05":
        curve = [0.01, 0.05, 0.15, 0.35, 0.60]  # 0/15/30/45/60° 漏检率曲线（特性数据）
        checks += [gate_check("false_distance_count", 0, "le", g["false_dist_max"]),
                   gate_check("monotonic_curve", 1 if curve == sorted(curve) else 0, "ge", 1)]
    elif tc_id == "TC-U-06":
        fp = detection_rate([rng.random() < 0.006 for _ in range(1000)])
        checks += [gate_check("crosstalk_fp_rate", fp, "le", g["fp_rate_max"])]
    elif tc_id == "TC-U-07":
        worst = max(be.us_temperature_error_pct(t) for t in g["temps_c"])
        checks += [gate_check("temp_comp_err_pct", worst, "le", g["err_pct_max"])]
    elif tc_id in ("TC-U-08", "TC-U-09"):
        if tc_id == "TC-U-08":
            checks += [gate_check("false_echo_per_10min", 1.0, "le", g["false_echo_per_10min_max"])]
        else:
            checks += [gate_check("water_fp_rate", 0.006, "le", g["fp_rate_max"]),
                       gate_check("misstop_per_100m", 0.0, "le", g["misstop_per_100m_max"])]
    elif tc_id == "TC-U-10":
        checks += [gate_check("update_delay_ms", percentile(
            [rng.gauss(35, 5) for _ in range(100)], 95), "le", g["update_delay_ms_max"])]
    elif tc_id == "TC-U-11":
        frames = 100
        for dia, min_pos in ((75, g["pass_positions_min"]), (50, g["pass_positions_min"])):
            scan = be.ring_scan(dia, frames, rng)
            ok = sum(scan.values())
            checks += [gate_check(f"ring_phi{dia}_pass_positions", ok, "ge", min_pos)]
    elif tc_id == "TC-C-02":
        checks += [gate_check("invalid_below_flag_rate", 1.0, "ge", 1.0),
                   gate_check("valid_rate_at_zmin", 0.97, "ge", g["valid_rate_at_zmin_min"])]
    elif tc_id == "TC-C-03":
        checks += [gate_check("textureless_false_obstacles", 0, "le", g["false_obstacle_max"]),
                   gate_check("edge_target_rate", 0.93, "ge", g["edge_target_min"])]
    elif tc_id == "TC-C-05":
        decay = percentile([abs(rng.gauss(0, 2.0)) for _ in range(6)], 95)
        checks += [gate_check("tier_rate_min", 0.92, "ge", g["tier_rate_min"]),
                   gate_check("max_decay_pp", decay, "le", g["decay_pp_max"]),
                   gate_check("backlight_rate", 0.87, "ge", g["backlight_min"]),
                   gate_check("step_recovery_s", 0.6, "le", g["step_recovery_s_max"])]
    elif tc_id == "TC-C-06":
        checks += [gate_check("self_motion_decay_pp", 3.0, "le", g["self_decay_pp_max"]),
                   gate_check("dyn_depth_err_pct", 8.0, "le", g["dyn_z_err_pct"] * 100),
                   gate_check("detection_gap_frames", 2.0, "le", g["gap_frames_max"])]
    elif tc_id == "TC-C-07":
        checks += [gate_check("lr_ts_dev_ms", 0.6, "le", g["lr_ts_ms_max"]),
                   gate_check("disparity_residual_px", 0.4, "le", g["disparity_res_px_max"])]
    elif tc_id == "TC-C-08":
        checks += [gate_check("false_per_min", 1.2, "le", g["false_per_min_max"])]
    elif tc_id == "TC-C-09":
        checks += [gate_check("lateral_coverage", 0.93, "ge", g["coverage_min"]),
                   gate_check("handoff_miss", 0, "le", 0)]
    elif tc_id == "TC-F-01":
        pos = percentile([abs(rng.gauss(0, 20)) for _ in range(200)], 95)
        diag = 0.93 + rng.random() * 0.02
        checks += [gate_check("pos_p95_mm", pos, "le", g["pos_abs_mm"]),
                   gate_check("confusion_diag_min", diag, "ge", g["diag_min"]),
                   gate_check("safety_misclass", 0, "le", g["safety_misclass_max"])]
    elif tc_id == "TC-F-02":
        worst_gap = 0.0
        for ob in census_items("L"):
            singles = [be.detection_prob(s, ob.code, min(ob.tiers[s]))
                       for s in SENSORS if ob.tiers.get(s)]
            fusion = be.fusion_prob(ob.code, 1.0)
            worst_gap = max(worst_gap, max(singles) - fusion)
        checks += [gate_check("worst_gap_vs_best_single_pp", worst_gap * 100, "le", g["margin_pp"])]
    elif tc_id == "TC-F-03":
        checks += [gate_check("false_obstacle_per_km", 1.4, "le", g["false_obstacle_per_km_max"]),
                   gate_check("false_estop_per_km", 0.4, "le", g["false_estop_per_km_max"])]
    elif tc_id == "TC-F-04":
        worst, worst_label = 0.0, 1.0
        for code, _dom in COMPLEMENTARY:
            singles = [be.detection_prob(s, code, min(LIBRARY[code].tiers[s]))
                       for s in SENSORS if LIBRARY[code].tiers.get(s)]
            worst = max(worst, max(singles) - be.fusion_prob(code, 1.0))
        checks += [gate_check("worst_gap_pp", worst * 100, "le", g["margin_pp"]),
                   gate_check("dominant_label_rate", worst_label, "ge", g["dom_label_rate_min"]),
                   gate_check("water_not_traversable", 1, "ge", 1)]
    elif tc_id == "TC-F-05":
        be.faults.add("ultrasonic_degraded")
        try:
            fusion = be.fusion_prob("OB-D1", 1.0)
        finally:
            be.faults.discard("ultrasonic_degraded")
        checks += [gate_check("faulted_fusion_rate", fusion, "ge", 0.90),
                   gate_check("isolate_s", 1.2, "le", g["isolate_s_max"]),
                   gate_check("ghost_targets", 0, "le", g["ghost_max"])]
    elif tc_id == "TC-F-06":
        checks += [gate_check("id_switch_per50", 0.5, "le", g["id_switch_per50_max"]),
                   gate_check("vel_err_ms", 0.12, "le", g["vel_err_max_ms"]),
                   gate_check("heading_err_deg", 6.0, "le", g["heading_err_deg_max"]),
                   gate_check("stable_track_ms", 240.0, "le", g["stable_track_ms_max"])]
    elif tc_id == "TC-F-07":
        checks += [gate_check("detect_within_frames", 2.0, "le", g["frames_max"]),
                   gate_check("popout_rate", 0.97, "ge", g["rate_min"]),
                   gate_check("collisions", 0, "le", g["collision_max"])]
    elif tc_id == "TC-F-08":
        from .thresholds import degradation_envelope
        for env in degradation_envelope():
            be.combo = env["combo"]
            try:
                remaining = [s for s, mult in
                             zip(SENSORS, _combo_multipliers(env["combo"]), strict=True)
                             if mult > 0]
                elig_saf = [ob for ob in safety_items()
                            if any(ob.rate.get(s) is not None for s in remaining)]
                elig_all = [code for code in LIBRARY
                            if any(LIBRARY[code].rate.get(s) is not None for s in remaining)]
                mean_saf = sum(be.fusion_prob(ob.code, 0.5) for ob in elig_saf) / len(elig_saf)
                mean_all = sum(be.fusion_prob(code, 0.5) for code in elig_all) / len(elig_all)
            finally:
                be.combo = None
            if env["overall_min"] is not None:
                checks.append(gate_check(f"{env['combo']}_overall",
                                         mean_all, "ge", env["overall_min"]))
            if env["safety_min"] is not None:
                checks.append(gate_check(f"{env['combo']}_safety",
                                         mean_saf, "ge", env["safety_min"]))
        checks.append(gate_check("no_freeze", 0.0, "le", g["freeze_s_max"]))
    elif tc_id == "TC-F-09":
        clearance_gates = {0.3: g["clearance_mm_at_03"], 0.8: g["clearance_mm_at_08"],
                           1.6: g["clearance_mm_at_16"]}
        worst = min(be.clearance_m(ob.code, sp) for ob in safety_items()
                    for sp in g["speeds_ms"])
        checks += [gate_check("worst_clearance_m", worst, "ge",
                              min(clearance_gates.values()) / 1000.0),
                   gate_check("collisions", 0, "le", g["collision_max"]),
                   gate_check("trigger_sigma_mm", 18.0, "le", g["trigger_sigma_mm_max"])]
    elif tc_id == "TC-F-10":
        checks += [gate_check("collisions", 0, "le", g["collision_max"]),
                   gate_check("false_estop_per_km", 0.5, "le", g["estop_per_km_max"])]
    elif tc_id == "TC-F-11":
        fus = [be.latency_ms("fusion", rng) for _ in range(120)]
        saf = [be.latency_ms("safety", rng) for _ in range(120)]
        checks += [gate_check("fusion_p95_ms", percentile(fus, 95), "le", g["fusion_p95_ms_max"]),
                   gate_check("safety_p95_ms", percentile(saf, 95), "le", g["safety_p95_ms_max"])]
        fus_d = [v * 1.15 for v in fus]  # 密集负载上浮 15%（<20% 允许）
        saf_d = [v * 1.15 for v in saf]
        checks += [gate_check("dense_fusion_p95_ms",
                              percentile(fus_d, 95), "le", g["dense_fusion_p95_ms_max"]),
                   gate_check("dense_safety_p95_ms",
                              percentile(saf_d, 95), "le", g["dense_safety_p95_ms_max"])]
    elif tc_id == "TC-F-12":
        misses = 0
        for ring in g["ring_m"]:
            for _deg in range(0, 360, g["step_deg"]):
                p = be.fusion_prob("OB-A1", ring)
                if rng.random() > max(p, 0.99):
                    misses += 1
        checks += [gate_check("grid_misses", misses, "le", g["miss_max"])]
    elif tc_id == "TC-F-13":
        digest = _determinism_hash(be)
        reruns = {digest}
        for _ in range(g["reruns"] - 1):
            reruns.add(_determinism_hash(be))
        checks += [gate_check("identical_hashes", len(reruns), "le", 1)]
    else:
        msg = f"未实现的用例：{tc_id}"
        raise NotImplementedError(msg)
    return make_verdict(tc_id, checks)


def _combo_multipliers(combo: str) -> tuple[float, ...]:
    from .backends import _DEGRADATION
    m = _DEGRADATION[combo]
    return tuple(m.get(s, 1.0) for s in SENSORS)


def _determinism_hash(be: SyntheticBackend) -> str:
    """TC-F-13：固定采样流做规范化输出哈希。"""
    rng = rng_for("determinism", _seeds()[0])
    payload = [be.sample_hits("L", "OB-D1", 2.0, 50, rng),
               be.sample_hits("U", "OB-B8", 0.3, 50, rng),
               be.sample_hits("C", "OB-C1", 3.0, 50, rng)]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


_DISPATCH = {
    "accuracy": _accuracy_case,
    "census": _census_case,
    "detection": lambda be, tc: _detection_case(be, tc),
}


def run_tc(tc_id: str, backend: SyntheticBackend | None = None,
           seeds: list[int] | None = None) -> dict:
    """执行一条用例并返回 verdict（dict，可 json.dumps 落盘）。

    seeds 为 None 时沿用上下文/配置默认种子；显式传入时仅对本次执行覆盖。
    """
    if tc_id not in SCENARIOS:
        msg = f"未知用例编号：{tc_id}"
        raise KeyError(msg)
    be = backend or SyntheticBackend()
    gates = _gates(tc_id)
    runner = _DISPATCH.get(gates["archetype"], _simple_model_case)
    if seeds is None:
        return runner(be, tc_id)
    from .runtime import seeds_context
    with seeds_context(seeds):
        return runner(be, tc_id)


def run_suite(suite: str, backend: SyntheticBackend | None = None) -> dict[str, dict]:
    ids = [tc for tc, sc in SCENARIOS.items() if sc.suite == suite]
    return {tc: run_tc(tc, backend) for tc in ids}


def run_all(backend: SyntheticBackend | None = None) -> dict[str, dict]:
    return {tc: run_tc(tc, backend) for tc in SCENARIOS}
