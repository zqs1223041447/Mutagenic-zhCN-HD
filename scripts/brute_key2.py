#!/usr/bin/env python3
"""Brute-force Godot .gde AES key over PE section windows (no magic filter).

Scans every 4-byte-aligned 32-byte window inside the PE's loadable sections
(.text/.rdata/.data/_RDATA/.rsrc/.reloc; skips the pck section) and fully
decrypts + MD5-verifies each window as the AES-256-ECB key.

Usage:
    python scripts/brute_key2.py <exe> <gde_file> [-o keyfile] [--procs N]
"""

import argparse
import hashlib
import multiprocessing as mp
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES

SKIP_NAMES = {"pck"}


def parse_pe_sections(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    coff = e_lfanew + 4
    machine, n_sec, ts, sp, sc, opt_size, chars = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    sec_off = opt + opt_size
    sections = []
    for i in range(n_sec):
        off = sec_off + i * 40
        name = data[off:off + 8].rstrip(b"\0").decode("latin-1")
        _n, vsize, vaddr, raw_size, raw_ptr, *_ = struct.unpack_from("<8sIIII", data, off)
        sections.append({"name": name, "raw_ptr": raw_ptr, "raw_size": raw_size})
    return sections


def scan_region(args):
    data, start, end, step, md5d, plen, enc = args
    hits = []
    for off in range(start, end - 31, step):
        key = data[off:off + 32]
        try:
            plain = AES.new(key, AES.MODE_ECB).decrypt(enc)[:plen]
        except ValueError:
            continue
        if hashlib.md5(plain).digest() == md5d:
            hits.append((off, key))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", type=Path)
    ap.add_argument("gde", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--step", type=int, default=4)
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()

    gde = args.gde.read_bytes()
    md5d, plen, enc = gde[8:24], int.from_bytes(gde[24:32], "little"), gde[32:]
    print(f"gde: plen={plen} md5={md5d.hex()}")

    data = args.exe.read_bytes()
    sections = [s for s in parse_pe_sections(data) if s["name"] not in SKIP_NAMES]
    total = sum(s["raw_size"] for s in sections)
    print(f"sections scanned: {[(s['name'], s['raw_size']) for s in sections]}")
    print(f"total bytes: {total} windows ~{total // args.step}")

    tasks = []
    window = 8 * 1024 * 1024
    for sec in sections:
        sp, ss = sec["raw_ptr"], sec["raw_size"]
        if ss <= 32:
            continue
        for start in range(sp, sp + ss - 31, window):
            end = min(start + window, sp + ss)
            tasks.append((data, start, end, args.step, md5d, plen, enc))
    print(f"tasks: {len(tasks)}")

    with mp.Pool(args.procs) as pool:
        done = 0
        for hits in pool.imap_unordered(scan_region, tasks):
            done += 1
            for off, key in hits:
                print(f"KEY FOUND at offset {off}: {key.hex()}")
                if args.output:
                    args.output.write_bytes(key)
                    print(f"saved: {args.output}")
                return 0
            if done % 10 == 0:
                print(f"progress {done}/{len(tasks)}")
    print("no key found")
    return 1


if __name__ == "__main__":
    sys.exit(main())