#!/usr/bin/env python3
"""Verify a Godot 3 STEX asset replacement preserves runtime format and dimensions."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


def read_stex(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 28 or data[:4] != b"GDST":
        raise ValueError(f"not a Godot STEX file: {path}")
    return {
        "path": str(path.resolve()),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": data[:4].decode("ascii"),
        "width": struct.unpack_from("<I", data, 4)[0],
        "height": struct.unpack_from("<I", data, 8)[0],
        "flags": struct.unpack_from("<I", data, 12)[0],
        "format_marker": data[28:36].decode("ascii", "replace") if len(data) >= 36 else "",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("replacement", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    errors: list[str] = []
    before = read_stex(args.before.resolve())
    after = read_stex(args.after.resolve())
    replacement = read_stex(args.replacement.resolve())
    for key in ("width", "height", "flags", "format_marker"):
        if after[key] != replacement[key]:
            errors.append(f"after/replacement {key} differs: {after[key]!r} != {replacement[key]!r}")
        if before[key] != after[key]:
            errors.append(f"target {key} changed: {before[key]!r} -> {after[key]!r}")
    if before["sha256"] == after["sha256"]:
        errors.append("target STEX bytes did not change")
    if after["sha256"] != replacement["sha256"]:
        errors.append("target after hash does not equal declared replacement hash")
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "before": before,
        "after": after,
        "replacement": replacement,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "proves": "the runtime asset bytes changed while preserving STEX format, dimensions, flags, and marker",
        "not_proven": "source-art authoring quality, Godot reimport equivalence, or visual quality beyond runtime screenshot",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"errors": errors, "before": before, "after": after, "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
