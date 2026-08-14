# Mode: submission-check

**Purpose**: the submission-readiness gate. Verify the draft carries every
artifact the venue requires before `stage` may advance to `final`.

## Inputs

- Draft (`paper/main.tex`) — required
- `venue_target` — required
- Research state (for the latest citation audit result)
- Validated current evidence packet(s) for every invoked substantive claim
- `lifecycle_gates.scientific_review.status: pass` bound to current draft and
  all upstream method/protocol/result/evidence hashes

## Procedure

Load the venue's `must_include` list and limits from the `Defaults by venue`
block in `shared/venue_profiles.md`.

First gather the mechanical evidence with the static checker — pass the
venue's `must_include` tokens straight through:

```bash
python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_tex.py" paper/main.tex \
  --bib refs/<slug>.bib --must-include <tokens from venue profile> \
  <one --pattern token=regex per entry in the venue's must_include_patterns> \
  [--abstract-word-limit <venue abstract_word_limit, omit when null>] \
  --json
python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_prose.py" paper/main.tex
python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_venues.py"
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
   compiled. Also **abstract length**: if the venue's `abstract_word_limit` is
   non-null, pass it to `check_tex.py --abstract-word-limit` and judge from
   `abstract_words` / `abstract_over_limit` in its output — N/A when the field
   is `null`, WARN (not FAIL) when it is listed in the venue's `unverified:`.
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
7. **Citations and evidence**: most recent `citation-audit` has 0
   `fabricated`/`mismatched`/`contradicts`, every invoked substantive claim is
   passage-grounded in a validated current packet, and every audited key claim
   is `verified`. Abstract-only support or a clean `.bib` alone is FAIL. If no
   audit/packet exists, FAIL and route through retrieval then `citation-audit`.
   Every empirical/numeric claim must also trace to the current audited result
   manifest/artifact hashes and uncertainty under the frozen protocol.
8. **Figures**: every figure is referenced in text, captioned, and vector
   (PDF). Run
   `"$PLUGIN_ROOT/skills/paper-writer/scripts/build_paper.sh" compile paper/main.tex`
   — the draft must build. For ML venues, a **method/architecture figure** must
   exist and be referenced in the text; its absence is FAIL for
   NeurIPS/ICML/AISTATS (reviewers read the figure before the method section).

9. **Prose format**: `check_prose.py` reports no blocking findings on any
   section, except those explicitly waived as §F slots (Intro contribution
   bullets, enumerated assumptions). A bullet-shaped section reads as
   machine-written and is a desk-risk.

10. **Complexity analysis**: the paper contains the **per-phase** cost analysis
    from the algorithm card (preprocessing/decomposition, training,
    calibration/adaptation, inference) plus the scaling regime beyond the tested
    one. A single aggregate $O(\cdot)$ for the whole method is FAIL.

    **Blocking acceptance rule**: if the audited Cost analysis shows the method
    **infeasible in a regime that a spine claim targets**, this item FAILs and
    submission is blocked until either the claim is narrowed to a feasible
    regime or the method changes. Report which of the two is required and name
    the claim ID and the regime. A paper may not claim a regime its own
    complexity analysis rules out.

## Output

A markdown checklist table. List required FAILs as blocking action items
separately from N/A and optional items.

## Gate

If any **required** item is FAIL, refuse to advance `stage` to `final`; report
the blocking items. Only on all-required-PASS:

```yaml
stage: final
research_phase: final
lifecycle_gates:
  submission:
    status: pass
    artifact: .research-state/<slug>-submission-check-<date>.md
    artifact_hash: <64-char-sha256-hex>
```

Before writing `final`, revalidate **every** lifecycle gate and artifact hash,
not just the draft/audit. A stale upstream method, protocol, manifest, evidence
audit, results red team, or scientific review blocks submission.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] `check_tex.py` ran with the venue's `must_include` tokens and its
      `abstract_word_limit` when non-null; output pasted and used as evidence,
      not paraphrased from memory.
- [ ] `check_prose.py` ran on the full draft; output pasted; item 9 judged
      from it (blocking findings fixed or waived as §F slots).
- [ ] `check_venues.py` ran; venue's `must_include_patterns` passed through
      as `--pattern`; unverified-field items reported WARN, never FAIL.
- [ ] `"$PLUGIN_ROOT/skills/paper-writer/scripts/build_paper.sh" compile
      paper/main.tex` ran; the draft builds.
- [ ] Packet IDs/hashes/status validate against the exact candidate and invoked
      claim set; every substantive claim's audit has passage provenance.
- [ ] Scientific-review gate and every upstream lifecycle artifact/hash were
      revalidated against the current draft before `final`.
- [ ] ML venue: method/architecture figure exists and is referenced in text.
- [ ] Per-phase complexity analysis present in the paper (not one aggregate
      bound); feasibility checked against every regime a spine claim targets,
      and an infeasible-regime finding blocked submission with the required
      remedy named (narrow the claim / change the method).
- [ ] Every checklist item is PASS / FAIL / N-A with a one-line reason —
      no blanks.
- [ ] Required FAILs listed separately as blocking action items.
- [ ] `stage: final` written **only** on all-required-PASS.
