# Module: `skills/literature-explorer`

## Summary
Bundled retrieval backends for the `literature-explorer` skill (`/explore`), one script per source: arXiv (Atom/XML via `xml.etree`), OpenAlex, and Semantic Scholar (both JSON over `httpx` with `tenacity` retries). Each exposes a `search()` plus a CLI `main()` and prints normalized records the skill folds into its multi-perspective survey + BibTeX. These are the fallback path: if the external `literature-review-ml` skill is installed the skill prefers it, otherwise these run with no configuration. The skill's prompt logic lives in the sibling Markdown (`SKILL.md`, `perspectives.md`, `expert-dialogue.md`), not here.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (3)
- `skills/literature-explorer/scripts/search_arxiv.py`
- `skills/literature-explorer/scripts/search_openalex.py`
- `skills/literature-explorer/scripts/search_semantic_scholar.py`

## Public symbols (10)
- `namespace ET` — skills/literature-explorer/scripts/search_arxiv.py:9
- `function search` — skills/literature-explorer/scripts/search_arxiv.py:17
- `function main` — skills/literature-explorer/scripts/search_arxiv.py:59
- `function _get` — skills/literature-explorer/scripts/search_openalex.py:17
- `function _reconstruct_abstract` — skills/literature-explorer/scripts/search_openalex.py:23
- `function search` — skills/literature-explorer/scripts/search_openalex.py:34
- `function main` — skills/literature-explorer/scripts/search_openalex.py:68
- `function _get` — skills/literature-explorer/scripts/search_semantic_scholar.py:18
- `function search` — skills/literature-explorer/scripts/search_semantic_scholar.py:26
- `function main` — skills/literature-explorer/scripts/search_semantic_scholar.py:51

## Dependencies (imports)
- `__future__`
- `argparse`
- `httpx`
- `json`
- `os`
- `sys`
- `tenacity`
- `time`
- `xml`
<!-- projectmap:auto:end -->
