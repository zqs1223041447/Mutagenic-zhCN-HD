#!/usr/bin/env python3
"""Phase A Freeze: generate workspace-pre-git SHA256 inventory.

Records key assets (path, size, sha256, classification, immutable flag) so the
workspace has a defined freeze point before any governance/cleanup/git work.

WRITE-ONLY to manifests/provenance/; reads everywhere else. Never modifies inputs.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

# (path, classification, immutable)
TARGETS = [
    ("00_original/Mutagenic.exe", "immutable-provenance", True),
    ("01_baseline/game_fingerprint.json", "immutable-provenance", True),
    ("03_raw", "immutable-provenance", True),        # directory -> count + total
    ("04_recovered", "immutable-provenance", True),
    ("manifests/recovered_clean_manifest.json", "immutable-provenance", True),
    ("manifests/raw_manifest.json", "immutable-provenance", True),
    ("manifests/script_key.txt", "local-secret", True),  # hash only, never content
    ("tools.lock.json", "source-of-truth", False),
    ("status.json", "source-of-truth", False),
    ("10_logs/status.json", "source-of-truth", False),
    ("09_output/Mutagenic_zhCN_MOD_Handoff_20260816.zip", "accepted-release", True),
    ("09_output/zh_CN_Core_Playable_v81", "accepted-release", True),  # dir
    ("Mutagenic.exe", "root-runtime-copy", False),
    ("steam_api64.dll", "root-runtime-copy", False),
]

def scan_dir(d: Path) -> dict:
    files = [p for p in d.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    return {"file_count": len(files), "total_bytes": total}

inventory = []
for rel, cls, immutable in TARGETS:
    p = ROOT / rel
    entry = {"path": rel, "classification": cls, "immutable": immutable}
    if p.is_dir():
        entry.update(scan_dir(p))
        entry["sha256"] = None
    elif p.is_file():
        entry["size"] = p.stat().st_size
        entry["sha256"] = sha256(p)
    else:
        entry["error"] = "MISSING"
    inventory.append(entry)
    print(f"{entry['path']}: {'OK' if 'error' not in entry else 'MISSING'}")

out = {
    "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "workspace_root": str(ROOT),
    "purpose": "pre-git freeze snapshot; key assets SHA256 before governance/cleanup/git",
    "entries": inventory,
}
out_dir = ROOT / "manifests/provenance"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "workspace-pre-git-20260816.json"
out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"\nWROTE {out_path}")
print(f"entries: {len(inventory)}")
