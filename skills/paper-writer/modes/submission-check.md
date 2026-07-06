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
  --bib refs/<slug>.bib --must-include <tokens from venue profile> --json
```

Use its output as the evidence for items 2, 7 (static part), and 8 below —
do not re-derive those by reading (rule 4 of `execution_discipline.md`).

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
- [ ] `build_paper.sh compile` ran; the draft builds.
- [ ] Every checklist item is PASS / FAIL / N-A with a one-line reason —
      no blanks.
- [ ] Required FAILs listed separately as blocking action items.
- [ ] `stage: final` written **only** on all-required-PASS.
