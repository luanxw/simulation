"""场景注册表：46 条测试用例（TC-L 11 / TC-U 12 / TC-C 10 / TC-F 13）。

对应 spec 0002 第 4/5 章；场景即代码，随机量一律经 rng_for(场景键, seed) 派生。
named 条件表编码 spec 中"专项检出"用例的（障碍物, 传感器, 距离, 最低稳定检出率）。
"""

from __future__ import annotations

from dataclasses import dataclass

from .obstacles import census_items


@dataclass(frozen=True)
class Scenario:
    tc_id: str
    suite: str  # L / U / C / F
    title: str
    world: str  # W0 / W1 / W2 / W3 或组合
    kind: str   # static / dynamic / drive / safety


S = Scenario
SCENARIOS: dict[str, Scenario] = {
    # ---- LiDAR（11） ----
    "TC-L-01": S("TC-L-01", "L", "静态测距精度与线性度", "W0", "static"),
    "TC-L-02": S("TC-L-02", "L", "角度分辨率与方位精度", "W0", "static"),
    "TC-L-03": S("TC-L-03", "L", "量程边界与盲区", "W0", "static"),
    "TC-L-04": S("TC-L-04", "L", "反射率响应矩阵", "W0", "static"),
    "TC-L-05": S("TC-L-05", "L", "细长障碍检出（高尔夫专项）", "W1", "static"),
    "TC-L-06": S("TC-L-06", "L", "近地低矮目标与地面分割", "W1", "static"),
    "TC-L-07": S("TC-L-07", "L", "半透明/穿透类响应", "W1/W2", "static"),
    "TC-L-08": S("TC-L-08", "L", "运动畸变补偿与动态目标", "W1", "dynamic"),
    "TC-L-09": S("TC-L-09", "L", "环境鲁棒矩阵", "W3", "static"),
    "TC-L-10": S("TC-L-10", "L", "数据完整性与时间同步", "W1", "drive"),
    "TC-L-11": S("TC-L-11", "L", "全库 LiDAR 普查（单传感器基线载体）", "W1/W2", "static"),
    # ---- 超声（12） ----
    "TC-U-01": S("TC-U-01", "U", "通道级静态精度", "W0", "static"),
    "TC-U-02": S("TC-U-02", "U", "波束角测绘", "W0", "static"),
    "TC-U-03": S("TC-U-03", "U", "最小目标截面", "W0/W1", "static"),
    "TC-U-04": S("TC-U-04", "U", "软/吸声目标", "W0", "static"),
    "TC-U-05": S("TC-U-05", "U", "斜入射镜面失配", "W0", "static"),
    "TC-U-06": S("TC-U-06", "U", "通道间串扰", "W0", "static"),
    "TC-U-07": S("TC-U-07", "U", "温度声速补偿", "W3", "static"),
    "TC-U-08": S("TC-U-08", "U", "地面与草被伪影", "W1", "drive"),
    "TC-U-09": S("TC-U-09", "U", "水面回波", "W1", "drive"),
    "TC-U-10": S("TC-U-10", "U", "动态接近响应", "W0", "dynamic"),
    "TC-U-11": S("TC-U-11", "U", "环形覆盖连续性", "W0", "static"),
    "TC-U-12": S("TC-U-12", "U", "全库超声普查（单传感器基线载体）", "W0/W1/W2", "static"),
    # ---- 双目（10） ----
    "TC-C-01": S("TC-C-01", "C", "深度精度标定", "W0", "static"),
    "TC-C-02": S("TC-C-02", "C", "近距饱和与盲区 fail-safe", "W0", "static"),
    "TC-C-03": S("TC-C-03", "C", "无纹理表面", "W1/W2", "static"),
    "TC-C-04": S("TC-C-04", "C", "细长与线状目标", "W1/W2", "static"),
    "TC-C-05": S("TC-C-05", "C", "光照矩阵（含夜场）", "W2/W3", "static"),
    "TC-C-06": S("TC-C-06", "C", "自运动模糊与动态目标", "W2", "dynamic"),
    "TC-C-07": S("TC-C-07", "C", "双目同步与外参稳定", "W0", "static"),
    "TC-C-08": S("TC-C-08", "C", "镜头污染与雨雾", "W3", "static"),
    "TC-C-09": S("TC-C-09", "C", "侧向视场覆盖测绘", "W0", "static"),
    "TC-C-10": S("TC-C-10", "C", "全库双目普查（单传感器基线载体）", "W1/W2", "static"),
    # ---- 融合（13） ----
    "TC-F-01": S("TC-F-01", "F", "目标级精度与分类", "W1/W2", "static"),
    "TC-F-02": S("TC-F-02", "F", "检出完备性", "W1/W2", "static"),
    "TC-F-03": S("TC-F-03", "F", "虚警抑制", "W1/W2", "drive"),
    "TC-F-04": S("TC-F-04", "F", "互补专项矩阵", "W1/W2", "static"),
    "TC-F-05": S("TC-F-05", "F", "冲突仲裁", "W1", "static"),
    "TC-F-06": S("TC-F-06", "F", "动态跟踪", "W2", "dynamic"),
    "TC-F-07": S("TC-F-07", "F", "遮挡 pop-out", "W1", "dynamic"),
    "TC-F-08": S("TC-F-08", "F", "降级模式", "W1/W2", "static"),
    "TC-F-09": S("TC-F-09", "F", "安全功能——静态避碰", "W1/W2", "safety"),
    "TC-F-10": S("TC-F-10", "F", "安全功能——动态避碰", "W1/W2", "safety"),
    "TC-F-11": S("TC-F-11", "F", "端到端延迟", "W1", "dynamic"),
    "TC-F-12": S("TC-F-12", "F", "周身覆盖完备性", "W0", "static"),
    "TC-F-13": S("TC-F-13", "F", "确定性与可复现", "任意", "static"),
}

ALL_TC_IDS: tuple[str, ...] = tuple(SCENARIOS)


def _c(code: str, sensor: str, distance: float, min_rate: float) -> dict:
    return {"code": code, "sensor": sensor, "distance": distance, "min_rate": min_rate,
            "label": f"{code}@{sensor}:{distance}m"}


# ---- 专项检出条件表（spec 4/5 章逐条对应） ----
NAMED: dict[str, tuple[dict, ...]] = {
    "TC-L-05": (
        _c("OB-B1", "L", 0.5, 0.98), _c("OB-B1", "L", 1.0, 0.98), _c("OB-B1", "L", 2.0, 0.98),
        _c("OB-B1", "L", 3.0, 0.98), _c("OB-B1", "L", 5.0, 0.90),
        _c("OB-B7", "L", 3.0, 0.95), _c("OB-D5", "L", 2.0, 0.85),
    ),
    "TC-L-06": (
        _c("OB-B8", "L", 1.0, 0.80), _c("OB-B8", "L", 2.0, 0.90),
        _c("OB-B5", "L", 1.0, 0.90), _c("OB-B3a", "L", 0.8, 0.99),
    ),
    "TC-L-07": (
        _c("OB-B20", "L", 2.0, 0.95), _c("OB-C2", "L", 2.0, 0.95),
        _c("OB-D4", "L", 2.0, 0.90), _c("OB-B13", "L", 1.0, 0.95),
    ),
    "TC-U-03": (
        _c("OB-A1", "U", 0.5, 0.95), _c("OB-B1", "U", 0.5, 0.90),
        _c("OB-B8", "U", 0.3, 0.90), _c("OB-B8", "U", 0.5, 0.80),
        _c("OB-B5", "U", 0.3, 0.95), _c("OB-B17", "U", 0.3, 0.90),
        _c("OB-C10", "U", 0.3, 0.85),
    ),
    "TC-U-04": (_c("OB-A5", "U", 0.5, 0.90), _c("OB-D3", "U", 0.5, 0.90)),
    "TC-C-04": (
        _c("OB-C1", "C", 3.0, 0.98), _c("OB-C3", "C", 2.0, 0.90),
        _c("OB-D4", "C", 2.0, 0.85), _c("OB-A1", "C", 2.0, 0.95),
        _c("OB-B1", "C", 2.0, 0.90),
    ),
}

# TC-F-04 互补组（障碍物, 主导传感器；水面组为 pending_backend）
COMPLEMENTARY: tuple[tuple[str, str], ...] = (
    ("OB-B1", "L"), ("OB-B8", "U"), ("OB-A2", "L"), ("OB-D4", "F"),
)

L_ACCURACY_DISTANCES = (0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0)
U_ACCURACY_DISTANCES = (0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5)
C_ACCURACY_DISTANCES = (0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)


def census_conditions(sensor: str) -> list[dict]:
    """普查条件：该传感器列有档且有门限的障碍物 × 其全部距离档。"""
    conds = []
    for ob in census_items(sensor):
        for d in ob.tiers[sensor]:
            conds.append(_c(ob.code, sensor, d, min(ob.rate[sensor], 0.99)))
    return conds
