#!/usr/bin/env python3
"""Turn venue-provenance staleness into a failing signal on a schedule.

`CLAUDE.md` requires that venue and NSTC ground truth carry `as_of`/`sources`
and be re-verified per cycle. `check_venues.py` already computes the age, but
reports staleness as a *warning* (exit 0) — correct for a per-commit gate,
where a stale CFP must not block an unrelated change, and useless as a
reminder, because nothing ever goes red.

This wrapper re-reads the same computation and exits non-zero, so the
scheduled maintenance workflow surfaces staleness instead of the author
having to remember. It deliberately does not re-implement the age check:
`check_venues.py` stays the single source of truth for what "stale" means.
The coupling is the warning shape, pinned by
`tests/test_maintenance_scripts.py::test_stale_warning_shape_is_still_matched`.

Usage:
    python3 scripts/check_freshness.py [--max-age-days 180]

Exit codes: 0 = fresh, 1 = stale or blocking findings, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_VENUES = ROOT / "skills" / "paper-writer" / "scripts" / "check_venues.py"
# Matches check_venues.py's staleness warning: "<venue>: as_of <date> is N days old".
STALE_RE = re.compile(r"\bas_of\s+\d{4}-\d{2}-\d{2}\s+is\s+\d+\s+days old\b")


def run_check_venues(max_age_days: int) -> dict:
    result = subprocess.run(
        [sys.executable, str(CHECK_VENUES), "--json",
         "--max-age-days", str(max_age_days)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"check_venues.py did not emit JSON (rc={result.returncode}): "
            f"{exc}\n{result.stdout}{result.stderr}"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-age-days", type=int, default=180,
        help="re-verify before the next submission cycle rather than after "
             "(check_venues.py's own default of 365 is a full cycle too late)")
    args = parser.parse_args()

    try:
        report = run_check_venues(args.max_age_days)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    blocking = report.get("blocking", [])
    stale = [w for w in report.get("warnings", []) if STALE_RE.search(w)]

    for item in blocking:
        print(f"ERROR: {item}")
    for item in stale:
        print(f"STALE: {item}")

    if blocking or stale:
        print(f"\nfreshness: FAIL ({len(blocking)} blocking, {len(stale)} stale) — "
              "re-verify against the current CFP via paper-writer "
              "venue-calibration, then update as_of/sources.")
        return 1
    print(f"freshness: PASS ({len(report.get('venues_checked', []))} venue(s) "
          f"within {args.max_age_days} days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
