# Module: `scripts`

## Summary
Repo-level maintenance check, not part of any skill's runtime. `check_host_parity.py` asserts that the Codex (`.codex-plugin/plugin.json`, name `research-ai`) and Claude Code (`.claude-plugin/plugin.json` + `marketplace.json`, name `research-assistant`) wrappers front one shared `skills/` core: matching base versions across both manifests and `pyproject.toml`, no host-specific `.claude/skills` or `.codex/skills` fork, all six required skills present, and README documenting both invocation styles. It also lints every runtime Markdown file for cwd-relative script invocations — bare `python3 script.py`, `uv run` without `--project "$PLUGIN_ROOT"`, `cd "$PLUGIN_ROOT"` — which would break when a skill runs from the user's project directory. Exercised by `tests/test_host_parity.py`; run it after touching manifests, README, or any documented command line.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (1)
- `scripts/check_host_parity.py`

## Public symbols (6)
- `function _read_json` — scripts/check_host_parity.py:50
- `function _base_version` — scripts/check_host_parity.py:57
- `function _runtime_markdown` — scripts/check_host_parity.py:63
- `function _validate_documented_usage` — scripts/check_host_parity.py:74
- `function validate` — scripts/check_host_parity.py:150
- `function main` — scripts/check_host_parity.py:218

## Dependencies (imports)
- `__future__`
- `argparse`
- `json`
- `pathlib`
- `re`
- `tomllib`
<!-- projectmap:auto:end -->
