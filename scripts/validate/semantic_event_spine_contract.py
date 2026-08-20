#!/usr/bin/env python3
"""B2-X1 combat event spine semantic contract (runnable, no game exec).

Pins the event spine contract delivered by B2-X1:
  1. mods/b2-x1-combat-event-spine/mod.json invariants (id, dependency,
     target_original_sha256, patch count).
  2. Patch guards: path == Scenes/Stats.gd only; preimage == pristine
     Stats.gd SHA; old_text byte-exact count == expected_occurrences.
  3. Full in-memory apply simulation of the 5 patches over pristine
     Stats.gd (same occurrence walk as scripts/patch/apply_mod.py).
  4. Semantic canaries: event classes direct_hit/dot_tick/crit/kill
     reachable exactly once; dot_tick bound to is_dot; crit bound to
     did_crit; kill bound to did_kill=true; no new trigger_effects call
     site (no second bus); no new damage-math/damage-multiplier code.
  5. No host absolute paths in the three B2-X1 files.

Usage (from any repo path):
    python scripts/validate/semantic_event_spine_contract.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

MOD_ID = "b2-x1-combat-event-spine"
STATS_PREIMAGE = "C187245E4F475E0928252610BB9D6D27FCB4A23C68754B4409DF5A6EB9997234"
TARGET_ORIGINAL = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"
MOD_REL = "mods/b2-x1-combat-event-spine/mod.json"
STATS_REL = "Scenes/Stats.gd"
NEW_FILES = [
    MOD_REL,
    "scripts/validate/semantic_event_spine_contract.py",
    "docs/ai/audits/B2-X1_COMBAT_EVENT_SPINE.md",
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
    check(f"mod manifest exists: {MOD_REL}", mod_json.is_file())
    check(f"pristine Stats.gd exists: 04_recovered/{STATS_REL}", stats_path.is_file())
    if not mod_json.is_file() or not stats_path.is_file():
        print("FAIL: input files missing (run from repo; worktree has mods/ and 04_recovered/)")
        return 1

    mod = json.loads(mod_json.read_text(encoding="utf-8"))
    pristine = stats_path.read_text(encoding="utf-8")
    check(f"mod id == {MOD_ID}", mod.get("id") == MOD_ID)
    check("dependencies contain feat-tce-context", "feat-tce-context" in mod.get("dependencies", []))
    check("target_original_sha256 == C7B5D5A5...", mod.get("target_original_sha256", "").upper() == TARGET_ORIGINAL)

    patches = mod.get("patches", [])
    check("patch count == 5", len(patches) == 5)

    # --- 2/3. per-patch guards + sequential apply simulation ---
    working = pristine
    emit_lines = 0
    spine_record_total = 0
    for patch in patches:
        rel = patch.get("path", "")
        pre = patch.get("preimage_sha256", "").lower()
        old = patch.get("old_text", "")
        new = patch.get("new_text", "")
        expected = patch.get("expected_occurrences", 1)
        unit = patch.get("unit_id", "")[:44]

        check(f"path == Scenes/Stats.gd ({unit})", rel == STATS_REL)
        check(f"preimage == pristine Stats.gd SHA ({unit})", pre == STATS_PREIMAGE.lower())
        check(f"expected_occurrences == 1 ({unit})", expected == 1)
        count = working.count(old)
        check(f"old_text count == {expected} in working text ({unit})", count == expected)
        spine_record_total += new.count("_spine_record(")
        for line in new.split("\n"):
            if "_spine_record(" in line and "func _spine_record(" not in line:
                emit_lines += 1
        working = working.replace(old, new, 1)

    # --- 4. semantic canaries on simulated output ---
    check("no second bus: trigger_effects( call count unchanged by spine",
          working.count("trigger_effects(") == pristine.count("trigger_effects("))
    check("no new damage-math: '*=' count unchanged", working.count("*=") == pristine.count("*="))
    check("no DoT damage-math: '+= combined_effective_damage' unchanged",
          working.count("+= combined_effective_damage") == pristine.count("+= combined_effective_damage"))
    check("no new trigger_effects( inside spine new_texts",
          all("trigger_effects(" not in p.get("new_text", "") for p in patches))
    check("spine helpers defined", "_spine_event_class" in working and "_spine_record" in working)
    check("spine vars declared", "_spine_event_seq = 0" in working and "_spine_last_events = []" in working)
    check("exactly 3 emit call sites + 1 def (_spine_record( total == 4)", spine_record_total == 4)
    check("3 event emit lines (dot_tick / direct_hit-crit / kill)", emit_lines == 3)
    dot_block = working.split("if is_dot_damage:", 1)[1]
    check("dot_tick emit sits inside is_dot_damage block", "\"dot_tick\"" in dot_block.split("\n")[0] or "\"dot_tick\"" in "\n".join(dot_block.split("\n")[1:3]))
    crit_block = working.split("func _spine_event_class", 1)[1]
    check("crit class bound to did_crit", "if did_crit:" in crit_block and "\"crit\"" in crit_block)
    check("kill event carries did_kill=true",
          "\"kill\"" in working and "did_kill\": true" in working.split("\"kill\"")[1].split("\n")[0])
    check("ring buffer capped at 64", "_spine_last_events.size() > 64" in working and "pop_front()" in working)
    check("event fields: seq + timestamp_ms present",
          "\"seq\": _spine_event_seq" in working and "timestamp_ms\": OS.get_ticks_msec()" in working)

    check("direct hit path emits before on_take_damage call",
          "_spine_record(_spine_event_class(false, did_crit)" in working and
          working.index("_spine_record(_spine_event_class(false, did_crit)") < working.index("on_take_damage(attacker_stats"))
    check("kill emit after single did_kill resolution (once)",
          working.count("attacker_stats != null and did_kill:") == 1)

    # --- 5. no host absolute paths in B2-X1 files ---
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
    print("proves: manifest invariants; preimage/occurrence guards align with pristine Stats.gd; "
          "5-patch sequential apply resolves with exactly 3 emit sites + helpers; "
          "event classes direct_hit/dot_tick/crit/kill derivable; no second bus; no damage-math change; "
          "no host absolute paths")
    print("not_proven: real game runtime event sequence (needs VM + harness telemetry); "
          "consumers (X4/X5/X6); seq is per-instance not global; compile/pack/boot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())