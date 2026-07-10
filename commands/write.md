---
description: Run a mode of the paper-writer skill. Modes: outline, full-draft, revision, citation-audit, self-review, submission-check, venue-calibration.
argument-hint: <mode> [--venue <key from shared/venue_profiles.md>] [--council]
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
- `venue-calibration` — add or re-verify a venue profile from official
  sources (CFP / author guidelines), optionally grounded in exemplar
  papers, with provenance; the only mode that edits
  `shared/venue_profiles.md` and `style/`

Pre-flight: refuse to emit `full-draft` if `red-team` mode has any
`blocking: true` finding unresolved, or if `algorithm_card` / `refs/<slug>.bib`
are missing. Refer to `shared/venue_profiles.md` and the per-venue style
files in `skills/paper-writer/style/` for tone and structure.

If the arguments include `--council` (supported by `outline` and
`self-review`), additionally run the multi-model panel in
`shared/prompts/council_panel.md` after the mode's gating — fan out to
Codex / Gemini / Claude / DeepSeek via `python3 shared/council.py`, then chair
the synthesis (`self-review` becomes a multi-reviewer meta-review; `outline`
becomes a structure bake-off). The panel never bypasses citation discipline —
any `\cite{...}` it emits is stripped or `[BIBKEY MISSING — verify]`. Without
`--council`, run the mode single-model.
