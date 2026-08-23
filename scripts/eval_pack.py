#!/usr/bin/env python3
"""Emit an eval pack with the answer key withheld.

An agent that can see the key while producing the answer optimizes against the
key. The failure is architectural, not a matter of intent — so the key never
enters the run at all: this writes prompts, and only prompts, into a directory
the runner reads. Scoring happens afterwards, in `scripts/eval_score.py`, which
reads the key from the repo the runner never touched.

The pack records a digest of the case files it was built from. `eval_score.py`
refuses to score a pack whose cases have since changed, so an edited case
cannot be used to explain away a wrong answer after the fact.

Usage:
    python3 scripts/eval_pack.py --out <dir> [--surface evidence-gating]

Exit codes: 0 = pack written, 1 = no cases matched, 2 = usage error.
Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "evals" / "cases"
WITHHELD = ("answer", "because")
# A one-word rationale would match somewhere in any pack by chance, making the
# leak check meaningless. Such a rationale is also useless to whoever reads a
# wrong-answer report, so it is rejected rather than skipped.
MIN_RATIONALE = 20


def load_surfaces(cases_dir: Path, wanted: str | None) -> list[dict]:
    surfaces = []
    for path in sorted(cases_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if wanted and data.get("surface") != wanted:
            continue
        surfaces.append(data)
    return surfaces


def cases_digest(cases_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(cases_dir.glob("*.json")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def render_prompts(surfaces: list[dict]) -> str:
    out = [
        "# Eval pack",
        "",
        "Answer every case. Load the rule files named under each surface first;",
        "they are the specification you are being measured against, not a hint.",
        "Write answers into `answers.json` as `{\"<surface>/<case id>\": \"<ANSWER>\"}`.",
        "",
        "Answer with the exact token given — no explanation in the answer field.",
        "",
    ]
    for surface in surfaces:
        out.extend([
            f"## {surface['surface']}",
            "",
            f"**Question**: {surface['question']}",
            "",
            f"**Allowed answers**: {' | '.join(surface['answers'])}",
            "",
            "**Rules to load**: " + ", ".join(f"`{rule}`" for rule in surface["rules"]),
            "",
        ])
        for case in surface["cases"]:
            out.extend([
                f"### `{surface['surface']}/{case['id']}`",
                "",
                case["prompt"],
                "",
            ])
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cases-dir", type=Path, default=CASES_DIR)
    parser.add_argument("--surface", default=None, help="pack one surface only")
    parser.add_argument("--today", type=dt.date.fromisoformat, default=None)
    args = parser.parse_args()

    surfaces = load_surfaces(args.cases_dir, args.surface)
    if not surfaces:
        print(f"ERROR: no case files matched in {args.cases_dir}")
        return 1

    keys = [f"{s['surface']}/{c['id']}" for s in surfaces for c in s["cases"]]
    manifest = {
        "created": (args.today or dt.date.today()).isoformat(),
        "cases_digest": cases_digest(args.cases_dir),
        "case_count": len(keys),
        "surfaces": [
            {
                "surface": s["surface"],
                "question": s["question"],
                "answers": s["answers"],
                "rules": s["rules"],
                "case_ids": [c["id"] for c in s["cases"]],
            }
            for s in surfaces
        ],
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out / "prompts.md").write_text(render_prompts(surfaces), encoding="utf-8")
    (args.out / "answers.json").write_text(
        json.dumps({key: "" for key in keys}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # Belt and braces: the key must not have leaked into anything just written.
    thin = [
        f"{s['surface']}/{c['id']}"
        for s in surfaces for c in s["cases"]
        if len(c.get("because", "")) < MIN_RATIONALE
    ]
    if thin:
        for case_id in thin:
            print(f"ERROR: {case_id} has a rationale under {MIN_RATIONALE} characters — "
                  "too short to leak-check, and too short to explain a wrong answer")
        return 1

    leaked = []
    for path in sorted(args.out.iterdir()):
        text = path.read_text(encoding="utf-8")
        for surface in surfaces:
            for case in surface["cases"]:
                for field in WITHHELD:
                    value = case.get(field, "")
                    if field == "because" and value and value in text:
                        leaked.append(f"{path.name}: rationale for {case['id']}")
    if leaked:
        for item in leaked:
            print(f"ERROR: answer key leaked into the pack — {item}")
        return 1

    print(f"eval pack: {len(keys)} case(s) written to {args.out} (key withheld)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
