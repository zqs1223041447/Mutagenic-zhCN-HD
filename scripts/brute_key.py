#!/usr/bin/env python3
"""Brute-force Godot .gde AES key by scanning every 32-byte window of the EXE.

Filter: decrypted first block must equal the GDScript bytecode magic "GDCC".
Verify: full-decrypt + MD5 check against the GDEC header.

Usage:
    python scripts/brute_key.py <exe> <gde_file> [-o <keyfile>] [--step N] [--procs N]
"""

import argparse
import hashlib
import multiprocessing as mp
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES

GDCC = b"GDCC"


def load_gde(path: Path):
    d = path.read_bytes()
    assert d[:4] == b"GDEC", "not a GDEC script"
    md5d = d[8:24]
    plen = int.from_bytes(d[24:32], "little")
    enc = d[32:]
    return md5d, plen, enc


def scan_chunk(args):
    """Scan one chunk; returns list of (offset_in_chunk, key_bytes)."""
    chunk, base_off, step, md5d, plen, enc = args
    hits = []
    n = len(chunk)
    for off in range(0, n - 31, step):
        key = chunk[off:off + 32]
        try:
            cipher = AES.new(key, AES.MODE_ECB)
        except ValueError:
            continue
        block = cipher.decrypt(enc[:16])
        if block == GDCC or all(b == 9 or b == 10 or b == 13 or 32 <= b < 127 for b in block):
            plain = cipher.decrypt(enc)[:plen]
            if hashlib.md5(plain).digest() == md5d:
                hits.append((base_off + off, key))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Brute-force Godot .gde script key")
    ap.add_argument("exe", type=Path)
    ap.add_argument("gde", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()

    md5d, plen, enc = load_gde(args.gde)
    print(f"gde {args.gde}: plaintext_len={plen} enc_len={len(enc)} "
          f"md5={md5d.hex()} step={args.step} procs={args.procs}")

    exe = args.exe.read_bytes()
    size = len(exe)
    print(f"exe size={size} windows={size // args.step}")

    chunk_size = 8 * 1024 * 1024
    tasks = []
    for start in range(0, size, chunk_size):
        end = min(start + chunk_size, size)
        # overlap by 31 bytes so windows crossing chunk borders are covered
        chunk = exe[start:min(end + 31, size)]
        tasks.append((chunk, start, args.step, md5d, plen, enc))

    with mp.Pool(args.procs) as pool:
        for hits in pool.imap_unordered(scan_chunk, tasks):
            for off, key in hits:
                print(f"KEY FOUND at offset {off}: {key.hex()}")
                if args.output:
                    args.output.write_bytes(key)
                    print(f"saved raw key: {args.output}")
                return 0

    print("no key found")
    return 1


if __name__ == "__main__":
    sys.exit(main())
