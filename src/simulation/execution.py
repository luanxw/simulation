"""批次执行编排（spec 0003 FR-3）：执行矩阵 = 数据集 × 用例。

execute_batch 产出纯 dict 的 RunRecord（可 json.dumps），结构：
    schema_version / batch（归一化快照）/ datasets（含生效 seeds）/
    tcs（有序用例编号）/ results（按数据集分组的 verdict）/ summary（总体+四专题）。
"""

from __future__ import annotations

from typing import Any

from .backends import SyntheticBackend
from .runner import run_tc
from .scenarios import SCENARIOS
from .selection import (
    BatchConfig,
    SelectionOverride,
    resolve_datasets,
    select_tcs,
)

SCHEMA_VERSION = 1

# 报告/总览统一使用的专题中文名（固定，spec 0003 约束）
SUITE_TITLES: dict[str, str] = {
    "L": "激光 LiDAR",
    "U": "USS 超声",
    "C": "相机",
    "F": "融合",
}
SUITE_ORDER: tuple[str, ...] = ("L", "U", "C", "F")


def execute_batch(batch: BatchConfig, override: SelectionOverride | None = None,
                  backend: SyntheticBackend | None = None,
                  seed_override: int | None = None) -> dict[str, Any]:
    """按 数据集 × 用例 矩阵执行，返回 RunRecord。"""
    tcs = select_tcs(batch, override)
    datasets = resolve_datasets(batch, seed_override)
    be = backend or SyntheticBackend()

    results: list[dict[str, Any]] = []
    for ds in datasets:
        runs: dict[str, dict[str, Any]] = {}
        for tc in tcs:
            runs[tc] = run_tc(tc, be, seeds=ds["seeds"])
        results.append({"dataset": ds["id"], "runs": runs})

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "batch": batch.to_dict(),
        "datasets": datasets,
        "tcs": list(tcs),
        "results": results,
    }
    record["summary"] = summarize(record)
    return record


def _iter_verdicts(record: dict[str, Any]):
    for group in record["results"]:
        for tc, verdict in group["runs"].items():
            yield group["dataset"], tc, verdict


def _check_counts(verdict: dict[str, Any]) -> tuple[int, int]:
    """返回单条 verdict 的（live 检查项数, 通过数）；pending_backend 不计入分母。"""
    live = [c for c in verdict["checks"] if c.get("status") != "pending_backend"]
    passed = sum(1 for c in live if c.get("status") == "pass")
    return len(live), passed


def summarize(record: dict[str, Any]) -> dict[str, Any]:
    """总体 + 四专题统计：执行次数（数据集×用例）、通过率、检查项通过率。

    未出现的专题计数为 0、rate 为 None（报告层显示「—」），不抛异常。
    """
    stats = {
        suite: {"tc_total": 0, "tc_passed": 0, "tc_rate": None,
                "check_total": 0, "check_passed": 0, "check_rate": None}
        for suite in SUITE_ORDER
    }
    for _ds_id, tc, verdict in _iter_verdicts(record):
        suite = tc.split("-")[1]
        bucket = stats[suite]
        bucket["tc_total"] += 1
        if verdict["pass"]:
            bucket["tc_passed"] += 1
        live, passed = _check_counts(verdict)
        bucket["check_total"] += live
        bucket["check_passed"] += passed

    for bucket in stats.values():
        if bucket["tc_total"]:
            bucket["tc_rate"] = round(bucket["tc_passed"] / bucket["tc_total"], 4)
        if bucket["check_total"]:
            bucket["check_rate"] = round(bucket["check_passed"] / bucket["check_total"], 4)

    total_tc = sum(b["tc_total"] for b in stats.values())
    passed_tc = sum(b["tc_passed"] for b in stats.values())
    total_check = sum(b["check_total"] for b in stats.values())
    passed_check = sum(b["check_passed"] for b in stats.values())
    overall = {
        "tc_total": total_tc,
        "tc_passed": passed_tc,
        "tc_failed": total_tc - passed_tc,
        "tc_rate": round(passed_tc / total_tc, 4) if total_tc else None,
        "check_total": total_check,
        "check_passed": passed_check,
        "check_rate": round(passed_check / total_check, 4) if total_check else None,
        "datasets": len(record.get("datasets", ())),
        "unique_tcs": len(record.get("tcs", ())),
    }
    return {"overall": overall, "by_suite": stats,
            "suite_titles": {k: SUITE_TITLES[k] for k in SUITE_ORDER}}


def tc_title(tc_id: str) -> str:
    """供报告层取用例中文标题。"""
    return SCENARIOS[tc_id].title
