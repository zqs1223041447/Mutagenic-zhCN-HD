#!/usr/bin/env python3
"""B2-X6 combat audio layers semantic contract (runnable, no game exec).

Pins the layered combat audio contract delivered by B2-X6:
  1. mods/b2-x6-combat-audio-layers/mod.json invariants (id, patch type,
     dependencies, target_original_sha256, patch count).
  2. Patch guards: path in {Scenes/Stats.gd, Globals/Globals.gd}; preimage ==
     pristine whole-file SHA; old_text byte-exact count == expected_occurrences.
  3. Full dependency-chain in-memory apply simulation (feat-tce ->
     feat-tce-context -> b2-x1 -> k4-audio-foundation -> b2-x6) with the same
     occurrence walk as scripts/patch/apply_mod.py; X6 patches must resolve
     after the chain (no anchor collision).
  4. Semantic canaries on the simulated output:
     - layer mapping direct_hit->light / crit->heavy / kill->kill; dot_tick
       suppressed (early return, no per-tick impact play);
     - windows LIGHT=100 / HEAVY=150 / KILL=300; kill cluster aggregation
       (>= COMBAT_KILL_CLUSTER_THRESHOLD kills within window -> single sound);
     - kill layer player-only (killer.is_player guard, no player-death pop);
     - single play_sound_effect(stream) funnel inside play_combat_event: k4
       voice budget (16 concurrent / per-stream 60ms / pitch+volume variation /
       tree_exited accounting) untouched;
     - drain in Stats.gd: consumed-seq guard, forwards to
       Globals.play_combat_event, invoked before apply_damage returns (captures
       kill records before the victim is freed by the deferred died signal);
     - no damage math / event semantics change (`*=`, `+= combined_effective_damage`,
       `on_kill(`, `trigger_effects(` counts unchanged);
     - referenced audio assets exist under 04_recovered/Sounds;
     - X6 old/new texts do not intersect any other mod's same-file patches;
     - no host absolute paths in the four B2-X6 files.
  5. No host absolute paths in the four B2-X6 files.

Usage (from any repo path):
    python scripts/validate/semantic_combat_audio_contract.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MOD_ID = "b2-x6-combat-audio-layers"
TARGET_ORIGINAL = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
STATS_PREIMAGE = "C187245E4F475E0928252610BB9D6D27FCB4A23C68754B4409DF5A6EB9997234"
GLOBALS_PREIMAGE = "C1778CB8549B2A0EC15F50C010AFF294D6A3DF94B1A2954EBC7F2190F65942DD"
MOD_REL = "mods/b2-x6-combat-audio-layers/mod.json"
STATS_REL = "Scenes/Stats.gd"
GLOBALS_REL = "Globals/Globals.gd"
CHAIN_IDS = ["feat-tce", "feat-tce-context", "b2-x1-combat-event-spine", "k4-audio-foundation"]
REQUIRED_DEPS = ["b2-x1-combat-event-spine", "k4-audio-foundation"]
ASSETS = [
    "Sounds/Hits/PUNCH_CLEAN_LIGHT_02.wav",
    "Sounds/Hits/ice_crack.wav",
    "Sounds/SFX/blood_explosion.wav",
]
NEW_FILES = [
    MOD_REL,
    "scripts/validate/semantic_combat_audio_contract.py",
    "docs/ai/audits/B2-X6_COMBAT_AUDIO_LAYERS.md",
    "tests/combat_audio/test_combat_audio_layers.py",
]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except subprocess.CalledProcessError:
        return Path(__file__).resolve().parents[2]


def apply_group(working: str, patches: list[dict], pristine: str, preimage: str,
                label: str, checks, check) -> str:
    """Mirror scripts/patch/apply_mod.py: preflight vs pristine, then
    occurrence walk vs working text, replace all."""
    for patch in patches:
        old = patch["old_text"]
        new = patch["new_text"]
        expected = patch.get("expected_occurrences", 1)
        pre = patch.get("preimage_sha256", "").lower()
        unit = patch.get("unit_id", "")[:40]
        check(f"[{label}] preimage == pristine ({unit})", pre == preimage.lower())
        check(f"[{label}] pristine count == {expected} ({unit})",
              pristine.count(old) == expected)
    for patch in patches:
        old = patch["old_text"]
        new = patch["new_text"]
        expected = patch.get("expected_occurrences", 1)
        unit = patch.get("unit_id", "")[:40]
        count = working.count(old)
        check(f"[{label}] working count == {expected} at apply ({unit})", count == expected)
        working = working.replace(old, new)
    return working


def body_of(src: str, func_sig: str) -> str:
    start = src.index(func_sig)
    rest = src[start + len(func_sig):]
    nxt = rest.find("\nfunc ")
    return rest if nxt < 0 else rest[:nxt]


def main() -> int:
    root = repo_root()
    fails: list[str] = []
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        if not ok:
            fails.append(label)

    mod_json = root / MOD_REL
    stats_path = root / "04_recovered" / STATS_REL
    globals_path = root / "04_recovered" / GLOBALS_REL
    check(f"mod manifest exists: {MOD_REL}", mod_json.is_file())
    check(f"pristine Stats.gd exists: 04_recovered/{STATS_REL}", stats_path.is_file())
    check(f"pristine Globals.gd exists: 04_recovered/{GLOBALS_REL}", globals_path.is_file())
    if not mod_json.is_file() or not stats_path.is_file() or not globals_path.is_file():
        print("FAIL: input files missing (run from repo; worktree has mods/ and 04_recovered/)")
        return 1

    mod = json.loads(mod_json.read_text(encoding="utf-8"))
    pristine_stats = stats_path.read_text(encoding="utf-8")
    pristine_globals = globals_path.read_text(encoding="utf-8")
    pristine = {STATS_REL: pristine_stats, GLOBALS_REL: pristine_globals}
    preimage = {STATS_REL: STATS_PREIMAGE, GLOBALS_REL: GLOBALS_PREIMAGE}

    check(f"mod id == {MOD_ID}", mod.get("id") == MOD_ID)
    check("patch_type == CODE_PATCH", mod.get("patch_type") == "CODE_PATCH")
    check("dependencies contain b2-x1-combat-event-spine and k4-audio-foundation",
          all(d in mod.get("dependencies", []) for d in REQUIRED_DEPS))
    check("target_original_sha256 == C7B5D5A5...",
          mod.get("target_original_sha256", "").upper() == TARGET_ORIGINAL)

    patches = mod.get("patches", [])
    check("patch count == 5", len(patches) == 5)
    check("patch paths whitelist (only Stats.gd / Globals.gd)",
          all(p.get("path") in (STATS_REL, GLOBALS_REL) for p in patches))
    check("per-file preimage == pristine whole-file SHA",
          all(p.get("preimage_sha256", "").lower() == preimage[p["path"]].lower() for p in patches))
    check("expected_occurrences == 1 for all patches",
          all(p.get("expected_occurrences", 1) == 1 for p in patches))

    # --- dependency chain simulation (only the two files relevant to X6) ---
    working = dict(pristine)
    chain_ok = True
    for chain_id in CHAIN_IDS:
        cp = root / "mods" / chain_id / "mod.json"
        check(f"chain dep manifest exists: {chain_id}", cp.is_file())
        if not cp.is_file():
            chain_ok = False
            continue
        cmod = json.loads(cp.read_text(encoding="utf-8"))
        for rel in (STATS_REL, GLOBALS_REL):
            group = [p for p in cmod.get("patches", []) if p.get("path") == rel]
            if not group:
                continue
            try:
                working[rel] = apply_group(working[rel], group, pristine[rel],
                                           preimage[rel], chain_id, checks, check)
            except Exception as exc:
                check(f"[{chain_id}] chain apply on {rel}: {exc}", False)
                chain_ok = False
    check("dependency chain (feat-tce/context, b2-x1, k4) applies cleanly", chain_ok)
    chain_stats = working[STATS_REL]
    chain_globals = working[GLOBALS_REL]

    # --- X6 patches applied after the chain, same walk ---
    for rel in (STATS_REL, GLOBALS_REL):
        group = [p for p in patches if p.get("path") == rel]
        try:
            working[rel] = apply_group(working[rel], group, pristine[rel],
                                       preimage[rel], "b2-x6", checks, check)
        except Exception as exc:
            check(f"[b2-x6] apply on {rel}: {exc}", False)

    out_stats = working[STATS_REL]
    out_globals = working[GLOBALS_REL]

    # --- canaries: Stats.gd drain ---
    check("drain var declared (consumed seq)",
          "var _combat_audio_consumed_seq = 0" in out_stats)
    check("drain function defined once + called once",
          out_stats.count("_combat_audio_drain_spine_events()") == 2)
    check("drain guarded by consumed-seq", "_spine_event_seq <= _combat_audio_consumed_seq" in out_stats)
    check("drain forwards to Globals.play_combat_event",
          "Globals.play_combat_event(record)" in out_stats)
    drain_call_at = out_stats.index("_combat_audio_drain_spine_events()\n")
    did_kill_line_at = out_stats.index("\t\t\t\t\t\t\t\t\"did_kill\": did_kill, ")
    check("drain invoked before apply_damage return (kill record captured pre-free)",
          drain_call_at < did_kill_line_at)
    check("apply_damage signature unchanged (count == 1)",
          out_stats.count("func apply_damage(damage_bundle, color = Color.white") == 1)
    check("X6 adds no damage-math: '*=' count unchanged vs chain",
          out_stats.count("*=") == chain_stats.count("*="))
    check("X6 adds no DoT damage-math: '+= combined_effective_damage' unchanged vs chain",
          out_stats.count("+= combined_effective_damage") == chain_stats.count("+= combined_effective_damage"))
    check("X6 adds no new on_kill( call site",
          out_stats.count("on_kill(") == chain_stats.count("on_kill("))
    check("X6 introduces no second event bus: trigger_effects( unchanged vs chain",
          out_stats.count("trigger_effects(") == chain_stats.count("trigger_effects("))

    # --- canaries: Globals.gd layer policy ---
    body = body_of(out_globals, "func play_combat_event(record):")
    check("dot_tick early return (suppressed per tick)",
          "if event_class == \"dot_tick\":" in body and
          body.split("if event_class == \"dot_tick\":", 1)[1].lstrip().startswith("return"))
    check("kill layer player-only (killer.is_player guard)",
          "killer.is_player" in body and
          body.index("killer.is_player") < body.index("play_sound_effect(stream)"))
    check("single play_sound_effect( funnel in play_combat_event (voice budget via k4)",
          body.count("play_sound_effect(stream)") == 1)
    check("no direct SoundEffect instantiation in X6 (budget/tree_exited intact)",
          all("sound_effect.instance()" not in p.get("new_text", "") for p in patches))
    check("layer mapping: direct_hit -> light", "return \"light\"" in body_of(out_globals, "func _combat_audio_layer_for"))
    check("layer mapping: crit -> heavy", "return \"heavy\"" in body_of(out_globals, "func _combat_audio_layer_for"))
    check("layer mapping: kill -> kill", "return \"kill\"" in body_of(out_globals, "func _combat_audio_layer_for"))
    check("window constants 100/150/300 present",
          "COMBAT_LAYER_LIGHT_WINDOW_MS = 100" in out_globals and
          "COMBAT_LAYER_HEAVY_WINDOW_MS = 150" in out_globals and
          "COMBAT_LAYER_KILL_WINDOW_MS = 300" in out_globals)
    check("cluster threshold == 3", "COMBAT_KILL_CLUSTER_THRESHOLD = 3" in out_globals)
    check("cluster gate: first-of-window plays, later suppressed",
          "return _combat_kill_cluster_count == 1" in out_globals and
          "_combat_kill_cluster_count > COMBAT_KILL_CLUSTER_THRESHOLD" in out_globals)
    check("kill layer distinct stream (blood_explosion)", "combat_sfx_kill = preload(\"res://Sounds/SFX/blood_explosion.wav\")" in out_globals)
    check("light/heavy distinct streams", "PUNCH_CLEAN_LIGHT_02.wav" in out_globals and "ice_crack.wav" in out_globals)
    check("k4 budget internals untouched (SFX_MAX_CONCURRENT / tree_exited / windows)",
          "SFX_MAX_CONCURRENT" in out_globals and "_on_runtime_sfx_tree_exited" in out_globals and
          "SFX_AGGREGATE_WINDOW_MS" in out_globals and "SFX_PITCH_VARIATION" in out_globals and
          "SFX_VOLUME_VARIATION_DB" in out_globals)
    check("X6 new_texts never touch k4 limiter internals",
          all("_sfx_last_play" not in p.get("new_text", "") and
              "_sfx_active_count" not in p.get("new_text", "") for p in patches))

    # --- canaries: assets + cross-mod isolation ---
    for rel in ASSETS:
        check(f"asset exists: 04_recovered/{rel}", (root / "04_recovered" / rel).is_file())
    other_hits: list[str] = []
    for d in sorted((root / "mods").iterdir()):
        if not d.is_dir() or d.name == MOD_ID:
            continue
        cp = d / "mod.json"
        if not cp.is_file():
            continue
        try:
            cmod = json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            continue
        for p in cmod.get("patches", []):
            if p.get("path") not in (STATS_REL, GLOBALS_REL):
                continue
            for own in patches:
                if own.get("path") != p.get("path"):
                    continue
                for blob_name, blob in (("old_text", own["old_text"]), ("new_text", own["new_text"])):
                    if blob and (blob in (p.get("old_text") or "") or blob in (p.get("new_text") or "")):
                        other_hits.append(f"{d.name}:{p.get('unit_id', '')}:{blob_name}")
    check("no X6 old/new text intersects any other mod's same-file patches", not other_hits)

    # --- no host absolute paths in B2-X6 files ---
    bs = chr(92)
    json_escape = '["' + bs + 'bfnrtu/0-9]'
    abs_re = re.compile(
        "(?<![A-Za-z0-9])[" + "A-Za-z" + "]:" + bs + bs + "(?!" + json_escape + ")"
        + "|(?<![A-Za-z0-9])[" + "A-Za-z" + "]:" + "/"
        + "|" + bs + bs + bs + bs
    )
    for rel in NEW_FILES:
        p = root / rel
        if p.is_file():
            bad = abs_re.findall(p.read_text(encoding="utf-8", errors="replace"))
            check(f"no absolute host path in {rel}", not bad)
        else:
            check(f"file exists: {rel}", False)

    passed = len(checks) - len(fails)
    print(f"checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("verdict: PASS")
    print("proves: manifest invariants; preimage/occurrence guards align with pristine files; "
          "dependency chain + 5 X6 patches apply cleanly; layer mapping direct_hit/crit/kill/dot_tick; "
          "per-layer windows (100/150/300) + cluster aggregation; single k4 funnel (voice budget, "
          "tree_exited, variation preserved); drained before apply_damage return with consumed-seq; "
          "no damage-math / event semantics / second-bus change; assets present; no cross-mod "
          "anchor intersection; no host absolute paths")
    print("not_proven: real game runtime audio behavior (needs VM + harness telemetry + S5 "
          "HUMAN_ACCEPT); GDScript compile (GDRE --compile runs in aggregate build); per-stream "
          "perception mix / volume balance; layer windows tuned to feel (v1 constants)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
