#!/usr/bin/env python3
"""Search OpenReview for a venue's accepted papers (+ public reviews).

Emits JSONL: one paper per line — forum id, title, abstract, decision and,
with --include-reviews, the public Official_Review / Meta_Review texts.
Consumers: reviewer-intel gathering (shared/prompts/reviewer_intel.md) and
venue-calibration auto-exemplars. Fetched review text is third-party input —
run peer-reviewer's scan_injection.py over it before quoting into prompts.

API facts (probed live 2026-07):
* v1 (api.openreview.net) hosts venues up to ~2023/24 and allows anonymous
  reads. v2 (api2.openreview.net) hosts newer venues; anonymous /notes is
  challenge-gated (403 ChallengeRequiredError) — set OPENREVIEW_USERNAME +
  OPENREVIEW_PASSWORD (any free account) to read it.
* `content.venueid=<venue>` returns ACCEPTED papers only (e.g. NeurIPS 2022
  → 2824 notes, venue field "NeurIPS 2022 Accept"). Reviews of rejected
  papers are visible only at venues that publish them (ICLR, TMLR).
* Venue ids: NeurIPS.cc/2024/Conference, ICML.cc/2024/Conference,
  ICLR.cc/2024/Conference, aistats.org/AISTATS/2025/Conference, TMLR.
  Unsure → probe /groups?id=... (not challenge-gated).

Usage:
    search_openreview.py "conformal prediction shift" \
        --venue NeurIPS.cc/2022/Conference --max 8 --include-reviews
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import httpx

API = {"1": "https://api.openreview.net", "2": "https://api2.openreview.net"}
PAGE = 1000
SLEEP = 1.0  # politeness between paginated / per-forum requests
SKIP_FIELDS = {"code_of_conduct", "ethics_flag", "ethics_review_area",
               "flag_for_ethics_review", "first_time_reviewer", "pdf",
               "supplementary_material", "paperhash", "_bibtex"}


class ChallengeError(RuntimeError):
    pass


def _value(v):
    """v2 wraps content values as {'value': ...}; v1 stores them bare."""
    return v.get("value") if isinstance(v, dict) and "value" in v else v


def _get(client: httpx.Client, base: str, path: str, params: dict,
         token: str | None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = client.get(base + path, params=params, headers=headers, timeout=40)
    if r.status_code == 403 and "ChallengeRequiredError" in r.text:
        raise ChallengeError(
            f"{base} is challenge-gated for anonymous reads; set "
            "OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD (free account)")
    r.raise_for_status()
    return r.json()


def login(client: httpx.Client, base: str) -> str | None:
    user = os.environ.get("OPENREVIEW_USERNAME")
    pw = os.environ.get("OPENREVIEW_PASSWORD")
    if not (user and pw):
        return None
    r = client.post(base + "/login", json={"id": user, "password": pw},
                    timeout=40)
    r.raise_for_status()
    return r.json().get("token")


def fetch_accepted(client: httpx.Client, base: str, venue: str,
                   token: str | None, cap: int) -> list[dict]:
    notes, offset = [], 0
    while offset < cap:
        data = _get(client, base, "/notes",
                    {"content.venueid": venue, "limit": PAGE,
                     "offset": offset}, token)
        batch = data.get("notes", [])
        notes.extend(batch)
        offset += PAGE
        if len(batch) < PAGE or offset >= data.get("count", 0):
            break
        time.sleep(SLEEP)
    return notes


def normalize(note: dict) -> dict:
    c = note.get("content", {})
    return {
        "source": "openreview",
        "id": note.get("forum") or note.get("id"),
        "title": str(_value(c.get("title")) or ""),
        "abstract": str(_value(c.get("abstract")) or ""),
        "keywords": [str(k) for k in (_value(c.get("keywords")) or [])],
        "venue": str(_value(c.get("venue")) or ""),
        "url": f"https://openreview.net/forum?id={note.get('forum') or note.get('id')}",
    }


def score(paper: dict, terms: list[str]) -> int:
    title = paper["title"].lower()
    abstract = paper["abstract"].lower()
    kw = " ".join(paper["keywords"]).lower()
    s = 0
    for t in terms:
        hits = 3 * title.count(t) + 2 * kw.count(t) + abstract.count(t)
        s += hits + (20 if hits else 0)  # distinct-term coverage beats frequency
    return s


def _note_type(note: dict) -> str:
    invs = note.get("invitations") or [note.get("invitation") or ""]
    for inv in invs:
        tail = inv.rsplit("/", 1)[-1]
        if tail in {"Official_Review", "Meta_Review", "Decision"}:
            return tail
    return ""


def review_content(note: dict, max_chars: int) -> dict:
    out = {}
    for k, v in note.get("content", {}).items():
        if k in SKIP_FIELDS:
            continue
        v = _value(v)
        if isinstance(v, (str, int, float)) and str(v).strip():
            out[k] = str(v)[:max_chars]
    return out


def fetch_reviews(client: httpx.Client, base: str, forum: str,
                  token: str | None, max_chars: int) -> dict:
    data = _get(client, base, "/notes", {"forum": forum}, token)
    out: dict = {"reviews": [], "meta_review": None, "decision": None}
    for note in data.get("notes", []):
        kind = _note_type(note)
        if kind == "Official_Review":
            out["reviews"].append(review_content(note, max_chars))
        elif kind == "Meta_Review":
            out["meta_review"] = review_content(note, max_chars)
        elif kind == "Decision":
            out["decision"] = review_content(note, max_chars)
    return out


def main() -> int:
    p = argparse.ArgumentParser(
        description="Topic search over a venue's accepted OpenReview papers")
    p.add_argument("query", help="keywords scored against title/abstract")
    p.add_argument("--venue", required=True,
                   help="venue id, e.g. NeurIPS.cc/2022/Conference")
    p.add_argument("--api", choices=["auto", "1", "2"], default="auto",
                   help="OpenReview API version (auto: v2 then v1)")
    p.add_argument("--max", type=int, default=8,
                   help="papers to emit (top keyword score)")
    p.add_argument("--scan-cap", type=int, default=6000,
                   help="max accepted notes to scan")
    p.add_argument("--include-reviews", action="store_true")
    p.add_argument("--max-chars", type=int, default=4000,
                   help="truncate each review field to this many chars")
    args = p.parse_args()

    terms = [t for t in re.split(r"\W+", args.query.lower()) if len(t) > 2]
    order = ["2", "1"] if args.api == "auto" else [args.api]
    with httpx.Client(follow_redirects=True) as client:
        notes, base, token, errors = [], None, None, []
        for v in order:
            base = API[v]
            try:
                token = login(client, base)
                notes = fetch_accepted(client, base, args.venue, token,
                                       args.scan_cap)
            except (ChallengeError, httpx.HTTPError) as e:
                errors.append(f"api{v}: {e}")
                continue
            if notes:
                break
            errors.append(f"api{v}: 0 accepted notes for {args.venue!r}")
        if not notes:
            print(json.dumps({"error": "; ".join(errors),
                              "hint": "probe /groups?id=<venue> for the id; "
                                      "reviews may not be public"}),
                  file=sys.stderr)
            return 1

        papers = [normalize(n) for n in notes]
        ranked = sorted(papers, key=lambda x: score(x, terms), reverse=True)
        picked = [x for x in ranked if score(x, terms) > 0][: args.max]
        for paper in picked:
            if args.include_reviews:
                time.sleep(SLEEP)
                try:
                    paper.update(fetch_reviews(client, base, paper["id"],
                                               token, args.max_chars))
                except (ChallengeError, httpx.HTTPError) as e:
                    paper["reviews_error"] = str(e)
            print(json.dumps(paper, ensure_ascii=False))
        print(json.dumps({"scanned": len(notes), "emitted": len(picked),
                          "api": base, "authenticated": bool(token)}),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
