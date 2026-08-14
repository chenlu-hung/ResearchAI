# Module: `skills/evidence-store`

## Summary
The `evidence-store` skill — the shared evidence layer the four pipeline skills call before they claim anything, rather than a mode-based workflow of its own. Its only Python file is a six-line shim: it resolves the plugin root, puts `shared/` on `sys.path`, and delegates to `evidence_core.cli:main`, so the skill ships one `evidencectl` entry point without vendoring a second copy of the core (see [shared/evidence_core](shared__evidence_core.md)). The substance is the sibling Markdown and JSON not indexed here: `SKILL.md` (grounding loop, evidence rules, command reference), `references/record-model.md`, `references/schemas/*.json`, and `agents/openai.yaml` for the Codex host.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (1)
- `skills/evidence-store/scripts/evidencectl.py`

## Public symbols (0)

## Dependencies (imports)
- `__future__`
- `evidence_core`
- `pathlib`
- `sys`
<!-- projectmap:auto:end -->
