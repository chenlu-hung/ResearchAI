#!/usr/bin/env python3
"""Search arXiv for a query and emit JSONL with id, title, authors, abstract, year, categories."""
from __future__ import annotations

import argparse
import json
import sys
import time
import xml.etree.ElementTree as ET

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def search(query: str, max_results: int = 25) -> list[dict]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    r = httpx.get(ARXIV_API, params=params, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    out = []
    for entry in root.findall("atom:entry", NS):
        arxiv_id = entry.findtext("atom:id", default="", namespaces=NS).rsplit("/", 1)[-1]
        title = (entry.findtext("atom:title", default="", namespaces=NS) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=NS) or "").strip()
        published = entry.findtext("atom:published", default="", namespaces=NS) or ""
        year = published[:4] if published else ""
        authors = [
            (a.findtext("atom:name", default="", namespaces=NS) or "").strip()
            for a in entry.findall("atom:author", NS)
        ]
        cats = [
            c.attrib.get("term", "")
            for c in entry.findall("atom:category", NS)
            if c.attrib.get("term")
        ]
        out.append(
            {
                "source": "arxiv",
                "id": arxiv_id,
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": summary,
                "categories": cats,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
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
    time.sleep(3)  # arXiv asks for 3s between requests
    return 0


if __name__ == "__main__":
    sys.exit(main())
