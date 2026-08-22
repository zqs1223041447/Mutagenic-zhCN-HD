#!/usr/bin/env python3
"""Negative fixture: a production script hardcoding one machine's absolute path.
The absolute-path scanner MUST classify this as production_hardcode/FAIL.
"""
from pathlib import Path

ROOT = Path(r"C:\Users\Someone\Mutagenic")
OUT = ROOT / "10_logs/sample.json"