# Module: `skills/paper-writer`

## Summary
The Python helpers behind the `paper-writer` skill (`/write`). `verify_citations.py` is the citation auditor: it matches each BibTeX entry against Semantic Scholar → OpenAlex → Crossref (DOI plus fuzzy title/author/year matching via `difflib`) to flag fabricated or mismatched references before submission. `figs.py` is a small matplotlib/numpy styling library (consistent fonts, confidence bands, ablation bars) imported by the auditor and runnable standalone as a figure smoketest. Not indexed here: `build_paper.sh` (LaTeX compile gate + DOCX export) and the skill's mode/style Markdown.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (2)
- `skills/paper-writer/scripts/figs.py`
- `skills/paper-writer/scripts/verify_citations.py`

## Public symbols (27)
- `function apply_style` — skills/paper-writer/scripts/figs.py:28
- `namespace mpl` — skills/paper-writer/scripts/figs.py:29
- `function save` — skills/paper-writer/scripts/figs.py:51
- `function band` — skills/paper-writer/scripts/figs.py:59
- `namespace np` — skills/paper-writer/scripts/figs.py:61
- `function ablation_bar` — skills/paper-writer/scripts/figs.py:69
- `namespace np` — skills/paper-writer/scripts/figs.py:71
- `namespace plt` — skills/paper-writer/scripts/figs.py:81
- `namespace np` — skills/paper-writer/scripts/figs.py:82
- `class Retryable` — skills/paper-writer/scripts/verify_citations.py:42
- `class AuditRow` — skills/paper-writer/scripts/verify_citations.py:47
- `function _get` — skills/paper-writer/scripts/verify_citations.py:69
- `function _s2` — skills/paper-writer/scripts/verify_citations.py:83
- `function _oa_row` — skills/paper-writer/scripts/verify_citations.py:101
- `function _openalex` — skills/paper-writer/scripts/verify_citations.py:114
- `function _cr_row` — skills/paper-writer/scripts/verify_citations.py:132
- `function _crossref` — skills/paper-writer/scripts/verify_citations.py:145
- `function _norm` — skills/paper-writer/scripts/verify_citations.py:162
- `function _sim` — skills/paper-writer/scripts/verify_citations.py:166
- `function _best` — skills/paper-writer/scripts/verify_citations.py:170
- `function _year_int` — skills/paper-writer/scripts/verify_citations.py:179
- `function _matches` — skills/paper-writer/scripts/verify_citations.py:185
- `function _first_author` — skills/paper-writer/scripts/verify_citations.py:192
- `function _bib_doi` — skills/paper-writer/scripts/verify_citations.py:200
- `function _fill` — skills/paper-writer/scripts/verify_citations.py:204
- `function audit_entry` — skills/paper-writer/scripts/verify_citations.py:213
- `function main` — skills/paper-writer/scripts/verify_citations.py:285

## Dependencies (imports)
- `__future__`
- `argparse`
- `dataclasses`
- `difflib`
- `figs`
- `httpx`
- `json`
- `matplotlib`
- `numpy`
- `os`
- `pybtex`
- `re`
- `sys`
- `tenacity`
- `time`
<!-- projectmap:auto:end -->
