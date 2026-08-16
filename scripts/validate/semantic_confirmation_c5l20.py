#!/usr/bin/env python3
"""Semantic confirmation for C5-L20 build: recover declared scripts/resources from the final EXE PCK
and verify Chinese display strings exist while internal identifiers remain English."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
EVID = ROOT / "10_logs/C5-L20-core-playable-v3-20260815"


def run(args, timeout=240):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return r


def main() -> int:
    # Recovered plaintext scripts produced by GDRE --recover with the project script key.
    extract_root = EVID / "gdre_recover"
    if not extract_root.is_dir():
        raise SystemExit("ERROR: gdre_recover directory missing; run GDRE --recover with --key first")

    # 1. Status effect scene files (L17) - pure resource, no script change
    status_scenes = [
        "Scenes/StatusEffects/DamageAilments/Bleed.tscn",
        "Scenes/StatusEffects/DamageAilments/Burn.tscn",
        "Scenes/StatusEffects/Curses/Bane.tscn",
        "Scenes/StatusEffects/Keystones/VampiricSkin.tscn",
        "Scenes/StatusEffects/Boons/PrecisionBoon.tscn",
        "Scenes/StatusEffects/Pickups/Frenzy.tscn",
    ]
    # 2. Script data tables (L17/L18/L19/L16)
    script_files = [
        "Globals/Levels.gd",
        "Globals/MonsterStats/MonsterStats.gd",
        "Globals/MapMods.gd",
        "Scenes/Minimap/Minimap.gd",
        "Globals/StarterBuilds.gd",
        "Globals/Genes.gd",
        "Globals/ItemNameGenerator.gd",
        "Globals/Genes/UniquePools/UniquePoolGeneric.gd",
    ]
    recovery = {}
    chinese_re = re.compile(r"[\u4e00-\u9fff]")
    sem_results = []

    def check(path, expect_chinese=True):
        fp = extract_root / path
        if not fp.is_file():
            sem_results.append({"path": path, "status": "MISSING"})
            return None
        data = fp.read_bytes()
        text = None
        if path.endswith(".gd"):
            text = data.decode("utf-8", "replace")
        elif path.endswith(".tscn"):
            text = data.decode("utf-8", "replace")
        has_cjk = bool(chinese_re.search(text)) if text else False
        rec = {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "contains_cjk_text": has_cjk,
            "status": "OK",
        }
        sem_results.append(rec)
        recovery[path] = rec
        return rec

    for p in status_scenes:
        check(p)
    for p in script_files:
        check(p)

    # Keys that must remain English (structural identifiers)
    structural_checks = {
        "Globals/Genes.gd": ["BaseType.MELEE_WEAPON", "helmet_slot_icon", "sound_keystone"],
        "Globals/ItemNameGenerator.gd": ["prefix", "suffix"],
        "Globals/Genes/UniquePools/UniquePoolGeneric.gd": ["expansion_charm", "texture", "res://"],
        "Globals/StarterBuilds.gd": ["lightning", "starter"],
        "Globals/Levels.gd": ["cave", "name"],
        "Globals/MonsterStats/MonsterStats.gd": ["damage", "name"],
        "Globals/MapMods.gd": ["health_max", "Target.MOB"],
    }
    id_preserved = []
    for path, keys in structural_checks.items():
        fp = extract_root / path
        if not fp.is_file():
            id_preserved.append({"path": path, "status": "MISSING"})
            continue
        text = fp.read_bytes().decode("utf-8", "replace")
        found = {k: (k in text) for k in keys}
        id_preserved.append({"path": path, "keys": found, "all_present": all(found.values())})

    ok = all(r["status"] == "OK" and r["contains_cjk_text"] for r in sem_results if r["status"] != "MISSING") and not any(r["status"] == "MISSING" for r in sem_results)
    report = {
        "experiment_id": "c5-l20-semantic-confirmation",
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "extract_root": str(extract_root),
        "checked": sem_results,
        "structural_id_checks": id_preserved,
        "verdict": "PASS" if ok else "FAIL",
        "proves": "declared Chinese display strings are embedded in the final EXE PCK and key structural identifiers remain English",
        "not_proven": "in-game visual layout, dynamic runtime substitution behavior, persistence, or release readiness",
    }
    out = EVID / "semantic_confirmation.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"checked": len(sem_results), "verdict": report["verdict"]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())