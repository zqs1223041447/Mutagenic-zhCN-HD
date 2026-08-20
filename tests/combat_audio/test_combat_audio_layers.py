#!/usr/bin/env python3
"""B2-X6 combat audio layers self-test (policy model, no game exec).

Three layers of assurance, all against repo files (read-only on
04_recovered / mods / scripts):
  1. Patch mechanics: the 5 X6 CODE_PATCHes apply cleanly over pristine
     files after the dependency chain (same occurrence walk as
     scripts/patch/apply_mod.py).
  2. Structure: applied output contains the drain, layer mapping, windows,
     cluster gate and single k4 funnel.
  3. Behavior: a pure-python transcription of the layer policy, fed with
     the constants extracted from the applied Globals.gd, is exercised over
     synthetic event timelines (machine-gun hits, crit bursts, kill clusters,
     DoT ticks) and must satisfy the audio-layer contract.

This is a policy-model test: it does not execute GDScript and does not
prove runtime feel.  Run from any repo path:
    python tests/combat_audio/test_combat_audio_layers.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except subprocess.CalledProcessError:
        return Path(__file__).resolve().parents[2]


STATS_REL = "Scenes/Stats.gd"
GLOBALS_REL = "Globals/Globals.gd"
STATS_PREIMAGE = "C187245E4F475E0928252610BB9D6D27FCB4A23C68754B4409DF5A6EB9997234"
GLOBALS_PREIMAGE = "C1778CB8549B2A0EC15F50C010AFF294D6A3DF94B1A2954EBC7F2190F65942DD"
CHAIN_IDS = ["feat-tce", "feat-tce-context", "b2-x1-combat-event-spine", "k4-audio-foundation"]


def apply_chain(root: Path, pristine: dict[str, str]) -> dict[str, str]:
    """Same walk as apply_mod.py: preflight vs pristine, working count, replace all."""
    working = dict(pristine)
    ids = CHAIN_IDS + ["b2-x6-combat-audio-layers"]
    for mid in ids:
        mod = json.loads((root / "mods" / mid / "mod.json").read_text(encoding="utf-8"))
        for rel in (STATS_REL, GLOBALS_REL):
            group = [p for p in mod.get("patches", []) if p.get("path") == rel]
            if not group:
                continue
            pre = STATS_PREIMAGE if rel == STATS_REL else GLOBALS_PREIMAGE
            for p in group:
                assert p["preimage_sha256"].lower() == pre.lower(), (mid, rel, "preimage")
                assert pristine[rel].count(p["old_text"]) == p.get("expected_occurrences", 1), \
                    (mid, rel, "pristine occurrence")
            for p in group:
                expected = p.get("expected_occurrences", 1)
                assert working[rel].count(p["old_text"]) == expected, (mid, rel, "working occurrence")
                working[rel] = working[rel].replace(p["old_text"], p["new_text"])
    return working


def extract_int(src: str, name: str) -> int:
    m = re.search(re.escape(name) + r"\s*=\s*(\d+)", src)
    assert m, f"constant not found: {name}"
    return int(m.group(1))


class LayerPolicy:
    """Transcription of the Globals.gd policy (play_combat_event + helpers)."""

    def __init__(self, globals_src: str) -> None:
        self.windows = {
            "light": extract_int(globals_src, "COMBAT_LAYER_LIGHT_WINDOW_MS"),
            "heavy": extract_int(globals_src, "COMBAT_LAYER_HEAVY_WINDOW_MS"),
            "kill": extract_int(globals_src, "COMBAT_LAYER_KILL_WINDOW_MS"),
        }
        self.threshold = extract_int(globals_src, "COMBAT_KILL_CLUSTER_THRESHOLD")
        self._last_played: dict[str, int] = {}
        self._cluster_start = 0
        self._cluster_count = 0

    def layer_for(self, event_class: str) -> str:
        if event_class == "crit":
            return "heavy"
        if event_class == "kill":
            return "kill"
        return "light"

    def _allow_kill_cluster(self, now: int) -> bool:
        if now - self._cluster_start > self.windows["kill"]:
            self._cluster_start = now
            self._cluster_count = 0
        self._cluster_count += 1
        if self._cluster_count > self.threshold:
            return False
        return self._cluster_count == 1

    def feed(self, event_class: str, now: int, killer_is_player: bool = True) -> bool:
        if event_class == "dot_tick":
            return False
        if event_class == "kill" and not killer_is_player:
            return False
        layer = self.layer_for(event_class)
        if self._last_played.get(layer, -10 ** 9) + self.windows[layer] > now:
            return False
        if layer == "kill" and not self._allow_kill_cluster(now):
            return False
        self._last_played[layer] = now
        return True


def run() -> int:
    root = repo_root()
    fails: list[str] = []
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        if not ok:
            fails.append(label)

    pristine = {
        STATS_REL: (root / "04_recovered" / STATS_REL).read_text(encoding="utf-8"),
        GLOBALS_REL: (root / "04_recovered" / GLOBALS_REL).read_text(encoding="utf-8"),
    }
    out = apply_chain(root, pristine)
    stats_src, globals_src = out[STATS_REL], out[GLOBALS_REL]

    check("chain + X6 apply: drain defined and called once",
          stats_src.count("_combat_audio_drain_spine_events()") == 2)
    check("chain + X6 apply: drain forwards to Globals.play_combat_event",
          "Globals.play_combat_event(record)" in stats_src)
    check("structure: windows 100/150/300 extracted",
          (extract_int(globals_src, "COMBAT_LAYER_LIGHT_WINDOW_MS"),
           extract_int(globals_src, "COMBAT_LAYER_HEAVY_WINDOW_MS"),
           extract_int(globals_src, "COMBAT_LAYER_KILL_WINDOW_MS")) == (100, 150, 300))
    check("structure: cluster threshold == 3",
          extract_int(globals_src, "COMBAT_KILL_CLUSTER_THRESHOLD") == 3)
    check("structure: single funnel in play_combat_event body",
          globals_src.split("func play_combat_event(record):", 1)[1].split("\nfunc ", 1)[0]
          .count("play_sound_effect(stream)") == 1)
    check("structure: three distinct streams preloaded",
          all(s in globals_src for s in (
              "PUNCH_CLEAN_LIGHT_02.wav", "ice_crack.wav", "blood_explosion.wav")))

    policy = LayerPolicy(globals_src)

    # T1: machine-gun light hits -> at most 1 per 100ms
    p = LayerPolicy(globals_src)
    plays = sum(1 for t in range(0, 500, 40) if p.feed("direct_hit", t))
    check("T1 machine-gun hits: 13 hits/500ms -> <= 5 light plays (1 per 100ms)", plays <= 5)
    # T2: crit burst -> 1 per 150ms
    p = LayerPolicy(globals_src)
    plays = sum(1 for t in range(0, 500, 40) if p.feed("crit", t))
    check("T2 crit burst: <= 4 heavy plays /500ms (1 per 150ms)", plays <= 4)
    # T3: kill cluster of 5 within 200ms -> exactly 1 kill sound
    p = LayerPolicy(globals_src)
    plays = sum(1 for t in range(0, 200, 40) if p.feed("kill", t))
    check("T3 kill cluster (5 kills/200ms) -> exactly 1 kill play", plays == 1)
    # T4: DoT ticks never play (per-tick suppression)
    p = LayerPolicy(globals_src)
    plays = sum(1 for t in range(0, 500, 50) if p.feed("dot_tick", t))
    check("T4 DoT ticks (10/500ms) -> 0 plays", plays == 0)
    # T5: player death (killer not player) -> no kill sound
    p = LayerPolicy(globals_src)
    check("T5 player death suppressed (killer.is_player guard)",
          not p.feed("kill", 0, killer_is_player=False))
    # T6: layered streams stay independent (light then kill both play same instant)
    p = LayerPolicy(globals_src)
    p1 = p.feed("direct_hit", 0)
    p2 = p.feed("kill", 0)
    check("T6 light + kill same instant -> both play (independent layers)", p1 and p2)
    # T7: kill after window resets -> plays again
    p = LayerPolicy(globals_src)
    p.feed("kill", 0)
    check("T7 kill 400ms after cluster start -> plays (window reset)", p.feed("kill", 500))
    # T8: hit flood across layers stays under voice budget order of magnitude
    # (theoretical per-layer cap for this stimulus: 20 light + 14 heavy = 34)
    p = LayerPolicy(globals_src)
    total = sum(1 for t in range(0, 2000, 20) if p.feed("direct_hit", t) or p.feed("crit", t))
    check(f"T8 100 mixed heavy-light events/2s -> {total} plays <= 34 (per-layer window caps)", total <= 34)

    passed = len(checks) - len(fails)
    print(f"selftest checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("verdict: PASS (policy model)")
    print("not_proven: GDScript runtime behavior, audio perception/mix, real VM play")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
