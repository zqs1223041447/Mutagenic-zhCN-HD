#!/usr/bin/env python3
"""OS-level default (Windows fonts dir). Scanner MUST classify local_config/INFO,
not production_hardcode.
"""
import argparse
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--cjk", type=Path, default=Path("C:/Windows/Fonts/Deng.ttf"))
args = ap.parse_args()
print(args.cjk)