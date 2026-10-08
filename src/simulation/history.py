"""跨版本历史总览（spec 0003 FR-8）：扫描归档根生成 index.html。

扫描 root/archive/*/manifest.json，按归档目录名（含 UTC 时间戳）排序，
聚合版本、运行时间、四专题与总体通过率，版本列相对链接到各 report.html。
损坏的归档目录跳过并在页内标注，不致命；重建幂等（除生成时间外内容稳定）。
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .archive import iso_now
from .execution import SUITE_ORDER, SUITE_TITLES
from .report import esc

# 目录名内嵌 UTC 时间戳：<slug>_YYYYMMDDTHHMMSSZ[ -同秒序号]，或 dev-YYYYMMDDTHHMMSSZ
_STAMP_RE = re.compile(r"(\d{8})T(\d{6})Z(?:-(\d+))?")


class HistoryError(RuntimeError):
    """历史总览生成失败。"""


def _archive_sort_key(item: dict[str, Any]) -> tuple[str, int, str]:
    """按归档真实时间排序（spec：总览排序即时间序），而非版本标签字典序。

    主键取目录名内嵌 UTC 时间戳（同秒冲突序号次之）；目录名缺时间戳时
    回退 manifest.created_at；都不可用则排最后并按目录名稳定排列。
    """
    name = item["dir"]
    match = _STAMP_RE.search(name)
    if match:
        stamp = match.group(1) + match.group(2)
        suffix = int(match.group(3) or 0)
        return stamp, suffix, name
    created_at = (item.get("manifest") or {}).get("created_at", "")
    digits = re.sub(r"\D", "", created_at)[:14]
    if len(digits) == 14:
        return digits, 0, name
    return "99999999999999", 0, name


def iter_archives(root: str | Path) -> list[dict[str, Any]]:
    """返回归档元信息列表（按内嵌 UTC 时间戳排序）；损坏条目标 invalid=True 但保留。"""
    root = Path(root)
    archive_root = root / "archive"
    if not archive_root.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for entry in archive_root.iterdir():
        if not entry.is_dir():
            continue
        item: dict[str, Any] = {"dir": entry.name, "has_report": (entry / "report.html").is_file()}
        manifest_path = entry / "manifest.json"
        try:
            item["manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            item["invalid"] = f"manifest 无法解析：{type(exc).__name__}"
        else:
            item["invalid"] = None
        items.append(item)
    return sorted(items, key=_archive_sort_key)


def _pct(rate: float | None) -> str:
    return "—" if rate is None else f"{rate * 100:.1f}%"


def _css() -> str:
    return """
body { margin:0; background:#f6f8fa; color:#1f2328;
       font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; }
.wrap { max-width:1080px; margin:0 auto; padding:24px 20px 64px; }
h1 { font-size:22px; margin:0 0 4px; }
.sub { color:#6e7781; font-size:13px; margin-bottom:16px; }
table { width:100%; border-collapse:collapse; background:#fff;
        border:1px solid #d0d7de; border-radius:8px; font-size:13px; }
th, td { padding:7px 9px; border-bottom:1px solid #d0d7de; text-align:right; }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left; }
th { background:#eaeef2; color:#57606a; font-weight:600; }
tr:last-child td { border-bottom:none; }
a { color:#0969da; text-decoration:none; }
a:hover { text-decoration:underline; }
.bad { color:#cf2220; }
.muted { color:#6e7781; }
.empty { background:#fff; border:1px dashed #d0d7de; border-radius:8px;
         padding:28px; text-align:center; color:#6e7781; }
""".strip()


def _row(item: dict[str, Any]) -> str:
    dir_name = esc(item["dir"])
    if item.get("invalid"):
        return (f'<tr><td>{dir_name}</td><td colspan="{len(SUITE_ORDER) + 3}" '
                f'class="bad">⚠ {esc(item["invalid"])}</td></tr>')
    m = item["manifest"]
    counts = m.get("counts", {})
    overall = counts.get("overall", {})
    by_suite = counts.get("by_suite", {})
    cells = []
    for suite in SUITE_ORDER:
        stats = by_suite.get(suite, {})
        total = stats.get("tc_total", 0)
        if total:
            cells.append(
                f'<td>{_pct(stats.get("tc_rate"))} '
                f'<span class="muted">({stats.get("tc_passed")}/{total})</span></td>')
        else:
            cells.append('<td class="muted">—</td>')
    link = (f'<a href="archive/{dir_name}/report.html">{esc(m.get("version", dir_name))}</a>'
            if item["has_report"]
            else f'{esc(m.get("version", dir_name))} <span class="muted">(无报告)</span>')
    return (
        f"<tr><td>{link}</td>"
        f'<td class="muted">{esc(m.get("created_at", "—"))}</td>'
        f"{''.join(cells)}"
        f"<td><b>{_pct(overall.get('tc_rate'))}</b> "
        f'<span class="muted">({overall.get("tc_passed", 0)}/{overall.get("tc_total", 0)})'
        f"</span></td></tr>"
    )


def render_index(items: list[dict[str, Any]], *, generated_at: str | None = None) -> str:
    generated_at = generated_at or iso_now()
    suite_heads = "".join(f"<th>{esc(SUITE_TITLES[s])}</th>" for s in SUITE_ORDER)
    if not items:
        body = ('<div class="empty">暂无归档记录。执行一次批次运行后，'
                "归档将出现在 archive/ 目录并自动登记到本页。</div>")
    else:
        body = (
            "<table><thead><tr><th>版本</th><th>运行时间 (UTC)</th>"
            f"{suite_heads}<th>总体通过率</th></tr></thead>"
            f"<tbody>{''.join(_row(i) for i in items)}</tbody></table>"
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>传感器仿真测试 - 版本历史总览</title>
<style>{_css()}</style>
</head>
<body>
<div class="wrap">
<h1>传感器仿真测试 · 版本历史总览</h1>
<div class="sub">共 {len(items)} 个归档 · 本页生成于 {esc(generated_at)}（UTC）· 离线自包含</div>
{body}
</div>
</body>
</html>
"""


def rebuild_index(root: str | Path, *, now: datetime | None = None) -> Path:
    """扫描归档根并写入 index.html，返回其路径。"""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    items = iter_archives(root)
    page = render_index(items, generated_at=iso_now(now))
    index_path = root / "index.html"
    try:
        index_path.write_text(page, encoding="utf-8")
    except OSError as exc:
        msg = f"历史总览写入失败：{index_path}：{exc}"
        raise HistoryError(msg) from exc
    return index_path
