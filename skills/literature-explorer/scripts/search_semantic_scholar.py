#!/usr/bin/env python3
"""Search Semantic Scholar Graph API. Emits JSONL with paperId, title, authors, year, abstract, citationCount, venue."""
from __future__ import annotations

import argparse
import json
import os
import sys

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "paperId,externalIds,title,authors.name,year,abstract,citationCount,venue,publicationTypes,openAccessPdf"


@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=2, max=20))
def _get(url: str, params: dict, headers: dict) -> dict:
    r = httpx.get(url, params=params, headers=headers, timeout=30)
    if r.status_code == 429:
        raise httpx.HTTPError("rate limited")
    r.raise_for_status()
    return r.json()


def search(query: str, limit: int = 25) -> list[dict]:
    headers = {}
    if key := os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        headers["x-api-key"] = key
    data = _get(S2_API, {"query": query, "limit": limit, "fields": FIELDS}, headers)
    out = []
    for p in data.get("data", []):
        out.append(
            {
                "source": "semantic_scholar",
                "id": p.get("paperId"),
                "external_ids": p.get("externalIds") or {},
                "title": p.get("title") or "",
                "authors": [a.get("name", "") for a in (p.get("authors") or [])],
                "year": str(p.get("year") or ""),
                "abstract": p.get("abstract") or "",
                "citation_count": p.get("citationCount") or 0,
                "venue": p.get("venue") or "",
                "pdf": (p.get("openAccessPdf") or {}).get("url"),
                "url": f"https://www.semanticscholar.org/paper/{p.get('paperId')}",
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
