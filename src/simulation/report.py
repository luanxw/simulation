"""单次执行的自包含可视化 HTML 报告（spec 0003 FR-7）。

纯标准库字符串渲染：CSS 全内联、折叠用原生 <details>（无需 JS/网络），
断网 file:// 双击即可打开。首页按四专题汇总，展开用例即见每条检查项的
实测值 / 运算符 / 门限 / 样本量 / Wilson 95% 置信区间——数值证据用于对外自证。
"""

from __future__ import annotations

import html
from typing import Any

from .execution import SUITE_ORDER, SUITE_TITLES
from .scenarios import SCENARIOS

_OP_SYMBOLS = {"le": "≤", "ge": "≥", "lt": "<", "gt": ">"}
_STATUS_LABEL = {"pass": "通过", "fail": "失败", "pending_backend": "待后端"}


def esc(value: Any) -> str:
    """所有入页动态内容统一 HTML 转义。"""
    return html.escape("" if value is None else str(value), quote=True)


def _pct(rate: float | None) -> str:
    return "—" if rate is None else f"{rate * 100:.1f}%"


def _css() -> str:
    return """
:root { --green:#1a7f37; --red:#cf2220; --gray:#6e7781; --line:#d0d7de;
        --bg:#f6f8fa; --ink:#1f2328; --blue:#0969da; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
       line-height:1.5; }
.wrap { max-width:1080px; margin:0 auto; padding:24px 20px 64px; }
h1 { font-size:22px; margin:0 0 4px; }
h2 { font-size:17px; margin:28px 0 10px; padding-top:14px; border-top:2px solid var(--line); }
.meta { border:1px solid var(--line); border-radius:8px; background:#fff;
        padding:12px 14px; margin:12px 0; font-size:13px; }
.meta table { border-collapse:collapse; }
.meta td { padding:2px 14px 2px 0; vertical-align:top; }
.meta td.k { color:var(--gray); white-space:nowrap; }
.overall { display:flex; gap:16px; flex-wrap:wrap; margin:14px 0 6px; }
.card { flex:1 1 220px; background:#fff; border:1px solid var(--line);
        border-radius:8px; padding:14px 16px; }
.card .num { font-size:26px; font-weight:700; }
.card .sub { color:var(--gray); font-size:13px; }
.card.pass .num { color:var(--green); }
.card.fail .num { color:var(--red); }
.suite-stats { font-size:13px; color:var(--gray); margin:0 0 8px; }
details.tc { background:#fff; border:1px solid var(--line); border-radius:8px;
            margin:8px 0; padding:0; }
details.tc > summary { cursor:pointer; padding:10px 14px; list-style:none;
                       display:flex; gap:10px; align-items:baseline; font-size:14px; }
details.tc > summary::-webkit-details-marker { display:none; }
details.tc > summary::before { content:"▸"; color:var(--gray); }
details.tc[open] > summary::before { content:"▾"; }
.tc-id { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-weight:700; }
.tc-title { flex:1; }
.badge { font-size:12px; font-weight:700; border-radius:10px; padding:1px 10px; }
.badge.pass { background:#dafbe1; color:var(--green); }
.badge.fail { background:#ffebe9; color:var(--red); }
.badge.pending { background:#eaeef2; color:var(--gray); }
.dataset-note { padding:4px 16px 0; font-size:12px; color:var(--gray); }
table.checks { width:calc(100% - 28px); margin:8px 14px 14px; border-collapse:collapse;
              font-size:13px; }
table.checks th, table.checks td { border-bottom:1px solid var(--line);
       padding:5px 8px; text-align:right; }
table.checks th:first-child, table.checks td:first-child,
table.checks td.name { text-align:left; }
table.checks th { color:var(--gray); font-weight:600; background:var(--bg); }
tr.fail td { color:var(--red); font-weight:600; }
.pending-backend td { color:var(--gray); }
footer { margin-top:32px; color:var(--gray); font-size:12px; text-align:center; }
.nav { font-size:13px; margin:8px 0; }
.nav a { color:var(--blue); margin-right:14px; }
""".strip()


def _badge(status: str) -> str:
    cls = {"pass": "pass", "fail": "fail"}.get(status, "pending")
    return f'<span class="badge {cls}">{esc(_STATUS_LABEL.get(status, status))}</span>'


def _check_row(check: dict[str, Any]) -> str:
    status = check.get("status", "")
    cls = {"pass": "", "fail": "fail"}.get(status, "pending-backend")
    tds = [
        f'<td class="name">{esc(check.get("name"))}</td>',
        f'<td>{_badge(status)}</td>',
        f"<td>{esc(check.get('value'))}</td>",
        f"<td>{esc(_OP_SYMBOLS.get(check.get('op'), check.get('op')))}</td>",
        f"<td>{esc(check.get('threshold'))}</td>",
    ]
    if status != "pending_backend":
        n = check.get("n")
        ci = check.get("ci")
        tds.append(f"<td>{esc(n) if n is not None else '—'}</td>")
        tds.append(f"<td>[{esc(ci[0])}, {esc(ci[1])}]</td>" if ci else "<td>—</td>")
    else:
        reason = esc(check.get("reason", ""))
        tds.append(f'<td colspan="2">{reason}</td>')
    return f'<tr class="{cls}">{"".join(tds)}</tr>'


def _check_table(checks: list[dict[str, Any]]) -> str:
    head = ("<tr><th>检查项</th><th>状态</th><th>实测值</th><th>判定</th>"
            "<th>门限</th><th>样本量 n</th><th>Wilson 95% CI</th></tr>")
    rows = "".join(_check_row(c) for c in checks)
    return f'<table class="checks"><thead>{head}</thead><tbody>{rows}</tbody></table>'


def _verdict_class(verdict: dict[str, Any]) -> str:
    return "pass" if verdict["pass"] else "fail"


def _render_tc(tc: str, groups: list[dict[str, Any]]) -> str:
    """groups: [{dataset: id, verdict: {...}}] 同一用例在各数据集上的结果。"""
    overall_fail = any(not g["verdict"]["pass"] for g in groups)
    state = "fail" if overall_fail else "pass"
    title = SCENARIOS[tc].title
    multi = len(groups) > 1
    body_parts = []
    for g in groups:
        if multi:
            body_parts.append(
                f'<div class="dataset-note">数据集：{esc(g["dataset"])}</div>')
        body_parts.append(_check_table(g["verdict"]["checks"]))
    return (
        f'<details class="tc">'
        f'<summary><span class="tc-id">{esc(tc)}</span>'
        f'<span class="tc-title">{esc(title)}</span>'
        f'{_badge(state)}</summary>'
        f'{"".join(body_parts)}'
        f'</details>'
    )


def _render_suite(suite: str, record: dict[str, Any]) -> str:
    stats = record["summary"]["by_suite"][suite]
    tcs = [tc for tc in record["tcs"] if tc.split("-")[1] == suite]
    if not tcs:
        return ""
    groups_by_tc = {tc: [] for tc in tcs}
    for group in record["results"]:
        for tc in tcs:
            groups_by_tc[tc].append(
                {"dataset": group["dataset"], "verdict": group["runs"][tc]})
    tc_html = "".join(_render_tc(tc, groups_by_tc[tc]) for tc in tcs)
    return (
        f'<h2 id="suite-{suite}">{esc(SUITE_TITLES[suite])} '
        f'<span class="badge {"pass" if stats["tc_total"] == stats["tc_passed"] else "fail"}">'
        f'{stats["tc_passed"]}/{stats["tc_total"]} 通过（{_pct(stats["tc_rate"])}）</span></h2>'
        f'<p class="suite-stats">用例执行 {stats["tc_total"]} 条 · 通过 {stats["tc_passed"]} 条'
        f' · 检查项 {stats["check_passed"]}/{stats["check_total"]}'
        f'（{_pct(stats["check_rate"])}）</p>'
        f'{tc_html}'
    )


def _meta_table(record: dict[str, Any], manifest: dict[str, Any]) -> str:
    git = manifest.get("git", {})
    if git.get("dirty") is True:
        dirty = "（工作区有未提交改动）"
    else:
        dirty = ""
    ds_lines = "<br>".join(
        f'{esc(d["id"])} [{esc(d["kind"])}] seeds={esc(d.get("seeds"))}'
        f'（{esc(d.get("seed_source", ""))}）'
        for d in record["datasets"])
    rows = [
        ("版本", esc(manifest.get("version"))),
        ("运行时间 (UTC)", esc(manifest.get("created_at"))),
        ("代码提交", f'{esc(git.get("commit"))}{dirty}'),
        ("后端", esc(manifest.get("backend"))),
        ("Python", esc(manifest.get("python"))),
        ("批次", esc(record["batch"].get("name"))),
        ("数据集", ds_lines),
        ("归档目录", esc(manifest.get("archive"))),
    ]
    body = "".join(f'<tr><td class="k">{k}</td><td>{v}</td></tr>' for k, v in rows)
    return f'<div class="meta"><table>{body}</table></div>'


def render_report(record: dict[str, Any], manifest: dict[str, Any]) -> str:
    """渲染单次执行报告 HTML（自包含字符串）。"""
    overall = record["summary"]["overall"]
    tc_cls = "pass" if overall["tc_failed"] == 0 else "fail"
    tc_sub = (
        f'用例通过率：{overall["tc_passed"]}/{overall["tc_total"]} 条通过'
        f'（{overall["unique_tcs"]} 条用例 × {overall["datasets"]} 个数据集），'
        f'失败 {overall["tc_failed"]} 条'
    )
    check_sub = (f'检查项通过率：{overall["check_passed"]}/{overall["check_total"]} 项')
    nav = " · ".join(
        f'<a href="#suite-{s}">{esc(SUITE_TITLES[s])}</a>'
        for s in SUITE_ORDER
        if any(tc.split("-")[1] == s for tc in record["tcs"]))
    suites_html = "".join(_render_suite(s, record) for s in SUITE_ORDER)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>传感器仿真测试报告 - {esc(manifest.get("version", ""))}</title>
<style>{_css()}</style>
</head>
<body>
<div class="wrap">
<h1>割草机器人传感器仿真测试报告</h1>
<div class="nav">专题跳转：{nav}</div>
{_meta_table(record, manifest)}
<div class="overall">
  <div class="card {tc_cls}">
    <div class="num">{_pct(overall["tc_rate"])}</div>
    <div class="sub">{tc_sub}</div>
  </div>
  <div class="card">
    <div class="num">{_pct(overall["check_rate"])}</div>
    <div class="sub">{check_sub}</div>
  </div>
</div>
{suites_html}
<footer>由 simulation 批次执行器自动生成 · 证据为数值型结果（实测值/门限/Wilson 95% CI）
· 本页面离线自包含</footer>
</div>
</body>
</html>
"""
