#!/usr/bin/env python3
"""Skill-local entry point that delegates to the plugin's shared evidence core."""

from __future__ import annotations

import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SHARED = PLUGIN_ROOT / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from evidence_core.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
