# Module: `shared/evidence_core`

## Summary
The canonical data plane: a stdlib-only, Markdown-backed evidence store holding works, immutable source versions, atomic claims, passages, readings, methods, datasets, query runs, evidence packets, and audit verdicts in a user-selected Obsidian vault. `model.py` defines the record types, controlled vocabularies (relations, verdicts, evidence scopes, source-hash kinds), stable IDs, and the JSON-in-YAML frontmatter serialization chosen so both Claude Code and Codex can read it with no host or package dependency; `store.py` implements atomic writes, the `EVIDENCECTL:BEGIN/END` generated-block contract, validation, and packet freeze/invalidation; `cli.py` exposes it all as the `evidencectl` command tree. It exists so evidence survives across sessions and hosts and so `verified` claims must carry a locator plus matching passage hash — the machinery behind `shared/prompts/evidence_grounding.md` and the lifecycle gates. Reached through the thin wrappers in [shared](shared.md) and [skills/evidence-store](skills__evidence-store.md); covered by `tests/test_evidence_store.py`.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (4)
- `shared/evidence_core/__init__.py`
- `shared/evidence_core/cli.py`
- `shared/evidence_core/model.py`
- `shared/evidence_core/store.py`

## Public symbols (30)
- `function _leaf` — shared/evidence_core/cli.py:15
- `function build_parser` — shared/evidence_core/cli.py:21
- `function _emit` — shared/evidence_core/cli.py:216
- `function dispatch` — shared/evidence_core/cli.py:220
- `function main` — shared/evidence_core/cli.py:413
- `function now_utc` — shared/evidence_core/model.py:168
- `function normalize_text` — shared/evidence_core/model.py:172
- `function slugify` — shared/evidence_core/model.py:177
- `function digest` — shared/evidence_core/model.py:186
- `function hash_file` — shared/evidence_core/model.py:198
- `function semantic_hash` — shared/evidence_core/model.py:206
- `function make_record` — shared/evidence_core/model.py:212
- `function _frontmatter_value` — shared/evidence_core/model.py:226
- `function parse_markdown` — shared/evidence_core/model.py:246
- `function default_body` — shared/evidence_core/model.py:284
- `function render_markdown` — shared/evidence_core/model.py:299
- `function normalize_doi` — shared/evidence_core/model.py:318
- `function normalize_arxiv` — shared/evidence_core/model.py:326
- `function work_id` — shared/evidence_core/model.py:335
- `function base_record_errors` — shared/evidence_core/model.py:357
- `class EvidenceStoreError` — shared/evidence_core/store.py:42
- `class ValidationIssue` — shared/evidence_core/store.py:47
- `function _atomic_write` — shared/evidence_core/store.py:58
- `function _replace_generated` — shared/evidence_core/store.py:78
- `function _ordered_unique` — shared/evidence_core/store.py:91
- `function _is_sha256` — shared/evidence_core/store.py:95
- `class EvidenceStore` — shared/evidence_core/store.py:99
- `function base_key` — shared/evidence_core/store.py:1563
- `function bib_value` — shared/evidence_core/store.py:1585
- `function require_ref` — shared/evidence_core/store.py:1716

## Dependencies (imports)
- ``
- `__future__`
- `argparse`
- `contextlib`
- `dataclasses`
- `datetime`
- `hashlib`
- `json`
- `os`
- `pathlib`
- `re`
- `shutil`
- `sys`
- `tempfile`
- `time`
- `typing`
- `unicodedata`
<!-- projectmap:auto:end -->
