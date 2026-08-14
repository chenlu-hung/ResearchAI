# Module: `shared`

## Summary
`shared` holds cross-skill infrastructure used by every skill. `council.py` is a stdlib-only dispatcher that fans one prompt out to a multi-model panel (Codex, Gemini, Claude, DeepSeek) in parallel — each reached through its own subscription CLI inside a read-only sandbox — and returns parsed JSON for the orchestrating session to synthesize; it backs the opt-in `--council` flag, and is invoked as `python3 "$PLUGIN_ROOT/shared/council.py"` since skills run from the user's project cwd. `evidencectl.py` is a two-line stable entry point onto `evidence_core.cli` (see [shared/evidence_core](shared__evidence_core.md)). The rest of `shared/` is Markdown not indexed here: `prompts/` (anti-hallucination, council panel, prose hygiene, venue calibration, reviewer intel, grill, execution discipline, model dispatch, plus `evidence_grounding.md` and `research_lifecycle.md`), `venue_profiles.md`, and `research_state.schema.md`.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (2)
- `shared/council.py`
- `shared/evidencectl.py`

## Public symbols (7)
- `function run_codex` — shared/council.py:53
- `function run_gemini` — shared/council.py:80
- `function run_claude` — shared/council.py:97
- `function run_opencode` — shared/council.py:120
- `function dispatch` — shared/council.py:156
- `function read_prompt` — shared/council.py:171
- `function main` — shared/council.py:182

## Dependencies (imports)
- `argparse`
- `concurrent`
- `evidence_core`
- `json`
- `os`
- `re`
- `shutil`
- `subprocess`
- `sys`
- `tempfile`
- `time`
<!-- projectmap:auto:end -->
