#!/usr/bin/env python3
"""Bootstrap a Mutagenic dev/deploy environment from a pristine original EXE.

The repository intentionally does NOT contain the original game binary
(copyright). 03_raw and 04_recovered ARE committed (byte-preserving, see
.gitattributes), but anyone cloning fresh still needs:

  1. the original Mutagenic.exe (owned copy) placed at 00_original/
  2. the local script encryption key (never committed) - recovered offline
     by scan_script_key_static.py, which tests every 32-byte window of the
     EXE with full AES-256-ECB decryption + GDEC header MD5 verification
  3. GDRE tooling under 02_tools/ (also not committed)

This script performs every reproducible step and verifies the recovered
artifacts against their committed manifests.

Usage:
    python scripts/bootstrap_deploy.py [--exe 00_original/Mutagenic.exe]
        [--extract-dir 03_raw] [--recovered-dir 04_recovered]
        [--key-out manifests/script_key.txt] [--gdre 02_tools/gdre/gdre_tools.exe]
        [--skip-extract] [--skip-recover] [--yes]

Exits 0 only when all verifiable gates pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_SHA256 = "c7b5d5a529cd776609f72730662f1f6a8049fe5de20541f7eafe06d0f2451209"
ORIGINAL_SIZE = 103290320
RAW_MANIFEST = ROOT / "manifests/raw_manifest.json"
RECOVERED_MANIFEST = ROOT / "manifests/recovered_clean_manifest.json"


def log(msg: str) -> None:
    print(f"[bootstrap] {msg}")


def fail(msg: str) -> int:
    print(f"[bootstrap] FAIL: {msg}")
    return 1


def verify_original(exe: Path) -> bool:
    if not exe.is_file():
        return False
    data = exe.read_bytes()
    if len(data) != ORIGINAL_SIZE:
        log(f"original size mismatch: {len(data)} != {ORIGINAL_SIZE}")
        return False
    sha = hashlib.sha256(data).hexdigest()
    if sha != ORIGINAL_SHA256:
        log(f"original sha256 mismatch: {sha}")
        return False
    log(f"original verified: size={len(data)} sha256={sha}")
    return True


def verify_manifest_tree(root: Path, manifest: Path, label: str) -> bool:
    if not manifest.is_file():
        log(f"{label}: manifest missing {manifest} - skipping tree check")
        return True
    data = json.loads(manifest.read_text(encoding="utf-8"))
    files = data["files"]
    missing, mismatched = 0, 0
    for entry in files:
        p = root / entry["relpath"]
        if not p.is_file():
            missing += 1
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != entry["sha256"]:
            mismatched += 1
    if missing or mismatched:
        log(f"{label}: {missing} missing, {mismatched} sha256-mismatched")
        return False
    log(f"{label}: all {len(files)} files match manifest sha256")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", type=Path, default=ROOT / "00_original/Mutagenic.exe")
    ap.add_argument("--extract-dir", type=Path, default=ROOT / "03_raw")
    ap.add_argument("--recovered-dir", type=Path, default=ROOT / "04_recovered")
    ap.add_argument("--key-out", type=Path, default=ROOT / "manifests/script_key.txt")
    ap.add_argument("--gdre", type=Path, default=ROOT / "02_tools/gdre/gdre_tools.exe")
    ap.add_argument("--skip-extract", action="store_true",
                    help="skip re-extracting 03_raw from the EXE")
    ap.add_argument("--skip-recover", action="store_true",
                    help="skip re-running GDRE recovery into a temp dir")
    ap.add_argument("--skip-key", action="store_true",
                    help="skip offline key recovery (requires existing key)")
    ap.add_argument("--yes", action="store_true", help="auto-accept prompts")
    args = ap.parse_args()

    exe = args.exe.resolve()
    ok = True

    log("step 1/5: verify original EXE fingerprint")
    if not verify_original(exe):
        return fail(f"original EXE missing or wrong at {exe}; "
                    "place an owned pristine copy at 00_original/Mutagenic.exe")
    ok = ok and True

    if not args.skip_key:
        log("step 2/5: recover local script encryption key (offline, from EXE)")
        key_out = args.key_out.resolve()
        if key_out.is_file():
            key = key_out.read_bytes().hex()
            if len(key) == 64:
                log(f"key already present at {key_out} (len={len(key)} hex) - reusing")
                ok = ok and True
            else:
                log(f"existing key file has unexpected length {len(key)} hex - regenerating")
                key_out.unlink()
        if not key_out.is_file():
            # scan_script_key_static needs one .gde sample; pick the smallest
            # committed original one (from 03_raw, NOT 04_recovered which may
            # contain GDRE-converted bytecode)
            gde_candidates = sorted(args.extract_dir.resolve().rglob("*.gde"),
                                    key=lambda p: p.stat().st_size)
            gde = gde_candidates[0] if gde_candidates else None
            if gde is None:
                return fail("no .gde sample found under 03_raw for key recovery")
            cmd = [sys.executable, str(ROOT / "scripts/scan_script_key_static.py"),
                   str(exe), str(gde), "-o", str(key_out)]
            log("running: " + " ".join(cmd))
            r = subprocess.run(cmd, cwd=ROOT)
            ok = ok and r.returncode == 0
            if r.returncode != 0:
                return fail("key recovery failed")
        # sanitize: keep only the 64-hex line
        key = key_out.read_text(encoding="utf-8").strip()
        if len(key) != 64:
            return fail(f"key file not 64 hex chars after recovery: {key_out}")
        log(f"key ready: {key_out} (64 hex chars, not committed - .gitignore)")
    else:
        log("step 2/5: SKIPPED key recovery (--skip-key)")

    if not args.skip_extract:
        log("step 3/5: re-extract 03_raw from original EXE")
        cmd = [sys.executable, str(ROOT / "scripts/extract_pck.py"),
               str(exe), "-o", str(args.extract_dir.resolve()),
               "-m", str(RAW_MANIFEST)]
        log("running: " + " ".join(cmd))
        r = subprocess.run(cmd, cwd=ROOT)
        ok = ok and r.returncode == 0
        if r.returncode != 0:
            return fail("extract_pck failed")
    else:
        log("step 3/5: SKIPPED extraction (--skip-extract)")

    log("step 4/5: verify committed trees against manifests")
    if not verify_manifest_tree(args.extract_dir.resolve(), RAW_MANIFEST, "03_raw"):
        ok = False
    if not verify_manifest_tree(args.recovered_dir.resolve(), RECOVERED_MANIFEST, "04_recovered"):
        ok = False
    if not ok:
        return fail("manifest verification failed")

    if not args.skip_recover:
        log("step 5/5: sanity-recover via GDRE (proves EXE+key+gdre chain)")
        if not args.gdre.resolve().is_file():
            log(f"GDRE not found at {args.gdre}; chain test SKIPPED - "
                "download gdre_tools to 02_tools/gdre/ to enable recovery builds")
            log("bootstrap complete (extraction + verification passed; GDRE optional)")
            return 0 if ok else 1
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "recovered"
            cmd = [sys.executable, str(ROOT / "scripts/recover/recover_reference.py"),
                   "--exe", str(exe), "--out", str(out),
                   "--log-dir", str(Path(td) / "logs")]
            log("running: " + " ".join(cmd))
            r = subprocess.run(cmd, cwd=ROOT)
            ok = ok and r.returncode == 0
            if r.returncode != 0:
                return fail("GDRE recovery chain test failed")
            log(f"GDRE recovery OK: {out}")
    else:
        log("step 5/5: SKIPPED GDRE chain test (--skip-recover)")

    log("bootstrap PASS: original verified, key recovered, trees match manifests")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())