#!/usr/bin/env python3
"""Verify that governance docs point at files that exist.

A boundary document is only worth writing if it stays true. `POSITIONING.md`
says where each refusal is enforced, `shared/firm_rules.md` says which files
mirror a rule, `shared/mode_registry.md` says where each mode lives — and every
one of those claims decays the moment a file is renamed. A doc full of dead
paths reads exactly like a doc full of live ones.

Checks every backticked repo-relative path in the governance docs. Skipped by
design:

  * templates and globs — anything containing `...`, `<`, `{`, or `*`
  * directory references (trailing `/`), which include the deliberately absent
    ones like `.claude/skills/` that POSITIONING.md names as *rejected*
  * runtime output paths under gitignored trees (`docs/`, `paper/`, `refs/`,
    `reviews/`, `private/`, `results/`, `.research-state/`)
  * bare filenames with no `/`, which are usually prose ("this `SKILL.md`")

Usage:
    python3 scripts/check_doc_refs.py [doc ...]

Exit codes: 0 = every reference resolves, 1 = dead reference, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = (
    "README.md",
    "CLAUDE.md",
    "POSITIONING.md",
    "shared/firm_rules.md",
    "shared/mode_registry.md",
    "audits/README.md",
    "evals/README.md",
)
BACKTICKED_RE = re.compile(r"`([^`\n]+)`")
PATHISH_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]*$|^\.[A-Za-z0-9_][A-Za-z0-9_./-]*$")
RUNTIME_PREFIXES = (
    "docs/", "paper/", "refs/", "reviews/", "private/", "results/",
    ".research-state/", ".venv/", "tmp/",
)


def candidates(text: str) -> set[str]:
    found: set[str] = set()
    for token in BACKTICKED_RE.findall(text):
        token = token.strip()
        if "/" not in token or token.endswith("/"):
            continue
        if any(bad in token for bad in ("...", "<", ">", "{", "}", "*", " ", "$")):
            continue
        if not PATHISH_RE.match(token):
            continue
        if token.startswith(RUNTIME_PREFIXES):
            continue
        found.add(token)
    return found


def check(root: Path, docs: list[str]) -> list[str]:
    errors: list[str] = []
    for relative in docs:
        path = root / relative
        if not path.is_file():
            errors.append(f"governance doc {relative} does not exist")
            continue
        for reference in sorted(candidates(path.read_text(encoding="utf-8"))):
            if not (root / reference).exists():
                errors.append(f"{relative} references `{reference}`, which does not exist")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs", nargs="*", default=None)
    args = parser.parse_args()
    docs = list(args.docs) if args.docs else list(DEFAULT_DOCS)

    errors = check(ROOT, docs)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    checked = sum(len(candidates((ROOT / d).read_text(encoding="utf-8"))) for d in docs)
    print(f"doc refs: PASS ({len(docs)} doc(s), {checked} path reference(s) resolved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
