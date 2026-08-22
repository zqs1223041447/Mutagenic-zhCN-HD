#!/usr/bin/env python3
"""B1-X4 audit: verify k4-audio-foundation mod.json patches byte-exactly
against the immutable 04_recovered/Globals/Globals.gd preimage and confirm
the SoundEffect.tscn node structure used by sfx.get_node("Audio").

Read-only audit; writes only the audit JSON report.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GLD = ROOT / "04_recovered/Globals/Globals.gd"
TSN = ROOT / "04_recovered/Scenes/SoundEffect.tscn"
MOD = ROOT / "mods/k4-audio-foundation/mod.json"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    gd = GLD.read_bytes()
    gd_sha = sha256_bytes(gd)
    mod = json.loads(MOD.read_text(encoding="utf-8"))
    ts = TSN.read_text(encoding="utf-8")

    results = []
    ok = True
    for patch in mod.get("patches", []):
        old = patch["old_text"].encode("utf-8")
        count = gd.count(old)
        pre_ok = patch["preimage_sha256"].lower() == gd_sha.lower()
        occ_ok = count == patch.get("expected_occurrences", 1)
        row = {
            "path": patch["path"],
            "unit_id": patch["unit_id"],
            "old_text_bytes": len(old),
            "occurrences_in_preimage": count,
            "expected_occurrences": patch.get("expected_occurrences", 1),
            "preimage_matches_file_sha256": pre_ok,
            "occurrence_ok": occ_ok,
        }
        results.append(row)
        ok = ok and pre_ok and occ_ok

    # Node structure: root "SoundEffect" (Node2D) with direct child "Audio"
    lines = ts.splitlines()
    nodes = [ln for ln in lines if ln.startswith("[node ")]
    root_line = nodes[0] if nodes else ""
    has_audio_child = any('name="Audio"' in ln and 'parent="."' in ln for ln in lines)
    node_check = {
        "scene": "res://Scenes/SoundEffect.tscn",
        "root_line": root_line,
        "direct_child_audio": has_audio_child,
        "sfx_get_node_Audio_valid": has_audio_child,
    }
    ok = ok and has_audio_child

    report = {
        "experiment_id": "B1-X4-AUDIT-preimage-and-node-structure",
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mod": "mods/k4-audio-foundation/mod.json",
        "mod_version": mod.get("version"),
        "preimage_file": "04_recovered/Globals/Globals.gd",
        "preimage_sha256": gd_sha.upper(),
        "patches": results,
        "sound_effect_scene": node_check,
        "verdict": "PASS" if ok else "FAIL",
        "proves": "both patch old_text blocks exist byte-exactly with declared occurrence count in the immutable preimage; SoundEffect.tscn has an 'Audio' AudioStreamPlayer direct child so sfx.get_node('Audio') is a real path",
        "not_proven": "compile success, runtime effect, packaging integrity",
    }
    out = ROOT / "10_logs/b1-x4-k4-audio-foundation-20260819"
    out.mkdir(parents=True, exist_ok=True)
    report_file = out / "audit_preimage_node.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"preimage_sha256": gd_sha.upper(), "patches": results, "node_check": node_check, "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())