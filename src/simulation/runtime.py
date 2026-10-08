"""批次执行时的运行时上下文（spec 0003 Task 3）。

数据集粒度的 seeds 覆盖经 ContextVar 传递：runner._seeds() 优先读取上下文，
未设置时回退 test_thresholds.yaml 的 sampling.default_seeds——
保证 run_tc / run_suite / run_all 的既有调用行为零变化。
"""

from __future__ import annotations

import contextlib
import contextvars

_seeds_override: contextvars.ContextVar[list[int] | None] = contextvars.ContextVar(
    "simulation_seeds_override", default=None,
)


def current_seeds() -> list[int] | None:
    """当前执行上下文中的种子覆盖；未设置返回 None。"""
    return _seeds_override.get()


@contextlib.contextmanager
def seeds_context(seeds: list[int]):
    """在上下文内把默认种子替换为数据集指定种子，退出时自动恢复。"""
    token = _seeds_override.set(list(seeds))
    try:
        yield
    finally:
        _seeds_override.reset(token)
