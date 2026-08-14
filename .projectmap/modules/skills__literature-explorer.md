# Module: `skills/literature-explorer`

## Summary
Bundled retrieval + ranking backends for the `literature-explorer` skill (`/explore`): one search script per source — arXiv (Atom/XML via `xml.etree`), OpenAlex, and Semantic Scholar (JSON over `httpx` with `tenacity` retries) — each exposing `search()` plus a CLI `main()` that prints normalized JSONL. `dedupe_rank.py` (stdlib-only) then owns the pipeline's "Dedup + rank" step deterministically: it merges records across sources on arXiv id / DOI / normalized title+author and scores by citations × recency-decay × perspective-hits, so the merge never depends on the running model. `search_openreview.py` is a separate venue-scoped fetcher (accepted papers + public reviews, v1 anonymous / v2 token-authenticated) serving `shared/prompts/reviewer_intel.md` and venue-calibration exemplars — not part of the survey trio. The search scripts are the default external-retrieval step (an installed `literature-review-ml` skill may replace it), and they run only after the evidence vault has been queried; their output feeds `corpus-prefetch.md`'s broad shallow sweep and is persisted as query runs via `evidencectl`. The skill's prompt logic lives in the sibling Markdown, not here.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (5)
- `skills/literature-explorer/scripts/dedupe_rank.py`
- `skills/literature-explorer/scripts/search_arxiv.py`
- `skills/literature-explorer/scripts/search_openalex.py`
- `skills/literature-explorer/scripts/search_openreview.py`
- `skills/literature-explorer/scripts/search_semantic_scholar.py`

## Public symbols (35)
- `namespace _dt` — skills/literature-explorer/scripts/dedupe_rank.py:23
- `function norm_title` — skills/literature-explorer/scripts/dedupe_rank.py:34
- `function first_author_lastname` — skills/literature-explorer/scripts/dedupe_rank.py:39
- `function _to_year` — skills/literature-explorer/scripts/dedupe_rank.py:45
- `function _norm_doi` — skills/literature-explorer/scripts/dedupe_rank.py:53
- `function _arxiv_id` — skills/literature-explorer/scripts/dedupe_rank.py:61
- `function keys_for` — skills/literature-explorer/scripts/dedupe_rank.py:71
- `class _Groups` — skills/literature-explorer/scripts/dedupe_rank.py:83
- `function merge_group` — skills/literature-explorer/scripts/dedupe_rank.py:117
- `function longest` — skills/literature-explorer/scripts/dedupe_rank.py:118
- `function score` — skills/literature-explorer/scripts/dedupe_rank.py:144
- `function load` — skills/literature-explorer/scripts/dedupe_rank.py:150
- `function to_markdown` — skills/literature-explorer/scripts/dedupe_rank.py:170
- `function main` — skills/literature-explorer/scripts/dedupe_rank.py:190
- `namespace ET` — skills/literature-explorer/scripts/search_arxiv.py:9
- `function search` — skills/literature-explorer/scripts/search_arxiv.py:17
- `function main` — skills/literature-explorer/scripts/search_arxiv.py:59
- `function _get` — skills/literature-explorer/scripts/search_openalex.py:17
- `function _reconstruct_abstract` — skills/literature-explorer/scripts/search_openalex.py:23
- `function search` — skills/literature-explorer/scripts/search_openalex.py:34
- `function main` — skills/literature-explorer/scripts/search_openalex.py:68
- `class ChallengeError` — skills/literature-explorer/scripts/search_openreview.py:47
- `function _value` — skills/literature-explorer/scripts/search_openreview.py:51
- `function _get` — skills/literature-explorer/scripts/search_openreview.py:56
- `function login` — skills/literature-explorer/scripts/search_openreview.py:68
- `function fetch_accepted` — skills/literature-explorer/scripts/search_openreview.py:79
- `function normalize` — skills/literature-explorer/scripts/search_openreview.py:95
- `function score` — skills/literature-explorer/scripts/search_openreview.py:108
- `function _note_type` — skills/literature-explorer/scripts/search_openreview.py:119
- `function review_content` — skills/literature-explorer/scripts/search_openreview.py:128
- `function fetch_reviews` — skills/literature-explorer/scripts/search_openreview.py:139
- `function main` — skills/literature-explorer/scripts/search_openreview.py:154
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
