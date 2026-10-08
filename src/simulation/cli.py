"""命令行入口（spec 0003 FR-2 / FR-8 / FR-9）。

用法：
    python -m simulation.cli run [--batch B.yaml] [--version v1.0]
        [--suite L,U] [--tc TC-L-01]... [--tag world=W1]... [--exclude PAT]...
        [--seed N] [--out reports] [--dry-run]
    python -m simulation.cli rebuild-index [--out reports]

退出码：0 全部通过；1 有用例失败（归档与报告仍完整）；2 选择/配置错误（不产生归档）。
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .archive import write_archive
from .datasets import DatasetError
from .execution import SUITE_ORDER, SUITE_TITLES, execute_batch
from .history import rebuild_index
from .report import render_report
from .selection import (
    BatchConfig,
    SelectionError,
    SelectionOverride,
    default_batch,
    load_batch,
    preview,
)

EXIT_OK = 0
EXIT_TC_FAILED = 1
EXIT_USAGE = 2


def _csv(value: str) -> tuple[str, ...]:
    return tuple(v.strip() for v in value.split(",") if v.strip())


def _tag(value: str) -> tuple[str, str]:
    if "=" not in value:
        msg = f"标签格式应为 world=W1 或 kind=static，得到：{value!r}"
        raise argparse.ArgumentTypeError(msg)
    key, raw_value = value.split("=", 1)
    key, raw_value = key.strip(), raw_value.strip()
    if key not in ("world", "kind"):
        msg = f"标签键仅支持 world/kind，得到：{key!r}"
        raise argparse.ArgumentTypeError(msg)
    if not raw_value:
        msg = f"标签 {key} 的值不能为空"
        raise argparse.ArgumentTypeError(msg)
    return key, raw_value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simulation",
        description="割草机器人传感器仿真测试：批次选择执行、HTML 报告与归档。")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="按批次执行用例×数据集并生成归档报告")
    run.add_argument("--batch", help="批次 YAML 路径；省略时全量执行 46 条用例")
    run.add_argument("--version", help="被测版本标识（优先于批次内 version_label）")
    run.add_argument("--suite", help="逗号分隔专题收窄：L,U,C,F，如 L,U")
    run.add_argument("--tc", action="append", default=[], metavar="TC-ID",
                     help="按编号/通配收窄，可重复，如 TC-L-01 或 TC-L-*")
    run.add_argument("--tag", action="append", default=[], type=_tag, metavar="K=V",
                     help="按场景标签收窄，可重复：world=W1 / kind=static")
    run.add_argument("--exclude", action="append", default=[], metavar="PATTERN",
                     help="追加排除编号/通配，可重复")
    run.add_argument("--seed", type=int, help="把所有数据集种子覆盖为单个 N")
    run.add_argument("--out", default="reports", help="归档根目录（默认 reports）")
    run.add_argument("--dry-run", action="store_true",
                     help="只预览数据集×用例清单，不执行、不归档")

    idx = sub.add_parser("rebuild-index", help="根据归档目录重建历史总览 index.html")
    idx.add_argument("--out", default="reports", help="归档根目录（默认 reports）")
    return parser


def _override_from_args(args: argparse.Namespace) -> SelectionOverride:
    tags: dict[str, list[str]] = {}
    for key, value in args.tag:
        tags.setdefault(key, []).append(value)
    return SelectionOverride(
        suites=_csv(args.suite) if args.suite else (),
        tcs=tuple(args.tc),
        tags={k: tuple(v) for k, v in tags.items()},
        exclude=tuple(args.exclude),
    )


def _load_target_batch(args: argparse.Namespace) -> BatchConfig:
    return load_batch(args.batch) if args.batch else default_batch()


def _print_summary(record: dict) -> None:
    overall = record["summary"]["overall"]
    print(f"执行完成：{overall['datasets']} 数据集 × {overall['unique_tcs']} 用例 "
          f"= {overall['tc_total']} 次执行")
    for suite in SUITE_ORDER:
        stats = record["summary"]["by_suite"][suite]
        if stats["tc_total"]:
            rate = "—" if stats["tc_rate"] is None else f"{stats['tc_rate'] * 100:.1f}%"
            print(f"  {SUITE_TITLES[suite]}：{stats['tc_passed']}/{stats['tc_total']} "
                  f"通过（{rate}），检查项 {stats['check_passed']}/{stats['check_total']}")
    print(f"总体：{overall['tc_passed']}/{overall['tc_total']} 用例通过，"
          f"失败 {overall['tc_failed']}；"
          f"检查项 {overall['check_passed']}/{overall['check_total']}")


def _run(args: argparse.Namespace) -> int:
    batch = _load_target_batch(args)
    override = _override_from_args(args)

    if args.dry_run:
        print(preview(batch, override, seed_override=args.seed))
        return EXIT_OK

    record = execute_batch(batch, override, seed_override=args.seed)
    archive_path = write_archive(
        args.out, record, version=args.version, report_renderer=render_report)
    index_path = rebuild_index(args.out)
    _print_summary(record)
    print(f"归档目录：{archive_path}")
    print(f"单次报告：{archive_path / 'report.html'}")
    print(f"历史总览：{index_path}")
    return EXIT_TC_FAILED if record["summary"]["overall"]["tc_failed"] else EXIT_OK


def _rebuild_index(args: argparse.Namespace) -> int:
    path = rebuild_index(args.out)
    print(f"历史总览已重建：{path}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return _run(args)
        if args.command == "rebuild-index":
            return _rebuild_index(args)
    except (SelectionError, DatasetError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return EXIT_USAGE
    parser.error(f"未知子命令：{args.command}")
    return EXIT_USAGE  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
