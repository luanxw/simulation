"""集中配置装载：传感器参数与测试阈值（AGENTS.md §4 数值参数集中配置）。"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent / "config"


@functools.cache
def load_sensor_params() -> dict[str, Any]:
    with open(CONFIG_DIR / "sensor_params.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@functools.cache
def load_thresholds() -> dict[str, Any]:
    with open(CONFIG_DIR / "test_thresholds.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def tc_gates(tc_id: str) -> dict[str, Any]:
    """取某条用例的阈值字典，未登记则抛 KeyError（禁止散落硬编码）。"""
    suite = tc_id.split("-")[1]  # TC-L-01 -> L
    gates = load_thresholds()["suites"][suite].get(tc_id)
    if gates is None:
        msg = f"{tc_id} 未在 test_thresholds.yaml 登记"
        raise KeyError(msg)
    return gates


def sampling() -> dict[str, Any]:
    return load_thresholds()["sampling"]


def sensor_envelope() -> dict[str, Any]:
    return load_thresholds()["sensor_envelope"]


def degradation_envelope() -> list[dict[str, Any]]:
    return load_thresholds()["degradation_envelope"]
