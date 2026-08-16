#!/usr/bin/env python3
"""Record the immutable original fingerprint and complete raw PCK inventory.

This command is read-only with respect to the game inputs.  It refuses to
record a baseline when the supplied executable does not match the expected
SHA-256, and writes the protocol-required baseline products as generated
evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_exe import detect_godot, parse_pe  # noqa: E402
from extract_pck import find_pck, parse_entries  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", type=Path, default=ROOT / "00_original/Mutagenic.exe")
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "01_baseline")
    args = ap.parse_args()

    exe = args.exe.resolve()
    if not exe.is_file():
        raise SystemExit(f"ERROR: original executable not found: {exe}")
    data = exe.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    expected = args.expected_sha256.lower()
    if actual != expected:
        raise SystemExit(f"ERROR: original SHA-256 mismatch: expected {expected}, got {actual}")

    pe = parse_pe(data)
    godot = detect_godot(data)
    pck = find_pck(data)
    entries = parse_entries(data, pck)
    paths = []
    for entry in entries:
        chunk = data[entry["offset"]:entry["offset"] + entry["size"]]
        paths.append({
            "path": entry["path"],
            "offset": entry["offset"],
            "size": entry["size"],
            "md5": hashlib.md5(chunk).hexdigest(),
            "sha256": hashlib.sha256(chunk).hexdigest(),
            "stored_md5": entry["md5_expected"],
            "md5_match": hashlib.md5(chunk).hexdigest() == entry["md5_expected"],
        })

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fingerprint = {
        "recorded_at": stamp,
        "source": str(exe),
        "file": {"size": len(data), "sha256": actual},
        "pe": pe,
        "godot": godot,
        "pck_inventory": {
            "start": pck["pck_start"],
            "version": pck["version"],
            "header_len": pck["header_len"],
            "godot_version": pck["godot_version"],
            "pack_flags": pck["pack_flags"],
            "file_base": pck["file_base"],
            "count": len(entries),
            "paths": paths,
        },
    }
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "game_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "pe.json").write_text(
        json.dumps({"recorded_at": stamp, "source": str(exe), "file": fingerprint["file"], "pe": pe},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "pck_manifest.json").write_text(
        json.dumps({"recorded_at": stamp, "source": str(exe), "file": fingerprint["file"],
                    "pck": fingerprint["pck_inventory"]}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    bad = [p["path"] for p in paths if not p["md5_match"]]
    print(f"original_sha256={actual}")
    print(f"pck_start={pck['pck_start']} pck_size={len(data) - pck['pck_start']} entries={len(entries)}")
    print(f"md5_valid={len(paths) - len(bad)}/{len(paths)}")
    if bad:
        print("bad_entries:")
        for path in bad[:20]:
            print(f"  {path}")
        return 1
    print(f"written={out / 'game_fingerprint.json'}")
    print(f"written={out / 'pe.json'}")
    print(f"written={out / 'pck_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
