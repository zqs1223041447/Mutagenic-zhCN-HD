#!/usr/bin/env python3
"""P3-A/H2 probe CLI: E1 character entry + E8 save/load roundtrip + H2 position.

Runs two headless driver scenes and emits two evidence files:

  1. res://scenes/Levels/_validate/P3ADriver.tscn
     -> E1 (LoadGame -> character selectable/selected) and the original E8
        identity/class/account_level/account_xp roundtrip.
     -> evidence: migration/conversion/p3_a_character_save.json

  2. res://scenes/Projectiles/_validate/p3_h2_position_driver.tscn
     -> P3-H2 position persistence: enter world context -> do_save_game ->
        reset_saved_state -> load_game -> position roundtrips within
        tolerance; without world context the field is omitted entirely
        (pre-H2 schema shape, backward compatible).
     -> evidence: migration/conversion/p3_h2_position_save.json

Overall verdict is PASS only when both drivers pass.

Usage:
    python scripts/validate/run_p3_a_character_save.py \
        [--out PATH] [--h2-out PATH] [--timeout 240]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p3_probe_common as common  # noqa: E402

LEGACY_DRIVER = "res://scenes/Levels/_validate/P3ADriver.tscn"
H2_DRIVER = "res://scenes/Projectiles/_validate/p3_h2_position_driver.tscn"


def _run_phase(engine: dict, product: Path, driver_scene: str,
               timeout_s: int) -> tuple[dict, list[dict], bool, dict | None, list[str]]:
    final, attempts, flaked = common.execute_with_retry(
        Path(str(engine["binary"])), product, driver_scene, timeout_s=timeout_s)
    result = common.extract_result_line(final["stdout"])
    script_errors = common.extract_script_errors(final["stdout"], final["stderr"])
    return final, attempts, flaked, result, script_errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None,
                    help="legacy E1/E8 evidence path")
    ap.add_argument("--h2-out", dest="h2_out", type=Path, default=None,
                    help="P3-H2 position evidence path")
    ap.add_argument("--timeout", type=int, default=240)
    args = ap.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    product = (args.product or (root / "product")).resolve()
    legacy_out = (args.out or (root / "migration" / "conversion"
                               / "p3_a_character_save.json")).resolve()
    h2_out = (args.h2_out or (root / "migration" / "conversion"
                              / "p3_h2_position_save.json")).resolve()

    discovery = common.discover_product_godot(root)
    engine = discovery.get("engine") or {}
    if engine.get("status") != "SUCCESS" or not engine.get("binary"):
        print(f"ERROR: engine binary not found ({engine.get('status')})", file=sys.stderr)
        return common.EXIT_NOT_PROVEN

    # --- phase 1: legacy E1/E8 driver ---------------------------------------
    l_final, l_attempts, l_flaked, l_result, l_errors = _run_phase(
        engine, product, LEGACY_DRIVER, args.timeout)
    l_evidence = common.build_evidence(
        task="P3-A", probe_id="P3-A-E1-E8", exit_criteria=["E1", "E8"],
        driver_scene=LEGACY_DRIVER,
        proves=("headless boot reaches Menu via LoadGame; StartButton opens the "
                "CharacterSelect popup; a character can be created and selected "
                "(E1); do_save_game writes a parsable save whose identity/class/"
                "account_level/account_xp survive GameState.load_game (E8)."),
        not_proven=("rendering/input fidelity of the real UI; position "
                    "persistence is covered by the P3-H2 phase of this CLI."),
        engine=engine, final=l_final, attempts=l_attempts, flaked=l_flaked,
        result=l_result, script_errors=l_errors)
    common.write_evidence(l_evidence, legacy_out)

    # --- phase 2: P3-H2 position roundtrip ----------------------------------
    h_final, h_attempts, h_flaked, h_result, h_errors = _run_phase(
        engine, product, H2_DRIVER, args.timeout)
    h_evidence = common.build_evidence(
        task="P3-H2", probe_id="P3-H2-position-save", exit_criteria=["E8"],
        driver_scene=H2_DRIVER,
        proves=("with a world context published into the globals, "
                "do_save_game persists the active character's position "
                "(x/y/level) into the per-character save schema; after "
                "reset_saved_state + the real load_game() the position "
                "roundtrips within 0.01 tolerance; without a world context "
                "the field is omitted entirely so pre-H2 saves stay "
                "backward compatible."),
        not_proven=("actual on-level player teleport on load (restore "
                    "application lives with the level lane); Steam-cloud "
                    "save paths; multi-character position isolation under "
                    "real gameplay."),
        engine=engine, final=h_final, attempts=h_attempts, flaked=h_flaked,
        result=h_result, script_errors=h_errors)
    common.write_evidence(h_evidence, h2_out)

    print(f"P3-A-E1-E8={l_evidence['verdict']} "
          f"(rc={l_final['returncode']}, script_errors={len(l_errors)}, "
          f"flaked={l_flaked}) evidence={legacy_out}")
    print(f"P3-H2-position-save={h_evidence['verdict']} "
          f"(rc={h_final['returncode']}, script_errors={len(h_errors)}, "
          f"flaked={h_flaked}) evidence={h2_out}")

    if l_evidence["verdict"] == "PASS" and h_evidence["verdict"] == "PASS":
        return common.EXIT_PASS
    if l_evidence["verdict"] in ("FAIL", "FLAKE") \
            or h_evidence["verdict"] in ("FAIL", "FLAKE"):
        return common.EXIT_FAIL
    return common.EXIT_NOT_PROVEN


if __name__ == "__main__":
    raise SystemExit(main())
