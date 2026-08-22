#!/usr/bin/env python3
"""P4-B F1 C1 real loot chain probe CLI (re-verifies E6 without the stub).

Launches the headless driver scene
res://scenes/UI/probes/p4_b_loot_real_probe.tscn: the restored REAL
OrbPickup/PortalPickup scenes plus the real Mob elite drop branch replace the
P3-D drop stub, and the E6 loop is re-verified end to end (touch -> vacuum ->
Stats.add_orb credit -> orb_pickup signal; elite kill -> OrbPickup on the
ground; portal confirm -> DeathScreen popup queued).

    python scripts/validate/p4_b_loot_real_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from p3_probe_common import probe_main

TASK = "P4-B"
PROBE_ID = "p4_b_loot_real_probe"


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
    out = _resolve_out(argv, root / "migration" / "conversion" / "p4_b_loot_real.json")
    code = probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["E6", "C1"],
        driver_scene="res://scenes/UI/probes/p4_b_loot_real_probe.tscn",
        default_out=out,
        proves=("the restored real scenes close the E6 loop without a stub: "
                "OrbPickup vacuum-pickup credits Stats.add_orb and fires "
                "orb_pickup; an elite mob killed via the real damage pipeline "
                "drops an OrbPickup through Mob._on_death; PortalPickup is "
                "persistent and its confirmation queues the DeathScreen "
                "popup through PopupManager"),
        not_proven=("visual art for the portal/orb drops (art lane owns "
                    "portal.png and aseprite orb animations); boss-kill "
                    "portal branch under a full stage run (harness scope)"),
    )
    _sanitize_evidence(out)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
