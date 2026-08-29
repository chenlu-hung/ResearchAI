---
description: Run a mode of the paper-writer skill. Modes: positioning-skeleton, outline, full-draft, revision, citation-audit, self-review, submission-check, venue-calibration, post-mortem, grant-nstc.
argument-hint: <mode> [--venue <key from shared/venue_profiles.md>] [--council]
---

Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
it is the absolute parent of the file's `commands/` directory. Never derive it
from the user's working directory. Resolve every `skills/...`, `shared/...`, or
other plugin resource below as `$PLUGIN_ROOT/<path>`. Dependency-bearing Python
scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Invoke the `paper-writer` skill in the mode specified: $ARGUMENTS

Modes (see `skills/paper-writer/SKILL.md`):

- `positioning-skeleton` — intro, related work, contribution statements (from
  the frozen spine), and **empty** result-table/figure shells, drafted *before*
  the experiments run; the promised rows become the experiment contract's input
  spec. The one mode exempt from the results-gate pre-flight — and the one
  forbidden a results section or any numeric cell
- `outline` — section-by-section outline tailored to venue
- `full-draft` — complete LaTeX draft, section by section
- `revision` — targeted edits to a specific section
- `citation-audit` — verify generated BibTeX metadata against Semantic Scholar →
  OpenAlex → Crossref, then verify every atomic cited claim against its exact passage
- `self-review` — one-pass venue-reviewer critique of the draft (distinct
  from `algo-brainstorm`'s method-level `red-team`)
- `submission-check` — submission-readiness gate before `stage: final`
- `venue-calibration` — add or re-verify a venue profile from official
  sources (CFP / author guidelines), optionally grounded in exemplar
  papers, with provenance; the only mode that edits
  `shared/venue_profiles.md` and `style/`
- `post-mortem` — decompose a rejection's reviews into atomic objections and
  attribute each to the lifecycle gate that should have caught it, proposing a
  change to that gate's owning mode / artifact schema / exit checklist /
  hard-stop list. Runs after `final`/rejection or on a retrofit entry; sets
  `research_phase` back to the earliest gate its findings invalidate. Venue-wide
  lessons route through `venue-calibration` as `unverified` single-paper
  evidence; paper edits go to `revision`'s reviewer-response sub-mode
- `grant-nstc` — draft/revise an NSTC (國科會) 專題研究計畫 CM03 in the
  proposal register (vision + feasibility, review-weight-aware); needs no
  research state, reuses one if present

Pre-flight exemption: `positioning-skeleton` alone runs before the results chain
exists — it is exempt from the experiment-contract/protocol/results/audit/
red-team requirement below, but not from method freeze (with a spine), a current
packet, or the synced `.bib`. All other modes gate as stated.

Pre-flight: refuse to emit `full-draft` if `red-team` mode has any
`blocking: true` finding unresolved, or if `algorithm_card`, a validated current
candidate/claim evidence packet, or the generated `refs/<slug>.bib` view is
missing. Method freeze, applicable protocol/real-results ingest, evidence audit,
and results-aware red team must also pass with matching artifact hashes; after
drafting, scientific review + passage audit gate submission. A legacy `.bib` or
abstract is not claim support. Refer to `shared/prompts/research_lifecycle.md`,
`shared/prompts/evidence_grounding.md`, `shared/venue_profiles.md`, and the per-venue style
files in `skills/paper-writer/style/` for tone and structure.

If the arguments include `--council` (supported by `outline` and
`self-review`), additionally run the multi-model panel in
`shared/prompts/council_panel.md` after the mode's gating — fan out to
Codex / Gemini / Claude / opencode via
`python3 "$PLUGIN_ROOT/shared/council.py"`, then chair
the synthesis (`self-review` becomes a multi-reviewer meta-review; `outline`
becomes a structure bake-off). Panel claims/citations become queries and cannot
enter prose until vault-first retrieval, passage linking, and packet refresh.
Without `--council`, run the mode single-model.
