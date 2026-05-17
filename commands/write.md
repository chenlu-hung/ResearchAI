---
description: Run a mode of the paper-writer skill. Modes: outline, full-draft, revision, citation-audit.
argument-hint: <mode> [--venue neurips|icml|jmlr|aistats]
---

Invoke the `paper-writer` skill in the mode specified: $ARGUMENTS

Modes (see `skills/paper-writer/SKILL.md`):

- `outline` — section-by-section outline tailored to venue
- `full-draft` — complete LaTeX draft, section by section
- `revision` — targeted edits to a specific section
- `citation-audit` — verify every citation against Semantic Scholar +
  claim-support pass

Pre-flight: refuse to emit `full-draft` if `red-team` mode has any
`blocking: true` finding unresolved, or if `algorithm_card` / `refs/<slug>.bib`
are missing. Refer to `shared/venue_profiles.md` and the per-venue style
files in `skills/paper-writer/style/` for tone and structure.
