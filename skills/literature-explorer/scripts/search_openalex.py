#!/usr/bin/env python3
"""Search OpenAlex for a query. Emits JSONL with id, title, authors, year, abstract, cited_by_count."""
from __future__ import annotations

import argparse
import json
import os
import sys

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

OA_API = "https://api.openalex.org/works"


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=2, max=20))
def _get(params: dict) -> dict:
    r = httpx.get(OA_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _reconstruct_abstract(idx: dict | None) -> str:
    if not idx:
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in idx.items():
        for loc in locs:
            positions.append((loc, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def search(query: str, per_page: int = 25) -> list[dict]:
    params = {
        "search": query,
        "per-page": per_page,
        "sort": "relevance_score:desc",
    }
    if mailto := os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = mailto
    data = _get(params)
    out = []
    for w in data.get("results", []):
        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in (w.get("authorships") or [])
        ]
        out.append(
            {
                "source": "openalex",
                "id": w.get("id", "").rsplit("/", 1)[-1],
                "doi": w.get("doi"),
                "title": w.get("title") or "",
                "authors": authors,
                "year": str(w.get("publication_year") or ""),
                "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
                "citation_count": w.get("cited_by_count") or 0,
                "venue": ((w.get("primary_location") or {}).get("source") or {}).get(
                    "display_name", ""
                ),
                "url": w.get("id", ""),
            }
        )
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--max", type=int, default=25)
    args = p.parse_args()
    try:
        results = search(args.query, args.max)
    except httpx.HTTPError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1
    for r in results:
        print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
