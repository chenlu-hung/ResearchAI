#!/usr/bin/env python3
"""Verify entries in a BibTeX file against Semantic Scholar.

Outputs JSON with per-entry classification: verified / mismatched / fabricated / unreachable.

Usage:
    python verify_citations.py --bib refs/<slug>.bib --out audit.json
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass

import httpx
from pybtex.database import parse_file
from tenacity import retry, stop_after_attempt, wait_exponential

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "paperId,externalIds,title,authors.name,year,abstract,venue"
TITLE_SIM_THRESHOLD = 0.85
TITLE_SOFT_THRESHOLD = 0.70


@dataclass
class AuditRow:
    bibkey: str
    bib_title: str
    bib_first_author: str
    bib_year: str | None
    status: str  # verified | mismatched | fabricated | unreachable
    matched_title: str | None = None
    matched_authors: list[str] | None = None
    matched_year: int | None = None
    matched_paper_id: str | None = None
    title_similarity: float | None = None
    notes: str = ""


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=2, max=20))
def _search(query: str, headers: dict) -> dict:
    r = httpx.get(
        S2_SEARCH,
        params={"query": query, "limit": 5, "fields": S2_FIELDS},
        headers=headers,
        timeout=30,
    )
    if r.status_code == 429:
        raise httpx.HTTPError("rate limited")
    r.raise_for_status()
    return r.json()


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _title_sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _first_author_lastname(entry) -> str:
    persons = entry.persons.get("author", [])
    if not persons:
        return ""
    last = persons[0].last_names
    return last[0] if last else ""


def audit_entry(bibkey: str, entry, headers: dict) -> AuditRow:
    title = " ".join(entry.fields.get("title", "").replace("{", "").replace("}", "").split())
    first_author = _first_author_lastname(entry)
    year = entry.fields.get("year", "")
    row = AuditRow(
        bibkey=bibkey,
        bib_title=title,
        bib_first_author=first_author,
        bib_year=year,
        status="unreachable",
    )
    if not title:
        row.status = "fabricated"
        row.notes = "Empty title in .bib"
        return row
    query = f"{title} {first_author}".strip()
    try:
        data = _search(query, headers)
    except httpx.HTTPError as e:
        row.notes = f"API error: {e}"
        return row

    candidates = data.get("data") or []
    if not candidates:
        row.status = "fabricated"
        row.notes = "No candidates returned by Semantic Scholar"
        return row

    best = None
    best_sim = -1.0
    for c in candidates:
        sim = _title_sim(title, c.get("title") or "")
        if sim > best_sim:
            best = c
            best_sim = sim
    assert best is not None
    row.matched_title = best.get("title")
    row.matched_year = best.get("year")
    row.matched_authors = [a.get("name") for a in (best.get("authors") or [])]
    row.matched_paper_id = best.get("paperId")
    row.title_similarity = round(best_sim, 3)

    year_ok = (not year) or (
        best.get("year") is not None and abs(int(best["year"]) - int(year)) <= 1
    )
    author_ok = (not first_author) or any(
        first_author.lower() in (a or "").lower() for a in (row.matched_authors or [])
    )

    if best_sim >= TITLE_SIM_THRESHOLD and year_ok and author_ok:
        row.status = "verified"
    elif best_sim >= TITLE_SOFT_THRESHOLD:
        row.status = "mismatched"
        problems = []
        if not year_ok:
            problems.append(f"year mismatch (.bib={year}, S2={best.get('year')})")
        if not author_ok:
            problems.append(
                f"first author mismatch (.bib={first_author}, S2={row.matched_authors[:2] if row.matched_authors else []})"
            )
        if best_sim < TITLE_SIM_THRESHOLD:
            problems.append(f"title similarity {best_sim:.2f} below {TITLE_SIM_THRESHOLD}")
        row.notes = "; ".join(problems)
    else:
        row.status = "fabricated"
        row.notes = f"Best title similarity {best_sim:.2f} below soft threshold"
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bib", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sleep", type=float, default=1.0, help="Sec between S2 calls")
    args = p.parse_args()

    headers = {}
    if key := os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = key

    db = parse_file(args.bib)
    rows: list[AuditRow] = []
    for bibkey, entry in db.entries.items():
        row = audit_entry(bibkey, entry, headers)
        rows.append(row)
        status_label = {
            "verified": "OK",
            "mismatched": "WARN",
            "fabricated": "FAIL",
            "unreachable": "RETRY",
        }[row.status]
        print(f"[{status_label}] {bibkey}: {row.notes or row.matched_title or ''}", file=sys.stderr)
        time.sleep(args.sleep)

    summary = {
        "total": len(rows),
        "verified": sum(1 for r in rows if r.status == "verified"),
        "mismatched": sum(1 for r in rows if r.status == "mismatched"),
        "fabricated": sum(1 for r in rows if r.status == "fabricated"),
        "unreachable": sum(1 for r in rows if r.status == "unreachable"),
    }
    out = {"summary": summary, "rows": [asdict(r) for r in rows]}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary), file=sys.stderr)
    return 0 if summary["fabricated"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
