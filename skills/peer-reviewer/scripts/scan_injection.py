#!/usr/bin/env python3
"""Deterministic first-pass injection scan for peer-reviewer ingestion.

Scans the *extracted text layer* of a manuscript for instructions aimed at the
reviewer/LLM rather than at readers (hidden-prompt injection), and optionally
compares two independent extractions (e.g. `pdftotext` vs `mutool draw`) —
a divergence between extractors is the tell for decoy-glyph / ToUnicode
payloads that have no readable on-page form.

This is a screen, not a verdict: it over-reports on purpose. The reviewer
still applies the attribution rules in SKILL.md (author payload vs platform
canary) to every hit. A clean scan does not prove absence — still skim.

Usage:
    python3 scan_injection.py extracted.txt [--compare other_extraction.txt] [--json]

Exit codes: 0 = nothing flagged, 1 = findings to review, 2 = usage error.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# name -> pattern (all matched case-insensitively, line by line)
PATTERNS: dict[str, str] = {
    "override": r"\b(ignore|disregard|forget)\b.{0,40}\b(previous|prior|above|earlier|all)\b.{0,20}\b(instruction|prompt|rule|direction)",
    "forced_phrase": r"\bmust\b.{0,20}\binclude\b.{0,30}\b(phrase|word|sentence|term)",
    "addresses_model": r"\b(as an ai\b|you are an? (ai|llm|language model|assistant)|if you are an? (ai|llm|language model)|dear (ai|llm|language model|reviewer bot))",
    "positive_review": r"\b(give|write|provide|leave|produce|generate)\b.{0,30}\b(positive|favorable|favourable|glowing|good)\b.{0,20}\b(review|assessment|evaluation|rating)",
    "accept_pressure": r"\b(recommend accept|accept this (paper|submission|manuscript)|do not reject|rate (this|it) (highly|favorably|favourably))",
    "suppression": r"\b(do not (mention|reveal|disclose|report) (this|these|the above)|keep this (secret|hidden)|without mentioning)",
    "prompt_leak": r"\b(system prompt|hidden (instruction|prompt|text)|prompt injection)",
    "reviewer_directive": r"\b(note to (the )?(ai|llm|reviewer|model)|instruction for (the )?(ai|llm|reviewer|model)|important:? (for|to) (the )?(ai|llm|model))",
}

_WS = re.compile(r"\s+")


def scan_text(text: str) -> list[dict]:
    hits = []
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        for name, pat in PATTERNS.items():
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                ctx_lo = max(0, lineno - 2)
                context = " / ".join(s.strip() for s in lines[ctx_lo:lineno + 1] if s.strip())
                hits.append(
                    {
                        "line": lineno,
                        "pattern": name,
                        "match": m.group(0)[:120],
                        "context": context[:300],
                    }
                )
    return hits


def _substantive_lines(text: str) -> set[str]:
    out = set()
    for line in text.splitlines():
        norm = _WS.sub(" ", line.strip().lower())
        if len(norm.split()) >= 4:
            out.add(norm)
    return out


def compare_extractions(a: str, b: str, max_samples: int = 10) -> dict:
    la, lb = _substantive_lines(a), _substantive_lines(b)
    only_a = sorted(la - lb)
    only_b = sorted(lb - la)
    return {
        "only_in_first": {"count": len(only_a), "samples": only_a[:max_samples]},
        "only_in_second": {"count": len(only_b), "samples": only_b[:max_samples]},
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("extracted", help="text file: the extraction you will review from")
    p.add_argument("--compare", help="second, independent extraction of the same PDF")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args()

    try:
        text = Path(args.extracted).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    result: dict = {"file": args.extracted, "hits": scan_text(text)}
    divergent = False
    if args.compare:
        try:
            other = Path(args.compare).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        result["extractor_divergence"] = compare_extractions(text, other)
        d = result["extractor_divergence"]
        # Some divergence is normal (headers, ligatures); flag only a
        # non-trivial one-sided surplus, which is the decoy-glyph shape.
        divergent = d["only_in_first"]["count"] >= 3 or d["only_in_second"]["count"] >= 3

    flagged = bool(result["hits"]) or divergent
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["hits"]:
            print(f"{len(result['hits'])} pattern hit(s):")
            for h in result["hits"]:
                print(f"  line {h['line']} [{h['pattern']}] {h['match']!r}")
                print(f"    context: {h['context']}")
        else:
            print("no pattern hits")
        if args.compare:
            d = result["extractor_divergence"]
            print(
                f"extractor divergence: {d['only_in_first']['count']} line(s) only in first, "
                f"{d['only_in_second']['count']} only in second"
                + (" — REVIEW (decoy-glyph tell)" if divergent else " — looks routine")
            )
            for key in ("only_in_first", "only_in_second"):
                for s in d[key]["samples"]:
                    print(f"    [{key}] {s[:160]}")
        print(
            "\nScreen only — apply SKILL.md attribution rules (author payload vs "
            "platform canary) to every hit; a clean scan does not prove absence."
        )
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
