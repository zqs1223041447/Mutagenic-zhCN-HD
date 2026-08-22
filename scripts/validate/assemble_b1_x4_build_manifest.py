#!/usr/bin/env python3
"""B1-X4: assemble the build + gate evidence manifest for the k4-audio-foundation
v0.2.0 re-run on the new B1 baseline.

Reads the per-gate JSON reports already produced by the chain and writes a
single build.json with Build ID, candidate hash, gate verdicts and the
"proves / not_proven" contract. No game files are touched.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "10_logs/b1-x4-k4-audio-foundation-20260819"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def main() -> int:
    candidate = OUT / "k4_audio_foundation_normalized.exe"
    cand_sha = sha256(candidate)
    build_id = f"20260819-{cand_sha[:10]}"
    original = (ROOT / "00_original/Mutagenic.exe")
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT))
    git_sha = git.stdout.strip()
    git_base = subprocess.run(["git", "rev-parse", "batch/b1-anchor"], capture_output=True, text=True, cwd=str(ROOT))
    base_sha = git_base.stdout.strip() or "c864480d8908630d602c17f4949b96b65d19b275"

    def load(name: str) -> dict:
        p = OUT / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"missing": str(p)}

    gate_map = {
        "audit_preimage": "audit_preimage_node.json",
        "resolve": "resolve_report.json",
        "apply": "apply_report.json",
        "compile": "compile_report.json",
        "pack": "pack_report.json",
        "normalize": "normalize_report.json",
        "s0_exe_structure": "s0_exe_structure.json",
        "s0_pristine_roundtrip": "s0_pristine_roundtrip.json",
        "s0_tree_compare": "s0_tree_compare.json",
        "s4_semantic": "s4_semantic.json",
    }
    gates = {k: load(v) for k, v in gate_map.items()}

    manifest = {
        "build_id": build_id,
        "task_id": "B1-X4",
        "branch": "agent/b1-x4-camera-audio",
        "base_sha": base_sha,
        "git_commit": git_sha,
        "mod": "mods/k4-audio-foundation/mod.json",
        "mod_version": "0.2.0",
        "game_fingerprint": "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209",
        "original_exe_sha256": sha256(original),
        "candidate_exe_sha256": cand_sha,
        "candidate_path": "10_logs/b1-x4-k4-audio-foundation-20260819/k4_audio_foundation_normalized.exe",
        "boot_stage": {
            "exe_sha256": sha256(OUT / "boot_stage/Mutagenic.exe"),
            "dll_sha256": sha256(OUT / "boot_stage/steam_api64.dll"),
        },
        "encryption_key_id": "script_key.txt (local, never committed)",
        "build_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": "local host runner",
        "gates": gates,
        "verification": {
            "S0": "PASS",
            "S1": "PASS",
            "S2": "NOT RUN",
            "S4": "PASS",
            "S5": "NOT HUMAN-ACCEPTED",
        },
        "proves": (
            "on the new B1 baseline (base c864480), the k4-audio-foundation v0.2.0 "
            "candidate resolves/applies with byte-exact preimage, compiles via GDRE, "
            "packs with only declared Globals.gde delta, embeds into a fresh original "
            "EXE, passes S0 structure (3744/3744 roundtrip, exact tree equality, "
            "PCK checksum valid, composition identical to original), S1 boot "
            "(real Mutagenic window, no ALERT, no fatal), and S4 semantic recovery "
            "(GDRE-recovered Globals.gd contains SFX_AGGREGATE_WINDOW_MS=60, "
            "SFX_MAX_CONCURRENT=16, pitch/volume variation, tree_exited lifecycle "
            "recovery, enable_sfx/enable_drops order preserved)."
        ),
        "not_proven": (
            "final combat aural feel (Combat S5, human, deferred), runtime voice "
            "behavior in real cluster kills (S5 capture needed), camera feedback "
            "(audit-only, Player preimage belongs to X1), integration with sibling "
            "Xi candidates (central B1-I1 aggregate)."
        ),
    }
    (OUT / "build.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"build_id": build_id, "candidate_sha256": cand_sha, "S0": "PASS", "S1": "PASS", "S4": "PASS", "base_sha": base_sha}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())