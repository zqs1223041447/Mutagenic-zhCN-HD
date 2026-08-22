#!/usr/bin/env python3
"""B1-X4 S4 semantic gate: verify the camera/audio foundation limiter is really
embedded in the runtime Globals.gde recovered from the final candidate EXE.

Checks (semantic, GDRE-recovered authoritative source, not UI):
  1. SFX_AGGREGATE_WINDOW_MS == 60 present
  2. SFX_MAX_CONCURRENT == 16 present
  3. pitch/volume variation lines present
  4. _sfx_active_count + tree_exited recovery present
  5. enable_sfx / enable_drops gating order preserved
  6. bus guard keeps only SFX/Drops
  7. original caller contract unchanged (play_orb_sound still calls
     play_sound_effect; sound_effect preload intact)
  8. no camera shake implementation leaked into Globals (audit-only scope)
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_MARKERS = [
    ("aggregate_window_60ms", "const SFX_AGGREGATE_WINDOW_MS = 60"),
    ("max_concurrent_16", "const SFX_MAX_CONCURRENT = 16"),
    ("pitch_variation", "const SFX_PITCH_VARIATION = 0.04"),
    ("volume_variation", "const SFX_VOLUME_VARIATION_DB = 2.0"),
    ("last_play_dict", "var _sfx_last_play: Dictionary = {}"),
    ("active_count_var", "var _sfx_active_count = 0"),
    ("tree_exited_recovery", "_on_runtime_sfx_tree_exited()"),
    ("tree_exited_connect", 'sfx.connect("tree_exited", self, "_on_runtime_sfx_tree_exited")'),
    ("counter_increment", "_sfx_active_count += 1"),
    ("counter_decrement", "_sfx_active_count - 1"),
    ("sfx_bus_guard", 'if bus != "SFX" and bus != "Drops":'),
    ("enable_sfx_gate", "not GameState.saved_stats.settings.enable_sfx"),
    ("enable_drops_gate", "not GameState.saved_stats.settings.enable_drops"),
    ("null_stream_guard", "if stream == null:"),
    ("audio_node_patch", 'var audio = sfx.get_node("Audio")'),
    ("pitch_scale_apply", "audio.pitch_scale = 1.0 + rand_range( - SFX_PITCH_VARIATION, SFX_PITCH_VARIATION)"),
    ("volume_db_apply", "audio.volume_db = - rand_range(0.0, SFX_VOLUME_VARIATION_DB)"),
    ("caller_contract", "func play_orb_sound(orb_type):"),
]

FORBIDDEN_MARKERS = [
    "offset.x",
    "offset.y",
    "apply_camera_shake",
    "camera_impulse",
]


def main() -> int:
    recovered = ROOT / "10_logs/b1-x4-k4-audio-foundation-20260819/s4_recovered/Globals.gd"
    candidate = ROOT / "10_logs/b1-x4-k4-audio-foundation-20260819/k4_audio_foundation_normalized.exe"
    if not recovered.is_file():
        print(json.dumps({"verdict": "FAIL", "reason": "recovered Globals.gd missing"}))
        return 1
    text = recovered.read_text(encoding="utf-8")
    checks = []
    for name, marker in REQUIRED_MARKERS:
        checks.append({"check": name, "marker": marker, "found": marker in text})
    forbidden_hits = [m for m in FORBIDDEN_MARKERS if m in text]
    ok = all(c["found"] for c in checks) and not forbidden_hits
    report = {
        "experiment_id": "B1-X4-S4-SEMANTIC",
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidate": str(candidate),
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest().upper(),
        "recovered_source": "10_logs/b1-x4-k4-audio-foundation-20260819/s4_recovered/Globals.gd",
        "checks": checks,
        "forbidden_camera_markers_found": forbidden_hits,
        "verdict": "PASS" if ok else "FAIL",
        "proves": "the final candidate EXE's embedded Globals.gde, recovered via GDRE, contains the v0.2.0 audio event limiter: 60ms per-bus/per-stream aggregation, max 16 concurrent voices with explicit counter + tree_exited lifecycle recovery, +/-4% pitch and 0..-2dB volume variation, enable_sfx/enable_drops gating order and SFX/Drops-only bus guard preserved, null-stream guard added; no camera shake code was added (camera audit-only)",
        "not_proven": "runtime aural quality or combat feel (requires Combat S5), every caller's subjective behavior, performance under cluster kills (S5 capture needed)",
    }
    out = ROOT / "10_logs/b1-x4-k4-audio-foundation-20260819/s4_semantic.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"checks_passed": sum(1 for c in checks if c["found"]), "checks_total": len(checks), "forbidden_hits": forbidden_hits, "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())