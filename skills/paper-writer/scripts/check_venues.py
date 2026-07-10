#!/usr/bin/env python3
"""Consistency check for the venue-knowledge triple:
`shared/venue_profiles.md` (prose profiles + Defaults YAML block) ↔
`skills/paper-writer/style/<venue>.md` ↔ `check_tex.py` MUST_INCLUDE_PATTERNS.

Venue knowledge lives in three places that must not drift. Deterministically
verifies, per venue in the `Defaults by venue` block:

  * a matching `## <Venue>` prose section exists          (missing = blocking)
  * a `style/<venue>.md` file exists                      (missing = blocking)
  * every `must_include` token resolves — builtin in check_tex.py or in the
    venue's own `must_include_patterns`                   (unknown = blocking)
  * every `must_include_patterns` regex compiles          (invalid = blocking)
  * provenance present: `as_of` (ISO date) + `sources`    (missing = blocking)
  * `unverified` entries name real fields of that venue   (unknown = blocking)
  * `as_of` older than --max-age-days                     (stale = warning)
  * prose section with no Defaults entry (except Generic) (orphan = warning)
  * pattern shadowing a builtin token                     (shadow = warning)

Run after every venue-calibration and in CI; it would have caught the
`proofs` vs `proofs_in_main` drift that shipped with the initial profiles.

Usage:
    python3 check_venues.py [--profiles shared/venue_profiles.md]
        [--style-dir skills/paper-writer/style] [--max-age-days 365] [--json]

Exit codes: 0 = clean, 1 = blocking findings, 2 = usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_tex  # noqa: E402  (MUST_INCLUDE_PATTERNS is the builtin token table)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILES = SCRIPT_DIR.parent.parent.parent / "shared" / "venue_profiles.md"
DEFAULT_STYLE_DIR = SCRIPT_DIR.parent / "style"

DEFAULTS_HEADING_RE = re.compile(
    r"^## Defaults by venue.*?```yaml\n(.*?)```", re.DOTALL | re.MULTILINE)
SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)
PERSONA_ONLY_SECTIONS = {"generic"}  # peer-reviewer fallback: no Defaults by design


def slug(heading: str) -> str:
    base = heading.split(" (")[0]
    return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")


def strip_quotes(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def parse_value(v: str):
    if v == "{}":
        return {}
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [strip_quotes(x.strip()) for x in inner.split(",")] if inner else []
    return strip_quotes(v)


def parse_defaults(yaml_text: str) -> tuple[dict, list[str]]:
    """Parse the restricted YAML subset used by the Defaults block:
    venue → flat keys with scalar / inline-list values, plus one nesting
    level for block lists (`- item`) and string maps (`key: value`)."""
    venues: dict[str, dict] = {}
    errors: list[str] = []
    venue = subkey = None
    for lineno, raw in enumerate(yaml_text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0:
            m = re.match(r"^([A-Za-z0-9_]+):\s*$", line)
            if not m:
                errors.append(f"yaml line {lineno}: expected '<venue>:', got {line!r}")
                venue = None
                continue
            venue = m.group(1)
            venues[venue] = {}
            subkey = None
        elif indent == 2 and venue:
            m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
            if not m:
                errors.append(f"yaml line {lineno}: expected 'key: value'")
                continue
            key, val = m.group(1), m.group(2).strip()
            if val:
                venues[venue][key] = parse_value(val)
                subkey = None
            else:
                venues[venue][key] = {}
                subkey = key
        elif indent >= 4 and venue and subkey is not None:
            container = venues[venue][subkey]
            if line.startswith("- "):
                if container == {}:
                    container = venues[venue][subkey] = []
                if isinstance(container, list):
                    container.append(strip_quotes(line[2:].strip()))
                else:
                    errors.append(f"yaml line {lineno}: list item under map {subkey!r}")
            else:
                m = re.match(r"^([A-Za-z0-9_]+):\s*(.+)$", line)
                if m and isinstance(container, dict):
                    container[m.group(1)] = strip_quotes(m.group(2).strip())
                else:
                    errors.append(f"yaml line {lineno}: cannot parse under {subkey!r}")
        else:
            errors.append(f"yaml line {lineno}: unexpected indent {indent}")
    return venues, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profiles", default=str(DEFAULT_PROFILES),
                    help="path to venue_profiles.md")
    ap.add_argument("--style-dir", default=str(DEFAULT_STYLE_DIR),
                    help="directory of per-venue style files")
    ap.add_argument("--max-age-days", type=int, default=365,
                    help="as_of older than this → stale warning (default 365)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    profiles_path = Path(args.profiles)
    style_dir = Path(args.style_dir)
    if not profiles_path.exists():
        print(f"error: {profiles_path} not found", file=sys.stderr)
        return 2
    if not style_dir.is_dir():
        print(f"error: style dir {style_dir} not found", file=sys.stderr)
        return 2

    md = profiles_path.read_text(encoding="utf-8", errors="replace")
    blocking: list[str] = []
    warnings: list[str] = []

    m = DEFAULTS_HEADING_RE.search(md)
    if not m:
        blocking.append("'## Defaults by venue' yaml block not found")
        venues = {}
    else:
        venues, errors = parse_defaults(m.group(1))
        blocking.extend(errors)

    prose_sections = {slug(h) for h in SECTION_RE.findall(md)
                      if not h.startswith("Defaults by venue")}

    today = dt.date.today()
    for name, fields in venues.items():
        prefix = f"{name}: "
        if name not in prose_sections:
            blocking.append(prefix + f"no '## {name}' prose section in profiles")
        if not (style_dir / f"{name}.md").exists():
            blocking.append(prefix + f"style file missing: {style_dir / (name + '.md')}")

        patterns = fields.get("must_include_patterns", {})
        if not isinstance(patterns, dict):
            blocking.append(prefix + "must_include_patterns must be a map")
            patterns = {}
        for token, regex in patterns.items():
            try:
                re.compile(regex)
            except re.error as exc:
                blocking.append(prefix + f"pattern {token!r} does not compile: {exc}")
            if token in check_tex.MUST_INCLUDE_PATTERNS:
                warnings.append(prefix + f"pattern {token!r} shadows a builtin")

        tokens = fields.get("must_include", [])
        if not isinstance(tokens, list):
            blocking.append(prefix + "must_include must be a list")
            tokens = []
        for token in tokens:
            if token not in check_tex.MUST_INCLUDE_PATTERNS and token not in patterns:
                blocking.append(
                    prefix + f"must_include token {token!r} has no pattern "
                    "(not builtin in check_tex.py, not in must_include_patterns)")

        as_of = fields.get("as_of")
        if not as_of or not isinstance(as_of, str):
            blocking.append(prefix + "missing as_of (ISO date of verification)")
        else:
            try:
                age = (today - dt.date.fromisoformat(as_of)).days
                if age > args.max_age_days:
                    warnings.append(
                        prefix + f"as_of {as_of} is {age} days old — re-verify "
                        "against current CFP (run venue-calibration)")
            except ValueError:
                blocking.append(prefix + f"as_of {as_of!r} is not an ISO date")
        sources = fields.get("sources")
        if not sources or not isinstance(sources, list):
            blocking.append(prefix + "missing sources (official URLs backing "
                            "the verified fields)")

        unverified = fields.get("unverified", [])
        if not isinstance(unverified, list):
            blocking.append(prefix + "unverified must be a list of field names")
            unverified = []
        for field in unverified:
            if field not in fields:
                blocking.append(prefix + f"unverified names unknown field {field!r}")

    for section in prose_sections - set(venues) - PERSONA_ONLY_SECTIONS:
        warnings.append(f"prose section '{section}' has no Defaults entry "
                        "(persona-only sections other than Generic are suspicious)")

    report = {"venues_checked": sorted(venues), "blocking": blocking,
              "warnings": warnings}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"checked {len(venues)} venue(s) in {profiles_path}")
        for item in blocking:
            print(f"  BLOCKING {item}")
        for item in warnings:
            print(f"  warning {item}")
        print("RESULT: " + ("BLOCKING FINDINGS" if blocking else
                            f"clean ({len(warnings)} warning(s))"))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
