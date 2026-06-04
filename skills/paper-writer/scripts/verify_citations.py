#!/usr/bin/env python3
"""Verify BibTeX entries against Semantic Scholar, with OpenAlex + Crossref fallback.

Per entry -> verified | mismatched | fabricated | unreachable.

A DOI in the .bib that resolves on Crossref/OpenAlex short-circuits to
`verified`; title/author search then tries S2 -> OpenAlex -> Crossref and stops
at the first match. Multi-source fallback avoids false `fabricated` verdicts on
very recent preprints that one index has not yet ingested.

Usage:
    uv run python skills/paper-writer/scripts/verify_citations.py \
        --bib refs/<slug>.bib --out audit.json

Env: SEMANTIC_SCHOLAR_API_KEY (optional), OPENALEX_MAILTO (polite pool).
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass

import httpx
from pybtex.database import parse_file
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

TITLE_SIM = 0.85
TITLE_SOFT = 0.70
MAILTO = os.environ.get("OPENALEX_MAILTO", "research-assistant@example.org")


class Retryable(httpx.HTTPError):
    """Transient failure (429 / timeout / transport) — worth retrying."""


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
    matched_doi: str | None = None
    matched_source: str | None = None  # s2 | openalex | crossref | doi
    title_similarity: float | None = None
    notes: str = ""


@retry(
    retry=retry_if_exception_type(Retryable),
    stop=stop_after_attempt(4),
    wait=wait_exponential(min=2, max=20),
    reraise=True,  # re-raise the underlying Retryable (an httpx.HTTPError), not RetryError,
    # so callers' `except httpx.HTTPError` triggers the next-source fallback.
)
def _get(url: str, params: dict | None = None, headers: dict | None = None) -> dict:
    try:
        r = httpx.get(url, params=params, headers=headers or {}, timeout=30)
    except (httpx.TimeoutException, httpx.TransportError) as e:
        raise Retryable(str(e)) from e
    if r.status_code == 429:
        raise Retryable("rate limited")
    r.raise_for_status()  # 4xx (e.g. DOI 404) -> HTTPStatusError, not retried
    return r.json()


# --- per-source candidate fetch; each returns [{title, authors, year, doi}] ---


def _s2(title: str, first: str, headers: dict) -> list[dict]:
    d = _get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        {"query": f"{title} {first}".strip(), "limit": 5,
         "fields": "title,authors.name,year,externalIds"},
        headers,
    )
    return [
        {
            "title": c.get("title") or "",
            "authors": [a.get("name", "") for a in c.get("authors") or []],
            "year": c.get("year"),
            "doi": (c.get("externalIds") or {}).get("DOI"),
        }
        for c in d.get("data") or []
    ]


def _oa_row(w: dict) -> dict:
    return {
        "title": w.get("title") or "",
        "authors": [
            a["author"]["display_name"]
            for a in w.get("authorships") or []
            if a.get("author")
        ],
        "year": w.get("publication_year"),
        "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
    }


def _openalex(title: str, first: str | None = None, doi: str | None = None) -> list[dict]:
    if doi:
        try:
            return [_oa_row(_get(f"https://api.openalex.org/works/doi:{doi}", {"mailto": MAILTO}))]
        except httpx.HTTPError:
            return []
    if not title:
        return []
    # title.search filter matches the title field specifically — far more
    # precise than the generic `search` param, which buries exact titles.
    # `,` and `|` are OpenAlex filter separators (a raw comma -> 400); strip
    # them — title.search is fuzzy, so dropping punctuation is harmless.
    safe = re.sub(r"[,|:]", " ", title)
    d = _get("https://api.openalex.org/works",
             {"filter": f"title.search:{safe}", "per-page": 5, "mailto": MAILTO})
    return [_oa_row(w) for w in d.get("results") or []]


def _cr_row(m: dict) -> dict:
    dp = (m.get("published") or m.get("issued") or {}).get("date-parts")
    return {
        "title": (m.get("title") or [""])[0],
        "authors": [
            " ".join(filter(None, [a.get("given"), a.get("family")]))
            for a in m.get("author") or []
        ],
        "year": dp[0][0] if dp and dp[0] else None,
        "doi": m.get("DOI"),
    }


def _crossref(title: str, first: str | None = None, doi: str | None = None) -> list[dict]:
    base = "https://api.crossref.org/works"
    if doi:
        try:
            return [_cr_row(_get(f"{base}/{doi}", {"mailto": MAILTO}).get("message", {}))]
        except httpx.HTTPError:
            return []
    if not title:
        return []
    q = f"{title} {first}".strip() if first else title
    d = _get(base, {"query.bibliographic": q, "rows": 5, "mailto": MAILTO})
    return [_cr_row(m) for m in d.get("message", {}).get("items") or []]


# --- matching helpers ---------------------------------------------------------


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _best(title: str, cands: list[dict]) -> tuple[dict | None, float]:
    best, bs = None, -1.0
    for c in cands:
        s = _sim(title, c["title"])
        if s > bs:
            best, bs = c, s
    return best, bs


def _year_int(y) -> int | None:
    """Leading 4-digit year, or None. Tolerates '2019a', 'in press', '2019--2020'."""
    m = re.match(r"\s*(\d{4})", str(y or ""))
    return int(m.group(1)) if m else None


def _matches(title: str, first: str, year: str, c: dict, sim: float) -> tuple[bool, bool, bool]:
    by = _year_int(year)
    year_ok = (by is None) or (c["year"] is not None and abs(int(c["year"]) - by) <= 1)
    author_ok = (not first) or any(first.lower() in (a or "").lower() for a in c["authors"])
    return (sim >= TITLE_SIM and year_ok and author_ok), year_ok, author_ok


def _first_author(entry) -> str:
    persons = entry.persons.get("author", [])
    if not persons:
        return ""
    last = persons[0].last_names
    return last[0] if last else ""


def _bib_doi(entry) -> str | None:
    return entry.fields.get("doi", "").strip().replace("https://doi.org/", "") or None


def _fill(row: AuditRow, c: dict, src: str, sim: float) -> None:
    row.matched_title = c["title"]
    row.matched_authors = c["authors"]
    row.matched_year = c["year"]
    row.matched_doi = c["doi"]
    row.matched_source = src
    row.title_similarity = round(sim, 3)


def audit_entry(bibkey: str, entry, headers: dict) -> AuditRow:
    title = " ".join(entry.fields.get("title", "").replace("{", "").replace("}", "").split())
    first = _first_author(entry)
    year = entry.fields.get("year", "")
    doi = _bib_doi(entry)
    row = AuditRow(bibkey, title, first, year, "unreachable")
    if not title and not doi:
        row.status, row.notes = "fabricated", "Empty title and no DOI in .bib"
        return row

    # 1. DOI exact resolution (strongest signal).
    if doi:
        for src, fn in (("crossref", _crossref), ("openalex", _openalex)):
            cands = fn(title, doi=doi)
            if cands and cands[0]["title"]:
                c = cands[0]
                sim = _sim(title, c["title"]) if title else 1.0
                _fill(row, c, "doi", sim)
                row.status = "verified" if (not title or sim >= TITLE_SOFT) else "mismatched"
                if row.status == "mismatched":
                    row.notes = f"DOI resolves on {src} but title sim {sim:.2f} low"
                return row

    # 2. Title + author search across sources; stop at first verified. Each
    # source builds its own optimal query (S2/Crossref: title+author;
    # OpenAlex: title filter).
    sources = [
        ("s2", lambda: _s2(title, first, headers)),
        ("openalex", lambda: _openalex(title, first)),
        ("crossref", lambda: _crossref(title, first)),
    ]
    best_overall: tuple[dict, float, str, bool, bool] | None = None
    for src, fn in sources:
        try:
            cands = fn()
        except Exception as e:  # noqa: BLE001 — one bad source/entry must not abort the audit
            row.notes = f"{src} error: {type(e).__name__}: {e}"
            continue
        if not cands:
            continue
        c, sim = _best(title, cands)
        ok, yok, aok = _matches(title, first, year, c, sim)
        if ok:
            _fill(row, c, src, sim)
            row.status = "verified"
            return row
        if best_overall is None or sim > best_overall[1]:
            best_overall = (c, sim, src, yok, aok)

    if best_overall is None:
        row.status = "unreachable" if row.notes else "fabricated"
        row.notes = row.notes or "No candidates from s2/openalex/crossref"
        return row

    c, sim, src, yok, aok = best_overall
    _fill(row, c, src, sim)
    if sim >= TITLE_SOFT:
        row.status = "mismatched"
        probs = []
        if not yok:
            probs.append(f"year (.bib={year}, src={c['year']})")
        if not aok:
            probs.append("first author")
        if sim < TITLE_SIM:
            probs.append(f"title sim {sim:.2f}<{TITLE_SIM}")
        row.notes = "mismatch: " + ", ".join(probs)
    else:
        row.status = "fabricated"
        row.notes = f"best title sim {sim:.2f}<{TITLE_SOFT} across s2/openalex/crossref"
    return row


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bib", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sleep", type=float, default=1.0, help="Sec between entries")
    args = p.parse_args()

    headers = {}
    if key := os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = key

    db = parse_file(args.bib)
    rows: list[AuditRow] = []
    label = {"verified": "OK", "mismatched": "WARN", "fabricated": "FAIL", "unreachable": "RETRY"}
    for bibkey, entry in db.entries.items():
        row = audit_entry(bibkey, entry, headers)
        rows.append(row)
        src = f" via {row.matched_source}" if row.matched_source else ""
        print(f"[{label[row.status]}] {bibkey}{src}: {row.notes or row.matched_title or ''}", file=sys.stderr)
        time.sleep(args.sleep)

    summary = {k: sum(1 for r in rows if r.status == k) for k in label}
    summary["total"] = len(rows)
    out = {"summary": summary, "rows": [asdict(r) for r in rows]}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary), file=sys.stderr)
    return 0 if summary["fabricated"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
