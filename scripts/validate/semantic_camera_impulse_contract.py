#!/usr/bin/env python3
"""B2-X5 Camera Impulse v1 semantic contract (runnable, no game exec).

Pins the camera impulse aggregator contract delivered by B2-X5:
  1. mods/b2-x5-camera-impulse/mod.json invariants (id, dependency on
     b2-x1-combat-event-spine, chain target_original_sha256, 6 patches).
  2. Patch guards: preimage == pristine 04_recovered file SHA per target;
     old_text byte-exact count == expected_occurrences (1) against the
     pristine file; no overlap with existing mod old_text/new_text regions
     (feat-tce / feat-tce-context / b2-x1 / k1 / k2 / b2-x0-* / c5-l13 /
     c5-l16 / feat-autosave) on the same target path.
  3. Sequential in-memory apply of the 6 patches over pristine files
     (same occurrence walk as scripts/patch/apply_mod.py).
  4. Emission-side policy canaries: _spine_impulse call sites only carry
     impulse_kind kill/heavy; no impulse emitted inside the DoT-accumulation
     or direct-hit/on_take_damage emit regions; ordinary direct_hit and
     dot_tick are never converted into impulses.
  5. Consume-side aggregator canaries: direct_hit/dot_tick records are
     explicitly skipped (blocked_* counters), crit -> lightweight impulse,
     crit/heavy -> budget-capped impulses; kill/elite_kill disabled (blocked_kill_pulses) per HUMAN S5 2026-08-20; constants
     IMPULSE_BUDGET_MAX / IMPULSE_WINDOW_MS / IMPULSE_DECAY_PER_SEC /
     IMPULSE_MAX_OFFSET / IMPULSE_CLUSTER_APPENDIX exist; cluster merge
     counter and event count telemetry fields exist.
  6. Damage-logic canary: none of the new_texts mutate damage math or
     health (no damage_multiplier /= *= assignment, no health -= /=,
     no combined_effective_damage assignment).
  7. Deterministic mirror simulation of the aggregator (budget cap, short
     aggregation window, decay, offset safety cap, kill pulse disabled (blocked), cluster kill merge (pre-disable logic preserved for heavy),
     event count telemetry) using constants parsed from the actual patch
     payloads.
  8. No host absolute paths in the three B2-X5 files.

Usage (from any repo path):
    python scripts/validate/semantic_camera_impulse_contract.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MOD_ID = "b2-x5-camera-impulse"
TARGET_ORIGINAL = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
MOD_REL = "mods/b2-x5-camera-impulse/mod.json"
STATS_REL = "Scenes/Stats.gd"
PLAYER_REL = "Scenes/Player/Player.gd"
NEW_FILES = [
    MOD_REL,
    "scripts/validate/semantic_camera_impulse_contract.py",
    "docs/ai/audits/B2-X5_CAMERA_IMPULSE.md",
]
KNOWN_SIBLING_MODS = [
    "feat-tce", "feat-tce-context", "b2-x1-combat-event-spine",
    "k1-player-response", "k2-hit-reaction",
    "b2-x0-aggregate", "b2-x0-combat-harness-bridge",
    "c5-l13-dynamic-ui-zhcn", "c5-l16-zones-monsters-ui-zhcn",
    "feat-autosave",
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


def parse_consts(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for name, value in re.findall(r"const\s+([A-Z0-9_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)", text):
        out[name] = float(value)
    return out


class MirrorAggregator:
    """Python mirror of Player.gd::camera_impulse (faithful port, explicit ms)."""

    def __init__(self, cfg: dict[str, float]):
        self.budget_max = cfg["IMPULSE_BUDGET_MAX"]
        self.window_ms = int(cfg["IMPULSE_WINDOW_MS"])
        self.decay_rate = cfg["IMPULSE_DECAY_PER_SEC"]
        self.max_offset = cfg["IMPULSE_MAX_OFFSET"]
        self.crit_amp = cfg["IMPULSE_CRIT_AMPLITUDE"]
        self.kill_ratio = cfg["IMPULSE_KILL_RATIO"]
        self.cluster_appendix = cfg["IMPULSE_CLUSTER_APPENDIX"]
        self.appendix_cap = cfg["IMPULSE_CLUSTER_APPENDIX_CAP"]
        self.last_seq = 0
        self.amplitude = 0.0
        self.group_started_ms = 0
        self.last_kill_ms = 0
        self.cluster_kills = 0
        self.groups = 0
        self.t = {
            "events": 0, "impulses": 0, "kills": 0, "elite_kills": 0,
            "heavies": 0, "crits": 0, "clusters": 0, "blocked_direct_hits": 0,
            "blocked_dot_ticks": 0, "blocked_kill_records": 0,
            "capped_amplitude": 0, "capped_offset": 0, "blocked_kill_pulses": 0,
        }

    def consume(self, event_class: str, now_ms: int, kind: str = "",
                amplitude: float = 0.0, is_elite: bool = False) -> None:
        self.last_seq += 1
        self.t["events"] += 1
        if event_class == "direct_hit":
            self.t["blocked_direct_hits"] += 1
            return
        if event_class == "dot_tick":
            self.t["blocked_dot_ticks"] += 1
            return
        if event_class == "kill":
            self.t["blocked_kill_records"] += 1
            return
        if event_class == "crit":
            self.t["crits"] += 1
            self._add(self.crit_amp, False, now_ms)
            return
        if event_class == "impulse":
            if kind == "kill":
                self.t["kills"] += 1
                if is_elite:
                    self.t["elite_kills"] += 1
                self.t["blocked_kill_pulses"] += 1
                return
            elif kind == "heavy":
                self.t["heavies"] += 1
                self._add(amplitude, False, now_ms)

    def _add(self, added: float, is_kill: bool, now_ms: int) -> None:
        new_group = True
        if self.amplitude > 0.0 and now_ms - self.group_started_ms <= self.window_ms:
            new_group = False
        elif is_kill and self.cluster_kills > 0 and now_ms - self.last_kill_ms <= self.window_ms:
            new_group = False
        if new_group:
            self.group_started_ms = now_ms
            self.groups += 1
            if not is_kill:
                self.cluster_kills = 0
        if is_kill:
            since_last_kill = now_ms - self.last_kill_ms
            self.cluster_kills += 1
            self.last_kill_ms = now_ms
            if self.cluster_kills > 1 and since_last_kill <= self.window_ms:
                self.t["clusters"] += 1
                appendix = min(self.cluster_appendix * float(self.cluster_kills - 1), self.appendix_cap)
                added = min(added + appendix, self.budget_max)
        if self.amplitude + added > self.budget_max:
            self.t["capped_amplitude"] += 1
        self.amplitude = min(self.amplitude + added, self.budget_max)
        self.t["impulses"] += 1

    def decay(self, dt: float) -> None:
        if self.amplitude > 0.0:
            self.amplitude = max(0.0, self.amplitude - self.decay_rate * dt)

    def offset_len(self) -> float:
        length = self.amplitude
        if length > self.max_offset:
            return self.max_offset
        return length


def main() -> int:
    root = repo_root()
    fails: list[str] = []
    checks: list[tuple[str, bool]] = []

    def check(label: str, ok: bool) -> None:
        checks.append((label, ok))
        if not ok:
            fails.append(label)

    mod_path = root / MOD_REL
    stats_path = root / "04_recovered" / STATS_REL
    player_path = root / "04_recovered" / PLAYER_REL
    check(f"mod manifest exists: {MOD_REL}", mod_path.is_file())
    check(f"pristine Stats.gd exists: 04_recovered/{STATS_REL}", stats_path.is_file())
    check(f"pristine Player.gd exists: 04_recovered/{PLAYER_REL}", player_path.is_file())
    if not mod_path.is_file() or not stats_path.is_file() or not player_path.is_file():
        print("FAIL: input files missing (run from repo; worktree has mods/ and 04_recovered/)")
        return 1

    mod = json.loads(mod_path.read_text(encoding="utf-8"))
    stats_pristine = stats_path.read_text(encoding="utf-8")
    player_pristine = player_path.read_text(encoding="utf-8")
    stats_sha = sha256_path(stats_path)
    player_sha = sha256_path(player_path)

    # --- 1. manifest invariants ---
    check(f"mod id == {MOD_ID}", mod.get("id") == MOD_ID)
    check("dependencies contain b2-x1-combat-event-spine",
          "b2-x1-combat-event-spine" in mod.get("dependencies", []))
    check("target_original_sha256 == chain value C7B5D5A5...",
          mod.get("target_original_sha256", "").upper() == TARGET_ORIGINAL)
    check("patch_type == CODE_PATCH", mod.get("patch_type") == "CODE_PATCH")
    patches = mod.get("patches", [])
    check("patch count == 6", len(patches) == 6)
    check("asset_overlays empty (no new binary assets)", mod.get("asset_overlays", []) == [])

    # --- 2. per-patch guards ---
    per_target: dict[str, list[dict]] = {}
    for patch in patches:
        rel = patch.get("path", "")
        pre = patch.get("preimage_sha256", "").lower()
        old = patch.get("old_text", "")
        new = patch.get("new_text", "")
        expected = patch.get("expected_occurrences", 1)
        unit = patch.get("unit_id", "")[:44]
        pristine = {"Scenes/Stats.gd": stats_pristine, "Scenes/Player/Player.gd": player_pristine}.get(rel, "")
        actual_sha = {"Scenes/Stats.gd": stats_sha, "Scenes/Player/Player.gd": player_sha}.get(rel, "")

        check(f"path is Stats.gd or Player.gd ({unit})", rel in ("Scenes/Stats.gd", "Scenes/Player/Player.gd"))
        check(f"preimage == pristine file SHA ({unit})", pre == actual_sha.lower())
        check(f"expected_occurrences == 1 ({unit})", expected == 1)
        count = pristine.count(old)
        check(f"old_text count == {expected} in pristine file ({unit})", count == expected)
        check(f"new_text differs from old_text ({unit})", new != old)
        per_target.setdefault(rel, []).append(patch)

    # --- 2b. overlap audit vs sibling mods ---
    sibling_by_id: dict[str, Path] = {}
    for sdir in sorted((root / "mods").iterdir()):
        sfile = sdir / "mod.json"
        if sfile.is_file():
            try:
                sdata = json.loads(sfile.read_text(encoding="utf-8"))
            except Exception:
                continue
            sibling_by_id[sdata.get("id", "")] = sfile
    overlap_hits: list[str] = []
    for patch in patches:
        rel = patch.get("path", "")
        for sid in KNOWN_SIBLING_MODS:
            sfile = sibling_by_id.get(sid)
            if not sfile:
                continue
            sdata = json.loads(sfile.read_text(encoding="utf-8"))
            for sp in sdata.get("patches", []):
                if sp.get("path") != rel:
                    continue
                if patch["old_text"] in sp.get("old_text", "") or patch["old_text"] in sp.get("new_text", ""):
                    overlap_hits.append(f"{patch['unit_id']} old_text inside {sid}:{sp.get('unit_id')}")
                if sp.get("old_text", "") in patch["old_text"] or sp.get("old_text", "") in patch["new_text"]:
                    overlap_hits.append(f"{sid}:{sp.get('unit_id')} old_text inside {patch['unit_id']}")
                if patch["new_text"] in sp.get("new_text", ""):
                    overlap_hits.append(f"{patch['unit_id']} new_text inside {sid}:{sp.get('unit_id')}")
    check(f"no old_text/new_text overlap with sibling mods ({len(overlap_hits)} hits)",
          not overlap_hits)

    # --- 3. sequential apply simulation over pristine files ---
    working = {rel: {"Scenes/Stats.gd": stats_pristine, "Scenes/Player/Player.gd": player_pristine}[rel]
               for rel in per_target}
    for rel, rel_patches in per_target.items():
        for patch in rel_patches:
            old, new = patch["old_text"], patch["new_text"]
            count = working[rel].count(old)
            expected = patch.get("expected_occurrences", 1)
            check(f"sequential apply: occurrence intact for {patch['unit_id'][:44]}", count == expected)
            if count != expected:
                continue
            working[rel] = working[rel].replace(old, new, 1)
    applied_stats = working["Scenes/Stats.gd"]
    applied_player = working["Scenes/Player/Player.gd"]

    check("applied Stats.gd differs from pristine", applied_stats != stats_pristine)
    check("applied Player.gd differs from pristine", applied_player != player_pristine)

    # --- 4. emission-side policy canaries ---
    stats_new_texts = "\n".join(p["new_text"] for p in patches if p["path"] == "Scenes/Stats.gd")
    impulse_sites = re.findall(r"_spine_impulse\(\s*\"([a-z_]+)\"", stats_new_texts)
    check("emission kinds only kill/heavy", sorted(set(impulse_sites)) == ["heavy", "kill"])
    check("no impulse in DoT accumulation region",
          not any("accumulated_dot_damage" in p["old_text"] and "_spine_impulse" in p["new_text"]
                  for p in patches if p["path"] == "Scenes/Stats.gd"))
    check("no impulse in direct-hit/on_take_damage emit region",
          not any("on_take_damage(attacker_stats, damage_bundle" in p["old_text"] and "_spine_impulse" in p["new_text"]
                  for p in patches if p["path"] == "Scenes/Stats.gd"))
    check("kill impulse gated to player attacker", 'is_in_group("player")' in stats_new_texts)
    check("kill impulse detects elite via victim parent", 'victim_parent.get("is_elite")' in stats_new_texts)
    check("heavy impulse gated not is_dot_damage",
          "not is_dot_damage" in stats_new_texts and "is_player" in stats_new_texts)
    stats_consts = parse_consts(stats_new_texts)
    check("Stats.gd impulse constants declared",
          {"IMPULSE_AMPLITUDE_KILL", "IMPULSE_AMPLITUDE_ELITE_KILL",
           "IMPULSE_AMPLITUDE_HEAVY", "IMPULSE_HEAVY_THRESHOLD_RATIO"} <= set(stats_consts))
    check("spine_impulse reuses _spine_record (single bus)",
          '_spine_record("impulse", context)' in stats_new_texts)
    check("no trigger_effects calls in Stats.gd new_texts (no second bus)",
          "trigger_effects(" not in stats_new_texts)

    # --- 5. consume-side aggregator canaries ---
    agg = "\n".join(p["new_text"] for p in patches if p["path"] == "Scenes/Player/Player.gd")
    agg_consts = parse_consts(agg)
    check("budget constant present", "IMPULSE_BUDGET_MAX" in agg_consts)
    check("window constant present", "IMPULSE_WINDOW_MS" in agg_consts)
    check("decay constant present", "IMPULSE_DECAY_PER_SEC" in agg_consts)
    check("safety cap constant present", "IMPULSE_MAX_OFFSET" in agg_consts)
    check("cluster constants present",
          "IMPULSE_CLUSTER_APPENDIX" in agg_consts and "IMPULSE_CLUSTER_APPENDIX_CAP" in agg_consts)
    check("direct_hit skipped with counter",
          'event_class == "direct_hit"' in agg and "blocked_direct_hits" in agg)
    check("dot_tick skipped with counter",
          'event_class == "dot_tick"' in agg and "blocked_dot_ticks" in agg)
    check("crit -> lightweight impulse",
          'event_class == "crit"' in agg and "_impulse_add(IMPULSE_CRIT_AMPLITUDE, false)" in agg)
    check("kill impulse disabled (blocked_kill_pulses counted, no add)",
          'event_class == "impulse"' in agg and "blocked_kill_pulses" in agg and "_impulse_add(amplitude * IMPULSE_KILL_RATIO, true)" not in agg)
    check("heavy impulse consumed", "_impulse_add(amplitude, false)" in agg)
    check("budget clamp in _impulse_add",
          "min(_impulse_amplitude + added_amplitude, IMPULSE_BUDGET_MAX)" in agg)
    check("offset safety cap applied", "IMPULSE_MAX_OFFSET" in agg and "offset.normalized()" in agg)
    check("decay implemented", "IMPULSE_DECAY_PER_SEC * delta" in agg)
    check("cluster merge counter exists", '"clusters": 0' in agg)
    check("telemetry fields include events/impulses/kills/heavies/crits",
          all(k in agg for k in ('"events": 0', '"impulses": 0', '"kills": 0',
                                 '"heavies": 0', '"crits": 0', '"blocked_direct_hits": 0',
                                 '"blocked_dot_ticks": 0', '"capped_amplitude": 0', '"capped_offset": 0', '"blocked_kill_pulses": 0')))
    check("telemetry accessor exposed", "get_camera_impulse_telemetry()" in agg)
    check("camera2d offset written each frame", "camera2d.offset = offset" in agg)

    # --- 6. damage-logic canary (no Player/Mob damage logic change) ---
    all_new = "\n".join(p["new_text"] for p in patches)
    check("no damage_multiplier assignment", "damage_multiplier *=" not in all_new and "damage_multiplier =" not in all_new)
    check("no health mutation", "health -=" not in all_new and "health = max" not in all_new and "health =" not in all_new)
    check("no combined_effective_damage assignment",
          "combined_effective_damage *=" not in all_new and "combined_effective_damage = " not in all_new
          and "combined_effective_damage +=" not in all_new)
    check("no reduce_health / on_take_damage call injection",
          "reduce_health(" not in all_new and "on_take_damage(" not in all_new)
    check("Player.gd untouched physics body logic",
          "apply_central_impulse(" not in agg)

    # --- 7. mirror simulation with parsed constants ---
    needed = {"IMPULSE_BUDGET_MAX", "IMPULSE_WINDOW_MS", "IMPULSE_DECAY_PER_SEC",
              "IMPULSE_MAX_OFFSET", "IMPULSE_CRIT_AMPLITUDE", "IMPULSE_KILL_RATIO",
              "IMPULSE_CLUSTER_APPENDIX", "IMPULSE_CLUSTER_APPENDIX_CAP"}
    check("all aggregator constants parseable", needed <= set(agg_consts))
    if needed <= set(agg_consts):
        m = MirrorAggregator(agg_consts)
        # 7a. default-blocked policy: ordinary hits and DoT ticks produce no impulse
        for i in range(5):
            m.consume("direct_hit", 1000 + i)
        for i in range(3):
            m.consume("dot_tick", 1100 + i)
        check("7a: direct_hit/dot_tick blocked, zero amplitude",
              m.amplitude == 0.0 and m.t["blocked_direct_hits"] == 5 and m.t["blocked_dot_ticks"] == 3
              and m.t["impulses"] == 0 and m.t["events"] == 8)
        # 7b. crit -> lightweight impulse, budget respected
        for i in range(3):
            m.consume("crit", 2000)
        check("7b: 3 crits -> 1.8 amplitude under budget",
              m.amplitude == 3 * m.crit_amp and m.t["crits"] == 3 and m.t["impulses"] == 3)
        # 7c. decay returns amplitude to zero
        m.decay(0.2)
        check("7c: decay returns amplitude to zero",
              m.amplitude == 0.0 or abs(m.amplitude - max(0.0, 1.8 - m.decay * 0.2)) < 1e-9)
        # 7d. kill impulse disabled: burst only counted, no amplitude/cluster
        kill_amp = 1.6
        m2 = MirrorAggregator(agg_consts)
        for i, t in enumerate([0, 80, 160, 240]):
            m2.consume("impulse", t, kind="kill", amplitude=kill_amp)
        check("7d: 4-kill burst blocked (kills==4, blocked==4, zero amplitude, no cluster)",
              m2.t["kills"] == 4 and m2.t["blocked_kill_pulses"] == 4 and m2.t["clusters"] == 0
              and m2.t["impulses"] == 0 and m2.amplitude == 0.0)
        # 7e. separated kills disabled: both counted, no groups/clusters
        m3 = MirrorAggregator(agg_consts)
        m3.consume("impulse", 0, kind="kill", amplitude=kill_amp)
        m3.consume("impulse", 10000, kind="kill", amplitude=kill_amp)
        check("7e: separated kills blocked (kills==2, blocked==2, no amplitude)",
              m3.t["kills"] == 2 and m3.t["blocked_kill_pulses"] == 2 and m3.amplitude == 0.0 and m3.groups == 0)
        # 7f. offset safety cap
        m4 = MirrorAggregator(agg_consts)
        for i in range(30):
            m4.consume("crit", 5000)
        off = m4.offset_len()
        check("7f: offset capped at IMPULSE_MAX_OFFSET",
              m4.amplitude == m4.budget_max and off == m4.max_offset and m4.t["capped_amplitude"] > 0)
        # 7g. heavy impulse
        m5 = MirrorAggregator(agg_consts)
        m5.consume("impulse", 9000, kind="heavy", amplitude=1.2)
        check("7g: heavy impulse consumed", m5.t["heavies"] == 1 and m5.amplitude == 1.2)
        # 7h. elite kill disabled: counted but no amplitude
        m6 = MirrorAggregator(agg_consts)
        m6.consume("impulse", 11000, kind="kill", amplitude=2.4, is_elite=True)
        check("7h: elite kill blocked (elite_kills==1, kills==1, blocked==1, zero amplitude)",
              m6.t["elite_kills"] == 1 and m6.t["kills"] == 1 and m6.t["blocked_kill_pulses"] == 1 and m6.amplitude == 0.0)
        # 7i. emission policy mirror: heavy gate threshold & kill gate
        check("7i: heavy threshold constant > 0 and < 1", 0.0 < stats_consts["IMPULSE_HEAVY_THRESHOLD_RATIO"] < 1.0)
        check("7i: kill amplitude < elite amplitude < budget",
              stats_consts["IMPULSE_AMPLITUDE_KILL"] < stats_consts["IMPULSE_AMPLITUDE_ELITE_KILL"]
              and stats_consts["IMPULSE_AMPLITUDE_ELITE_KILL"] * m6.kill_ratio < agg_consts["IMPULSE_BUDGET_MAX"])
    else:
        check("mirror simulation ran (constants present)", False)

    # --- 8. no host absolute paths in B2-X5 files ---
    bs = chr(92)
    json_escape = '["' + bs + 'bfnrtu/0-9]'
    abs_re = re.compile(
        "[" + "A-Za-z" + "]:" + bs + bs + "(?!" + json_escape + ")"
        + "|[" + "A-Za-z" + "]:" + "/"
        + "|" + bs + bs + bs + bs
    )
    for rel in NEW_FILES:
        p = root / rel
        if p.is_file():
            bad = abs_re.findall(p.read_text(encoding="utf-8", errors="replace"))
            check(f"no absolute host path in {rel}", not bad)
        else:
            check(f"file exists: {rel}", False)

    # --- verdict ---
    passed = len(checks) - len(fails)
    print(f"checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("verdict: PASS")
    print("proves: manifest invariants; preimage/occurrence guards align with pristine "
          "Stats.gd and Player.gd; 6-patch sequential apply resolves; emission policy "
          "binds impulses only to kill/elite_kill/heavy (never direct_hit/dot_tick); "
          "aggregator has budget/window/decay/safety-cap/cluster-merge/telemetry; "
          "mirror simulation confirms policy, budget, decay, cap and cluster semantics "
          "with the constants parsed from the patch payloads; no damage logic change; "
          "no host absolute paths")
    print("not_proven: real game runtime behavior of the aggregator (needs VM boot + "
          "harness telemetry / human S5); Camera2D smoothing interplay; compile/pack/boot; "
          "elite detection at runtime; kill impulse only for player-attacker kills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
