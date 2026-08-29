#!/usr/bin/env python3
"""Score a completed eval pack against the withheld key.

Reads the key from `evals/cases/` — the directory the runner never saw — and
compares it with the submitted answers. Prints the rationale only for cases
that were answered wrongly, so a scoring run does not itself become a way to
read the key for the cases that were not attempted.

Usage:
    python3 scripts/eval_score.py --answers <answers.json>
                                  [--pack <dir>] [--min-accuracy 0.8]

Exit codes: 0 = scored (and above --min-accuracy if given), 1 = below
threshold, digest mismatch, or unusable input, 2 = usage error. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "evals" / "cases"


def load_key(cases_dir: Path) -> dict[str, dict]:
    key: dict[str, dict] = {}
    for path in sorted(cases_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for case in data["cases"]:
            key[f"{data['surface']}/{case['id']}"] = {
                "surface": data["surface"],
                "answer": case["answer"],
                "because": case["because"],
            }
    return key


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", type=Path, required=True)
    parser.add_argument("--cases-dir", type=Path, default=CASES_DIR)
    parser.add_argument("--pack", type=Path, default=None,
                        help="verify the pack was built from the current cases")
    parser.add_argument("--min-accuracy", type=float, default=None)
    args = parser.parse_args()

    key = load_key(args.cases_dir)
    if not key:
        print(f"ERROR: no cases in {args.cases_dir}")
        return 1

    if args.pack:
        import hashlib
        digest = hashlib.sha256()
        for path in sorted(args.cases_dir.glob("*.json")):
            digest.update(path.name.encode("utf-8"))
            digest.update(path.read_bytes())
        manifest = json.loads((args.pack / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("cases_digest") != digest.hexdigest():
            print("ERROR: the cases changed after this pack was built — rebuild and "
                  "re-run rather than scoring against edited ground truth.")
            return 1

    submitted = json.loads(args.answers.read_text(encoding="utf-8"))
    by_surface: dict[str, list[int]] = {}
    wrong: list[tuple[str, str, str, str]] = []
    unanswered: list[str] = []

    for case_id, expected in sorted(key.items()):
        given = str(submitted.get(case_id, "")).strip().upper()
        surface = expected["surface"]
        by_surface.setdefault(surface, [0, 0])
        by_surface[surface][1] += 1
        if not given:
            unanswered.append(case_id)
            continue
        if given == expected["answer"].strip().upper():
            by_surface[surface][0] += 1
        else:
            wrong.append((case_id, given, expected["answer"], expected["because"]))

    for case_id, given, expected, because in wrong:
        print(f"WRONG {case_id}: answered {given}, key says {expected}")
        print(f"      {because}")
    for case_id in unanswered:
        print(f"BLANK {case_id}")

    print()
    total_right = sum(right for right, _ in by_surface.values())
    total = sum(count for _, count in by_surface.values())
    for surface in sorted(by_surface):
        right, count = by_surface[surface]
        print(f"{surface}: {right}/{count}")
    accuracy = total_right / total if total else 0.0
    print(f"overall: {total_right}/{total} ({accuracy:.0%})")

    if args.min_accuracy is not None and accuracy < args.min_accuracy:
        print(f"FAIL: below --min-accuracy {args.min_accuracy:.0%}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
