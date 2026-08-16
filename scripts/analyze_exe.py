#!/usr/bin/env python3
"""Baseline analyzer for Godot Windows executables.

Parses PE structure (sections, subsystem, timestamp) and detects
Godot / embedded PCK features in the binary.

Usage:
    python scripts/analyze_exe.py <exe_path> [-o <output.json>]

Outputs JSON to stdout or the given file. Pure stdlib, no dependencies.
"""

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PCK_MAGIC_GD = b"GDPC"          # Godot 3.x/4.x PCK v1/v2
PCK_MAGIC_GPK = b"GPK"          # very old Godot pack format
GODOT_MARKERS = [b"Godot Engine", b"godot", b"Godot"]


def parse_pe(data: bytes) -> dict:
    """Parse minimal PE header info: machine, sections, subsystem, timestamp."""
    if len(data) < 0x40:
        return {"error": "file too small for DOS header"}
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        return {"error": "no PE signature", "e_lfanew": e_lfanew}

    coff = e_lfanew + 4
    machine, n_sections, timestamp, _sym_ptr, _sym_count, opt_size, chars = \
        struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    is_pe32plus = magic == 0x20B
    subsystem = struct.unpack_from("<H", data, opt + 68)[0] if len(data) >= opt + 70 else None

    sections = []
    sec_off = opt + opt_size
    for i in range(n_sections):
        off = sec_off + i * 40
        name = data[off:off + 8].rstrip(b"\0").decode("latin-1", "replace")
        _name, vsize, vaddr, raw_size, raw_ptr, _reloc, _lnno, _nrel, _nln, s_chars = \
            struct.unpack_from("<8sIIIIIIHHI", data, off)
        sections.append({
            "name": name,
            "virtual_size": vsize,
            "virtual_address": vaddr,
            "raw_size": raw_size,
            "raw_ptr": raw_ptr,
            "characteristics": hex(s_chars),
        })

    return {
        "e_lfanew": e_lfanew,
        "machine": hex(machine),
        "machine_name": {
            0x14C: "i386", 0x8664: "x86-64", 0xAA64: "ARM64",
        }.get(machine, "unknown"),
        "number_of_sections": n_sections,
        "timestamp": timestamp,
        "timestamp_utc": _pe_timestamp(timestamp),
        "optional_header_magic": hex(magic),
        "pe32plus": is_pe32plus,
        "subsystem": subsystem,
        "subsystem_name": {
            2: "GUI", 3: "CUI",
        }.get(subsystem, "unknown"),
        "sections": sections,
    }


def _pe_timestamp(ts: int) -> str:
    import datetime
    try:
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OSError, ValueError, OverflowError):
        return "invalid"


def find_all(data: bytes, needle: bytes, limit: int = 20) -> list:
    """Return up to `limit` offsets of needle in data (0-padded search)."""
    out = []
    start = 0
    while True:
        idx = data.find(needle, start)
        if idx == -1 or len(out) >= limit:
            break
        out.append(idx)
        start = idx + 1
    return out


def parse_pck_at(data: bytes, off: int) -> dict:
    """Try to parse a Godot PCK header + directory at the given offset.

    Supports PCK v1 (32B header), v1+extra-zero-padding, and v2 (160B header).
    Returns a self-consistent report, or None if parsing fails validation.
    """
    if data[off:off + 4] != PCK_MAGIC_GD:
        return None
    if off + 28 > len(data):
        return None
    result = {"pck_start": off}
    magic, version = struct.unpack_from("<II", data, off)
    result["version"] = version
    if version == 1:
        result["format"] = "v1"
        header_candidates = [32, 84]
    elif version == 2:
        result["format"] = "v2"
        header_candidates = [160]
    else:
        return None
    major, minor_, patch, flags = struct.unpack_from("<IIII", data, off + 8)
    file_base = struct.unpack_from("<Q", data, off + 24)[0]
    result["godot_version"] = f"{major}.{minor_}.{patch}"
    result["pack_flags"] = hex(flags)
    result["encrypted"] = bool(flags & 1)
    result["file_base"] = file_base

    for hlen in header_candidates:
        cnt_off = off + hlen
        if cnt_off + 4 > len(data):
            continue
        cnt = struct.unpack_from("<I", data, cnt_off)[0]
        if not (100 < cnt < 100000):
            continue
        # Try to parse entries; validate first and last path look sane.
        p = cnt_off + 4
        entries = []
        ok = True
        for i in range(min(cnt, 5000)):
            if p + 4 > len(data):
                ok = False
                break
            plen = struct.unpack_from("<I", data, p)[0]
            if plen <= 0 or plen > 4096:
                ok = False
                break
            path = data[p + 4:p + 4 + plen]
            p += 4 + plen + ((4 - plen % 4) % 4)
            if p + 24 > len(data):
                ok = False
                break
            off64, size64 = struct.unpack_from("<QQ", data, p)
            p += 32  # offset(8) + size(8) + md5(16)
            entries.append({"path": path, "offset": off64, "size": size64})
            if not ok:
                break
        if not ok or len(entries) < 10:
            continue
        # Validate offsets lie inside the file.
        if all(0 <= e["offset"] <= len(data) and e["offset"] + e["size"] <= len(data)
               for e in (entries[0], entries[-1])):
            result["header_len"] = hlen
            result["file_count"] = cnt
            result["first_entry"] = {
                "path": entries[0]["path"].decode("utf-8", "replace"),
                "offset": entries[0]["offset"], "size": entries[0]["size"],
            }
            result["last_entry"] = {
                "path": entries[-1]["path"].decode("utf-8", "replace"),
                "offset": entries[-1]["offset"], "size": entries[-1]["size"],
            }
            result["pck_data_end"] = max(e["offset"] + e["size"] for e in entries)
            return result
    return result


def detect_godot(data: bytes) -> dict:
    """Detect Godot engine presence and PCK embedding."""
    result = {
        "engine_strings": [],
        "version_strings": [],
        "gdpc_offsets": [],
        "gpk_offsets": [],
        "pck_at_tail": None,
        "pck_size": None,
        "pck": None,
    }
    for marker in (b"Godot Engine", b"Godot"):
        for off in find_all(data, marker, limit=5):
            result["engine_strings"].append({
                "offset": off,
                "snippet": data[off:off + 96].decode("utf-8", "replace"),
            })
    # Godot version strings like "4.2.1.stable.official" or "3.5.2.stable"
    for off in find_all(data, b".stable.", limit=10):
        # walk back to digits
        s = off
        while s > 0 and (data[s - 1:s] in (b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9", b".")):
            s -= 1
        snippet = data[s:off + 32].decode("utf-8", "replace")
        result["version_strings"].append({"offset": s, "snippet": snippet})

    result["gdpc_offsets"] = find_all(data, PCK_MAGIC_GD, limit=20)
    result["gpk_offsets"] = find_all(data, PCK_MAGIC_GPK, limit=10)

    # PCK at tail: last bytes should be the PCK; magic appears at tail-4
    if len(data) >= 4 and data[-4:] == PCK_MAGIC_GD:
        result["pck_at_tail"] = "gdpc"
        # tail marker layout (custom build): [.. 4B 0][file_base u64][magic]
        tail_fb = struct.unpack_from("<Q", data, len(data) - 12)[0]
        result["tail_file_base"] = tail_fb

    # Find the real PCK header: the first GDPC offset that parses self-consistently
    for off in result["gdpc_offsets"]:
        parsed = parse_pck_at(data, off)
        if parsed and "file_count" in parsed:
            result["pck"] = parsed
            result["pck_size"] = len(data) - parsed["pck_start"]
            break
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Baseline PE/Godot/PCK analyzer")
    ap.add_argument("exe", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    data = args.exe.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()

    report = {
        "tool": "scripts/analyze_exe.py",
        "analyzed_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "file": {
            "path": str(args.exe.resolve()),
            "size": len(data),
            "sha256": sha256,
        },
        "pe": parse_pe(data),
        "godot": detect_godot(data),
    }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"written: {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
