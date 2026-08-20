#!/usr/bin/env python3
"""B3-P2-X2 S3 persistence gate - OFFLINE self-tests.

Runs without any game/VM.  It imports the pure logic of
scripts/validate/s3_persistence_gate.py (canonicalization, semantic
snapshot/compare, planted-marker checks, save parsing, verdict
classification) and exercises it against fixtures.  The runtime launch
portion (save->exit->reload) is intentionally NOT executed here; it is the
explicit S3 gate run against a candidate EXE.

Emits an evidence JSON under 10_logs (git-ignored, via --out or a default
derived from the repo root).  Exit codes: 0 = PASS, 1 = SELFTEST_FAIL.

Usage:
    python scripts/validate/s3_persistence_selftests.py [--out <path>]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

# Files whose portability/secret hygiene this selftest verifies.
S3_FILES = [
    "scripts/validate/s3_persistence_gate.py",
    "scripts/validate/s3_persistence_selftests.py",
    "tests/s3_persistence/run_selfchecks.py",
]

_BS = chr(92)
_COLON = chr(58)
DRIVE_RE = re.compile(
    r"(?<![A-Za-z0-9_%])[A-Za-z]:" + _BS + _BS + r"|[a-z]:" + _COLON + r"/"
)
SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)secret\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)token\s*=\s*['\"][^'\"]{16,}['\"]"),
]


def import_gate(root: Path):
    path = root / "scripts" / "validate" / "s3_persistence_gate.py"
    spec = importlib.util.spec_from_file_location("s3_persistence_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_save(**overrides) -> dict:
    import copy
    save = {
        "save_version": 1,
        "settings": {
            "enable_music": True, "enable_sfx": True, "enable_drops": True,
            "enable_floating_damage": True, "enable_fullscreen": False,
            "enable_fx": True, "enable_status_bars": True,
            "enable_vsync": True, "enable_stats_panel": True,
            "enable_health_globe": True, "enable_floating_xp": True,
            "show_advanced_mods": True, "hide_low_level": False,
            "volume": {"music": 100, "sfx": 100, "drops": 80},
        },
        "shared_stash": {"item_1": {"id": "sword", "qty": 1}},
        "keybind_overrides": {"jump": "Space"},
        "characters": {
            "default": {
                "character_name": "default", "account_level": 3,
                "account_xp": 120, "account_xp_next": 50, "next_gene_id": 2,
                "needs_starter": False, "orbs": {"blue": 5, "green": 0,
                    "red": 0, "gold": 1, "freeze": 0, "corruption": 0,
                    "tear": 0, "moon_shard": 0, "sun_shard": 0},
                "recent_stage": None,
                "completed_stages": {"root": True, "dungeon_1": True},
                "outfit": {"helmet": None, "head": None, "feet": None,
                    "hands": None, "pants": None, "back": "cape"},
                "help_tips": {}, "new_item_ids": {}, "new_item_types": {},
                "tutorial_events": {},
                "mutation_tree_loadout": {"class": "WARRIOR",
                                          "passives": ["root_warrior"]},
                "specialization_loadout": {"class": None, "passives": ["root"]},
                "skill_loadout": {},
                "gene_loadout": {}, "genes": {}, "stored_mods": {},
                "filters": {},
            },
        },
        "completed_achievements": ["ach_first_kill"],
        "timestamp": 270127312.5,
        "checksum": "deadbeef",
        "stamp": "cafebabe",
    }
    save.update(overrides)
    return save


def semantic_twin(save: dict) -> dict:
    """Same semantic state, fresh volatile values (what a second run's
    do_save_game() would produce)."""
    import copy
    twin = copy.deepcopy(save)
    twin["timestamp"] = twin["timestamp"] + 1.0
    twin["checksum"] = "00000000"
    twin["stamp"] = "11111111"
    return twin


def tc_semantic_snapshot_excludes_volatile(g, root, out) -> tuple[bool, str]:
    save = make_save()
    snap = g.semantic_snapshot(save)
    missing = sorted(set(g.VOLATILE_KEYS) - set(snap))
    if missing != sorted(g.VOLATILE_KEYS):
        return False, f"volatile keys not all dropped: {missing}"
    leftover = set(snap) & g.VOLATILE_KEYS
    if leftover:
        return False, f"volatile keys still present: {sorted(leftover)}"
    if set(snap) != set(save) - g.VOLATILE_KEYS:
        return False, "snapshot key set mismatch"
    return True, "volatile keys excluded, all semantic keys kept"


def tc_semantic_sha_ignores_volatile(g, root, out) -> tuple[bool, str]:
    save = make_save()
    twin = semantic_twin(save)
    h1 = g.semantic_sha256(save)
    h2 = g.semantic_sha256(twin)
    if h1 != h2:
        return False, f"volatile-only rewrite changed semantic sha ({h1[:10]} vs {h2[:10]})"
    if save["timestamp"] == twin["timestamp"]:
        return False, "fixture is not a real twin"
    return True, f"volatile-only rewrite -> same semantic sha {h1[:12]}"


def tc_semantic_sha_changes_on_field(g, root, out) -> tuple[bool, str]:
    save = make_save()
    edited = make_save()
    edited["characters"]["default"]["account_level"] = 9
    h1 = g.semantic_sha256(save)
    h2 = g.semantic_sha256(edited)
    if h1 == h2:
        return False, "semantic sha did not change on account_level edit"
    return True, "semantic sha sensitive to real state changes"


def tc_compare_identical(g, root, out) -> tuple[bool, str]:
    save = make_save()
    diffs = g.compare_semantic(save, semantic_twin(save))
    if diffs:
        return False, f"expected no diffs, got {diffs}"
    return True, "identical semantic states compare clean"


def tc_compare_reports_paths(g, root, out) -> tuple[bool, str]:
    save = make_save()
    edited = make_save()
    edited["characters"]["default"]["orbs"]["blue"] = 999
    edited["settings"]["volume"]["drops"] = 0
    edited["completed_achievements"] = []
    diffs = g.compare_semantic(save, edited)
    paths = {d.split(" (", 1)[0] for d in diffs}
    expected = {
        "characters.default.orbs.blue",
        "settings.volume.drops",
        "completed_achievements",
    }
    missing = expected - paths
    if missing:
        return False, f"diff paths missing: {sorted(missing)}; got {diffs}"
    return True, f"{len(diffs)} precise diff paths ({', '.join(sorted(paths))})"


def tc_compare_missing_branch(g, root, out) -> tuple[bool, str]:
    save = make_save()
    edited = make_save()
    del edited["characters"]["default"]["genes"]
    edited["shared_stash"] = {}
    diffs = g.compare_semantic(save, edited)
    if not any("characters.default.genes" in d for d in diffs):
        return False, f"missing-key branch not reported: {diffs}"
    if not any("shared_stash" in d for d in diffs):
        return False, f"emptied dict branch not reported: {diffs}"
    return True, "missing/emptied branches reported"


def tc_planted_marker_ok(g, root, out) -> tuple[bool, str]:
    save = make_save()
    rep = g.planted_marker_report(save, "default")
    if not rep["ok"]:
        return False, f"markers should pass: {rep}"
    if rep["needs_starter"] is not False:
        return False, f"needs_starter should be False: {rep}"
    return True, "planted markers present (name + needs_starter=false)"


def tc_planted_marker_missing(g, root, out) -> tuple[bool, str]:
    save = make_save()
    save["characters"]["default"]["needs_starter"] = True
    rep = g.planted_marker_report(save, "default")
    if rep["ok"]:
        return False, "fresh-profile-shaped save must not pass planted check"
    del save["characters"]["default"]
    rep2 = g.planted_marker_report(save, "default")
    if rep2["ok"]:
        return False, "missing character must not pass planted check"
    return True, "fresh-profile shape correctly rejected"


def tc_parse_valid(g, root, out) -> tuple[bool, str]:
    ok, save, err = g.parse_save_bytes(
        json.dumps(make_save()).encode("utf-8"))
    if not ok or save is None:
        return False, f"valid save rejected: {err}"
    return True, "valid GameState save parses"


def tc_parse_invalids(g, root, out) -> tuple[bool, str]:
    bad: list[tuple[bytes, str]] = [
        (b"not json {{", "garbage"),
        (b"[1,2,3]", "list root"),
        (b"{\"x\": 1}", "no characters dict"),
        (b"\xff\xfe invalid utf8", "bad utf-8"),
    ]
    for data, label in bad:
        ok, save, err = g.parse_save_bytes(data)
        if ok:
            return False, f"invalid input ({label}) accepted"
        if save is not None or not err:
            return False, f"invalid input ({label}) returned weak error"
    return True, f"all {len(bad)} invalid inputs rejected with reasons"


def tc_reload_equal_fixture(g, root, out) -> tuple[bool, str]:
    run1 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": True,
            "parse_error": "",
            "settled_snapshot": {"save": make_save()},
            "post_exit_snapshot": {"save": semantic_twin(make_save())}}
    run2 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": True,
            "parse_error": "",
            "settled_snapshot": {"save": semantic_twin(make_save())},
            "post_exit_snapshot": {"save": semantic_twin(make_save())}}
    seed_stage = {"staged": True}
    verdict, detail = g.classify_verdict(run1, run2, seed_stage, "default")
    if verdict != "PASS":
        return False, f"expected PASS, got {verdict}: {detail}"
    return True, "save->exit->reload equal fixture -> PASS"


def tc_reload_diff_fixture(g, root, out) -> tuple[bool, str]:
    save1 = make_save()
    save2 = semantic_twin(make_save())
    save2["characters"]["default"]["account_level"] = 99
    run1 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": True, "parse_error": "",
            "settled_snapshot": {"save": save1},
            "post_exit_snapshot": {"save": save1}}
    run2 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": True, "parse_error": "",
            "settled_snapshot": {"save": save2},
            "post_exit_snapshot": {"save": save2}}
    verdict, detail = g.classify_verdict(run1, run2, {"staged": True},
                                         "default")
    if verdict != "FAIL":
        return False, f"expected FAIL, got {verdict}"
    if not detail.get("diff_paths"):
        return False, "FAIL without diff_paths detail"
    return True, f"semantic divergence -> FAIL with diff ({detail['diff_paths'][0]})"


def tc_blocked_no_trigger(g, root, out) -> tuple[bool, str]:
    run1 = {"window_found": True, "load_triggered": False,
            "load_marker_seen": False, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": False,
            "rewrite_count": 0, "exit_stable": False,
            "parse_error": "n/a", "summary": {"no": "signal"}}
    run2 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True,
            "no_save_marker": False, "fatal_markers": [],
            "save_parse_ok": True, "rewrite_count": 1,
            "exit_stable": True, "parse_error": "",
            "settled_snapshot": {"save": make_save()},
            "post_exit_snapshot": {"save": make_save()}}
    verdict, detail = g.classify_verdict(run1, run2, {"staged": True},
                                         "default")
    if verdict != "BLOCKED":
        return False, f"expected BLOCKED, got {verdict}: {detail}"
    return True, "missing load signal -> BLOCKED (not fake PASS)"


def tc_blocked_bad_seed(g, root, out) -> tuple[bool, str]:
    verdict, detail = g.classify_verdict({}, {},
                                         {"staged": False, "reason": "x"},
                                         "default")
    if verdict != "BLOCKED":
        return False, f"expected BLOCKED, got {verdict}"
    return True, "failed seed staging -> BLOCKED"


def tc_exit_integrity_fixture(g, root, out) -> tuple[bool, str]:
    save1 = make_save()
    run1 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": False, "parse_error": "",
            "settled_snapshot": {"save": save1},
            "post_exit_snapshot": {"save": save1}}
    run2 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True,
            "rewrite_count": 2, "exit_stable": True, "parse_error": "",
            "settled_snapshot": {"save": semantic_twin(save1)},
            "post_exit_snapshot": {"save": semantic_twin(save1)}}
    verdict, detail = g.classify_verdict(run1, run2, {"staged": True},
                                         "default")
    if verdict != "FAIL":
        return False, f"expected FAIL (exit mutated state), got {verdict}"
    return True, "unstable exit detected -> FAIL"


def tc_portability_self_scan(g, root, out) -> tuple[bool, str]:
    hits = []
    secrets = []
    for rel in S3_FILES:
        p = root / rel
        if not p.is_file():
            hits.append(f"missing file {rel}")
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#!"):
                continue
            if DRIVE_RE.search(line):
                hits.append(f"{rel}:{i}")
            for pat in SECRET_PATTERNS:
                if pat.search(line):
                    secrets.append(f"{rel}:{i}")
    if hits or secrets:
        return False, f"abs-path hits={hits} secret hits={secrets}"
    return True, f"{len(S3_FILES)} S3 files clean (abs-path=0 secret=0)"


def tc_evidence_schema(g, root, out) -> tuple[bool, str]:
    req = ["experiment_id", "tool_version", "recorded_at", "ended_at",
           "commands", "candidate", "same_state", "runs", "status",
           "verdict_detail", "proves", "not_proven"]
    save = make_save()
    run1 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True, "parse_error": "",
            "rewrite_count": 2, "exit_stable": True,
            "post_exit_snapshot": {"save": save, "semantic_sha256": "a",
                                   "raw_sha256": "b", "size": 10},
            "settled_snapshot": {"save": save, "semantic_sha256": "a",
                                 "raw_sha256": "b", "size": 10}}
    run2 = {"window_found": True, "load_triggered": True,
            "load_marker_seen": True, "no_save_marker": False,
            "fatal_markers": [], "save_parse_ok": True, "parse_error": "",
            "rewrite_count": 2, "exit_stable": True,
            "post_exit_snapshot": {"save": semantic_twin(save),
                                   "semantic_sha256": "a", "raw_sha256": "c",
                                   "size": 10},
            "settled_snapshot": {"save": semantic_twin(save),
                                 "semantic_sha256": "a", "raw_sha256": "c",
                                 "size": 10}}
    class Args:
        experiment_id = "B3-P2-S3-selftest"
        recorded_at = "2026-08-20T00:00:00Z"
        candidate_sha = "0" * 64
        candidate = "dummy"
        apdata = "dummy-missing"
        seed_save = "seed"
        character_name = "default"
    ev = g.build_evidence(Args(), "PASS",
                          {"run1_exit_vs_run2_diffs": [],
                           "planted_marker_run2": {"ok": True},
                           "exit_stable": True, "rewritten_twice": True,
                           "run2_load_marker": True},
                          run1, run2,
                          {"staged": True, "seed_sha_before": "x",
                           "seed_sha_after": "y", "seed_size": 1,
                           "finalize": "none"},
                          Path("dummy-outdir"))
    missing = [k for k in req if k not in ev]
    if missing:
        return False, f"evidence missing keys: {sorted(missing)}"
    if ev["proves"] is None or ev["not_proven"] is None:
        return False, "PASS evidence must state proves and not_proven"
    return True, f"evidence schema complete ({len(req)} keys)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None,
                    help="evidence JSON path (default: 10_logs/... under repo)")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    gate = import_gate(root)

    tests = [
        tc_semantic_snapshot_excludes_volatile,
        tc_semantic_sha_ignores_volatile,
        tc_semantic_sha_changes_on_field,
        tc_compare_identical,
        tc_compare_reports_paths,
        tc_compare_missing_branch,
        tc_planted_marker_ok,
        tc_planted_marker_missing,
        tc_parse_valid,
        tc_parse_invalids,
        tc_reload_equal_fixture,
        tc_reload_diff_fixture,
        tc_blocked_no_trigger,
        tc_blocked_bad_seed,
        tc_exit_integrity_fixture,
        tc_portability_self_scan,
        tc_evidence_schema,
    ]

    out_dir = root / "10_logs" / "b3-p2-x2-s3-persistence-20260820"
    if args.out:
        out_dir = args.out.resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for tc in tests:
        try:
            ok, detail = tc(gate, root, out_dir)
        except Exception as exc:  # noqa: BLE001 - self-tests must not crash
            ok, detail = False, f"exception: {type(exc).__name__}: {exc}"
        results.append({"test": tc.__name__, "pass": ok, "detail": detail})
        print(f"[{'PASS' if ok else 'FAIL'}] {tc.__name__}: {detail}")

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    verdict = "PASS" if passed == total else "FAIL"
    evidence = {
        "experiment_id": "B3-P2-S3-selftests",
        "tool_version": gate.TOOL_VERSION,
        "recorded_at": gate.utc_now(),
        "scope": "offline only - no game launched; runtime save->exit->reload "
                 "is the explicit S3 gate run",
        "repo_root": str(root),
        "tests": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "verdict": verdict,
        "exit_code": 0 if verdict == "PASS" else 1,
        "proves": "semantic fingerprinting/canonicalization, volatile-key "
                  "exemption (timestamp/checksum/stamp), diff-path reporting, "
                  "planted-marker checks, verdict classification "
                  "(PASS/FAIL/BLOCKED), evidence schema completeness and "
                  "portability/secret hygiene of the S3 files",
        "not_proven": "any game runtime behaviour - the real save->exit->"
                      "reload cycle must be executed against a candidate via "
                      "s3_persistence_gate.py",
    }
    report = out_dir / "s3_persistence_selftests_evidence.json"
    report.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"\ns3-persistence selftests: {verdict}  ({passed}/{total})")
    print(f"evidence: {report}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())