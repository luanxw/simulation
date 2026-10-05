"""判定器（test oracle 的中文定名）：检出率、Wilson 置信区间、误差统计、稳定检出窗。

对应 spec 0002 第 2.4 节的全局统计定义；rule 证据一律为数值结果，禁止截图。
命名说明：本模块为测试判定逻辑，与任何数据库产品无关。
"""

from __future__ import annotations

import math
from collections.abc import Sequence

Z95 = 1.96


def detection_rate(hits: Sequence[bool]) -> float:
    if not hits:
        msg = "检出率样本不能为空"
        raise ValueError(msg)
    return sum(1 for h in hits if h) / len(hits)


def wilson_interval(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score 区间；n=0 返回 (0,0)。"""
    if n <= 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def stable_rate(hits: Sequence[bool], window: int = 10, min_hits: int = 8) -> float:
    """稳定检出率：10 帧滑窗内 >=8 帧检出的窗口占比。"""
    if len(hits) < window:
        msg = f"样本量 {len(hits)} 不足滑窗 {window}"
        raise ValueError(msg)
    ok = sum(1 for i in range(len(hits) - window + 1)
             if sum(hits[i:i + window]) >= min_hits)
    return ok / (len(hits) - window + 1)


def error_stats(errors_mm: Sequence[float]) -> dict[str, float]:
    """系统误差（均值）与随机误差（σ，无偏估计）。"""
    n = len(errors_mm)
    if n < 2:
        msg = "误差统计至少需要 2 个样本"
        raise ValueError(msg)
    mean = sum(errors_mm) / n
    var = sum((e - mean) ** 2 for e in errors_mm) / (n - 1)
    return {"systematic_mm": mean, "sigma_mm": math.sqrt(var), "n": n}


def linear_r2(pairs: Sequence[tuple[float, float]]) -> float:
    """(实测, 真值) 序列的线性拟合优度。"""
    n = len(pairs)
    if n < 3:
        msg = "R² 拟合至少需要 3 点"
        raise ValueError(msg)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        msg = "R² 拟合输入为常数序列"
        raise ValueError(msg)
    return (sxy * sxy) / (sxx * syy)


def percentile(values: Sequence[float], q: float) -> float:
    """最近邻法百分位。"""
    if not values:
        msg = "百分位输入不能为空"
        raise ValueError(msg)
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil(q / 100 * len(ordered)) - 1))
    return ordered[idx]


def gate_check(name: str, value: float, op: str, threshold: float) -> dict:
    """单条 rule 判定。op: le(<=) / ge(>=) / lt / gt。"""
    cmp_ok = {
        "le": value <= threshold,
        "ge": value >= threshold,
        "lt": value < threshold,
        "gt": value > threshold,
    }[op]
    return {
        "name": name,
        "status": "pass" if cmp_ok else "fail",
        "value": round(value, 6),
        "op": op,
        "threshold": threshold,
    }


def pending_check(name: str, reason: str) -> dict:
    """标记等待真实仿真引擎后端的检查项（不阻塞判定）。"""
    return {"name": name, "status": "pending_backend", "reason": reason}


def make_verdict(tc_id: str, checks: Sequence[dict]) -> dict:
    """汇总判定：live 检查全部通过且无 failed；pending_backend 不阻塞。"""
    live = [c for c in checks if c["status"] != "pending_backend"]
    failed = [c for c in live if c["status"] == "fail"]
    return {
        "tc": tc_id,
        "pass": not failed,
        "n_checks": len(checks),
        "n_live": len(live),
        "n_pending_backend": len(checks) - len(live),
        "failed": [c["name"] for c in failed],
        "checks": list(checks),
    }
