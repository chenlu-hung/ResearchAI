# Mode: submission-check

**Purpose**: the submission-readiness gate. Verify the draft carries every
artifact the venue requires before `stage` may advance to `final`.

## Inputs

- Draft (`paper/main.tex`) — required
- `venue_target` — required
- Research state (for the latest citation audit result)

## Procedure

Load the venue's `must_include` list and limits from the `Defaults by venue`
block in `shared/venue_profiles.md`.

First gather the mechanical evidence with the static checker — pass the
venue's `must_include` tokens straight through:

```bash
uv run python skills/paper-writer/scripts/check_tex.py paper/main.tex \
  --bib refs/<slug>.bib --must-include <tokens from venue profile> \
  <one --pattern token=regex per entry in the venue's must_include_patterns> \
  --json
uv run python skills/paper-writer/scripts/check_prose.py paper/main.tex
uv run python skills/paper-writer/scripts/check_venues.py
```

Use their output as the evidence for items 2, 7 (static part), 8, and 9
below — do not re-derive those by reading (rule 4 of
`execution_discipline.md`). `check_venues.py` guards the *profile itself*:
surface any staleness warning (as_of > 1 year) to the user.

**Unverified fields**: any checklist item whose backing field is listed in
the venue's `unverified:` (see `shared/prompts/venue_calibration.md`) may
not FAIL the gate — report it as **WARN** with "field unverified — re-run
venue-calibration". If the field is also in the venue's `observed_fields`,
cite the evidence instead: "unverified — observed in sample (n=k)".
Verified fields gate as usual.

Produce a checklist; each item is **PASS / FAIL / N/A** with a one-line
reason. Items:

1. **Length**: main-text pages ≤ `page_limit` (skip if `null`). Estimate if not
   compiled.
2. **Required sections**: every entry in the venue's `must_include` is present
   (e.g. `limitations`, `broader_impact`, `reproducibility`, `ai_disclosure`,
   `proofs_in_main`, `assumption_discussion`, `identifiability`).
3. **Compute reporting** (empirical papers; NeurIPS/ICML 2024+): GPU type+count,
   wall-clock, total compute stated.
4. **Reproducibility**: data/code availability statement present; multi-seed
   results meet `seed_count_min`.
5. **AI disclosure**: LLM-use statement present where the venue requires it.
6. **Anonymization** (double-blind venues): no author names, affiliations,
   funding/acknowledgments, or de-anonymizing links/URLs in the main text;
   self-citations phrased in third person ("Smith et al." not "our prior work").
7. **Citations**: most recent `citation-audit` has 0 `fabricated` and 0
   `contradicts`. If no audit exists, FAIL and tell the user to run
   `citation-audit` first.
8. **Figures**: every figure is referenced in text, captioned, and vector
   (PDF). Run `build_paper.sh compile` — the draft must build.
9. **Prose format**: `check_prose.py` reports no blocking findings on any
   section, except those explicitly waived as §F slots (Intro contribution
   bullets, enumerated assumptions). A bullet-shaped section reads as
   machine-written and is a desk-risk.

## Output

A markdown checklist table. List required FAILs as blocking action items
separately from N/A and optional items.

## Gate

If any **required** item is FAIL, refuse to advance `stage` to `final`; report
the blocking items. Only on all-required-PASS:

```yaml
stage: final
```

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] `check_tex.py` ran with the venue's `must_include` tokens; output
      pasted and used as evidence, not paraphrased from memory.
- [ ] `check_prose.py` ran on the full draft; output pasted; item 9 judged
      from it (blocking findings fixed or waived as §F slots).
- [ ] `check_venues.py` ran; venue's `must_include_patterns` passed through
      as `--pattern`; unverified-field items reported WARN, never FAIL.
- [ ] `build_paper.sh compile` ran; the draft builds.
- [ ] Every checklist item is PASS / FAIL / N-A with a one-line reason —
      no blanks.
- [ ] Required FAILs listed separately as blocking action items.
- [ ] `stage: final` written **only** on all-required-PASS.
