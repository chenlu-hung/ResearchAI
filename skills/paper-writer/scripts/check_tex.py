#!/usr/bin/env python3
"""Static cross-checks on a LaTeX draft — no LaTeX install needed.

Deterministically verifies the things full-draft / citation-audit /
submission-check would otherwise eyeball:

  * every \\cite-family key resolves in the .bib (undefined = blocking)
  * every \\ref/\\eqref/\\cref/... has a matching \\label (undefined = blocking)
  * duplicate \\label definitions
  * every \\includegraphics file exists on disk (missing = blocking)
  * unused .bib entries (informational)
  * optional --must-include tokens (venue_profiles.md `must_include`) found
    in the source (missing = blocking)

Follows \\input/\\include recursively from the main file. Comments stripped.

Usage:
    python3 check_tex.py paper/main.tex --bib refs/<slug>.bib \\
        [--must-include limitations broader_impact ...] [--json]

Exit codes: 0 = clean, 1 = blocking findings, 2 = usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CITE_RE = re.compile(r"\\(?:no)?[cC]ite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
REF_RE = re.compile(r"\\(?:[cC]ref|ref|eqref|autoref|pageref|vref)\*?\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]*)\}")
BIBKEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
COMMENT_RE = re.compile(r"(?<!\\)%.*")

# venue_profiles.md `must_include` token -> regex evidence in the source
MUST_INCLUDE_PATTERNS: dict[str, str] = {
    "limitations": r"limitation",
    "broader_impact": r"broader\s+impact",
    "reproducibility": r"reproducib",
    "ai_disclosure": r"(llm|language\s+model|generative\s+ai|\bai\b)[^.]{0,80}(use|usage|assist|disclos)|disclos[^.]{0,80}(llm|language\s+model|\bai\b)",
    "proofs_in_main": r"\\begin\{proof\}",
    "assumption_discussion": r"assumption",
    "identifiability": r"identifiab",
    "main_theorem": r"\\begin\{theorem\}",
    "simulation_section": r"simulat",
    "theory_contribution": r"\\begin\{(theorem|proposition|lemma|corollary)\}",
}

GRAPHIC_EXTS = ["", ".pdf", ".png", ".jpg", ".jpeg", ".eps"]


def strip_comments(tex: str) -> str:
    return "\n".join(COMMENT_RE.sub("", line) for line in tex.splitlines())


def gather_sources(main: Path) -> tuple[dict[str, str], list[str]]:
    """Return {path: stripped-source} for main + recursively \\input files."""
    sources: dict[str, str] = {}
    warnings: list[str] = []
    stack, seen = [main], set()
    while stack:
        f = stack.pop()
        key = str(f.resolve())
        if key in seen:
            continue
        seen.add(key)
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            warnings.append(f"cannot read {f}")
            continue
        text = strip_comments(raw)
        sources[str(f)] = text
        for m in INPUT_RE.finditer(text):
            child = m.group(1).strip()
            p = (f.parent / child)
            if p.suffix == "":
                p = p.with_suffix(".tex")
            if p.exists():
                stack.append(p)
            else:
                warnings.append(f"\\input{{{child}}} in {f.name}: file not found")
    return sources, warnings


def find_graphic(base: Path, ref: str) -> bool:
    for root in (base, base.parent):
        for ext in GRAPHIC_EXTS:
            if (root / (ref + ext)).exists():
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("main_tex", help="main .tex file (\\input files followed)")
    ap.add_argument("--bib", help=".bib file with the verified bibliography")
    ap.add_argument("--must-include", nargs="*", default=[],
                    help="venue must_include tokens (see venue_profiles.md)")
    ap.add_argument("--pattern", action="append", default=[], metavar="TOKEN=REGEX",
                    help="extra must_include token pattern (from the venue's "
                         "must_include_patterns block); repeatable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    patterns = dict(MUST_INCLUDE_PATTERNS)
    for spec in args.pattern:
        token, sep, regex = spec.partition("=")
        if not sep or not token or not regex:
            print(f"error: --pattern expects TOKEN=REGEX, got {spec!r}",
                  file=sys.stderr)
            return 2
        try:
            re.compile(regex)
        except re.error as exc:
            print(f"error: --pattern {token}: invalid regex ({exc})",
                  file=sys.stderr)
            return 2
        patterns[token] = regex

    main_path = Path(args.main_tex)
    if not main_path.exists():
        print(f"error: {main_path} not found", file=sys.stderr)
        return 2

    sources, warnings = gather_sources(main_path)
    all_text = "\n".join(sources.values())

    cites = sorted({k.strip() for m in CITE_RE.finditer(all_text)
                    for k in m.group(1).split(",") if k.strip()})
    refs = sorted({k.strip() for m in REF_RE.finditer(all_text)
                   for k in m.group(1).split(",") if k.strip()})
    labels = [m.group(1).strip() for m in LABEL_RE.finditer(all_text)]
    label_set = set(labels)
    dup_labels = sorted({k for k in label_set if labels.count(k) > 1})
    graphics = sorted({m.group(1).strip() for m in GRAPHICS_RE.finditer(all_text)})

    bib_keys: set[str] = set()
    if args.bib:
        bp = Path(args.bib)
        if not bp.exists():
            print(f"error: bib file {bp} not found", file=sys.stderr)
            return 2
        bib_keys = {m.group(1) for m in BIBKEY_RE.finditer(
            bp.read_text(encoding="utf-8", errors="replace"))}

    undefined_cites = sorted(set(cites) - bib_keys) if args.bib else []
    unused_bib = sorted(bib_keys - set(cites)) if args.bib else []
    undefined_refs = sorted(set(refs) - label_set)
    missing_graphics = sorted(g for g in graphics if not find_graphic(main_path.parent, g))

    low = all_text.lower()
    must_missing, must_found, must_unknown = [], [], []
    for token in args.must_include:
        pat = patterns.get(token)
        if pat is None:
            must_unknown.append(token)
        elif re.search(pat, low, re.IGNORECASE):
            must_found.append(token)
        else:
            must_missing.append(token)

    report = {
        "files_scanned": sorted(sources),
        "cite_keys": len(cites),
        "undefined_citations": undefined_cites,
        "unused_bib_entries": unused_bib,
        "undefined_refs": undefined_refs,
        "duplicate_labels": dup_labels,
        "missing_graphics": missing_graphics,
        "must_include_found": must_found,
        "must_include_missing": must_missing,
        "must_include_unknown_tokens": must_unknown,
        "warnings": warnings,
    }
    blocking = bool(undefined_cites or undefined_refs or missing_graphics
                    or must_missing or must_unknown)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"scanned {len(sources)} file(s), {len(cites)} distinct cite keys")
        for name in ("undefined_citations", "undefined_refs", "duplicate_labels",
                     "missing_graphics", "must_include_missing",
                     "must_include_unknown_tokens", "warnings"):
            items = report[name]
            if items:
                print(f"{name} ({len(items)}):")
                for it in items:
                    print(f"  - {it}")
        if unused_bib:
            print(f"unused_bib_entries (info, {len(unused_bib)}): {', '.join(unused_bib)}")
        if must_found:
            print(f"must_include_found: {', '.join(must_found)}")
        print("RESULT: " + ("BLOCKING FINDINGS" if blocking else "clean"))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
