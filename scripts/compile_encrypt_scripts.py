#!/usr/bin/env python3
"""Compile + encrypt GDScript: 06_worktree/*.gd -> 07_compiled/*.gde (+ .gd.remap)

Pipeline per script:
    .gd  --(GDRE --compile)-->  .gdc  --(AES-256-ECB)-->  .gde   + .gd.remap

GDEC container layout (Godot 3.x FileAccessEncrypted):
    0..4    "GDEC" magic
    4..8    u32 mode        (1 == MODE_WRITE_AES256)
    8..24   md5(plaintext)  16 bytes
    24..32  u64 plaintext length
    32..    AES-256-ECB ciphertext, zero-padded to a 16-byte boundary

Correctness is not asserted -- it is PROVEN by --self-test, which re-creates
.gde files for scripts that already exist in 03_raw and compares byte for byte.

Usage:
    python scripts/compile_encrypt_scripts.py --self-test [--limit 12]
    python scripts/compile_encrypt_scripts.py [--worktree 06_worktree] [--output 07_compiled]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from Crypto.Cipher import AES

ROOT = Path(__file__).resolve().parent.parent
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
KEY_FILE = ROOT / "manifests/script_key.txt"
BYTECODE = "3.5.3.stable"

GDEC_MAGIC = b"GDEC"
MODE_WRITE_AES256 = 1
SKIP_DIRS = {".autoconverted"}


def read_key() -> bytes:
    if not KEY_FILE.exists():
        sys.exit(f"ERROR: script key not found: {KEY_FILE}")
    key_hex = KEY_FILE.read_text().strip()
    if len(key_hex) != 64:
        sys.exit(f"ERROR: key must be 64 hex chars, got {len(key_hex)}")
    return bytes.fromhex(key_hex)


def make_gde(plaintext: bytes, key: bytes) -> bytes:
    """Wrap compiled bytecode into an encrypted GDEC container."""
    pad = (16 - len(plaintext) % 16) % 16
    cipher = AES.new(key, AES.MODE_ECB).encrypt(plaintext + b"\x00" * pad)
    return b"".join([
        GDEC_MAGIC,
        struct.pack("<I", MODE_WRITE_AES256),
        hashlib.md5(plaintext).digest(),
        struct.pack("<Q", len(plaintext)),
        cipher,
    ])


def compile_gd(gd_path: Path, out_dir: Path) -> Path | None:
    """Compile one .gd to .gdc with GDRE. Returns the .gdc path or None."""
    out_dir.mkdir(parents=True, exist_ok=True)
    gdc = out_dir / f"{gd_path.stem}.gdc"
    if gdc.exists():
        gdc.unlink()
    r = subprocess.run(
        [str(GDRE), "--headless", f"--compile={gd_path}",
         f"--bytecode={BYTECODE}", f"--output={out_dir}"],
        capture_output=True, text=True,
    )
    if not gdc.exists():
        print(f"    compile failed rc={r.returncode}: {r.stdout.strip()[-300:]}")
        return None
    return gdc


def remap_text(rel: Path) -> str:
    res = str(rel.with_suffix(".gde")).replace("\\", "/")
    return f'[remap]\n\npath="res://{res}"\n'


def self_test(key: bytes, limit: int) -> int:
    """Re-create .gde for scripts that already have one; compare byte for byte."""
    raw = ROOT / "03_raw"
    wt = ROOT / "06_worktree"
    tmp = ROOT / "10_logs/gde_selftest"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    originals = sorted(raw.rglob("*.gde"))
    targets = []
    for gde in originals:
        rel = gde.relative_to(raw)
        gd = wt / rel.with_suffix(".gd")
        if gd.exists():
            targets.append((rel, gde, gd))
        if len(targets) >= limit:
            break

    print(f"self-test on {len(targets)} scripts (of {len(originals)} .gde in 03_raw)\n")
    ok = bad = 0
    failures = []
    for rel, gde_orig, gd_src in targets:
        gdc = compile_gd(gd_src, tmp / rel.parent)
        if gdc is None:
            bad += 1
            failures.append((str(rel), "compile failed"))
            continue
        ours = make_gde(gdc.read_bytes(), key)
        theirs = gde_orig.read_bytes()
        if ours == theirs:
            ok += 1
            print(f"  MATCH  {rel}  ({len(theirs)} bytes)")
        else:
            bad += 1
            why = (f"size {len(ours)} vs {len(theirs)}" if len(ours) != len(theirs)
                   else "same size, different bytes")
            failures.append((str(rel), why))
            print(f"  DIFF   {rel}  ({why})")

    print(f"\n{'='*60}")
    print(f"byte-identical: {ok}/{len(targets)}    mismatched: {bad}")
    if failures:
        print("failures:")
        for name, why in failures[:10]:
            print(f"  - {name}: {why}")
    print(f"VERDICT: {'PASS' if bad == 0 and ok > 0 else 'FAIL'}")
    print(f"{'='*60}")
    return 0 if (bad == 0 and ok > 0) else 1


def build_all(key: bytes, worktree: Path, output: Path) -> int:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    gd_files = [p for p in sorted(worktree.rglob("*.gd"))
                if not any(sk in p.relative_to(worktree).parts for sk in SKIP_DIRS)]
    print(f"compiling + encrypting {len(gd_files)} scripts -> {output}\n")

    ok = 0
    failed = []
    for i, gd in enumerate(gd_files, 1):
        rel = gd.relative_to(worktree)
        gdc = compile_gd(gd, output / rel.parent)
        if gdc is None:
            failed.append(str(rel))
            continue
        gde = output / rel.with_suffix(".gde")
        gde.write_bytes(make_gde(gdc.read_bytes(), key))
        gdc.unlink()                                  # keep only .gde
        (output / f"{rel}.remap").write_text(remap_text(rel), encoding="utf-8")
        ok += 1
        if i % 100 == 0 or i == len(gd_files):
            print(f"  {i}/{len(gd_files)} ... ok={ok} failed={len(failed)}")

    manifest = ROOT / "manifests/compile_manifest.json"
    manifest.parent.mkdir(exist_ok=True)
    manifest.write_text(json.dumps({
        "worktree": str(worktree), "output": str(output),
        "bytecode": BYTECODE, "total": len(gd_files),
        "encrypted": ok, "failed": failed,
    }, indent=1), encoding="utf-8")

    print(f"\nencrypted: {ok}/{len(gd_files)}   failed: {len(failed)}")
    print(f"manifest: {manifest}")
    if failed:
        for f in failed[:10]:
            print(f"  - {f}")
    return 0 if not failed else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="re-create existing .gde files and compare byte for byte")
    ap.add_argument("--limit", type=int, default=12, help="self-test sample size")
    ap.add_argument("--worktree", type=Path, default=ROOT / "06_worktree")
    ap.add_argument("--output", type=Path, default=ROOT / "07_compiled")
    args = ap.parse_args()

    key = read_key()
    print(f"key: {KEY_FILE.name} (AES-256, {len(key)} bytes)\n")
    if args.self_test:
        return self_test(key, args.limit)
    return build_all(key, args.worktree, args.output)


if __name__ == "__main__":
    sys.exit(main())
