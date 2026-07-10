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
  asserted from model memory.
