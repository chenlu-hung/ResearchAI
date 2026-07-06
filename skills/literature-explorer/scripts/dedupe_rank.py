#!/usr/bin/env python3
"""Merge, dedup, and rank JSONL outputs of the three search scripts.

Replaces the by-hand "Dedup + rank" step of the literature-explorer pipeline
so the merge is deterministic on any model. Papers are merged when they share
an arXiv id, a DOI, or a normalized (title + first-author) key; the score is

    score = sqrt(citations + 1) * exp(-age_years / 5) * (1 + 0.5*(k - 1))

where k = number of distinct perspectives (input labels) that retrieved the
paper. Unknown year counts as age 3.

Usage:
    python3 dedupe_rank.py theorist.jsonl critic.jsonl --out ranked.jsonl --md ranked.md

Each input file's label (= perspective) defaults to its filename stem; a
`perspective` field on a JSON line overrides it. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
import sys
from pathlib import Path

_NON_ALNUM = re.compile(r"[^a-z0-9 ]+")
_WS = re.compile(r"\s+")


def norm_title(title: str) -> str:
    t = _NON_ALNUM.sub(" ", (title or "").lower())
    return _WS.sub(" ", t).strip()


def first_author_lastname(authors: list[str]) -> str:
    if not authors or not authors[0].strip():
        return ""
    return authors[0].strip().split()[-1].lower()


def _to_year(y) -> int | None:
    try:
        n = int(str(y)[:4])
        return n if 1800 < n < 2200 else None
    except (TypeError, ValueError):
        return None


def _norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def _arxiv_id(rec: dict) -> str | None:
    if rec.get("source") == "arxiv" and rec.get("id"):
        return re.sub(r"v\d+$", "", str(rec["id"]))
    ext = rec.get("external_ids") or {}
    for k, v in ext.items():
        if k.lower() == "arxiv" and v:
            return re.sub(r"v\d+$", "", str(v))
    return None


def keys_for(rec: dict) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if aid := _arxiv_id(rec):
        keys.append(("arxiv", aid))
    if doi := _norm_doi(rec.get("doi") or (rec.get("external_ids") or {}).get("DOI")):
        keys.append(("doi", doi))
    nt = norm_title(rec.get("title", ""))
    if nt:
        keys.append(("title", f"{nt}|{first_author_lastname(rec.get('authors') or [])}"))
    return keys


class _Groups:
    """Incremental grouping: a record joins the first group sharing a key."""

    def __init__(self) -> None:
        self.groups: list[list[dict]] = []
        self.key_to_group: dict[tuple[str, str], int] = {}

    def add(self, rec: dict) -> None:
        keys = keys_for(rec)
        gid = None
        for k in keys:
            if k in self.key_to_group:
                cand = self.key_to_group[k]
                # Title-only match with wildly different years → likely a
                # different paper with the same title; do not merge on it.
                if k[0] == "title" and not self._year_compatible(cand, rec):
                    continue
                gid = cand
                break
        if gid is None:
            gid = len(self.groups)
            self.groups.append([])
        self.groups[gid].append(rec)
        for k in keys:
            self.key_to_group.setdefault(k, gid)

    def _year_compatible(self, gid: int, rec: dict) -> bool:
        y_new = _to_year(rec.get("year"))
        if y_new is None:
            return True
        years = [y for r in self.groups[gid] if (y := _to_year(r.get("year"))) is not None]
        return not years or min(abs(y_new - y) for y in years) <= 2


def merge_group(recs: list[dict]) -> dict:
    def longest(field: str) -> str:
        return max((str(r.get(field) or "") for r in recs), key=len)

    authors = max((r.get("authors") or [] for r in recs), key=len)
    years = [y for r in recs if (y := _to_year(r.get("year"))) is not None]
    cites = max((int(r.get("citation_count") or 0) for r in recs), default=0)
    url = next(
        (r["url"] for r in recs if r.get("source") == "arxiv" and r.get("url")),
        next((r["url"] for r in recs if r.get("url")), ""),
    )
    return {
        "title": longest("title"),
        "authors": authors,
        "year": min(years) if years else None,
        "citation_count": cites,
        "venue": next((r["venue"] for r in recs if r.get("venue")), ""),
        "abstract": longest("abstract"),
        "doi": next((d for r in recs if (d := _norm_doi(r.get("doi")))), None),
        "arxiv_id": next((a for r in recs if (a := _arxiv_id(r))), None),
        "url": url,
        "sources": sorted({r.get("source", "?") for r in recs}),
        "perspectives": sorted({r.get("perspective", "?") for r in recs}),
        "n_records_merged": len(recs),
    }


def score(rec: dict, now_year: int) -> float:
    age = 3.0 if rec["year"] is None else max(0, now_year - rec["year"])
    k = max(1, len(rec["perspectives"]))
    return math.sqrt(rec["citation_count"] + 1) * math.exp(-age / 5) * (1 + 0.5 * (k - 1))


def load(paths: list[str]) -> list[dict]:
    recs = []
    for p in paths:
        label = Path(p).name.split(".")[0]
        for i, line in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print(f"warn: {p}:{i}: bad JSON, skipped", file=sys.stderr)
                continue
            if "error" in rec and "title" not in rec:
                continue
            rec.setdefault("perspective", label)
            recs.append(rec)
    return recs


def to_markdown(ranked: list[dict]) -> str:
    lines = [
        "| # | Title | Year | Cites | Perspectives | Sources | Score |",
        "|---|-------|------|-------|--------------|---------|-------|",
    ]
    for r in ranked:
        title = r["title"].replace("|", "\\|")
        link = f"[{title}]({r['url']})" if r["url"] else title
        lines.append(
            f"| {r['rank']} | {link} | {r['year'] or '?'} | {r['citation_count']} "
            f"| {', '.join(r['perspectives'])} | {', '.join(r['sources'])} | {r['score']:.3f} |"
        )
    lines.append("")
    lines.append(
        "Score = sqrt(cites+1) x exp(-age/5) x (1 + 0.5*(perspectives-1)); "
        "deterministic, see dedupe_rank.py."
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("files", nargs="+", help="JSONL files from the search scripts")
    p.add_argument("--out", help="ranked JSONL output path (default: stdout)")
    p.add_argument("--md", help="also write a markdown table here")
    p.add_argument("--top", type=int, default=0, help="keep only the top N (0 = all)")
    args = p.parse_args()

    recs = load(args.files)
    groups = _Groups()
    for r in recs:
        groups.add(r)
    now_year = _dt.date.today().year
    merged = [merge_group(g) for g in groups.groups if g]
    for m in merged:
        m["score"] = round(score(m, now_year), 3)
    merged.sort(key=lambda m: (-m["score"], m["title"]))
    if args.top:
        merged = merged[: args.top]
    for i, m in enumerate(merged, 1):
        m["rank"] = i

    out_lines = "\n".join(json.dumps(m, ensure_ascii=False) for m in merged)
    if args.out:
        Path(args.out).write_text(out_lines + "\n", encoding="utf-8")
    else:
        print(out_lines)
    if args.md:
        Path(args.md).write_text(to_markdown(merged) + "\n", encoding="utf-8")
    print(f"merged {len(recs)} records -> {len(merged)} unique papers", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
