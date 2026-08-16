"""Decisive test: pristine original source -> compile -> encrypt -> compare.

For each target script this does a full round trip that never touches the
possibly-contaminated 04_recovered / 06_worktree trees:

    03_raw/<rel>.gde --(GDRE --decompile)--> pristine .gd
                     --(GDRE --compile)---->        .gdc
                     --(AES-256-ECB+GDEC)-->        .gde
                     == 03_raw/<rel>.gde  ?

A byte-identical result proves the compile+encrypt pipeline has no defect and
that any earlier mismatch came from edited source, not from the pipeline.

Usage:
    python scripts/probe_pristine_roundtrip.py Globals/Constants Globals/GameState
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import json
from datetime import datetime, timezone
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
RAW = ROOT / "03_raw"
WORK = ROOT / "10_logs/pristine_roundtrip"
KEY_FILE = ROOT / "manifests/script_key.txt"
BYTECODE = "3.5.3.stable"

sys.path.insert(0, str(ROOT / "scripts"))
from compile_encrypt_scripts import make_gde  # noqa: E402


def run_gdre(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(GDRE), "--headless", *args],
                          capture_output=True, text=True)


def roundtrip(rel: str, key: bytes) -> dict:
    orig = RAW / f"{rel}.gde"
    if not orig.exists():
        print(f"  SKIP {rel}: no original .gde")
        return {"target": rel, "status": "FAIL", "reason": "missing_raw_gde"}

    stage = WORK / rel.replace("/", "_")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    name = Path(rel).name

    # 1. original .gde -> pristine .gd
    run_gdre(f"--decompile={orig}", f"--key={key.hex()}",
             f"--bytecode={BYTECODE}", f"--output={stage}")
    pristine = stage / f"{name}.gd"
    if not pristine.exists():
        print(f"  FAIL {rel}: decompile produced nothing")
        return {"target": rel, "status": "FAIL", "reason": "decompile_produced_nothing"}

    # 2. pristine .gd -> .gdc
    run_gdre(f"--compile={pristine}", f"--bytecode={BYTECODE}",
             f"--output={stage}")
    gdc = stage / f"{name}.gdc"
    if not gdc.exists():
        print(f"  FAIL {rel}: compile produced nothing")
        return {"target": rel, "status": "FAIL", "reason": "compile_produced_nothing"}

    # 3. .gdc -> .gde and compare
    ours = make_gde(gdc.read_bytes(), key)
    theirs = orig.read_bytes()
    same = ours == theirs
    verdict = "MATCH" if same else "DIFF"
    print(f"  {verdict}  {rel}: pristine_src={pristine.stat().st_size}B "
          f"gdc={gdc.stat().st_size}B ours={len(ours)}B orig={len(theirs)}B")
    return {
        "target": rel,
        "status": "PASS" if same else "FAIL",
        "source_bytes": pristine.stat().st_size,
        "compiled_bytes": gdc.stat().st_size,
        "result_bytes": len(ours),
        "original_bytes": len(theirs),
        "result_sha256": __import__("hashlib").sha256(ours).hexdigest(),
        "original_sha256": __import__("hashlib").sha256(theirs).hexdigest(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*", default=["Globals/Constants", "Globals/GameState"])
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()
    targets = args.targets
    key = bytes.fromhex(KEY_FILE.read_text().strip())
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"pristine round trip on {len(targets)} script(s)\n")
    result_rows = [roundtrip(t, key) for t in targets]
    results = {row["target"]: row for row in result_rows}

    print(f"\n{'='*60}")
    passed = sum(row.get("status") == "PASS" for row in result_rows)
    print(f"byte-identical: {passed}/{len(targets)}")
    verdict = "PASS - pipeline is defect-free" if passed == len(targets) else "FAIL - real pipeline defect"
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")
    if args.report:
        report = {
            "experiment_id": "C0-SCRIPT-ZERO-CHANGE-ROUNDTRIP",
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "baseline": "03_raw",
            "tool": str(GDRE),
            "bytecode": BYTECODE,
            "targets": result_rows,
            "passed": passed,
            "total": len(targets),
            "verdict": "PASS" if passed == len(targets) else "FAIL",
            "proves": "selected stratified scripts round-trip byte-identically",
            "not_proven": "all scripts, gameplay behavior, packaging, localization, persistence",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"report: {args.report}")
    return 0 if passed == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
