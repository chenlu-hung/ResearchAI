#!/usr/bin/env python3
"""Fail when the gate-retirement audit is overdue.

Checks accumulate: every gate, mode, and checklist that ships stays shipped,
because nothing forces anyone to ask whether it still earns its maintenance
and false-alarm cost. `audits/README.md` sets a quarterly review; this makes
"quarterly" observable instead of aspirational, by reading the newest dated
audit in `audits/` and going red once it ages out.

An audit is any `audits/YYYY-MM-DD-<topic>.md`. README and TEMPLATE files are
not audits and are ignored.

Age alone is a weak check: a generated-but-unreviewed inventory would satisfy
it while nothing was actually reviewed. So the newest audit is also scanned for
inventory rows whose `Verdict` cell is still blank, and any leftover row keeps
the check red.

Usage:
    python3 scripts/check_audit_due.py [--max-age-days 120] [--today YYYY-MM-DD]

Exit codes: 0 = current, 1 = overdue or no audit found, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDITS = ROOT / "audits"
AUDIT_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-.+\.md$")
# gate_inventory.py rows: | Surface | Name | Path | Lines | Touched | Age | Verdict | Rationale |
INVENTORY_COLUMNS = 8
VERDICT_COLUMN = 6


def unreviewed_rows(path: Path) -> int:
    """Count inventory rows in `path` whose Verdict cell is still blank."""
    blank = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if len(cells) != INVENTORY_COLUMNS:
            continue
        if set("".join(cells)) <= {"-", ":"}:  # separator row
            continue
        if cells[VERDICT_COLUMN].lower() in {"verdict", ""}:
            blank += cells[VERDICT_COLUMN] == ""
    return blank


def newest_audit(audits_dir: Path) -> tuple[dt.date, Path] | None:
    found: list[tuple[dt.date, Path]] = []
    for path in sorted(audits_dir.glob("*.md")):
        match = AUDIT_RE.match(path.name)
        if not match:
            continue
        try:
            found.append((dt.date.fromisoformat(match.group(1)), path))
        except ValueError:
            continue
    return max(found) if found else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audits-dir", type=Path, default=DEFAULT_AUDITS)
    parser.add_argument("--max-age-days", type=int, default=120,
                        help="quarterly cadence per audits/README.md")
    parser.add_argument("--today", type=dt.date.fromisoformat,
                        default=None, help="override for tests")
    args = parser.parse_args()

    today = args.today or dt.date.today()
    if not args.audits_dir.is_dir():
        print(f"ERROR: no audits directory at {args.audits_dir}")
        return 1

    newest = newest_audit(args.audits_dir)
    if newest is None:
        print(f"ERROR: no dated audit in {args.audits_dir} — "
              "run scripts/gate_inventory.py and record the first review "
              "per audits/README.md")
        return 1

    audit_date, path = newest
    age = (today - audit_date).days
    if age > args.max_age_days:
        print(f"ERROR: newest audit {path.name} is {age} days old "
              f"(limit {args.max_age_days}) — the retirement review is overdue. "
              "Run scripts/gate_inventory.py, rule on each row, and file the "
              "result in audits/.")
        return 1
    blank = unreviewed_rows(path)
    if blank:
        print(f"ERROR: {path.name} has {blank} inventory row(s) with no verdict — "
              "a generated inventory is not a review. Rule keep / merge / retire "
              "on every row per audits/README.md.")
        return 1

    print(f"audit cadence: PASS ({path.name}, {age} days old, "
          f"limit {args.max_age_days})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
