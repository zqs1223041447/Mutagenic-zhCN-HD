#!/usr/bin/env python3
"""One-shot rebuild pipeline: worktree -> 08_pack -> pck -> embedded exe.

Steps:
  1. build_pack.py       (03_raw + 06_worktree overlay -> 08_pack)
  2. merge CJK fonts into 08_pack/Fonts   (if --with-fonts)
  3. gdre --pck-create   (08_pack -> tmp pck)
  4. embed_pck.py        (original exe + pck -> 09_output/Mutagenic_zh.exe)

Usage:
    python scripts/rebuild.py [--no-fonts] [--output 09_output/Mutagenic_zh.exe]
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"
PY = ROOT / "02_tools/venv/Scripts/python.exe"


def run(args: list, cwd: Path = ROOT):
    print(f">>> {' '.join(str(a) for a in args)}")
    r = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    tail = "\n".join(r.stdout.strip().splitlines()[-6:])
    if r.stdout.strip():
        print(tail)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-2000:])
        sys.exit(r.returncode)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fonts", action="store_true")
    ap.add_argument("--output", type=Path, default=ROOT / "09_output/Mutagenic_zh.exe")
    ap.add_argument("--skip-pack-build", action="store_true",
                    help="skip build_pack (reuse existing 08_pack)")
    args = ap.parse_args()

    tmp_pck = ROOT / "09_output/_tmp_rebuild.pck"

    # 1. pack tree
    import json
    pack_dir = ROOT / "08_pack"
    if not args.skip_pack_build:
        if pack_dir.exists():
            shutil.rmtree(pack_dir)
        run([PY, "scripts/build_pack.py"])

    # 2. fonts overlay
    if not args.no_fonts:
        merged = ROOT / "02_tools/fonts_merged"
        if not merged.exists():
            print("merged fonts missing; run scripts/merge_fonts2.py first")
            return 1
        for f in merged.glob("*.ttf"):
            shutil.copy2(f, pack_dir / "Fonts" / f.name)
        print(f">>> fonts copied: {len(list(merged.glob('*.ttf')))}")

    # 3. pck
    if tmp_pck.exists():
        tmp_pck.unlink()
    run([GDRE, "--headless", f"--pck-create={pack_dir}",
         "--pck-version=1", "--pck-engine-version=3.5.3",
         f"--output={tmp_pck}"])

    # 4. embed
    run([PY, "scripts/embed_pck.py", "00_original/Mutagenic.exe",
         str(tmp_pck), "-o", str(args.output)])

    # 5. verify with gdre
    run([GDRE, "--headless", f"--list-files={args.output}"],
        )
    print("REBUILD COMPLETE:", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())