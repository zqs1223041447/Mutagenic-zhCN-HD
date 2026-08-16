#!/usr/bin/env python3
"""Extract files from the Mutagenic EXE's embedded Godot PCK (v1, custom header).

Known format facts (from manifests/baseline.json):
  - PCK v1 (version=1), unencrypted (pack_flags=0)
  - Header at PE "pck" section raw_ptr (0x26AB100), 84 bytes (32 std + 52 zero pad)
  - 3744 entries, each: path_len(u32) path(pad4) offset(u64) size(u64) md5(16)
  - Entry offsets are ABSOLUTE offsets into the EXE file

Usage:
    python scripts/extract_pck.py <exe> -o <out_dir> [-m <manifest.json>] [--dry-run]

Outputs a machine-readable manifest; validates md5 of every extracted file.
"""

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PCK_MAGIC_GD = b"GDPC"
HEADER_CANDIDATES = {1: [32, 84], 2: [160]}


def find_pck(data: bytes) -> dict:
    """Locate and parse the PCK header; returns dict or raises."""
    # Use known PE "pck" section if present, else scan for GDPC.
    offsets = []
    start = 0
    while True:
        idx = data.find(PCK_MAGIC_GD, start)
        if idx == -1 or len(offsets) >= 50:
            break
        offsets.append(idx)
        start = idx + 1

    for off in offsets:
        if off + 28 > len(data):
            continue
        magic, version = struct.unpack_from("<II", data, off)
        if magic != 0x43504447 or version not in HEADER_CANDIDATES:
            continue
        major, minor_, patch, flags = struct.unpack_from("<IIII", data, off + 8)
        file_base = struct.unpack_from("<Q", data, off + 24)[0]
        for hlen in HEADER_CANDIDATES[version]:
            cnt_off = off + hlen
            if cnt_off + 4 > len(data):
                continue
            cnt = struct.unpack_from("<I", data, cnt_off)[0]
            if not (100 < cnt < 100000):
                continue
            return {
                "pck_start": off, "version": version, "header_len": hlen,
                "godot_version": f"{major}.{minor_}.{patch}",
                "pack_flags": flags, "encrypted": bool(flags & 1),
                "file_base": file_base, "count": cnt, "count_offset": cnt_off,
            }
    raise RuntimeError("no self-consistent PCK header found")


def parse_entries(data: bytes, pck: dict) -> list:
    """Parse all directory entries; returns list of dicts."""
    entries = []
    p = pck["count_offset"] + 4
    for i in range(pck["count"]):
        if p + 4 > len(data):
            raise RuntimeError(f"truncated directory at entry {i}")
        plen = struct.unpack_from("<I", data, p)[0]
        if plen <= 0 or plen > 4096:
            raise RuntimeError(f"bad path_len {plen} at entry {i} (offset {p})")
        raw_path = data[p + 4:p + 4 + plen]
        p += 4 + plen + ((4 - plen % 4) % 4)
        if p + 24 > len(data):
            raise RuntimeError(f"truncated entry {i}")
        off64, size64 = struct.unpack_from("<QQ", data, p)
        entry_md5 = data[p + 16:p + 32]
        p += 32
        path = raw_path.rstrip(b"\x00").decode("utf-8", "replace")
        if off64 + size64 > len(data):
            raise RuntimeError(f"entry {i} {path!r}: offset+size out of file")
        entries.append({
            "index": i, "path": path, "offset": off64, "size": size64,
            "md5_expected": entry_md5.hex(),
        })
    return entries


def safe_relpath(path: str) -> Path:
    """Convert res://path to a safe relative Path under out_dir."""
    if path.startswith("res://"):
        rel = path[len("res://"):]
    else:
        rel = path
    p = Path(rel.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or p.drive:
        raise RuntimeError(f"unsafe path: {path!r}")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract embedded Godot PCK files")
    ap.add_argument("exe", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("-m", "--manifest", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = args.exe.read_bytes()
    pck = find_pck(data)
    entries = parse_entries(data, pck)
    print(f"PCK: version={pck['version']} godot={pck['godot_version']} "
          f"header_len={pck['header_len']} encrypted={pck['encrypted']} "
          f"files={len(entries)} start={pck['pck_start']}")

    seen = {}
    manifest = []
    errors = []
    for e in entries:
        rel = safe_relpath(e["path"])
        if rel in seen:
            errors.append(f"duplicate path: {e['path']}")
            continue
        seen[rel] = e
        chunk = data[e["offset"]:e["offset"] + e["size"]]
        md5 = hashlib.md5(chunk).hexdigest()
        sha256 = hashlib.sha256(chunk).hexdigest()
        ok = md5 == e["md5_expected"]
        if not ok:
            errors.append(f"md5 mismatch entry {e['index']} {e['path']}: "
                          f"expected {e['md5_expected']} got {md5}")
        manifest.append({
            "path": e["path"],
            "relpath": str(rel),
            "offset": e["offset"],
            "size": e["size"],
            "md5": md5,
            "sha256": sha256,
            "md5_match": ok,
        })
        if not args.dry_run:
            dst = args.out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(chunk)

    if args.manifest:
        report = {
            "tool": "scripts/extract_pck.py",
            "pck": {k: pck[k] for k in
                    ("pck_start", "version", "header_len", "godot_version",
                     "pack_flags", "encrypted", "file_base", "count")},
            "extracted": len(manifest),
            "errors": errors,
            "files": manifest,
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                 encoding="utf-8")
        print(f"manifest: {args.manifest}")

    print(f"extracted={len(manifest)} md5_mismatch={len(errors)}")
    if errors:
        for e in errors[:10]:
            print("  ERROR:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
