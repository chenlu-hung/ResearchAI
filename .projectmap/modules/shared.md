# Module: `shared`

## Summary
`shared` holds cross-skill infrastructure used by all three research skills. Its only Python file, `council.py`, is a stdlib-only dispatcher that fans one prompt out to a multi-model panel (Codex, Gemini, Claude, DeepSeek) in parallel — each reached through its own subscription CLI inside a read-only sandbox — and returns parsed JSON for the orchestrating session to synthesize. It backs the opt-in `--council` flag in the algo/paper modes. The rest of `shared/` is Markdown not indexed here: `prompts/` (anti-hallucination, council protocol, prose hygiene, style calibration, grill), `venue_profiles.md`, and `research_state.schema.md`.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (1)
- `shared/council.py`

## Public symbols (7)
- `function run_codex` — shared/council.py:51
- `function run_gemini` — shared/council.py:78
- `function run_claude` — shared/council.py:95
- `function run_opencode` — shared/council.py:118
- `function dispatch` — shared/council.py:154
- `function read_prompt` — shared/council.py:169
- `function main` — shared/council.py:180

## Dependencies (imports)
- `argparse`
- `concurrent`
- `json`
- `os`
- `re`
- `shutil`
- `subprocess`
- `sys`
- `tempfile`
- `time`
<!-- projectmap:auto:end -->
