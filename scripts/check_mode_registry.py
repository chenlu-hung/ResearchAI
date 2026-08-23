#!/usr/bin/env python3
"""Keep the mode surface consistent across the four places that declare it.

A mode exists in four declarations at once: the file on disk, the owning
`SKILL.md`'s `## Modes` table, the conductor's `routing.md`, and
`shared/mode_registry.md`. Drift between them fails silently and late — the
conductor routes to a mode file that was renamed, or a mode ships that no
routing path can ever reach, and either only shows up mid-run.

Verifies, against `shared/mode_registry.md`:

  * every registry row's mode file exists                     (missing = fail)
  * `skills/*/modes/*.md` on disk is exactly the registered set
                                             (orphan file / phantom row = fail)
  * each skill's own `## Modes` table lists exactly the modes registered for it
                                                       (either direction = fail)
  * every mode file referenced in routing.md is registered   (unknown = fail)
  * skills declared mode-less ship no `modes/` directory     (violation = fail)

Usage:
    python3 scripts/check_mode_registry.py [--registry shared/mode_registry.md]

Exit codes: 0 = consistent, 1 = drift, 2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "shared" / "mode_registry.md"
ROUTING_RELATIVE = "skills/research-conductor/routing.md"

MODE_PATH_RE = re.compile(r"`(skills/[a-z0-9-]+/(?:modes/)?[a-zA-Z0-9._-]+\.md)`")
ROUTING_REF_RE = re.compile(
    r"skills/(?P<skill>[a-z0-9-]+)/modes/(?P<mode>\{[^}]+\}|[a-z0-9-]+)\.md")
NO_MODE_ROW_RE = re.compile(r"^\|\s*`(?P<skill>[a-z0-9-]+)`\s*\|", re.MULTILINE)


def cells(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line[1:-1].split("|")]


def normalize_mode(text: str) -> str:
    """`survey` *(default)* and *(default)* survey are the same mode name."""
    text = text.replace("`", "").replace("*", "")
    text = text.replace("(default)", "").strip()
    return text


def parse_registry(path: Path) -> tuple[list[tuple[str, str, str]], set[str]]:
    rows: list[tuple[str, str, str]] = []
    modeless: set[str] = set()
    in_modeless = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_modeless = line.strip() == "## Skills with no modes"
            continue
        parsed = cells(line)
        if in_modeless:
            match = NO_MODE_ROW_RE.match(line)
            if match:
                modeless.add(match.group("skill"))
            continue
        if len(parsed) != 5:
            continue
        skill, mode, file_cell = parsed[0], parsed[1], parsed[2]
        file_match = MODE_PATH_RE.fullmatch(file_cell)
        if not file_match:
            continue
        rows.append((skill, normalize_mode(mode), file_match.group(1)))
    return rows, modeless


def expand_braces(token: str) -> list[str]:
    if not token.startswith("{"):
        return [token]
    return [part.strip() for part in token[1:-1].split(",") if part.strip()]


def check(root: Path, registry_path: Path) -> list[str]:
    if not registry_path.is_file():
        return [f"missing mode registry {registry_path}"]
    rows, modeless = parse_registry(registry_path)
    errors: list[str] = []
    if not rows:
        return ["mode registry parsed to zero rows — the table shape changed"]

    registered_paths = {path for _, _, path in rows}
    registered_by_skill: dict[str, set[str]] = {}
    for skill, mode, _ in rows:
        registered_by_skill.setdefault(skill, set()).add(mode)

    for skill, mode, relative in rows:
        if not (root / relative).is_file():
            errors.append(f"registry row {skill}/{mode} points at missing file {relative}")
        if not relative.startswith(f"skills/{skill}/"):
            errors.append(f"registry row {skill}/{mode} points outside its skill: {relative}")

    on_disk = {
        str(path.relative_to(root)) for path in sorted(root.glob("skills/*/modes/*.md"))
    }
    registered_modes_dir = {p for p in registered_paths if "/modes/" in p}
    for relative in sorted(on_disk - registered_modes_dir):
        errors.append(f"mode file {relative} exists but has no registry row")
    for relative in sorted(registered_modes_dir - on_disk):
        errors.append(f"registry row claims {relative}, which is not on disk")

    for skill in sorted(registered_by_skill):
        skill_md = root / "skills" / skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"registry names skill {skill} with no SKILL.md")
            continue
        declared: set[str] = set()
        in_modes = False
        for line in skill_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                in_modes = line.strip() == "## Modes"
                continue
            if not in_modes:
                continue
            parsed = cells(line)
            if len(parsed) < 2 or parsed[0].lower().strip() == "mode":
                continue
            if set("".join(parsed)) <= {"-", ":"}:
                continue
            name = normalize_mode(parsed[0])
            if name:
                declared.add(name)
        if not declared:
            errors.append(f"skills/{skill}/SKILL.md has no parseable `## Modes` table")
            continue
        for mode in sorted(declared - registered_by_skill[skill]):
            errors.append(f"skills/{skill}/SKILL.md lists mode {mode!r}, absent from the registry")
        for mode in sorted(registered_by_skill[skill] - declared):
            errors.append(f"registry lists {skill}/{mode}, absent from that skill's `## Modes` table")

    routing = root / ROUTING_RELATIVE
    if routing.is_file():
        routed: set[str] = set()
        for match in ROUTING_REF_RE.finditer(routing.read_text(encoding="utf-8")):
            for mode in expand_braces(match.group("mode")):
                routed.add(f"skills/{match.group('skill')}/modes/{mode}.md")
        for relative in sorted(routed - registered_paths):
            errors.append(f"routing.md routes to {relative}, which has no registry row")
    else:
        errors.append(f"missing {ROUTING_RELATIVE}")

    for skill in sorted(modeless):
        if (root / "skills" / skill / "modes").is_dir():
            errors.append(f"{skill} is registered as mode-less but ships a modes/ directory")
        if skill in registered_by_skill:
            errors.append(f"{skill} is registered both as mode-less and with modes")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("root", nargs="?", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    registry = args.registry if args.registry.is_absolute() else root / args.registry

    errors = check(root, registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    rows, modeless = parse_registry(registry)
    skills = len({skill for skill, _, _ in rows})
    print(f"mode registry: PASS ({len(rows)} modes across {skills} skills, "
          f"{len(modeless)} mode-less skill(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
