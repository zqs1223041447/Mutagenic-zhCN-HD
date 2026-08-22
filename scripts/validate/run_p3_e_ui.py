#!/usr/bin/env python3
"""P3-E probe CLI: E7 skill-select UI + passive-tree UI popup roundtrip.

Usage:
    python scripts/validate/run_p3_e_ui.py \
        --out migration/conversion/p3_e_ui.json --timeout 300
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_probe_common import EXIT_CODES, gather_report  # noqa: E402

STEPS = ("skill_select", "passive_tree", "cleanup")


def summarize(report: dict) -> str:
    errors = report.get("errors") or {}
    by_domain = errors.get("by_domain") or {}
    driver = report.get("driver_result") or {}
    steps = {
        k: bool((driver.get(k) or {}).get("pass"))
        for k in STEPS
        if k in driver
    }
    return (
        f"{report['task']} overall={report.get('overall')}"
        f" rc={report.get('returncode')}"
        f" steps={steps}"
        f" script_errors={errors.get('script_error_total')}"
        f" domains={by_domain}"
        f" asset_family_lines={errors.get('missing_asset_family_lines')}"
        f" flake_retried={report.get('flake_retried')}"
        f" note={report.get('note') or '-'}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="P3-E UI popup roundtrip probe")
    ap.add_argument(
        "--out", type=Path, default=Path("migration/conversion/p3_e_ui.json"),
        help="evidence JSON path",
    )
    ap.add_argument("--timeout", type=int, default=300, help="engine run timeout seconds")
    args = ap.parse_args(argv)
    out_path = args.out if args.out.is_absolute() else (REPO / args.out)

    report = gather_report(
        task_id="P3-E",
        marker="P3E_RESULT_JSON<<<",
        driver_scene="res://scenes/Levels/_validate/P3EUIDriver.tscn",
        cli_line="",
        out_path=out_path,
        timeout_s=args.timeout,
    )
    report["cli"] = (
        f"python scripts/validate/run_p3_e_ui.py"
        f" --out {args.out.as_posix()} --timeout {args.timeout}"
    )
    report["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(summarize(report))
    return EXIT_CODES.get(report.get("overall"), 1)


if __name__ == "__main__":
    raise SystemExit(main())
