# Module: `tests`

## Summary
Pytest suite for the five deterministic helper scripts (`dedupe_rank.py`, `scan_injection.py`, `check_tex.py`, `check_prose.py`, `check_venues.py`). Each test drives the script as a subprocess via the `run_script` fixture in `conftest.py` — real CLI, tmp-dir fixtures, no network — asserting merge/rank behaviour, injection-pattern and extractor-divergence detection, TeX/bib cross-check findings, prose-hygiene blocking/warning findings, and venue-knowledge drift + exemplar-provenance validation (`observed_fields`/`observed_sample`), plus exit codes. `test_check_venues.py::test_repo_venue_knowledge_is_consistent` is the exception to the fixture pattern — it runs `check_venues.py` against this repo's real `venue_profiles.md`/`style/` as a live integration guard, not a synthetic tmp-dir case. Run with `uv run pytest tests/ -q`; these scripts carry integrity-gate duties, so keep them covered when extending.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (6)
- `tests/conftest.py`
- `tests/test_check_prose.py`
- `tests/test_check_tex.py`
- `tests/test_check_venues.py`
- `tests/test_dedupe_rank.py`
- `tests/test_scan_injection.py`

## Public symbols (36)
- `function run_script` — tests/conftest.py:11
- `function _run` — tests/conftest.py:14
- `function test_listy_ai_section_blocks` — tests/test_check_prose.py:82
- `function test_clean_section_passes` — tests/test_check_prose.py:96
- `function test_pseudo_list_run_blocks` — tests/test_check_prose.py:104
- `function test_rhythm_warnings_do_not_block` — tests/test_check_prose.py:114
- `function test_comments_math_and_envs_ignored` — tests/test_check_prose.py:127
- `function test_follows_inputs_and_reports_per_file` — tests/test_check_prose.py:148
- `function test_markdown_lists_and_phrases` — tests/test_check_prose.py:165
- `function _paper` — tests/test_check_tex.py:18
- `function test_blocking_findings_detected` — tests/test_check_tex.py:36
- `function test_clean_paper_exits_zero` — tests/test_check_tex.py:63
- `function test_unknown_must_include_token_blocks` — tests/test_check_tex.py:76
- `function test_pattern_flag_supplies_new_token` — tests/test_check_tex.py:83
- `function test_pattern_flag_rejects_bad_spec` — tests/test_check_tex.py:101
- `namespace dt` — tests/test_check_venues.py:1
- `function _setup` — tests/test_check_venues.py:35
- `function _run` — tests/test_check_venues.py:62
- `function test_consistent_profile_passes` — tests/test_check_venues.py:67
- `function test_unknown_token_without_pattern_blocks` — tests/test_check_venues.py:76
- `function test_venue_pattern_resolves_custom_token` — tests/test_check_venues.py:84
- `function test_missing_style_file_blocks` — tests/test_check_venues.py:92
- `function test_missing_as_of_blocks_and_stale_warns` — tests/test_check_venues.py:99
- `function test_observed_valid_pair_passes` — tests/test_check_venues.py:111
- `function test_observed_field_must_stay_unverified` — tests/test_check_venues.py:119
- `function test_observed_policy_field_blocks` — tests/test_check_venues.py:130
- `function test_observed_fields_without_sample_blocks` — tests/test_check_venues.py:141
- `function test_repo_venue_knowledge_is_consistent` — tests/test_check_venues.py:150
- `function _write_jsonl` — tests/test_dedupe_rank.py:6
- `function test_merges_across_sources_and_ranks` — tests/test_dedupe_rank.py:10
- `function test_same_title_far_apart_years_not_merged` — tests/test_dedupe_rank.py:74
- `function test_top_limit_and_bad_lines_skipped` — tests/test_dedupe_rank.py:90
- `function test_clean_text_exits_zero` — tests/test_scan_injection.py:18
- `function test_injected_text_flagged_with_patterns` — tests/test_scan_injection.py:26
- `function test_extractor_divergence_flagged` — tests/test_scan_injection.py:38
- `function test_identical_extractions_routine` — tests/test_scan_injection.py:53

## Dependencies (imports)
- `datetime`
- `json`
- `pathlib`
- `pytest`
- `subprocess`
- `sys`
<!-- projectmap:auto:end -->
