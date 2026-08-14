# Module: `skills/paper-writer`

## Summary
The Python helpers behind the `paper-writer` skill (`/write`) — one networked auditor plus four stdlib-only static gates. `verify_citations.py` matches each BibTeX entry against Semantic Scholar → OpenAlex → Crossref (DOI plus fuzzy title/author/year matching via `difflib`) to flag fabricated or mismatched references. `check_tex.py` is the static TeX gate — Stage 0 of `citation-audit` and the evidence source for `submission-check`: undefined `\cite`/`\ref`, missing figure files, venue `must_include` tokens, and (with `--abstract-word-limit`) a deterministic abstract word count that blocks when over the venue cap and warns when no abstract is found. `check_prose.py` lints paper prose against `shared/prompts/prose_hygiene.md` (list budget, pseudo-list runs, heading fragmentation, banned phrases, em-dash rate as blocking findings; rhythm/structural patterns and connective stacking as warnings for the LLM hygiene pass). `check_venues.py` cross-checks the venue-knowledge triple — `venue_profiles.md` Defaults ↔ `style/<venue>.md` ↔ `check_tex.py`'s `MUST_INCLUDE_PATTERNS` — for drift, stale provenance, and exemplar-provenance rules (`observed_fields` ⊆ `unverified`, `OBSERVABLE_FIELDS`-eligible, paired with `observed_sample` ids); meant to run after every venue-calibration. `figs.py` is a small matplotlib/numpy styling library runnable standalone as a smoketest; not indexed here: `build_paper.sh` (compile gate + DOCX export) and the skill's mode/style Markdown.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (5)
- `skills/paper-writer/scripts/check_prose.py`
- `skills/paper-writer/scripts/check_tex.py`
- `skills/paper-writer/scripts/check_venues.py`
- `skills/paper-writer/scripts/figs.py`
- `skills/paper-writer/scripts/verify_citations.py`

## Public symbols (60)
- `function blank_keep_newlines` — skills/paper-writer/scripts/check_prose.py:132
- `function strip_comments` — skills/paper-writer/scripts/check_prose.py:136
- `function blank_envs` — skills/paper-writer/scripts/check_prose.py:140
- `function blank_math` — skills/paper-writer/scripts/check_prose.py:148
- `function repl` — skills/paper-writer/scripts/check_prose.py:149
- `function strip_commands` — skills/paper-writer/scripts/check_prose.py:158
- `function count_words` — skills/paper-writer/scripts/check_prose.py:166
- `function line_of` — skills/paper-writer/scripts/check_prose.py:170
- `function extract_list_spans` — skills/paper-writer/scripts/check_prose.py:174
- `function blank_spans` — skills/paper-writer/scripts/check_prose.py:191
- `function build_paragraphs` — skills/paper-writer/scripts/check_prose.py:202
- `function split_sentences` — skills/paper-writer/scripts/check_prose.py:219
- `function maximal_runs` — skills/paper-writer/scripts/check_prose.py:228
- `function uniform_length_runs` — skills/paper-writer/scripts/check_prose.py:244
- `function snippet` — skills/paper-writer/scripts/check_prose.py:266
- `function scan_phrases` — skills/paper-writer/scripts/check_prose.py:272
- `function paragraph_head_runs` — skills/paper-writer/scripts/check_prose.py:289
- `function analyze_tex` — skills/paper-writer/scripts/check_prose.py:314
- `function analyze_md` — skills/paper-writer/scripts/check_prose.py:337
- `function check_file` — skills/paper-writer/scripts/check_prose.py:374
- `function gather_tex_files` — skills/paper-writer/scripts/check_prose.py:462
- `function main` — skills/paper-writer/scripts/check_prose.py:483
- `function strip_comments` — skills/paper-writer/scripts/check_tex.py:70
- `function count_abstract_words` — skills/paper-writer/scripts/check_tex.py:74
- `function gather_sources` — skills/paper-writer/scripts/check_tex.py:94
- `function find_graphic` — skills/paper-writer/scripts/check_tex.py:124
- `function main` — skills/paper-writer/scripts/check_tex.py:132
- `namespace dt` — skills/paper-writer/scripts/check_venues.py:37
- `function slug` — skills/paper-writer/scripts/check_venues.py:60
- `function strip_quotes` — skills/paper-writer/scripts/check_venues.py:65
- `function parse_value` — skills/paper-writer/scripts/check_venues.py:71
- `function parse_defaults` — skills/paper-writer/scripts/check_venues.py:80
- `function main` — skills/paper-writer/scripts/check_venues.py:133
- `function apply_style` — skills/paper-writer/scripts/figs.py:32
- `namespace mpl` — skills/paper-writer/scripts/figs.py:33
- `function save` — skills/paper-writer/scripts/figs.py:55
- `function band` — skills/paper-writer/scripts/figs.py:63
- `namespace np` — skills/paper-writer/scripts/figs.py:65
- `function ablation_bar` — skills/paper-writer/scripts/figs.py:73
- `namespace np` — skills/paper-writer/scripts/figs.py:75
- `namespace plt` — skills/paper-writer/scripts/figs.py:85
- `namespace np` — skills/paper-writer/scripts/figs.py:86
- `class Retryable` — skills/paper-writer/scripts/verify_citations.py:43
- `class AuditRow` — skills/paper-writer/scripts/verify_citations.py:48
- `function _get` — skills/paper-writer/scripts/verify_citations.py:70
- `function _s2` — skills/paper-writer/scripts/verify_citations.py:84
- `function _oa_row` — skills/paper-writer/scripts/verify_citations.py:102
- `function _openalex` — skills/paper-writer/scripts/verify_citations.py:115
- `function _cr_row` — skills/paper-writer/scripts/verify_citations.py:133
- `function _crossref` — skills/paper-writer/scripts/verify_citations.py:146
- `function _norm` — skills/paper-writer/scripts/verify_citations.py:163
- `function _sim` — skills/paper-writer/scripts/verify_citations.py:167
- `function _best` — skills/paper-writer/scripts/verify_citations.py:171
- `function _year_int` — skills/paper-writer/scripts/verify_citations.py:180
- `function _matches` — skills/paper-writer/scripts/verify_citations.py:186
- `function _first_author` — skills/paper-writer/scripts/verify_citations.py:193
- `function _bib_doi` — skills/paper-writer/scripts/verify_citations.py:201
- `function _fill` — skills/paper-writer/scripts/verify_citations.py:205
- `function audit_entry` — skills/paper-writer/scripts/verify_citations.py:214
- `function main` — skills/paper-writer/scripts/verify_citations.py:286

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
