# Module: `tests`

## Summary
Pytest suite for the three deterministic helper scripts (`dedupe_rank.py`, `scan_injection.py`, `check_tex.py`). Each test drives the script as a subprocess via the `run_script` fixture in `conftest.py` — real CLI, tmp-dir fixtures, no network — asserting merge/rank behaviour, injection-pattern and extractor-divergence detection, and TeX/bib cross-check findings plus exit codes. Run with `uv run pytest tests/ -q`; these scripts carry integrity-gate duties, so keep them covered when extending.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (4)
- `tests/conftest.py`
- `tests/test_check_tex.py`
- `tests/test_dedupe_rank.py`
- `tests/test_scan_injection.py`

## Public symbols (14)
- `function run_script` — tests/conftest.py:11
- `function _run` — tests/conftest.py:14
- `function _paper` — tests/test_check_tex.py:18
- `function test_blocking_findings_detected` — tests/test_check_tex.py:36
- `function test_clean_paper_exits_zero` — tests/test_check_tex.py:63
- `function test_unknown_must_include_token_blocks` — tests/test_check_tex.py:76
- `function _write_jsonl` — tests/test_dedupe_rank.py:6
- `function test_merges_across_sources_and_ranks` — tests/test_dedupe_rank.py:10
- `function test_same_title_far_apart_years_not_merged` — tests/test_dedupe_rank.py:74
- `function test_top_limit_and_bad_lines_skipped` — tests/test_dedupe_rank.py:90
- `function test_clean_text_exits_zero` — tests/test_scan_injection.py:18
- `function test_injected_text_flagged_with_patterns` — tests/test_scan_injection.py:26
- `function test_extractor_divergence_flagged` — tests/test_scan_injection.py:38
- `function test_identical_extractions_routine` — tests/test_scan_injection.py:53

## Dependencies (imports)
- `json`
- `pathlib`
- `pytest`
- `subprocess`
- `sys`
<!-- projectmap:auto:end -->
