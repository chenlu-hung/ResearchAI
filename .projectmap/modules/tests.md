# Module: `tests`

## Summary
Pytest suite covering both the deterministic helper scripts and the repo's own consistency invariants. The script tests (`dedupe_rank`, `scan_injection`, `check_tex`, `check_prose`, `check_venues`) drive each CLI as a subprocess via the `run_script` fixture in `conftest.py` — real CLI, tmp-dir fixtures, no network — asserting merge/rank behaviour, injection and extractor-divergence detection, TeX/bib cross-checks and the abstract word cap, prose-hygiene findings, and venue-knowledge drift plus exemplar provenance; `test_evidence_store.py` is the largest file and exercises `evidence_core` end to end (ingest dedup, verified-passage requirements, packet freeze/invalidation, deterministic BibTeX export). The rest assert repo-level invariants against the real tree rather than fixtures: `test_host_parity.py` (Codex/Claude wrapper parity, README invocations), `test_executable_paths.py` (no cwd-relative script invocations in runtime Markdown), `test_research_lifecycle.py` (phase→gate mapping matches `research_state.schema.md`), and `test_check_venues.py::test_repo_venue_knowledge_is_consistent`. Run with `uv run pytest tests/ -q`; these scripts carry integrity-gate duties, so keep them covered when extending.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (10)
- `tests/conftest.py`
- `tests/test_check_prose.py`
- `tests/test_check_tex.py`
- `tests/test_check_venues.py`
- `tests/test_dedupe_rank.py`
- `tests/test_evidence_store.py`
- `tests/test_executable_paths.py`
- `tests/test_host_parity.py`
- `tests/test_research_lifecycle.py`
- `tests/test_scan_injection.py`

## Public symbols (83)
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
- `function _abstract_paper` — tests/test_check_tex.py:109
- `function test_abstract_within_limit_is_clean` — tests/test_check_tex.py:117
- `function test_abstract_over_limit_blocks` — tests/test_check_tex.py:128
- `function test_abstract_word_count_ignores_tex_commands_and_counts_math_once` — tests/test_check_tex.py:138
- `function test_missing_abstract_warns_but_does_not_block` — tests/test_check_tex.py:153
- `function test_abstract_limit_absent_skips_the_check` — tests/test_check_tex.py:164
- `function test_abstract_limit_rejects_nonpositive` — tests/test_check_tex.py:173
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
- `function _grounded_store` — tests/test_evidence_store.py:15
- `function test_cli_init_and_validate` — tests/test_evidence_store.py:76
- `function test_cli_can_freeze_a_grounded_packet_end_to_end` — tests/test_evidence_store.py:87
- `function run` — tests/test_evidence_store.py:92
- `function test_work_ingest_deduplicates_and_uses_stable_ids` — tests/test_evidence_store.py:275
- `function test_url_cannot_masquerade_as_versioned_fulltext` — tests/test_evidence_store.py:300
- `function test_abstract_cannot_verify_or_support` — tests/test_evidence_store.py:311
- `function test_query_preserves_provider_rank_and_raw_response_hash` — tests/test_evidence_store.py:332
- `function test_material_candidate_change_invalidates_packet_and_preserves_snapshot` — tests/test_evidence_store.py:360
- `function test_stale_source_hash_is_detected` — tests/test_evidence_store.py:398
- `function test_dataset_without_real_hash_warns_and_later_hash_invalidates_packet` — tests/test_evidence_store.py:415
- `function test_human_notes_and_multiline_yaml_lists_coexist` — tests/test_evidence_store.py:445
- `function test_index_rebuild_preserves_manual_text` — tests/test_evidence_store.py:466
- `function test_reusable_reading_passage_method_and_audit_are_first_class` — tests/test_evidence_store.py:479
- `function test_bibtex_export_is_deterministic_with_stable_collision_keys` — tests/test_evidence_store.py:528
- `function test_init_seeds_single_source_schemas_and_all_templates_idempotently` — tests/test_evidence_store.py:552
- `function test_source_hash_kind_distinguishes_discovery_from_content` — tests/test_evidence_store.py:573
- `function test_verified_fulltext_link_requires_matching_passage` — tests/test_evidence_store.py:612
- `function test_packet_freezes_passage_and_auto_invalidation_is_scoped` — tests/test_evidence_store.py:647
- `function test_manual_packet_invalidation_preserves_snapshot` — tests/test_evidence_store.py:745
- `function test_audit_subject_and_artifact_hash_bindings_validate` — tests/test_evidence_store.py:762
- …and 23 more

## Dependencies (imports)
- `__future__`
- `datetime`
- `evidence_core`
- `json`
- `os`
- `pathlib`
- `pytest`
- `re`
- `shutil`
- `subprocess`
- `sys`
<!-- projectmap:auto:end -->
