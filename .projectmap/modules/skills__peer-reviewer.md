# Module: `skills/peer-reviewer`

## Summary
Deterministic helper behind the `peer-reviewer` skill's mandatory injection scan (`/review` `report`/`triage` pre-flight). `scan_injection.py` greps a manuscript's extracted text layer for reviewer-directed hidden prompts (a named regex per attack family) and, with `--compare`, diffs two independent extractions to catch decoy-glyph/ToUnicode payloads that never render on the page. It exists so the scan is a script run, not a model recollection (execution_discipline rule 4); hits are a screen the reviewer triages with SKILL.md's author-payload-vs-platform-canary rules. The skill's prompt logic lives in the sibling Markdown (`SKILL.md`, `modes/`, `checklists/`), not here.

<!-- projectmap:auto:start (generated — do not edit by hand) -->
## Files (1)
- `skills/peer-reviewer/scripts/scan_injection.py`

## Public symbols (4)
- `function scan_text` — skills/peer-reviewer/scripts/scan_injection.py:43
- `function _substantive_lines` — skills/peer-reviewer/scripts/scan_injection.py:63
- `function compare_extractions` — skills/peer-reviewer/scripts/scan_injection.py:72
- `function main` — skills/peer-reviewer/scripts/scan_injection.py:82

## Dependencies (imports)
- `__future__`
- `argparse`
- `json`
- `pathlib`
- `re`
- `sys`
<!-- projectmap:auto:end -->
