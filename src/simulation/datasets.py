"""数据集注册表装载（spec 0003 FR-3）。

批次（batch YAML）通过数据集 id 引用数据集；执行矩阵为「数据集 × 用例」。
- synthetic：合成后端数据集，params 仅允许 seeds（覆盖 sampling.default_seeds）。
- external：真实数据包的预留形态（path + 可选 checksum），本期只校验与归档引用，不执行。

新增合成数据集只需改 config/datasets.yaml，无需改代码。
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent / "config"
DATASET_KINDS = ("synthetic", "external")
_SYNTHETIC_PARAM_KEYS = {"seeds"}


class DatasetError(ValueError):
    """数据集注册结构错误或引用了未知数据集 id。"""


@dataclass(frozen=True)
class Dataset:
    id: str
    kind: str
    title: str
    description: str
    params: dict[str, Any]
    path: str | None = None
    checksum: dict[str, str] | None = None

    def effective_seeds(self, default_seeds: list[int]) -> list[int]:
        """数据集实际生效的种子：params.seeds 优先，否则沿用批次外的默认种子。"""
        seeds = self.params.get("seeds")
        return list(seeds) if seeds else list(default_seeds)


def parse_datasets(raw: Any) -> dict[str, Dataset]:
    """把注册表 YAML 解析为 {id: Dataset}，结构非法即抛 DatasetError。"""
    if not isinstance(raw, dict) or not isinstance(raw.get("datasets"), list):
        msg = "数据集注册表必须是含 datasets 列表的映射"
        raise DatasetError(msg)
    parsed: dict[str, Dataset] = {}
    for item in raw["datasets"]:
        ds = _parse_one(item)
        if ds.id in parsed:
            msg = f"数据集 id 重复：{ds.id}"
            raise DatasetError(msg)
        parsed[ds.id] = ds
    return parsed


def _parse_one(item: Any) -> Dataset:
    if not isinstance(item, dict):
        msg = f"数据集条目必须是映射，得到：{type(item).__name__}"
        raise DatasetError(msg)
    ds_id = item.get("id")
    if not isinstance(ds_id, str) or not ds_id:
        msg = f"数据集缺少非空 id 字段：{item!r}"
        raise DatasetError(msg)
    kind = item.get("kind")
    if kind not in DATASET_KINDS:
        msg = f"数据集 {ds_id} 的 kind 非法：{kind!r}，可选：{', '.join(DATASET_KINDS)}"
        raise DatasetError(msg)
    title = item.get("title", "")
    description = item.get("description", "")
    if not isinstance(title, str) or not isinstance(description, str):
        msg = f"数据集 {ds_id} 的 title/description 必须是字符串"
        raise DatasetError(msg)
    params = item.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, dict):
        msg = f"数据集 {ds_id} 的 params 必须是映射"
        raise DatasetError(msg)
    path = item.get("path")
    checksum = item.get("checksum")
    if kind == "synthetic":
        _validate_synthetic(ds_id, params)
        if path is not None:
            msg = f"数据集 {ds_id} 为 synthetic，不允许 path 字段"
            raise DatasetError(msg)
    else:
        if not isinstance(path, str) or not path:
            msg = f"数据集 {ds_id} 为 external，必须含非空 path 字段"
            raise DatasetError(msg)
        if checksum is not None and not _valid_checksum(ds_id, checksum):
            msg = f"数据集 {ds_id} 的 checksum 必须形如 {{alg: sha256, value: <非空字符串>}}"
            raise DatasetError(msg)
    return Dataset(id=ds_id, kind=kind, title=title, description=description,
                   params=params, path=path, checksum=checksum)


def _valid_checksum(ds_id: str, checksum: Any) -> bool:
    return (isinstance(checksum, dict)
            and isinstance(checksum.get("alg"), str) and bool(checksum["alg"])
            and isinstance(checksum.get("value"), str) and bool(checksum["value"]))


def _validate_synthetic(ds_id: str, params: dict[str, Any]) -> None:
    unknown = set(params) - _SYNTHETIC_PARAM_KEYS
    if unknown:
        msg = (f"数据集 {ds_id} 含未知 synthetic 参数：{sorted(unknown)}，"
               f"允许：{sorted(_SYNTHETIC_PARAM_KEYS)}")
        raise DatasetError(msg)
    if "seeds" in params:
        seeds = params["seeds"]
        if (not isinstance(seeds, list) or not seeds
                or any(isinstance(s, bool) or not isinstance(s, int) or s <= 0 for s in seeds)):
            msg = f"数据集 {ds_id} 的 seeds 必须是非空正整数列表，得到：{seeds!r}"
            raise DatasetError(msg)


@functools.cache
def load_datasets() -> dict[str, Dataset]:
    """装载 config/datasets.yaml（带缓存；测试可 parse_datasets 直接构造）。"""
    with open(CONFIG_DIR / "datasets.yaml", encoding="utf-8") as fh:
        return parse_datasets(yaml.safe_load(fh))


def get_dataset(dataset_id: str) -> Dataset:
    """按 id 取数据集；未知 id 报错并列出全部可用 id。"""
    table = load_datasets()
    if dataset_id not in table:
        avail = ", ".join(sorted(table))
        msg = f"未知数据集 id：{dataset_id}；可选：{avail}"
        raise DatasetError(msg)
    return table[dataset_id]
