# Module: `skills/paper-writer`

## Summary
The Python helpers behind the `paper-writer` skill (`/write`) — one networked auditor plus four stdlib-only static gates. `verify_citations.py` matches each BibTeX entry against Semantic Scholar → OpenAlex → Crossref (DOI plus fuzzy title/author/year matching via `difflib`) to flag fabricated or mismatched references. `check_tex.py` is the static TeX gate — Stage 0 of `citation-audit` and the evidence source for `submission-check`: undefined `\cite`/`\ref`, missing figure files, venue `must_include` tokens. `check_prose.py` lints paper prose against `shared/prompts/prose_hygiene.md` (list budget, pseudo-list runs, heading fragmentation, banned phrases, em-dash rate as blocking findings; rhythm/structural patterns as warnings for the LLM hygiene pass). `check_venues.py` cross-checks the venue-knowledge triple — `venue_profiles.md` Defaults ↔ `style/<venue>.md` ↔ `check_tex.py`'s `MUST_INCLUDE_PATTERNS` — for drift, stale provenance, and exemplar-provenance rules (`observed_fields` ⊆ `unverified`, `OBSERVABLE_FIELDS`-eligible, paired with `observed_sample` ids); meant to run after every venue-calibration. `figs.py` is a small matplotlib/numpy styling library runnable standalone as a smoketest; not indexed here: `build_paper.sh` (compile gate + DOCX export) and the skill's mode/style Markdown.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (5)
- `skills/paper-writer/scripts/check_prose.py`
- `skills/paper-writer/scripts/check_tex.py`
- `skills/paper-writer/scripts/check_venues.py`
- `skills/paper-writer/scripts/figs.py`
- `skills/paper-writer/scripts/verify_citations.py`

## Public symbols (59)
- `function blank_keep_newlines` — skills/paper-writer/scripts/check_prose.py:122
- `function strip_comments` — skills/paper-writer/scripts/check_prose.py:126
- `function blank_envs` — skills/paper-writer/scripts/check_prose.py:130
- `function blank_math` — skills/paper-writer/scripts/check_prose.py:138
- `function repl` — skills/paper-writer/scripts/check_prose.py:139
- `function strip_commands` — skills/paper-writer/scripts/check_prose.py:148
- `function count_words` — skills/paper-writer/scripts/check_prose.py:156
- `function line_of` — skills/paper-writer/scripts/check_prose.py:160
- `function extract_list_spans` — skills/paper-writer/scripts/check_prose.py:164
- `function blank_spans` — skills/paper-writer/scripts/check_prose.py:181
- `function build_paragraphs` — skills/paper-writer/scripts/check_prose.py:192
- `function split_sentences` — skills/paper-writer/scripts/check_prose.py:209
- `function maximal_runs` — skills/paper-writer/scripts/check_prose.py:218
- `function uniform_length_runs` — skills/paper-writer/scripts/check_prose.py:234
- `function snippet` — skills/paper-writer/scripts/check_prose.py:256
- `function scan_phrases` — skills/paper-writer/scripts/check_prose.py:262
- `function paragraph_head_runs` — skills/paper-writer/scripts/check_prose.py:279
- `function analyze_tex` — skills/paper-writer/scripts/check_prose.py:304
- `function analyze_md` — skills/paper-writer/scripts/check_prose.py:327
- `function check_file` — skills/paper-writer/scripts/check_prose.py:364
- `function gather_tex_files` — skills/paper-writer/scripts/check_prose.py:441
- `function main` — skills/paper-writer/scripts/check_prose.py:462
- `function strip_comments` — skills/paper-writer/scripts/check_tex.py:56
- `function gather_sources` — skills/paper-writer/scripts/check_tex.py:60
- `function find_graphic` — skills/paper-writer/scripts/check_tex.py:90
- `function main` — skills/paper-writer/scripts/check_tex.py:98
- `namespace dt` — skills/paper-writer/scripts/check_venues.py:35
- `function slug` — skills/paper-writer/scripts/check_venues.py:58
- `function strip_quotes` — skills/paper-writer/scripts/check_venues.py:63
- `function parse_value` — skills/paper-writer/scripts/check_venues.py:69
- `function parse_defaults` — skills/paper-writer/scripts/check_venues.py:78
- `function main` — skills/paper-writer/scripts/check_venues.py:131
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
- `check_tex`
- `dataclasses`
- `datetime`
- `difflib`
- `figs`
- `httpx`
- `json`
- `matplotlib`
- `numpy`
- `os`
- `pathlib`
- `pybtex`
- `re`
- `sys`
- `tenacity`
- `time`
<!-- projectmap:auto:end -->
