"""Compare script-file composition of two EXEs' embedded PCKs.

Uses GDRE --list-files and counts entries by suffix, so it verifies the FINAL
artifact rather than the intermediate 08_pack tree.

Usage:
    python scripts/verify_pck_composition.py 00_original/Mutagenic.exe 09_output/Mutagenic.exe
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"


def listing(exe: Path) -> list[str]:
    r = subprocess.run(
        [str(GDRE), "--headless", f"--list-files={exe}"],
        capture_output=True, text=True,
    )
    return [ln.strip() for ln in r.stdout.splitlines()
            if ln.strip().startswith("res://")]


def compose(paths: list[str]) -> dict:
    return {
        "total": len(paths),
        ".gde": sum(p.endswith(".gde") for p in paths),
        ".gd.remap": sum(p.endswith(".gd.remap") for p in paths),
        "plain .gd": sum(p.endswith(".gd") for p in paths),
        ".tscn": sum(p.endswith(".tscn") for p in paths),
        ".tres": sum(p.endswith(".tres") for p in paths),
    }


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    ca, cb = compose(listing(a)), compose(listing(b))

    print(f"{'metric':<14}{a.name:>22}{b.name:>22}{'':>4}")
    print("-" * 62)
    ok = True
    for k in ca:
        same = ca[k] == cb[k]
        ok &= same
        print(f"{k:<14}{ca[k]:>22}{cb[k]:>22}  {'OK' if same else 'DIFF'}")
    print("-" * 62)
    print(f"VERDICT: {'PASS - composition identical to original' if ok else 'DIFF - see above'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
