"""测试归档（spec 0003 FR-5 / FR-6）：每次执行落为不可变归档目录。

归档根（默认 reports/）结构：
    archive/<安全化版本>_<UTC时间戳>/
        results.json           # RunRecord 全部原始 verdict
        manifest.json          # 版本/环境/git/seed/选择条件/统计/文件清单
        batch.snapshot.yaml    # 归一化批次定义快照
        datasets.snapshot.yaml # 本次引用的数据集注册表原始定义
        report.html            # 可视化报告（Task 5 接入，可选）

测试数据（批次、数据集定义、seed）与测试结果归档在同一目录；同版本重复执行不覆盖。
"""

from __future__ import annotations

import json
import platform
import re
import subprocess
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .datasets import get_dataset

MANIFEST_SCHEMA = 1
PACKAGE_DIR = Path(__file__).resolve().parent
# 保留 Unicode 字母/数字（含中文版本标识），仅替换路径不安全字符
_UNSAFE_CHARS = re.compile(r"[^\w.-]+", re.UNICODE)


class ArchiveError(RuntimeError):
    """归档写入失败。"""


def safe_slug(label: str) -> str:
    """把版本标识安全化为文件名单段（字母数字 . _ -）。"""
    slug = _UNSAFE_CHARS.sub("-", label.strip()).strip("-._")
    return slug or "unnamed"


def utc_stamp(moment: datetime | None = None) -> str:
    """紧凑 UTC 时间戳：YYYYMMDDTHHMMSSZ。"""
    moment = moment or datetime.now(timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def iso_now(moment: datetime | None = None) -> str:
    """UTC ISO8601（Z 结尾）。"""
    moment = moment or datetime.now(timezone.utc)
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def detect_git(cwd: str | Path | None = None) -> dict[str, str | bool | None]:
    """探测被测代码 git 提交与工作区脏标记；非 git/失败环境返回 unavailable 且不致命。

    默认锚定包源码目录（而非归档输出目录或进程 cwd），使 reports/ 输出到
    仓库外任意路径时记录的仍是被测代码版本。
    """
    cwd = cwd or PACKAGE_DIR
    try:
        commit_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=5,
            check=False,
        )
        if commit_proc.returncode != 0:
            return {"commit": "unavailable", "dirty": None}
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True,
            timeout=5, check=False,
        )
        dirty = None if status_proc.returncode != 0 else bool(status_proc.stdout.strip())
        return {"commit": commit_proc.stdout.strip(), "dirty": dirty}
    except (OSError, subprocess.SubprocessError):
        return {"commit": "unavailable", "dirty": None}


def resolve_version(record: dict[str, Any], explicit: str | None,
                    stamp: str) -> str:
    """版本标识优先级：显式参数 > 批次 version_label > dev-<时间戳>。"""
    if explicit:
        return explicit
    label = record.get("batch", {}).get("version_label")
    return label or f"dev-{stamp}"


def _dataset_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    datasets = []
    for ds_id in (d["id"] for d in record["datasets"]):
        definition = {k: v for k, v in asdict(get_dataset(ds_id)).items() if v is not None}
        datasets.append(definition)
    return {"version": 1, "datasets": datasets}


def _seed_summary(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"dataset": d["id"], "seeds": d["seeds"], "source": d["seed_source"]}
            for d in record["datasets"]]


def build_manifest(record: dict[str, Any], *, version: str, archive_name: str,
                   created_at: str, git_info: dict[str, Any], backend_name: str) -> dict[str, Any]:
    batch = record["batch"]
    return {
        "schema_version": MANIFEST_SCHEMA,
        "version": version,
        "archive": archive_name,
        "created_at": created_at,
        "git": git_info,
        "python": platform.python_version(),
        "backend": backend_name,
        "seed": _seed_summary(record),
        "datasets": [
            {"id": d["id"], "kind": d["kind"], "title": d["title"],
             "seeds": d["seeds"], "seed_source": d["seed_source"],
             "path": d.get("path"), "checksum": d.get("checksum")}
            for d in record["datasets"]
        ],
        "selection": {
            "name": batch["name"],
            "datasets": list(batch["datasets"]),
            "suites": list(batch["suites"]),
            "include": list(batch["include"]),
            "exclude": list(batch["exclude"]),
            "tags": {k: list(v) for k, v in batch["tags"].items()},
        },
        "counts": record["summary"],
    }


def write_archive(root: str | Path, record: dict[str, Any], *,
                  version: str | None = None, backend_name: str = "SyntheticBackend",
                  report_renderer: Callable[[dict[str, Any], dict[str, Any]], str] | None = None,
                  moment: datetime | None = None,
                  git_info: dict[str, Any] | None = None) -> Path:
    """把一次执行写入归档目录，返回目录路径。

    report_renderer 传入时，用归档内部构建的 manifest 渲染 report.html 一并写入；
    渲染器抛错不吞，交由调用方处理（选择已合法、结果已产出时不应静默丢报告）。
    """
    root = Path(root)
    stamp = utc_stamp(moment)
    resolved_version = resolve_version(record, version, stamp)
    if version is not None or record.get("batch", {}).get("version_label"):
        dir_name = f"{safe_slug(resolved_version)}_{stamp}"
    else:
        # 自动版本 dev-<stamp> 已含时间戳，不再重复拼接
        dir_name = safe_slug(resolved_version)
    archive_dir = root / "archive" / dir_name

    # 同秒重名（测试注入固定时刻或极端并发）追加序号，绝不覆盖
    counter = 1
    while archive_dir.exists():
        archive_dir = root / "archive" / f"{safe_slug(resolved_version)}_{stamp}-{counter}"
        counter += 1
    archive_dir.mkdir(parents=True)

    try:
        (archive_dir / "results.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        (archive_dir / "batch.snapshot.yaml").write_text(
            yaml.safe_dump(record["batch"], allow_unicode=True, sort_keys=False),
            encoding="utf-8")
        (archive_dir / "datasets.snapshot.yaml").write_text(
            yaml.safe_dump(_dataset_snapshot(record), allow_unicode=True, sort_keys=False),
            encoding="utf-8")

        manifest = build_manifest(
            record, version=resolved_version, archive_name=archive_dir.name,
            created_at=iso_now(moment),
            git_info=git_info if git_info is not None else detect_git(),
            backend_name=backend_name)
        if report_renderer is not None:
            report_html = report_renderer(record, manifest)
            (archive_dir / "report.html").write_text(report_html, encoding="utf-8")

        manifest["files"] = sorted(p.name for p in archive_dir.iterdir() if p.is_file())
        (archive_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
    except OSError as exc:
        msg = f"归档写入失败：{archive_dir}：{exc}"
        raise ArchiveError(msg) from exc
    return archive_dir
