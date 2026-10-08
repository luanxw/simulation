"""批次配置与用例选择器（spec 0003 FR-1 / FR-2 / FR-4）。

批次 YAML（扁平结构）：
    name: lidar-suite            # 可缺省，缺省取文件名
    version_label: v1.0          # 被测版本，可缺省（CLI --version 优先级更高）
    datasets: [synthetic-default]
    suites: [L]                  # L/U/C/F，与 include 取并集
    include: ["TC-U-03", "TC-L-0[1-5]"]   # 精确编号或 fnmatch 通配
    exclude: ["TC-L-11"]         # 通配/精确，最后剔除
    tags:
      world: [W1]                # 场景 world 标签（兼容 W1/W2 组合值）
      kind: [static]             # static/dynamic/drive/safety

选择语义：（suites ∪ include 命中）→ tags 过滤 → 减去 exclude；suites/include 均空 = 全量。
CLI 覆盖（SelectionOverride）：与批次选择结果取**交集收窄**，exclude **追加**。
"""

from __future__ import annotations

import fnmatch
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .datasets import get_dataset
from .scenarios import SCENARIOS

VALID_SUITES = ("L", "U", "C", "F")
TAG_KEYS = ("world", "kind")
_TOP_KEYS = {"name", "version_label", "datasets", "suites", "include", "exclude", "tags"}
_DEFAULT_DATASETS = ("synthetic-default",)


class SelectionError(ValueError):
    """批次配置非法、选择条件无命中或最终选择结果为空。"""


@dataclass(frozen=True)
class SelectionOverride:
    """命令行临时覆盖：非空字段构成收窄条件，与批次结果取交集；exclude 追加。"""

    suites: tuple[str, ...] = ()
    tcs: tuple[str, ...] = ()
    tags: dict[str, tuple[str, ...]] = field(default_factory=dict)
    exclude: tuple[str, ...] = ()


@dataclass(frozen=True)
class BatchConfig:
    name: str
    version_label: str | None
    datasets: tuple[str, ...]
    suites: tuple[str, ...]
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    tags: dict[str, tuple[str, ...]]
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """归一化快照（供归档与 manifest）。"""
        return asdict(self) | {"source_path": self.source_path}


def load_batch(path: str | Path) -> BatchConfig:
    """从 YAML 文件装载批次；结构或引用非法即抛 SelectionError。"""
    path = Path(path)
    if not path.is_file():
        msg = f"批次文件不存在：{path}"
        raise SelectionError(msg)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        msg = f"批次文件 YAML 解析失败：{path}：{exc}"
        raise SelectionError(msg) from exc
    if not isinstance(raw, dict):
        msg = f"批次文件必须是 YAML 映射：{path}"
        raise SelectionError(msg)
    return parse_batch(raw, name=path.stem, source_path=str(path))


def parse_batch(raw: dict[str, Any], *, name: str | None = None,
                source_path: str | None = None) -> BatchConfig:
    """解析并校验批次映射。"""
    unknown = set(raw) - _TOP_KEYS
    if unknown:
        msg = f"批次含未知字段 {sorted(unknown)}；允许：{sorted(_TOP_KEYS)}"
        raise SelectionError(msg)

    batch_name = raw.get("name") or name
    if not isinstance(batch_name, str) or not batch_name:
        msg = "批次 name 必须是非空字符串"
        raise SelectionError(msg)

    version_label = raw.get("version_label")
    if version_label is not None and (not isinstance(version_label, str) or not version_label):
        msg = "批次 version_label 必须是非空字符串或省略"
        raise SelectionError(msg)

    datasets = _as_str_tuple(raw.get("datasets", list(_DEFAULT_DATASETS)), "datasets")
    if not datasets:
        msg = "批次 datasets 不能为空"
        raise SelectionError(msg)
    for ds_id in datasets:  # 未知数据集立即报错（联动 datasets.py 注册表）
        get_dataset(ds_id)

    suites = _as_str_tuple(raw.get("suites", ()), "suites")
    for s in suites:
        if s not in VALID_SUITES:
            msg = f"未知专题 {s!r}；可选：{', '.join(VALID_SUITES)}"
            raise SelectionError(msg)

    include = _as_str_tuple(raw.get("include", ()), "include")
    exclude = _as_str_tuple(raw.get("exclude", ()), "exclude")
    tags = _parse_tags(raw.get("tags", {}))

    return BatchConfig(
        name=batch_name,
        version_label=version_label,
        datasets=datasets,
        suites=_dedupe(suites),
        include=include,
        exclude=exclude,
        tags=tags,
        source_path=source_path,
    )


def default_batch() -> BatchConfig:
    """不带 --batch 时的全量默认批次（46 条 × synthetic-default）。"""
    return BatchConfig(
        name="all-default",
        version_label=None,
        datasets=_DEFAULT_DATASETS,
        suites=(),
        include=(),
        exclude=(),
        tags={},
    )


def _as_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if (not isinstance(value, (list, tuple))
            or any(not isinstance(v, str) or not v for v in value)):
        msg = f"批次字段 {field_name} 必须是非空字符串列表，得到：{value!r}"
        raise SelectionError(msg)
    return tuple(value)


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for v in values:
        seen.setdefault(v, None)
    return tuple(seen)


def _parse_tags(raw: Any) -> dict[str, tuple[str, ...]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        msg = f"批次 tags 必须是映射，得到：{type(raw).__name__}"
        raise SelectionError(msg)
    tags: dict[str, tuple[str, ...]] = {}
    for key, values in raw.items():
        if key not in TAG_KEYS:
            msg = f"未知标签键 {key!r}；可选：{', '.join(TAG_KEYS)}"
            raise SelectionError(msg)
        vals = _as_str_tuple(values, f"tags.{key}")
        valid_values = _valid_tag_values(key)
        bad = [v for v in vals if v not in valid_values]
        if bad:
            msg = (f"标签 {key} 含未知值 {bad}；可选：{sorted(valid_values)}")
            raise SelectionError(msg)
        tags[key] = vals
    return tags


def _valid_tag_values(key: str) -> set[str]:
    if key == "world":
        tokens: set[str] = set()
        for sc in SCENARIOS.values():
            tokens.update(t for t in sc.world.split("/") if t and t != "任意")
        return tokens
    return {sc.kind for sc in SCENARIOS.values()}


def _has_wildcard(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[")


def _expand_patterns(patterns: tuple[str, ...], *, strict: bool) -> set[str]:
    """把编号/通配模式展开为命中 TC 集合。

    strict=True（include）：精确编号必须存在、通配必须有命中，否则报错。
    strict=False（exclude）：无命中静默跳过。
    """
    hits: set[str] = set()
    all_ids = tuple(SCENARIOS)
    for pattern in patterns:
        matched = {tc for tc in all_ids if fnmatch.fnmatchcase(tc, pattern)}
        if not matched and strict:
            if _has_wildcard(pattern):
                examples = ", ".join(all_ids[:5])
                msg = f"通配模式 {pattern!r} 未命中任何用例；可选编号示例：{examples} …"
            else:
                msg = f"未知用例编号 {pattern!r}；全部 {len(all_ids)} 条编号见 scenarios.py"
            raise SelectionError(msg)
        hits |= matched
    return hits


def _world_matches(scenario_world: str, wanted: tuple[str, ...]) -> bool:
    tokens = set(scenario_world.split("/"))
    # world 标注为「任意」的用例在任何 world 条件下都适用；无条件不过滤
    return scenario_world == "任意" or any(w in tokens for w in wanted)


def _apply_tags(candidates: set[str], tags: dict[str, tuple[str, ...]]) -> set[str]:
    selected = set()
    for tc in candidates:
        sc = SCENARIOS[tc]
        if "world" in tags and not _world_matches(sc.world, tags["world"]):
            continue
        if "kind" in tags and sc.kind not in tags["kind"]:
            continue
        selected.add(tc)
    return selected


def _select_side(suites: tuple[str, ...], patterns: tuple[str, ...],
                 tags: dict[str, tuple[str, ...]], *, strict_patterns: bool) -> set[str]:
    """单侧（批次或覆盖）选择：suites ∪ 通配命中 → tags 过滤；全空 = 全量无约束。"""
    if not suites and not patterns:
        candidates = set(SCENARIOS)
    else:
        candidates = {tc for tc, sc in SCENARIOS.items() if sc.suite in suites}
        candidates |= _expand_patterns(patterns, strict=strict_patterns)
    return _apply_tags(candidates, tags)


def select_tcs(batch: BatchConfig, override: SelectionOverride | None = None) -> tuple[str, ...]:
    """按批次（及 CLI 覆盖）解析最终执行用例，按编号排序返回。"""
    selected = _select_side(batch.suites, batch.include, batch.tags, strict_patterns=True)

    if override is not None and _override_active(override):
        over = _select_side(override.suites, override.tcs, override.tags, strict_patterns=True)
        selected &= over

    excluded = _expand_patterns(batch.exclude, strict=False)
    if override is not None:
        excluded |= _expand_patterns(override.exclude, strict=False)
    selected -= excluded

    if not selected:
        msg = "选择结果为空：没有任何用例同时满足批次与命令行条件"
        raise SelectionError(msg)
    return tuple(sorted(selected, key=_tc_sort_key))


def _tc_sort_key(tc: str) -> tuple[int, int]:
    """专题按 L/U/C/F 固定顺序，同专题按编号数字排序（与用例注册顺序一致）。"""
    suite = tc.split("-")[1]
    number = int(tc.rsplit("-", 1)[1])
    return VALID_SUITES.index(suite), number


def _override_active(override: SelectionOverride) -> bool:
    return bool(override.suites or override.tcs or override.tags or override.exclude)


def resolve_datasets(batch: BatchConfig, seed_override: int | None = None) -> list[dict[str, Any]]:
    """解析批次引用的数据集，返回 id/kind/title 与实际生效 seeds（seed_override 为全局覆盖）。"""
    from .thresholds import sampling

    default_seeds = sampling()["default_seeds"]
    resolved: list[dict[str, Any]] = []
    for ds_id in batch.datasets:
        ds = get_dataset(ds_id)
        seeds = [seed_override] if seed_override is not None else ds.effective_seeds(default_seeds)
        resolved.append({
            "id": ds.id,
            "kind": ds.kind,
            "title": ds.title,
            "description": ds.description,
            "params": dict(ds.params),
            "path": ds.path,
            "checksum": ds.checksum,
            "seeds": seeds,
            "seed_source": "cli" if seed_override is not None else (
                "dataset" if ds.params.get("seeds") is not None else "sampling_default"),
        })
    return resolved


def preview(batch: BatchConfig, override: SelectionOverride | None = None,
            seed_override: int | None = None) -> str:
    """dry-run 文本：数据集 × 用例清单与计数。"""
    tcs = select_tcs(batch, override)
    datasets = resolve_datasets(batch, seed_override)
    lines = [f"批次：{batch.name}"]
    if batch.version_label:
        lines.append(f"批次标注版本：{batch.version_label}")
    lines.append(f"数据集（{len(datasets)}）：")
    for ds in datasets:
        lines.append(f"  - {ds['id']} [{ds['kind']}] {ds['title']} "
                     f"seeds={ds['seeds']}（来源 {ds['seed_source']}）")
    lines.append(f"用例（{len(tcs)}）：")
    for tc in tcs:
        lines.append(f"  {tc}  {SCENARIOS[tc].title}  [{SCENARIOS[tc].suite}]")
    lines.append(f"合计：{len(datasets)} 数据集 × {len(tcs)} 用例 "
                 f"= {len(datasets) * len(tcs)} 次执行")
    return "\n".join(lines)
