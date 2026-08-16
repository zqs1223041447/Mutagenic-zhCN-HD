#!/usr/bin/env python3
"""Validate embedded PCK PE metadata, trailer, offsets, and entry hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", type=Path)
    ap.add_argument("--pck-start", type=int, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    data = args.exe.read_bytes()
    start = args.pck_start
    errors = []
    if data[:2] != b"MZ": errors.append("missing MZ")
    if data[start:start + 4] != b"GDPC": errors.append("missing PCK magic at expected start")
    if data[-4:] != b"GDPC": errors.append("missing PCK trailer magic")
    ds = struct.unpack_from("<Q", data, len(data) - 12)[0]
    expected_ds = len(data) - start - 12
    if ds != expected_ds: errors.append(f"tail ds {ds} != {expected_ds}")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0": errors.append("missing PE signature")
    coff = pe + 4
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    n_sections = struct.unpack_from("<H", data, coff + 2)[0]
    sec = coff + 20 + opt_size
    pck_section = None
    for i in range(n_sections):
        off = sec + i * 40
        name = data[off:off + 8].rstrip(b"\0").decode("ascii", "replace")
        if name == "pck":
            pck_section = {"raw_ptr": struct.unpack_from("<I", data, off + 20)[0], "raw_size": struct.unpack_from("<I", data, off + 16)[0]}
            break
    if not pck_section: errors.append("pck PE section missing")
    elif pck_section["raw_ptr"] != start or pck_section["raw_size"] != len(data) - start:
        errors.append(f"pck section metadata mismatch: {pck_section}")
    count = None; valid = 0; bad = []
    if data[start:start + 4] == b"GDPC":
        count = struct.unpack_from("<I", data, start + 84)[0]
        pos = start + 88
        for index in range(count):
            plen = struct.unpack_from("<I", data, pos)[0]
            raw = data[pos + 4:pos + 4 + plen]
            pos += 4 + plen + ((4 - plen % 4) % 4)
            offset, size = struct.unpack_from("<QQ", data, pos)
            stored = data[pos + 16:pos + 32]
            chunk = data[offset:offset + size]
            actual = hashlib.md5(chunk).digest()
            if offset < start or offset + size > len(data) or stored != actual:
                bad.append({"entry": index, "path": raw.rstrip(b"\0").decode("utf-8", "replace"), "offset": offset, "size": size, "stored": stored.hex(), "actual": actual.hex()})
            else:
                valid += 1
            pos += 32
        if count != 3744: errors.append(f"unexpected entry count: {count}")
    else:
        errors.append("cannot parse PCK directory")
    report = {"recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "exe": str(args.exe.resolve()), "size": len(data), "pck_start": start, "tail_ds": ds, "expected_ds": expected_ds, "pck_section": pck_section, "entry_count": count, "valid_entries": valid, "bad_entries": bad, "errors": errors, "verdict": "PASS" if not errors and not bad else "FAIL", "proves": "embedded PE/PCK structural consistency and entry checksums", "not_proven": "runtime behavior, gameplay, visual quality, persistence"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"entry_count": count, "valid_entries": valid, "errors": errors, "bad_entries": len(bad), "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
