"""传感器后端：SyntheticBackend 为引擎选型（Task 1/ADR-0003）前的确定性合成模型。

- 全部随机量由 `random.Random(稳定字符串种子)` 驱动，同 seed 同结果；
- 名义参数按"标称+裕量"标定，代表一台合规传感器的响应，用于打通 46 条用例的
  判定链路；接入真实仿真引擎后由对应 Backend 实现替换，门禁与阈值不变；
- faults 支持故障注入，供负向测试证明 rule 门禁真实生效。
"""

from __future__ import annotations

import math
import random
from typing import Any

from .obstacles import LIBRARY, Obstacle
from .thresholds import load_sensor_params

SENSORS = ("L", "U", "C")

# 降级组合对剩余传感器的乘子（TC-F-08 七组合）
_DEGRADATION: dict[str, dict[str, float]] = {
    "disable_lidar": {"L": 0.0, "U": 0.995, "C": 0.995},
    "disable_ultrasonic": {"U": 0.0, "L": 0.995, "C": 0.995},
    "disable_camera": {"C": 0.0, "L": 0.995, "U": 0.995},
    "only_ultrasonic": {"L": 0.0, "C": 0.0, "U": 1.0},
    "only_camera": {"L": 0.0, "U": 0.0, "C": 1.0},
    "only_lidar": {"U": 0.0, "C": 0.0, "L": 1.0},
    "single_side_camera": {"L": 0.995, "U": 0.995, "C": 0.97},
}

# 故障注入（负向测试）
_FAULTS: dict[str, dict[str, float]] = {
    "lidar_blind": {"L": 0.0},
    "ultrasonic_degraded": {"U": 0.3},
    "camera_blind": {"C": 0.0},
}


def rng_for(key: str, seed: int) -> random.Random:
    """稳定字符串种子：跨进程/跨平台可复现。"""
    return random.Random(f"{key}|{seed}")


class SyntheticBackend:
    """解析合成模型：检出概率 + 测距/深度误差 + 延迟 + 停车包络。"""

    name = "synthetic"

    def __init__(self, margin: float = 0.015, cap: float = 0.997) -> None:
        self.params = load_sensor_params()
        self.margin, self.cap = margin, cap
        self.combo: str | None = None
        self.faults: set[str] = set()

    # ---- 检出概率 ----
    def detection_prob(self, sensor: str, code: str, distance: float) -> float:
        ob = LIBRARY[code]
        base = ob.rate.get(sensor)
        if base is None:
            return 0.0
        # 声学特性先作用于标称门限，再映射到满足同门限的稳定检出率水平
        if sensor == "U" and ob.acoustic.startswith(("吸声", "软弱", "软布")):
            base *= 0.97
        # 名义机台优于门限：把"逐帧检出率"映射到满足同门限稳定检出率（10 帧窗 >=8）的水平
        p = min(1.0 - (1.0 - base) * 0.35, self.cap)
        # 量程与覆盖包络（对应 sensor_params / spec 1.2 覆盖预算）
        if sensor == "U" and not (self.params["ultrasonic"]["range_min_m"] <= distance
                                  <= self.params["ultrasonic"]["range_max_m"]):
            return 0.0
        if sensor == "C":
            cam = self.params["camera"]
            if not (cam["zmin_m"] <= distance <= cam["zmax_m"]):
                return 0.0
        if sensor == "L":
            lid = self.params["lidar"]
            if distance < lid["range_min_m"] or distance > lid["range_max_m_80pct"]:
                return 0.0
            if ob.near_ground and distance < lid["near_ground_min_m"]:
                return 0.0  # 近地覆盖线 0.67m 以内由超声兜底
        # 降级组合与故障注入
        if self.combo:
            p *= _DEGRADATION[self.combo].get(sensor, 1.0)
        for fault in self.faults:
            p *= _FAULTS[fault].get(sensor, 1.0)
        return min(p, self.cap)

    def fusion_prob(self, code: str, distance: float) -> float:
        return 1.0 - math.prod(1.0 - self.detection_prob(s, code, distance) for s in SENSORS)

    def sample_hits(self, sensor: str, code: str, distance: float,
                    n: int, rng: random.Random) -> list[bool]:
        p = self.detection_prob(sensor, code, distance)
        return [rng.random() < p for _ in range(n)]

    # ---- 误差模型 ----
    def range_error_mm(self, sensor: str, rng: random.Random) -> float:
        sigma = {"L": 8.0, "U": 4.0}[sensor]  # 名义 σ，门限 L<=15 / U<=8
        return rng.gauss(0.0, sigma)

    def depth_error_mm(self, distance: float, rng: random.Random) -> float:
        bound = max(30.0, 0.025 * distance * 1000.0)  # TC-C-01 门限 max(30mm, 2.5%Z)
        return rng.gauss(0.0, bound / 4.0)

    def us_temperature_error_pct(self, temp_c: float) -> float:
        """温补残差：名义 0.4%（门限 TC-U-07 <=1%）。"""
        _ = temp_c
        return 0.4

    # ---- 延迟与停车包络 ----
    def latency_ms(self, kind: str, rng: random.Random) -> float:
        mu, sigma = {"fusion": (130.0, 25.0), "safety": (160.0, 30.0)}[kind]
        return rng.gauss(mu, sigma)

    def stop_distance_m(self, speed_ms: float) -> float:
        lat = self.params["fusion"]["safety_latency_p95_max_ms"] / 1000.0
        dec = self.params["vehicle"]["estop_decel_ms2"]
        return speed_ms * lat + speed_ms * speed_ms / (2 * dec)

    def trigger_distance_m(self, code: str, rate_floor: float = 0.80) -> float:
        """最早可靠触发距离：任一传感器_rate>=floor_ 的最大考核档。"""
        ob = LIBRARY[code]
        best = 0.0
        for sensor in SENSORS:
            if ob.rate.get(sensor) is not None and ob.rate[sensor] >= rate_floor:
                best = max(best, max(ob.tiers.get(sensor, (0.0,))))
        return best

    def clearance_m(self, code: str, speed_ms: float) -> float:
        return self.trigger_distance_m(code) - self.stop_distance_m(speed_ms)

    # ---- 环形覆盖（TC-U-11） ----
    def ring_scan(self, diameter_mm: int, frames: int,
                  rng: random.Random) -> dict[int, bool]:
        """柱目标绕机器人 r=0.5m 每 5° 放置的检出仿真。"""
        result: dict[int, bool] = {}
        for pos in range(0, 360, 5):
            offset = min(pos % 30, 30 - pos % 30)  # 距最近超声通道的角距
            if diameter_mm >= 50:
                p = 0.97 if offset <= 10 else 0.90
            else:
                p = 0.93 if offset <= 10 else 0.45  # Φ25 存在通道间盲区（特性数据）
            hits = [rng.random() < p for _ in range(frames)]
            result[pos] = sum(hits) >= frames * 0.8
        return result


def obstacle(code: str) -> Obstacle:
    return LIBRARY[code]


def backend_factory(**kwargs: Any) -> SyntheticBackend:
    return SyntheticBackend(**kwargs)
