"""Pytest bootstrap for scripts/ai/tests.

Several legacy test modules import sibling helpers directly
(`from test_helpers import ...`).  Under unittest discovery the start dir is
on sys.path so that works; under plain `pytest <path>` invocations it does
not.  Inserting this directory here keeps both styles working.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
