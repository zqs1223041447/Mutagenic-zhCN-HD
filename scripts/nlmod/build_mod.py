#!/usr/bin/env python3
"""NL2MOD Layer 3: one-command build pipeline from a mod.json to a candidate EXE.

Runs the established production chain, in order, with fail-closed gates:
  setup_worktree (04_recovered -> worktree base) [reused via copy]
  resolve_mod_chain (mod.json -> resolved manifest)
  apply_mod (resolved -> patched worktree)
  compile_declared_scripts (patched .gd -> .gde + .gd.remap)
  build_declared_pack (03_raw + compiled deltas -> pack tree)
  normalize_pck_md5 (zero-byte workaround)
  (embed + roundtrip + boot are the next stage; this script stops at a ready
   pack tree so the orchestrator can decide where to embed/output.)

Usage:
    python scripts/nlmod/build_mod.py --mod-id <id> [--out-dir 10_logs/nl2mod-<id>-YYYYMMDD]

Requires: project venv python (02_tools/venv), GDRE, scripts/lock files.
All writes go to --out-dir; immutable inputs (00_original/03_raw/04_recovered)
are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
PY = ROOT / "02_tools/venv/Scripts/python.exe"
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
MODS_ROOT = ROOT / "mods"
RAW = ROOT / "03_raw"
RECOVERED = ROOT / "04_recovered"
KEY_FILE = ROOT / "manifests/script_key.txt"
ORIGINAL_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"


def run(cmd: list[str], label: str, cwd: Path = ROOT) -> dict:
    print(f"\n=== {label} ===")
    p = subprocess.run([str(PY), *cmd], cwd=cwd, capture_output=True, text=True)
    if p.stdout:
        print(p.stdout[-2000:])
    if p.stderr:
        print("STDERR:", p.stderr[-1000:])
    if p.returncode != 0:
        raise SystemExit(f"FAILED at {label} (exit {p.returncode})")
    print(f"OK: {label}")
    return {"label": label, "exit": p.returncode}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mod-id", type=str, required=True)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--compile-cache", type=Path, default=None,
                    help="persistent .gde cache dir (default: <out-dir>/compile_cache); "
                         "unchanged sources are reused across builds for fast iteration")
    args = ap.parse_args()

    mod_dir = MODS_ROOT / args.mod_id
    mod_json = mod_dir / "mod.json"
    if not mod_json.exists():
        raise SystemExit(f"ERROR: manifest not found: {mod_json}")

    # --- NL2MOD safety guards (AGENTS.md §6 / docs/ai/nl2mod-guide.md) ---
    mod = json.loads(mod_json.read_text(encoding="utf-8"))
    # 1. Game fingerprint guard: manifest must target the pristine original
    declared_target = mod.get("target_original_sha256", ORIGINAL_SHA)
    if declared_target != ORIGINAL_SHA:
        raise SystemExit(f"ERROR: manifest targets {declared_target}, expected pristine {ORIGINAL_SHA}")
    # 2. Immutable input guard: 03_raw / 04_recovered must be untouched (only read)
    if not RAW.exists() or not RECOVERED.exists():
        raise SystemExit("ERROR: immutable inputs 03_raw/04_recovered missing")
    # 3. schema/toolchain present
    if not KEY_FILE.exists():
        raise SystemExit("ERROR: manifests/script_key.txt missing (local secret, never committed)")
    if not GDRE.exists():
        raise SystemExit(f"ERROR: GDRE not found: {GDRE}")
    print(f"guards OK: target={ORIGINAL_SHA[:12]}..., mods={len(mod.get('patches', []))} patch(es)")


    out = args.out_dir or (ROOT / f"10_logs/nl2mod-{args.mod_id}-{datetime.now():%Y%m%d-%H%M%S}")
    out.mkdir(parents=True, exist_ok=False)

    # 1. Fresh worktree base = copy of 04_recovered (source-of-truth recovered tree)
    base = out / "base_worktree"
    shutil.copytree(RECOVERED, base)
    print(f"base worktree copied from 04_recovered: {base}")

    # 2. Resolve dependency chain
    resolved = out / "resolved_mod.json"
    run([
        "scripts/patch/resolve_mod_chain.py",
        "--manifest", str(mod_json),
        "--mods-root", str(MODS_ROOT),
        "--output", str(resolved),
        "--report", str(out / "resolve_report.json"),
    ], "resolve_mod_chain")

    # 3. Apply patches to a disposable patched worktree
    patched = out / "patched_worktree"
    run([
        "scripts/patch/apply_mod.py",
        "--base", str(base),
        "--manifest", str(resolved),
        "--out", str(patched),
        "--report", str(out / "apply_report.json"),
    ], "apply_mod")

    # 4. Compile only declared scripts -> .gde + .gd.remap
    compiled = out / "compiled"
    compile_cmd = [
        "scripts/build/compile_declared_scripts.py",
        "--worktree", str(patched),
        "--manifest", str(resolved),
        "--out", str(compiled),
        "--report", str(out / "compile_report.json"),
    ]
    cache_dir = args.compile_cache or (out / "compile_cache")
    if cache_dir:
        compile_cmd += ["--cache", str(cache_dir)]
    run(compile_cmd, "compile_declared_scripts")

    # 5. Build pack tree = 03_raw + declared deltas
    pack = out / "pack"
    run([
        "scripts/build/build_declared_pack.py",
        "--base", str(RAW),
        "--worktree", str(patched),
        "--compiled", str(compiled),
        "--manifest", str(resolved),
        "--out", str(pack),
        "--report", str(out / "pack_report.json"),
    ], "build_declared_pack")

    # 6. Create PCK from pack tree via GDRE (pck-create) - GDRE requires --key=value form
    raw_pck = out / f"{args.mod_id}.pck"
    print(f"\n=== GDRE pck-create ===")
    p = subprocess.run([
        str(GDRE), "--headless",
        f"--pck-create={pack}",
        "--pck-version=1",
        "--pck-engine-version=3.5.3",
        f"--output={raw_pck}",
    ], cwd=ROOT, capture_output=True, text=True)
    if p.stdout:
        print(p.stdout[-1500:])
    if p.stderr:
        print("STDERR:", p.stderr[-800:])
    if not raw_pck.exists():
        raise SystemExit(f"FAILED: GDRE pck-create did not produce {raw_pck}")
    print(f"OK: GDRE pck-create -> {raw_pck} ({raw_pck.stat().st_size} bytes)")

    # 7. Normalize PCK MD5 (zero-byte workaround)
    pck = out / f"{args.mod_id}_normalized.pck"
    run([
        "scripts/build/normalize_pck_md5.py",
        "--input", str(raw_pck),
        "--output", str(pck),
        "--report", str(out / "normalize_report.json"),
    ], "normalize_pck_md5")

    print(f"\n=== NL2MOD BUILD PASS ===")
    print(f"pack tree : {pack}")
    print(f"normalized pck : {pck}")
    print(f"pck sha256 : {sha256_file(pck)}")
    print("Next: embed into a fresh 00_original copy (scripts/embed_pck.py), then roundtrip + boot gates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
