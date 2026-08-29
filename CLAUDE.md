## Project map
A `.projectmap/` index exists — use it before broad exploration:
- Read `.projectmap/ARCHITECTURE.md` for the module map, entry points, and conventions.
- To locate a symbol, grep `.projectmap/tags` (ctags format) instead of scanning the repo.
- Open `.projectmap/modules/<name>.md` only for the module you're working in.
- Note: `tags` indexes Python only. This repo's behaviour lives mostly in Markdown
  (`commands/*.md`, `skills/*/SKILL.md`, `skills/*/modes/*.md`, `shared/prompts/*.md`) —
  grep those directly.
Re-run `/project-map update` after substantial changes.

## Conventions
- Prose gates: any drafted/edited paper or proposal prose passes
  `shared/prompts/prose_hygiene.md`; its mechanical subset is
  `skills/paper-writer/scripts/check_prose.py` (run it and paste the
  result line — never eyeball).
- Provenance: venue and NSTC ground truth (page caps, review weights,
  policies) carries `as_of`/sources and is re-verified per cycle, never
  asserted from model memory. `check_venues.py` reports staleness as a
  warning so it cannot block an unrelated commit; the monthly `maintenance`
  workflow runs `scripts/check_freshness.py`, which turns the same finding
  red at 180 days.
- CI: `.github/workflows/checks.yml` gates every push and PR (ruff, pytest,
  test-count ratchet, host parity, venue consistency);
  `.github/workflows/maintenance.yml` runs monthly for the two time-based
  obligations no commit triggers — provenance freshness and audit cadence.
  A rule stated here that CI could check but doesn't is a rule that will
  drift; wire it or record why not.
- Test count: `tests/baseline_count.txt` is an exact ratchet, not a lower
  bound. Adding tests fails CI until you run
  `python3 scripts/check_test_count.py --update` and commit the new baseline
  alongside them.
- Firm rules: wording duplicated inline across runtime prompts is pinned in
  `shared/firm_rules.md` under an `R-*` id. To change such a rule, edit the
  canonical block first, then every mirror, in one commit;
  `scripts/check_firm_rules.py` names the mirrors you missed. Inlining is
  correct for prompt text — an agent will not follow a rule it never loaded —
  so the fix for duplication is a pin, not a pointer.
- Modes: `shared/mode_registry.md` is the single source of truth. Adding,
  renaming, or removing a mode means editing the registry first, then the
  owning `SKILL.md`, then `routing.md`; `scripts/check_mode_registry.py`
  enforces that all four declarations agree.
- Boundaries: `POSITIONING.md` records what the plugin refuses to do, why, and
  what kind of change would cross each line. A change that touches a recorded
  boundary edits the boundary first. `scripts/check_doc_refs.py` keeps its
  enforcement pointers from rotting.
- Evals: `evals/` holds held-out cases for the LLM-mediated judgments the test
  suite cannot reach. Ground truth never enters the run — build a pack with
  `scripts/eval_pack.py`, answer it in a fresh session, score with
  `scripts/eval_score.py`. Not wired into CI on purpose: a model grading cases
  it can see measures nothing.
- Audits: the check surface gets a retirement review every 120 days —
  generate the inventory with `scripts/gate_inventory.py`, rule keep / merge
  / retire on every row, file it in `audits/`. Retirement is recorded, never
  silent. Protocol: `audits/README.md`.
- Versioning: bump the version yourself when plugin behaviour changes —
  this is standing authorization, do not ask first. Patch = docs, wording,
  or bug fixes; minor = a new skill/mode/gate or a changed contract; major =
  a breaking `.research-state` or evidence-vault schema change. The same base
  version must appear in `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and
  `pyproject.toml`; run `python3 scripts/check_host_parity.py` and bump in the
  same commit as the change it describes.
