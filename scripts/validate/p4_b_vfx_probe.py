#!/usr/bin/env python3
"""P4-B F1 VFX-rhythm probe CLI.

Launches the headless driver scene
res://scenes/Mobs/_validate/p4_b_vfx_probe.tscn and emits machine-readable
evidence for the three F1 feedback points:

  * HitBurst element->color configuration + one-shot lifecycle + Mob wiring
    through the real Stats.apply_damage path (with per-mob cooldown throttle)
  * DissolveMob configurable death -> dissolve -> removal pacing
  * FloatingDamage normal/crit rhythm tiers

Subjective feel is out of scope; only machine-checkable structure/timing is
asserted.

    python scripts/validate/p4_b_vfx_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from p3_probe_common import probe_main

TASK = "P4-B"
PROBE_ID = "p4_b_vfx_probe"


def _resolve_out(argv: list[str] | None, default: Path) -> Path:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--out" in argv:
        return Path(argv[argv.index("--out") + 1])
    return default


def _sanitize_evidence(path: Path) -> None:
    """Replace host-absolute repo paths with a <repo> placeholder."""
    if not path.is_file():
        return
    root_str = str(Path(__file__).resolve().parents[2])

    def walk(obj):
        if isinstance(obj, dict):
            return {k: walk(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [walk(v) for v in obj]
        if isinstance(obj, str):
            return obj.replace(root_str, "<repo>").replace(
                root_str.replace("\\", "/"), "<repo>")
        return obj

    data = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(walk(data), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    out = _resolve_out(argv, root / "migration" / "conversion" / "p4_b_vfx.json")
    code = probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["F1"],
        driver_scene="res://scenes/Mobs/_validate/p4_b_vfx_probe.tscn",
        default_out=out,
        proves=("hit-burst element colors are configuration-driven and spawn "
                "through the real Mob damage path with cooldown throttling; "
                "death dissolve duration/delay drive both shader ramp and "
                "removal; floating-damage normal/crit rhythm tables differ "
                "and are honored (tint/pop/lifetime)"),
        not_proven=("subjective game feel (human adjudication lane); art "
                    "quality of procedural particles; GPUParticles rendering "
                    "on real hardware"),
    )
    _sanitize_evidence(out)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
