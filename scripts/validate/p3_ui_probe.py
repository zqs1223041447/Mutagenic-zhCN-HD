#!/usr/bin/env python3
"""P3-E UI probe CLI (Exit Criteria E7).

Launches the headless driver scene res://scenes/UI/probes/p3_ui_probe.tscn
(open SkillSelect and PassiveTreePopup via PopupManager, verify no crash,
close both, popup stack drains to zero) and emits machine-readable evidence.

    python scripts/validate/p3_ui_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from p3_probe_common import probe_main

TASK = "P3-E"
PROBE_ID = "p3_ui_probe"


def _resolve_out(argv: list[str] | None, default: Path) -> Path:
    """Mirror probe_main's --out handling so the wrapper can post-sanitize."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--out" in argv:
        return Path(argv[argv.index("--out") + 1])
    return default


def _sanitize_evidence(path: Path) -> None:
    """Replace host-absolute repo paths with a <repo> placeholder.

    Evidence records land in the git tree (migration/conversion/*.json);
    abs_path_scan classifies raw host paths there as production_hardcode.
    Runs after probe_main has already written the file.
    """
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
    out = _resolve_out(argv, root / "migration" / "conversion" / "p3_e_ui.json")
    code = probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["E7"],
        driver_scene="res://scenes/UI/probes/p3_ui_probe.tscn",
        default_out=out,
        proves=("the skill screen and the passive tree screen open headlessly "
                "through PopupManager against a seeded character, build their "
                "content (passive nodes instantiate) and close cleanly back "
                "to an empty popup stack without crashing"),
        not_proven=("visual layout/rendering fidelity, controller navigation "
                    "and allocation interactions inside the screens"),
    )
    _sanitize_evidence(out)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
