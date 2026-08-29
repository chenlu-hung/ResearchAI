#!/usr/bin/env python3
"""Pin the wording of rules that are duplicated across runtime prompts.

Several rules have to appear *inline* in many files: an agent that loads one
`SKILL.md` will not follow a rule that only lives in another file, so a
by-reference pointer would not work for them. Inlining is therefore correct —
and it is also how wording drifts. Nothing stops one copy being reworded while
the other twelve keep the old text, and the result is a repo that states two
different rules with equal authority.

`shared/firm_rules.md` is the canonical wording. Each rule block declares the
fragments every mirror must carry and the globs that select those mirrors.
This checks containment after whitespace normalization: re-wrapping a Markdown
paragraph is not drift, changing a word is.

Usage:
    python3 scripts/check_firm_rules.py [--rules shared/firm_rules.md]

Exit codes: 0 = every mirror carries its canonical fragments, 1 = drift,
2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "shared" / "firm_rules.md"

OPEN_RE = re.compile(
    r"<!--\s*firm-rule:\s*id=(?P<id>[A-Z0-9-]+)\s+mirrors=(?P<mirrors>[^>]+?)"
    r"(?:\s+match=(?P<match>exact|ci))?\s*-->")
CLOSE_TEMPLATE = "<!-- /firm-rule: {rule_id} -->"
INDEX_ROW_RE = re.compile(r"^\|\s*`(?P<id>[A-Z0-9-]+)`\s*\|", re.MULTILINE)


def normalize(text: str) -> str:
    """Collapse all whitespace, so re-wrapping a paragraph is not a difference."""
    return " ".join(text.split())


def parse_fragments(body: str) -> list[str]:
    """Blockquote paragraphs inside a rule block, split on a lone `>` line."""
    fragments: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == ">":
            if current:
                fragments.append(" ".join(current))
                current = []
        elif stripped.startswith("> "):
            current.append(stripped[2:].strip())
    if current:
        fragments.append(" ".join(current))
    return [fragment for fragment in fragments if fragment]


def parse_rules(path: Path) -> tuple[list[dict], list[str]]:
    text = path.read_text(encoding="utf-8")
    rules: list[dict] = []
    errors: list[str] = []
    for match in OPEN_RE.finditer(text):
        rule_id = match.group("id")
        close = CLOSE_TEMPLATE.format(rule_id=rule_id)
        end = text.find(close, match.end())
        if end == -1:
            errors.append(f"{rule_id}: no closing marker `{close}`")
            continue
        body = text[match.end():end]
        fragments = parse_fragments(body)
        if not fragments:
            errors.append(f"{rule_id}: block declares no `> ` fragments to pin")
        globs = [g.strip() for g in match.group("mirrors").split(";") if g.strip()]
        if not globs:
            errors.append(f"{rule_id}: block declares no mirrors")
        rules.append({"id": rule_id, "globs": globs, "fragments": fragments,
                      "match": match.group("match") or "exact"})

    indexed = set(INDEX_ROW_RE.findall(text))
    declared = {rule["id"] for rule in rules}
    for rule_id in sorted(declared - indexed):
        errors.append(f"{rule_id}: has a rule block but no row in the rule index")
    for rule_id in sorted(indexed - declared):
        errors.append(f"{rule_id}: listed in the rule index but has no rule block")
    return rules, errors


def check(root: Path, rules_path: Path) -> list[str]:
    if not rules_path.is_file():
        return [f"missing canonical rules file {rules_path}"]
    rules, errors = parse_rules(rules_path)

    for rule in rules:
        mirrors: list[Path] = []
        for pattern in rule["globs"]:
            matched = sorted(root.glob(pattern))
            if not matched:
                errors.append(
                    f"{rule['id']}: mirror glob {pattern!r} matches no file — "
                    "a typo here silently disables the pin")
            mirrors.extend(matched)
        for path in mirrors:
            if path.resolve() == rules_path.resolve():
                continue  # the canonical file is not a mirror of itself
            haystack = normalize(path.read_text(encoding="utf-8"))
            if rule["match"] == "ci":
                haystack = haystack.lower()
            for fragment in rule["fragments"]:
                needle = normalize(fragment)
                if rule["match"] == "ci":
                    needle = needle.lower()
                if needle not in haystack:
                    errors.append(
                        f"{rule['id']}: {path.relative_to(root)} has drifted from the "
                        f"canonical wording — missing: {fragment[:90]}...")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("root", nargs="?", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    errors = check(root, args.rules if args.rules.is_absolute() else root / args.rules)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    rules, _ = parse_rules(args.rules if args.rules.is_absolute() else root / args.rules)
    pinned = sum(len(rule["fragments"]) for rule in rules)
    print(f"firm rules: PASS ({len(rules)} rule(s), {pinned} pinned fragment(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
