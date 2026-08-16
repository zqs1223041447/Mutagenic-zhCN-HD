#!/usr/bin/env python3
"""Fail-closed workaround for GDRE's zero-byte PCK MD5 header bug.

GDRE v2.6.4 emits an all-zero MD5 for some zero-byte entries. Godot's PCK
reader expects the canonical MD5 of the empty byte string. This stage patches
only that exact known case and rejects every other mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path


EMPTY_MD5 = hashlib.md5(b"").digest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    src = args.input.resolve()
    dst = args.output.resolve()
    if not src.is_file():
        raise SystemExit(f"ERROR: PCK not found: {src}")
    if dst.exists():
        raise SystemExit(f"ERROR: refusing to overwrite PCK: {dst}")
    data = bytearray(src.read_bytes())
    if data[:4] != b"GDPC":
        raise SystemExit("ERROR: PCK does not start with GDPC")
    version = struct.unpack_from("<I", data, 4)[0]
    if version != 1:
        raise SystemExit(f"ERROR: unsupported PCK version: {version}")
    header_len = 84
    count = struct.unpack_from("<I", data, header_len)[0]
    pos = header_len + 4
    patched = []
    rejected = []
    valid = 0
    for index in range(count):
        plen = struct.unpack_from("<I", data, pos)[0]
        raw = bytes(data[pos + 4:pos + 4 + plen])
        pos += 4 + plen + ((4 - plen % 4) % 4)
        offset, size = struct.unpack_from("<QQ", data, pos)
        md5_pos = pos + 16
        stored = bytes(data[md5_pos:md5_pos + 16])
        chunk = bytes(data[offset:offset + size])
        actual = hashlib.md5(chunk).digest()
        path = raw.rstrip(b"\0").decode("utf-8", "replace")
        if stored == actual:
            valid += 1
        elif size == 0 and stored == b"\0" * 16 and actual == EMPTY_MD5:
            data[md5_pos:md5_pos + 16] = actual
            patched.append({"entry": index, "path": path, "size": size, "from": stored.hex(), "to": actual.hex()})
        else:
            rejected.append({"entry": index, "path": path, "size": size, "stored": stored.hex(), "actual": actual.hex()})
        pos += 32
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input": str(src),
        "output": str(dst),
        "entries": count,
        "already_valid": valid,
        "patched_known_zero_byte_md5": patched,
        "rejected_mismatches": rejected,
        "verdict": "PASS" if not rejected else "FAIL",
        "proves": "only the known GDRE zero-byte MD5 defect was normalized",
        "not_proven": "PCK embedding, runtime behavior, or semantic correctness of content",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if rejected:
        print(json.dumps({"patched": len(patched), "rejected": rejected, "verdict": "FAIL"}, ensure_ascii=False))
        return 1
    dst.write_bytes(data)
    print(json.dumps({"entries": count, "already_valid": valid, "patched": len(patched), "verdict": "PASS"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
