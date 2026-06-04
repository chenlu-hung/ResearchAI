---
description: Run a mode of the paper-writer skill. Modes: outline, full-draft, revision, citation-audit, self-review, submission-check.
argument-hint: <mode> [--venue neurips|icml|jmlr|aistats]
---

Invoke the `paper-writer` skill in the mode specified: $ARGUMENTS

Modes (see `skills/paper-writer/SKILL.md`):

- `outline` — section-by-section outline tailored to venue
- `full-draft` — complete LaTeX draft, section by section
- `revision` — targeted edits to a specific section
- `citation-audit` — verify every citation against Semantic Scholar →
  OpenAlex → Crossref + claim-support pass
- `self-review` — one-pass venue-reviewer critique of the draft (distinct
  from `algo-brainstorm`'s method-level `red-team`)
- `submission-check` — submission-readiness gate before `stage: final`

Pre-flight: refuse to emit `full-draft` if `red-team` mode has any
`blocking: true` finding unresolved, or if `algorithm_card` / `refs/<slug>.bib`
are missing. Refer to `shared/venue_profiles.md` and the per-venue style
files in `skills/paper-writer/style/` for tone and structure.
