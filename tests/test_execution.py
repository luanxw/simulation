"""批次执行编排测试（spec 0003 Task 3，TR-3.1~3.6）。"""

from simulation.backends import SyntheticBackend
from simulation.execution import SUITE_ORDER, SUITE_TITLES, execute_batch
from simulation.runner import run_tc
from simulation.selection import BatchConfig


def batch(**kw) -> BatchConfig:
    defaults = dict(
        name="t", version_label=None, datasets=("synthetic-default",),
        suites=(), include=(), exclude=(), tags={},
    )
    defaults.update(kw)
    return BatchConfig(**defaults)


def test_matrix_is_dataset_cross_tcs():
    rec = execute_batch(batch(
        datasets=("synthetic-default", "synthetic-seed42"),
        include=("TC-L-01", "TC-U-03", "TC-F-09"),
    ))
    assert len(rec["results"]) == 2
    assert [g["dataset"] for g in rec["results"]] == [
        "synthetic-default", "synthetic-seed42"]
    for group in rec["results"]:
        assert set(group["runs"]) == {"TC-L-01", "TC-U-03", "TC-F-09"}
    assert rec["summary"]["overall"]["tc_total"] == 6
    assert rec["summary"]["overall"]["unique_tcs"] == 3
    assert rec["summary"]["overall"]["datasets"] == 2


def test_dataset_seeds_recorded_in_record():
    rec = execute_batch(batch(datasets=("synthetic-seed42",), include=("TC-L-01",)))
    assert rec["datasets"][0]["seeds"] == [42]
    assert rec["datasets"][0]["seed_source"] == "dataset"

    default_rec = execute_batch(batch(include=("TC-L-01",)))
    assert default_rec["datasets"][0]["seeds"] == [11, 22, 33]


def test_seed_override_applies_to_all_datasets():
    rec = execute_batch(batch(include=("TC-L-01",)), seed_override=7)
    assert rec["datasets"][0]["seeds"] == [7]
    assert rec["datasets"][0]["seed_source"] == "cli"


def test_reproducible_same_input_same_verdicts():
    b = batch(datasets=("synthetic-default", "synthetic-seed42"), suites=("L",))
    r1 = execute_batch(b)
    r2 = execute_batch(b)

    def values(rec):
        return [[(tc, v["pass"], [c["value"] for c in v["checks"]])
                 for tc, v in g["runs"].items()] for g in rec["results"]]

    assert values(r1) == values(r2)


def test_run_tc_without_seeds_matches_legacy_behaviour():
    legacy = run_tc("TC-L-05")
    explicit_none = run_tc("TC-L-05", seeds=None)
    assert legacy == explicit_none


def test_summarize_counts_match_manual_tally():
    rec = execute_batch(batch(suites=("L",), include=("TC-F-09",)))
    summary = rec["summary"]
    by = summary["by_suite"]
    runs = rec["results"][0]["runs"]

    l_pass = sum(1 for tc in rec["tcs"] if tc.startswith("TC-L-") and runs[tc]["pass"])
    assert by["L"]["tc_total"] == 11
    assert by["L"]["tc_passed"] == l_pass
    assert by["F"]["tc_total"] == 1 and by["F"]["tc_passed"] == 1
    assert by["U"]["tc_total"] == 0 and by["U"]["tc_rate"] is None
    assert summary["overall"]["tc_total"] == 12

    # check 统计与全部 verdict 的 live checks 手工核对
    live = live_pass = 0
    for group in rec["results"]:
        for verdict in group["runs"].values():
            for check in verdict["checks"]:
                if check["status"] != "pending_backend":
                    live += 1
                    if check["status"] == "pass":
                        live_pass += 1
    assert summary["overall"]["check_total"] == live
    assert summary["overall"]["check_passed"] == live_pass


def test_summarize_includes_all_four_suite_titles():
    rec = execute_batch(batch(include=("TC-L-01",)))
    assert SUITE_TITLES == {"L": "激光 LiDAR", "U": "USS 超声", "C": "相机", "F": "融合"}
    titles = rec["summary"]["suite_titles"]
    assert [titles[k] for k in SUITE_ORDER] == [SUITE_TITLES[k] for k in SUITE_ORDER]


def test_failed_verdict_counted_in_summary():
    be = SyntheticBackend()
    be.faults.add("lidar_blind")
    rec = execute_batch(batch(include=("TC-L-05",)), backend=be)
    verdict = rec["results"][0]["runs"]["TC-L-05"]
    assert verdict["pass"] is False
    assert rec["summary"]["by_suite"]["L"]["tc_passed"] == 0
    assert rec["summary"]["overall"]["tc_failed"] == 1


def test_record_is_json_serializable():
    import json

    rec = execute_batch(batch(suites=("L",)))
    dumped = json.dumps(rec, ensure_ascii=False)
    restored = json.loads(dumped)
    assert restored["tcs"] == rec["tcs"]
