# Module: `skills/literature-explorer`

## Summary
Bundled retrieval + ranking backends for the `literature-explorer` skill (`/explore`): one search script per source — arXiv (Atom/XML via `xml.etree`), OpenAlex, and Semantic Scholar (JSON over `httpx` with `tenacity` retries) — each exposing `search()` plus a CLI `main()` that prints normalized JSONL. `dedupe_rank.py` (stdlib-only) then owns the pipeline's "Dedup + rank" step deterministically: it merges records across sources on arXiv id / DOI / normalized title+author and scores by citations × recency-decay × perspective-hits, so the merge never depends on the running model. `search_openreview.py` is a separate venue-scoped fetcher (accepted papers + public reviews, v1 anonymous / v2 token-authenticated) serving `shared/prompts/reviewer_intel.md` and venue-calibration exemplars — not part of the survey trio. Search scripts are the fallback path (the external `literature-review-ml` skill is preferred when installed); the skill's prompt logic lives in the sibling Markdown, not here.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (5)
- `skills/literature-explorer/scripts/dedupe_rank.py`
- `skills/literature-explorer/scripts/search_arxiv.py`
- `skills/literature-explorer/scripts/search_openalex.py`
- `skills/literature-explorer/scripts/search_openreview.py`
- `skills/literature-explorer/scripts/search_semantic_scholar.py`

## Public symbols (35)
- `namespace _dt` — skills/literature-explorer/scripts/dedupe_rank.py:22
- `function norm_title` — skills/literature-explorer/scripts/dedupe_rank.py:33
- `function first_author_lastname` — skills/literature-explorer/scripts/dedupe_rank.py:38
- `function _to_year` — skills/literature-explorer/scripts/dedupe_rank.py:44
- `function _norm_doi` — skills/literature-explorer/scripts/dedupe_rank.py:52
- `function _arxiv_id` — skills/literature-explorer/scripts/dedupe_rank.py:60
- `function keys_for` — skills/literature-explorer/scripts/dedupe_rank.py:70
- `class _Groups` — skills/literature-explorer/scripts/dedupe_rank.py:82
- `function merge_group` — skills/literature-explorer/scripts/dedupe_rank.py:116
- `function longest` — skills/literature-explorer/scripts/dedupe_rank.py:117
- `function score` — skills/literature-explorer/scripts/dedupe_rank.py:143
- `function load` — skills/literature-explorer/scripts/dedupe_rank.py:149
- `function to_markdown` — skills/literature-explorer/scripts/dedupe_rank.py:169
- `function main` — skills/literature-explorer/scripts/dedupe_rank.py:189
- `namespace ET` — skills/literature-explorer/scripts/search_arxiv.py:9
- `function search` — skills/literature-explorer/scripts/search_arxiv.py:17
- `function main` — skills/literature-explorer/scripts/search_arxiv.py:59
- `function _get` — skills/literature-explorer/scripts/search_openalex.py:17
- `function _reconstruct_abstract` — skills/literature-explorer/scripts/search_openalex.py:23
- `function search` — skills/literature-explorer/scripts/search_openalex.py:34
- `function main` — skills/literature-explorer/scripts/search_openalex.py:68
- `class ChallengeError` — skills/literature-explorer/scripts/search_openreview.py:45
- `function _value` — skills/literature-explorer/scripts/search_openreview.py:49
- `function _get` — skills/literature-explorer/scripts/search_openreview.py:54
- `function login` — skills/literature-explorer/scripts/search_openreview.py:66
- `function fetch_accepted` — skills/literature-explorer/scripts/search_openreview.py:77
- `function normalize` — skills/literature-explorer/scripts/search_openreview.py:93
- `function score` — skills/literature-explorer/scripts/search_openreview.py:106
- `function _note_type` — skills/literature-explorer/scripts/search_openreview.py:117
- `function review_content` — skills/literature-explorer/scripts/search_openreview.py:126
- `function fetch_reviews` — skills/literature-explorer/scripts/search_openreview.py:137
- `function main` — skills/literature-explorer/scripts/search_openreview.py:152
- `function _get` — skills/literature-explorer/scripts/search_semantic_scholar.py:18
- `function search` — skills/literature-explorer/scripts/search_semantic_scholar.py:26
- `function main` — skills/literature-explorer/scripts/search_semantic_scholar.py:51

## Dependencies (imports)
- `__future__`
- `argparse`
- `datetime`
- `httpx`
- `json`
- `math`
- `os`
- `pathlib`
- `re`
- `sys`
- `tenacity`
- `time`
- `xml`
<!-- projectmap:auto:end -->
