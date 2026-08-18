#!/usr/bin/env python3
"""Verify a Godot 3 STEX asset replacement preserves runtime format and dimensions.

Extended asset contract (ora-E / D1 option A1 + C2, PHASE6_PIXEL_ASSET_SPEC §3.3):
  - width/height: after == replacement AND after == declared target dimensions
    (--expected-width/--expected-height).  Up-resolution replacements such as
    16x16 -> 32x32 are allowed only when they match the declared target.
  - flags / bytes16-19 / format / format_marker: before == after (the runtime
    format contract is preserved; dimension fields are the only changeable ones).
  - sha256 double binding: target bytes changed (before != after) and
    after == replacement.
  - C2 self-consistency: data_size == payload length, payload is a pure VP8L
    chunk (no VP8X), and VP8L internal w-1/h-1 == header width/height.
"""

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
    width, height, flags = struct.unpack_from("<III", data, 4)
    format_id, data_size = struct.unpack_from("<II", data, 20)
    payload = data[28:]
    vp8l = None
    if len(payload) >= 29 and payload[4:8] == b"RIFF" and payload[16:20] == b"VP8L":
        bits = struct.unpack_from("<I", payload, 25)[0]
        vp8l = {
            "width_minus_1": bits & 0x3FFF,
            "height_minus_1": (bits >> 14) & 0x3FFF,
            "alpha_bit": bool(bits & (1 << 28)),
        }
    return {
        "path": str(path.resolve()),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": data[:4].decode("ascii"),
        "width": width,
        "height": height,
        "flags": flags,
        "bytes16_19": data[16:20].hex(),
        "format": format_id,
        "data_size": data_size,
        "payload_len": len(payload),
        "format_marker": payload[:8].decode("ascii", "replace") if len(payload) >= 8 else "",
        "chunk": payload[16:20].decode("ascii", "replace") if len(payload) >= 20 else "",
        "vp8l": vp8l,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("replacement", type=Path)
    ap.add_argument("--expected-width", type=int, required=True)
    ap.add_argument("--expected-height", type=int, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    errors: list[str] = []
    before = read_stex(args.before.resolve())
    after = read_stex(args.after.resolve())
    replacement = read_stex(args.replacement.resolve())
    for key in ("width", "height"):
        if after[key] != replacement[key]:
            errors.append(f"after/replacement {key} differs: {after[key]!r} != {replacement[key]!r}")
    expected = {"width": args.expected_width, "height": args.expected_height}
    for key in ("width", "height"):
        if after[key] != expected[key]:
            errors.append(f"target {key} does not match declared target: {after[key]!r} != {expected[key]!r}")
    for key in ("flags", "bytes16_19", "format", "format_marker"):
        if after[key] != replacement[key]:
            errors.append(f"after/replacement {key} differs: {after[key]!r} != {replacement[key]!r}")
        if before[key] != after[key]:
            errors.append(f"target {key} changed: {before[key]!r} -> {after[key]!r}")
    if before["sha256"] == after["sha256"]:
        errors.append("target STEX bytes did not change")
    if after["sha256"] != replacement["sha256"]:
        errors.append("target after hash does not equal declared replacement hash")
    for label, stex in (("before", before), ("after", after), ("replacement", replacement)):
        if stex["data_size"] != stex["payload_len"]:
            errors.append(f"{label} data_size {stex['data_size']} != payload length {stex['payload_len']}")
        if stex["chunk"] != "VP8L":
            errors.append(f"{label} payload chunk is {stex['chunk']!r}, expected pure VP8L (no VP8X)")
        if stex["vp8l"] is None:
            errors.append(f"{label} VP8L header not parseable")
        else:
            if stex["vp8l"]["width_minus_1"] != stex["width"] - 1:
                errors.append(
                    f"{label} VP8L internal width-1 {stex['vp8l']['width_minus_1']} != header width-1 {stex['width'] - 1}"
                )
            if stex["vp8l"]["height_minus_1"] != stex["height"] - 1:
                errors.append(
                    f"{label} VP8L internal height-1 {stex['vp8l']['height_minus_1']} != header height-1 {stex['height'] - 1}"
                )
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected_dimensions": {"width": args.expected_width, "height": args.expected_height},
        "before": before,
        "after": after,
        "replacement": replacement,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "proves": "the runtime asset bytes changed while preserving the STEX format contract (flags/bytes16-19/format/WebP marker unchanged), matching the declared target dimensions, with self-consistent data_size and VP8L payload dimensions",
        "not_proven": "source-art authoring quality, Godot reimport equivalence, or visual quality beyond runtime screenshot",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"errors": errors, "before": before, "after": after, "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())