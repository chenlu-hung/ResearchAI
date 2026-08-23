#!/usr/bin/env python3
"""Ratchet the test suite: the collected test count may never silently drop.

A deleted or accidentally un-collected test is invisible in a green CI run —
the suite still passes, it just checks less. This pins the count in
`tests/baseline_count.txt` and fails on any mismatch:

  * collected < baseline -> regression; tests disappeared.
  * collected > baseline -> the ratchet needs advancing; run --update and
    commit the new baseline in the same commit as the new tests.

Both directions fail so the baseline is always exact rather than a stale
lower bound that drifts far below reality.

Usage:
    python3 scripts/check_test_count.py [--update] [--baseline PATH]

Exit codes: 0 = matches baseline, 1 = mismatch or collection failure,
2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "tests" / "baseline_count.txt"
COLLECTED_RE = re.compile(r"(\d+) tests? collected")


def collect_count() -> tuple[int, str]:
    """Return (count, raw_output) from a pytest collection-only run."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--collect-only"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"pytest collection failed (rc={result.returncode}):\n{output}")
    match = COLLECTED_RE.search(output)
    if not match:
        raise RuntimeError(f"cannot parse a collected-test count from:\n{output}")
    return int(match.group(1)), output


def read_baseline(path: Path) -> int | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return int(text) if text.isdigit() else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--update", action="store_true",
                        help="write the current count to the baseline file")
    args = parser.parse_args()

    try:
        count, _ = collect_count()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.update:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(f"{count}\n", encoding="utf-8")
        print(f"test count baseline: written {count} to {args.baseline}")
        return 0

    baseline = read_baseline(args.baseline)
    if baseline is None:
        print(f"ERROR: no usable baseline at {args.baseline}; "
              "run scripts/check_test_count.py --update")
        return 1
    if count < baseline:
        print(f"ERROR: collected {count} tests, baseline is {baseline} — "
              f"{baseline - count} test(s) disappeared. Restore them, or lower the "
              "baseline deliberately with --update and say why in the commit.")
        return 1
    if count > baseline:
        print(f"ERROR: collected {count} tests, baseline is {baseline} — advance the "
              "ratchet: run scripts/check_test_count.py --update and commit "
              "tests/baseline_count.txt alongside the new tests.")
        return 1
    print(f"test count: PASS ({count} collected, baseline {baseline})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
