#!/usr/bin/env python3
"""Recover the Godot 3.5 script encryption key statically from the EXE.

The key is stored in the binary as a raw 32-byte AES-256 key (not as an
ASCII/hex string), so hex-candidate scanners (find_script_key.py) and
GDCC-magic filters (brute_key.py) both miss it. This script simply tests
every 32-byte window of the EXE with full AES-256-ECB decryption + GDEC
header MD5 verification - the MD5 is the only reliable judge.

Usage:
    python scripts/scan_script_key_static.py <exe> <gde_file> [-o <keyfile>]

Exits 0 and prints the 64-hex key when found.
"""

from __future__ import annotations

import argparse
import hashlib
import multiprocessing as mp
import sys
from pathlib import Path

from Crypto.Cipher import AES


def load_gde(path: Path):
    d = path.read_bytes()
    if d[:4] != b"GDEC":
        raise SystemExit(f"ERROR: {path} is not a GDEC script")
    md5d = d[8:24]
    plen = int.from_bytes(d[24:32], "little")
    enc = d[32:]
    return md5d, plen, enc


def scan_chunk(args):
    chunk, base_off, md5d, plen, enc = args
    n = len(chunk)
    hits = []
    for off in range(0, n - 31):
        key = chunk[off:off + 32]
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            plain = cipher.decrypt(enc)[:plen]
        except ValueError:
            continue
        if hashlib.md5(plain).digest() == md5d:
            hits.append((base_off + off, key.hex()))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Static script-key recovery")
    ap.add_argument("exe", type=Path)
    ap.add_argument("gde", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()

    md5d, plen, enc = load_gde(args.gde)
    print(f"gde {args.gde}: plaintext_len={plen} enc_len={len(enc)} "
          f"md5={md5d.hex()} procs={args.procs}")

    exe = args.exe.read_bytes()
    size = len(exe)
    print(f"exe size={size} windows={size - 31}")

    chunk_size = 8 * 1024 * 1024
    tasks = []
    for start in range(0, size, chunk_size):
        end = min(start + chunk_size, size)
        chunk = exe[start:min(end + 31, size)]
        tasks.append((chunk, start, md5d, plen, enc))

    found = 0
    with mp.Pool(args.procs) as pool:
        for hits in pool.imap_unordered(scan_chunk, tasks):
            for off, key_hex in hits:
                found += 1
                print(f"KEY FOUND at offset {off}: {key_hex}")
                if args.output:
                    args.output.write_text(key_hex + "\n", encoding="ascii")
                    print(f"saved: {args.output}")

    if found:
        return 0
    print("no key found")
    return 1


if __name__ == "__main__":
    sys.exit(main())