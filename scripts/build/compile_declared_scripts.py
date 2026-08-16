#!/usr/bin/env python3
"""Compile and encrypt only scripts declared by a Mod manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
KEY_FILE = ROOT / "manifests/script_key.txt"
BYTECODE = "3.5.3.stable"

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from compile_encrypt_scripts import make_gde, remap_text  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    mod = json.loads(args.manifest.read_text(encoding="utf-8"))
    key = bytes.fromhex(KEY_FILE.read_text(encoding="utf-8").strip())
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite compiled directory: {out}")
    out.mkdir(parents=True)
    rows = []
    for patch in mod.get("patches", []):
        rel = Path(patch["path"])
        if rel.suffix != ".gd":
            continue
        source = args.worktree.resolve() / rel
        if not source.is_file():
            raise SystemExit(f"ERROR: declared script missing: {rel}")
        stage = out / rel.parent
        stage.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([str(GDRE), "--headless", f"--compile={source}", f"--bytecode={BYTECODE}", f"--output={stage}"], capture_output=True, text=True)
        gdc = stage / f"{rel.stem}.gdc"
        if result.returncode != 0 or not gdc.is_file():
            raise SystemExit(f"ERROR: compile failed for {rel}: rc={result.returncode} {result.stderr[-500:]}")
        gde = stage / f"{rel.stem}.gde"
        gde.write_bytes(make_gde(gdc.read_bytes(), key))
        gdc.unlink()
        remap = stage / f"{rel.name}.remap"
        remap.write_text(remap_text(rel), encoding="utf-8")
        rows.append({"source": rel.as_posix(), "gde": gde.relative_to(out).as_posix(), "remap": remap.relative_to(out).as_posix(), "gde_sha256": hashlib.sha256(gde.read_bytes()).hexdigest(), "remap_sha256": hashlib.sha256(remap.read_bytes()).hexdigest()})
    declared_gd = [p["path"] for p in mod.get("patches", []) if Path(p["path"]).suffix == ".gd"]
    empty_ok = not declared_gd  # pure-resource slices legitimately declare no scripts
    ok = bool(rows) or empty_ok
    report = {"mod": mod["id"], "worktree": str(args.worktree.resolve()), "output": str(out), "bytecode": BYTECODE, "compiled": rows, "count": len(rows), "empty_ok": empty_ok, "verdict": "PASS" if ok else "FAIL", "proves": "only declared script paths were compiled and encrypted", "not_proven": "runtime semantic effect or PCK/EXE structural validation"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"compiled": len(rows), "empty_ok": empty_ok, "verdict": report["verdict"]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
