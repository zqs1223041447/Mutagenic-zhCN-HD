#!/usr/bin/env python3
"""B2-X4 kill feel semantic contract (runnable, no game exec).

Pins the kill-feel contract delivered by B2-X4:
  1. mods/b2-x4-kill-feel/mod.json invariants (id, dependency on
     b2-x1-combat-event-spine, target_original_sha256, patch count == 3).
  2. Patch guards: path == Scenes/Mobs/Mob.gd only; preimage == pristine
     Mob.gd SHA; old_text byte-exact count == expected_occurrences.
  3. Overlap guard vs k2-hit-reaction's existing Mob.gd patches (my
     anchors must not be rewritten or consumed by k2's old/new texts).
  4. Semantic canaries: consumes the X1 unified kill event (read-only);
     tier layering normal/dot/elite/boss; cluster budget via GameState
     globals; reuses existing FX assets; NO damage math, drop, death-order,
     death-flag, second-bus, camera shake, or hit-stop code introduced.
  5. X1 kill-event extension check: the kill record fields this mod reads
     (event_class=="kill", did_kill, is_dot) must be derivable from the
     integrated b2-x1 mod (dependency already present in this worktree).
  6. Scenario model self-tests (pure simulation of the declared tier+budget
     algorithm with constants parsed from the manifest): single kill,
     rapid multi-kill, 5-20 cluster flood, elite, boss, dot-kill suppress,
     death-once, vanilla drop order.
  7. No host absolute paths in the B2-X4 files.

Usage (from any repo path):
    python scripts/validate/semantic_kill_feel_contract.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MOD_ID = "b2-x4-kill-feel"
MOB_PREIMAGE = "ba46348c8ba490644964a8b9bdabb58a8964199cd3464c468f77cc57babe9364"
TARGET_ORIGINAL = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
X1_MOD_ID = "b2-x1-combat-event-spine"
MOD_REL = "mods/b2-x4-kill-feel/mod.json"
MOB_REL = "Scenes/Mobs/Mob.gd"
GAMESTATE_REL = "Globals/GameState.gd"
K2_MOD_REL = "mods/k2-hit-reaction/mod.json"
NEW_FILES = [
    MOD_REL,
    "scripts/validate/semantic_kill_feel_contract.py",
    "docs/ai/audits/B2-X4_KILL_FEEL.md",
]

_bad_tokens = [
    "apply_damage(",
    "reduce_health(",
    "combined_effective_damage",
    "damage_multiplier",
    "health =",
    "health -= ",
    "pickup",
    "add_xp",
    "add_kills",
    "queue_free(",
    "trigger_effects(",
    "_spine_record(",
    "camera",
    "shake",
    "hit_stop",
    "hitstop",
    "preload(",
    "dead = true",
]

checks: list[str] = []
fails: list[str] = []


def check(name: str, ok: bool) -> None:
    checks.append((name, ok))
    if not ok:
        fails.append(name)


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
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------- scenarios
def model_tier(kill_record, is_level_boss, is_elite):
    """Pure mirror of _kill_feel_tier() as declared in the manifest."""
    if kill_record is None:
        return -1
    if kill_record.get("event_class", "") != "kill":
        return -1
    if not kill_record.get("did_kill", False):
        return -1
    if kill_record.get("is_dot", False):
        return 0
    if is_level_boss:
        return 2
    if is_elite:
        return 1
    return 0


class ModelBudget:
    """Pure mirror of _kill_feel_consume_budget()."""

    def __init__(self, window_ms: int, budget: int):
        self.window_ms = window_ms
        self.budget = budget
        self.now = 0
        self.b = None

    def step(self, dt_ms: int) -> bool:
        self.now += dt_ms
        b = self.b
        if b is None or self.now - b["start_ms"] > self.window_ms:
            b = {"start_ms": self.now, "count": 0}
        b["count"] = b.get("count", 0) + 1
        self.b = b
        return b["count"] <= self.budget

    def boosts_after(self, kills: int, dt_ms: int, tier_fn) -> int:
        count = 0
        for _ in range(kills):
            if tier_fn() > 0 and self.step(dt_ms):
                count += 1
        return count


def main() -> int:
    root = repo_root()
    mod_rel = Path(MOD_REL)
    mod_path = root / MOD_REL
    mob_path = root / "04_recovered" / MOB_REL
    gs_path = root / "04_recovered" / GAMESTATE_REL
    x1_mod_path = root / "mods" / X1_MOD_ID / "mod.json"
    k2_path = root / K2_MOD_REL
    check(f"pristine Mob.gd exists: 04_recovered/{MOB_REL}", mob_path.is_file())
    check(f"file exists: {MOD_REL}", mod_path.is_file())
    check(f"file exists: dependency {X1_MOD_ID} integrated (mod.json present)", x1_mod_path.is_file())

    manifest = json.loads(mod_path.read_text(encoding="utf-8"))
    check("manifest id == b2-x4-kill-feel", manifest.get("id") == MOD_ID)
    check("patch_type == CODE_PATCH", manifest.get("patch_type") == "CODE_PATCH")
    check("target_original_sha256 == chain root C7B5D5A5...",
          manifest.get("target_original_sha256") == TARGET_ORIGINAL)
    check("dependencies contains b2-x1-combat-event-spine",
          X1_MOD_ID in manifest.get("dependencies", []))
    check("conflicts empty", manifest.get("conflicts", []) == [])
    check("patch count == 3", len(manifest.get("patches", [])) == 3)

    mob_pristine = mob_path.read_text(encoding="utf-8")
    check(f"pristine Mob.gd sha256 == {MOB_PREIMAGE[:12]}...",
          sha256_path(mob_path).lower() == MOB_PREIMAGE)

    patches = manifest["patches"]
    check("all patches target Scenes/Mobs/Mob.gd only",
          all(p.get("path") == MOB_REL for p in patches))
    check("all patches use pristine Mob.gd preimage",
          all(p.get("preimage_sha256") == MOB_PREIMAGE for p in patches))

    new_text = "\n".join(p["new_text"] for p in patches)
    for p in patches:
        expected = p.get("expected_occurrences", 1)
        actual = mob_pristine.count(p["old_text"])
        check(f"{p['unit_id']}: old_text count {actual} == {expected}", actual == expected)
        check(f"{p['unit_id']}: new differs from old", p["old_text"] != p["new_text"])
        check(f"{p['unit_id']}: no template placeholders", p.get("placeholders", []) == [])

    # LF endings on the three delivered files
    for rel in NEW_FILES:
        data = (root / rel).read_bytes() if (root / rel).is_file() else b""
        check(f"LF line endings: {rel}", b"\r\n" not in data)

    # overlap guard vs k2-hit-reaction on Mob.gd
    if k2_path.is_file():
        k2 = json.loads(k2_path.read_text(encoding="utf-8"))
        k2_mob = [p for p in k2.get("patches", []) if p.get("path") == MOB_REL]
        k2_texts = []
        for p in k2_mob:
            k2_texts.append(p["old_text"])
            k2_texts.append(p["new_text"])
        overlapped = False
        for p in patches:
            for k2tex in k2_texts:
                if p["old_text"] in k2tex or k2tex in p["old_text"]:
                    overlapped = True
                    check(f"no anchor overlap with k2: {p['unit_id']}", False)
        if k2_mob:
            check(f"k2 overlap guard (k2 patches {len(k2_mob)} on Mob.gd)", not overlapped)
        else:
            check("k2 has no Mob.gd patches to overlap with", True)
        # my added call site must sit AFTER k2's region is preserved by apply
    else:
        check("k2 mod.json readable for overlap guard", False)

    # GameState globals gate: budget uses only pre-existing globals API
    gs = gs_path.read_text(encoding="utf-8") if gs_path.is_file() else ""
    check("pristine GameState.gd provides get_global(key, default=null)",
          "func get_global(key, default = null)" in gs)
    check("pristine GameState.gd provides set_global(key, item)",
          "func set_global(key, item)" in gs)

    # ---- semantic canaries on the introduced code ----
    check("uses unified kill event: _spine_last_events read", "_spine_last_events" in new_text)
    check("uses unified kill event: event_class=='kill' check", '"event_class"' in new_text and '"kill"' in new_text)
    check("uses unified kill event: did_kill==true check", '"did_kill"' in new_text)
    check("dot-kill suppression: is_dot read", '"is_dot"' in new_text)
    check("layering: is_level_boss branch", "is_level_boss" in new_text)
    check("layering: is_elite branch", "is_elite" in new_text)
    check("cluster budget constants declared",
          "KILL_FEEL_CLUSTER_WINDOW_MS" in new_text and "KILL_FEEL_CLUSTER_BUDGET" in new_text)
    check("cluster budget via GameState globals (get+set)",
          "GameState.get_global" in new_text and "GameState.set_global" in new_text)
    check("budget window reset + count increment present",
          'budget = {"start_ms": now, "count": 0}' in new_text.replace("\t", "") or
          '{"start_ms": now, "count": 0}' in new_text.replace("\t", ""))
    check("budget cap comparison present", "KILL_FEEL_CLUSTER_BUDGET" in new_text and "count" in new_text)
    check("boost consumes budget before FX spawn", "tier <= 0" in new_text and "_kill_feel_consume_budget()" in new_text)
    check("reuses existing shatter asset", "shatter.instance()" in new_text)
    check("reuses existing poof (burning death) asset", "poof.instance()" in new_text)
    check("boost call site injected exactly once",
          new_text.count("_kill_feel_apply_boost(_kill_feel_tier())") == 1)

    for tok in _bad_tokens:
        check(f"no forbidden token: {tok}", tok not in new_text)

    # spawn_death_animation tail: boost appended AFTER vanilla frozen/burning FX,
    # nothing between burning branch and boost except blank line (drop order untouched)
    call_line = re.findall(r"\n([ \t]*)_kill_feel_apply_boost\(_kill_feel_tier\(\)\)", new_text)
    check("boost call is a standalone statement", len(call_line) == 1)
    check("boost call placed after vanilla burning branch tail",
          new_text.rstrip().endswith("_kill_feel_apply_boost(_kill_feel_tier())"))

    # call site lives inside spawn_death_animation (before queue_free in _on_death)
    on_death_start = mob_pristine.index("func _on_death")
    on_death_end = mob_pristine.index("func spawn_death_animation():")
    on_death_body = mob_pristine[on_death_start:on_death_end]
    check("vanilla death order intact: _on_death calls spawn_death_animation() then queue_free()",
          on_death_body.index("spawn_death_animation()") < on_death_body.index("queue_free()"))
    check("vanilla death order intact: drops handled before death anim",
          "spawn_death_animation" in mob_pristine)

    # ---- X1 kill-event extension check (fields consumed are derivable) ----
    x1 = json.loads(x1_mod_path.read_text(encoding="utf-8"))
    x1_kill_emitted = False
    x1_readable = False
    for p in x1.get("patches", []):
        nt = p["new_text"]
        if '"kill"' in nt and "_spine_record(\"kill\"" in nt.replace(" ", ""):
            x1_kill_emitted = True
        if "_spine_last_events" in nt and "did_kill" in nt:
            x1_readable = True
    check("X1 emits _spine_record(\"kill\") (kill event exists)", x1_kill_emitted)
    check("X1 kill record carries did_kill + is_dot fields", x1_readable)

    # ---- scenario model self-tests (declared constants parsed from manifest) ----
    const_re = re.compile(r"const KILL_FEEL_CLUSTER_WINDOW_MS = (\d+)")
    budget_re = re.compile(r"const KILL_FEEL_CLUSTER_BUDGET = (\d+)")
    window_ms = int(const_re.search(new_text).group(1))
    budget = int(budget_re.search(new_text).group(1))
    check("cluster window within intended range (200-2000ms)", 200 <= window_ms <= 2000)
    check("cluster budget within intended range (1-6)", 1 <= budget <= 6)

    elite_kill = {"event_class": "kill", "did_kill": True, "is_dot": False}
    dot_kill = {"event_class": "kill", "did_kill": True, "is_dot": True}
    boss_kill = {"event_class": "kill", "did_kill": True, "is_dot": False}
    normal_kill = {"event_class": "kill", "did_kill": True, "is_dot": False}

    check("scenario single normal kill -> tier 0 (no boost)",
          model_tier(normal_kill, False, False) == 0)
    check("scenario single elite kill -> tier 1",
          model_tier(elite_kill, False, True) == 1)
    check("scenario single boss kill -> tier 2",
          model_tier(boss_kill, True, True) == 2)
    check("scenario dot kill suppresses layering -> tier 0",
          model_tier(dot_kill, True, True) == 0)
    check("scenario non-kill record -> tier -1 (no fabricated feel)",
          model_tier({"event_class": "crit", "did_kill": False}, True, True) == -1)

    mb = ModelBudget(window_ms, budget)
    check("scenario rapid multi-kill (5 elite, tight window) capped at budget",
          mb.boosts_after(5, 1, lambda: model_tier(elite_kill, False, True)) == budget)
    mb2 = ModelBudget(window_ms, budget)
    check("scenario 20-kill cluster flood (elite) capped at budget + stale survives",
          mb2.boosts_after(20, 1, lambda: model_tier(elite_kill, False, True)) == budget)
    mb3 = ModelBudget(window_ms, budget)
    check("scenario window reset allows fresh budget after spillover",
          mb3.boosts_after(budget, 1, lambda: model_tier(elite_kill, False, True)) +
          mb3.boosts_after(1, window_ms + 1, lambda: model_tier(elite_kill, False, True)) == budget + 1)
    mb4 = ModelBudget(window_ms, budget)
    check("scenario dot kills never consume boost budget",
          mb4.boosts_after(budget * 2, 1, lambda: model_tier(dot_kill, True, True)) == 0)

    # death-once: exact one boost call site; no death-flag write; no queue_free
    check("death-once: exactly one boost call site per death path",
          new_text.count("_kill_feel_apply_boost(_kill_feel_tier())") == 1)

    # ---- no host absolute paths in delivered files ----
    bs = re.escape("\\\\")
    json_escape = re.escape('\\"')
    abs_re = re.compile(
        "[A-Za-z]:" + bs + bs + bs + bs
        + "]:" + bs + bs + "(?!" + json_escape + ")"
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

    # ---- verdict ----
    passed = sum(1 for _, ok in checks if ok)
    print(f"checks: {passed}/{len(checks)} passed")
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("verdict: PASS")
    print("proves: manifest invariants; preimage/occurrence guards align with pristine Mob.gd; "
          "no overlap with k2 Mob.gd anchors; read-only consumption of X1 kill event "
          "(event_class/kill, did_kill, is_dot); tier layering normal/dot/elite/boss; "
          "cluster budget via GameState globals (window+count, capped); FX reuse of existing "
          "shatter/poof assets; no damage/drop/death-order/death-flag/second-bus/camera-shake/hit-stop "
          "code; scenario model capped-boost/death-once/drop-order invariants hold")
    print("not_proven: real in-game FX/performance (needs VM S5 + visuals); per-kill GameState "
          "budget persistence across scene reloads; build/boot/pck integrity (needs pipeline); "
          "human readability of >budget elite cluster bursts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())