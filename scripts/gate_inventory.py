#!/usr/bin/env python3
"""Enumerate the repo's whole check surface, so a retirement audit starts from
a generated list rather than from memory.

Every quarterly review in `audits/` opens with this inventory. The script only
counts and dates things — it never rules on them. The `verdict` column is left
blank on purpose: keep / merge / retire is a human judgment, and recording it
is the point of the audit (see `audits/README.md`).

Surfaces covered:
  * lifecycle-gate   — gate artifacts in shared/prompts/research_lifecycle.md
  * mode             — every row of shared/mode_registry.md (the registry, not a
                       glob: literature-explorer's modes do not live under modes/)
  * checklist        — skills/<skill>/checklists/*.md
  * prompt-contract  — shared/prompts/*.md
  * executable-check — scripts/*.py, skills/<skill>/scripts/*.py
  * venue-style      — skills/paper-writer/style/*.md

Usage:
    python3 scripts/gate_inventory.py [--output audits/YYYY-MM-DD-gate-inventory.md]
                                      [--today YYYY-MM-DD]

Exit codes: 0 = inventory produced, 2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE = ROOT / "shared" / "prompts" / "research_lifecycle.md"
MODE_REGISTRY = ROOT / "shared" / "mode_registry.md"
GATE_SECTION_RE = re.compile(
    r"^## Gate artifact schemas\s*$(.*?)(?=^## )", re.DOTALL | re.MULTILINE)
SUBHEADING_RE = re.compile(r"^### (.+?)\s*$", re.MULTILINE)


def last_touched(path: Path) -> str:
    """Author date of the newest commit touching `path`, or 'untracked'."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", str(path)],
            capture_output=True, text=True, cwd=ROOT, check=False,
        )
    except OSError:
        return "unknown"
    date = result.stdout.strip()
    return date if date else "untracked"


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def age_days(date_text: str, today: dt.date) -> str:
    try:
        return str((today - dt.date.fromisoformat(date_text)).days)
    except ValueError:
        return "—"


def lifecycle_gates() -> list[str]:
    if not LIFECYCLE.is_file():
        return []
    match = GATE_SECTION_RE.search(LIFECYCLE.read_text(encoding="utf-8"))
    if not match:
        return []
    return SUBHEADING_RE.findall(match.group(1))


def registered_modes() -> list[tuple[str, str, str]]:
    """Rows of shared/mode_registry.md, via the checker that already parses it."""
    if not MODE_REGISTRY.is_file():
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_mode_registry import parse_registry  # noqa: PLC0415

    rows, _ = parse_registry(MODE_REGISTRY)
    return rows


def collect(today: dt.date) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    lifecycle_date = last_touched(LIFECYCLE) if LIFECYCLE.is_file() else "unknown"
    for name in lifecycle_gates():
        rows.append({
            "kind": "lifecycle-gate",
            "name": name,
            "path": f"{LIFECYCLE.relative_to(ROOT)} § {name}",
            "lines": "—",
            "touched": lifecycle_date,
            "age": age_days(lifecycle_date, today),
        })

    # Modes come from the registry rather than a glob, so a mode that does not
    # live under modes/ is still inventoried. check_mode_registry.py is what
    # keeps the registry honest about the filesystem.
    for skill, mode, relative in registered_modes():
        path = ROOT / relative
        touched = last_touched(path) if path.is_file() else "missing"
        rows.append({
            "kind": "mode",
            "name": f"{skill}/{mode}",
            "path": relative,
            "lines": str(line_count(path)) if path.is_file() else "—",
            "touched": touched,
            "age": age_days(touched, today),
        })

    globs: list[tuple[str, str]] = [
        ("checklist", "skills/*/checklists/*.md"),
        ("prompt-contract", "shared/prompts/*.md"),
        ("executable-check", "scripts/*.py"),
        ("executable-check", "skills/*/scripts/*.py"),
        ("venue-style", "skills/paper-writer/style/*.md"),
    ]
    for kind, pattern in globs:
        for path in sorted(ROOT.glob(pattern)):
            relative = path.relative_to(ROOT)
            touched = last_touched(path)
            parts = relative.parts
            name = f"{parts[1]}/{path.stem}" if parts[0] == "skills" else path.stem
            rows.append({
                "kind": kind,
                "name": name,
                "path": str(relative),
                "lines": str(line_count(path)),
                "touched": touched,
                "age": age_days(touched, today),
            })

    rows.sort(key=lambda row: (row["kind"], row["name"]))
    return rows


def render(rows: list[dict[str, str]], today: dt.date) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1

    out = [
        f"# Gate inventory — {today.isoformat()}",
        "",
        "Generated by `scripts/gate_inventory.py`. The inventory is mechanical;",
        "the `verdict` column is not. Fill it in per `audits/README.md` and save the",
        f"result as `audits/{today.isoformat()}-<topic>.md`.",
        "",
        "## Surface counts",
        "",
        "| Surface | Count |",
        "|---|---|",
    ]
    out.extend(f"| {kind} | {count} |" for kind, count in sorted(counts.items()))
    out.append(f"| **total** | **{len(rows)}** |")
    out.extend([
        "",
        "## Inventory",
        "",
        "`verdict` is one of keep / merge / retire; blank means not yet reviewed.",
        "",
        "| Surface | Name | Path | Lines | Last touched | Age (d) | Verdict | Rationale |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for row in rows:
        out.append(
            f"| {row['kind']} | {row['name']} | `{row['path']}` | {row['lines']} "
            f"| {row['touched']} | {row['age']} |  |  |"
        )
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="write here instead of stdout")
    parser.add_argument("--today", type=dt.date.fromisoformat, default=None,
                        help="override for tests")
    args = parser.parse_args()

    today = args.today or dt.date.today()
    text = render(collect(today), today)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"gate inventory: written to {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
