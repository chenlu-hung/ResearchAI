# Venue Profiles

Style parameters per submission target. `paper-writer` loads the relevant
profile when the user sets `venue_target`. `algo-brainstorm`'s `red-team` mode
uses these to predict reviewer concerns.

**Maintenance**: edited only via `/write venue-calibration`
(`shared/prompts/venue_calibration.md`). Policy fields carry `sources` +
`as_of`; anything resting on recall or community norms is listed in that
venue's `unverified:` and never hard-FAILs a gate. User-supplied exemplar
papers can upgrade a norm field's provenance to observed-in-sample
(`observed_fields`/`observed_sample`) — still `unverified:`, but the WARN
cites the sample instead of bare recall. `check_venues.py` verifies
the profile ↔ style-file ↔ token consistency and flags stale `as_of`.

---

## NeurIPS

- **Page limit**: 9 content pages including all figures/tables; references,
  technical appendices, and the mandatory paper checklist do not count
  (camera-ready gets +1 page).
- **Section template**: Abstract → Intro → Related Work → Method → Theory (optional) → Experiments → Discussion → Limitations. Paper checklist appended (in template).
- **Broader impact**: a separate "Broader Impacts" section is **not required**
  (2026 handbook: "You are not required to include a section titled 'broader
  impacts'") — but societal-impact consideration is still probed via the
  checklist. Write it where relevant, don't bolt on a boilerplate section.
- **LLM/AI policy**: LLM/agent use that is an important, original, or
  non-standard component of the *method* must be described in the experimental
  setup; routine writing/editing/code assistance is exempt from reporting.
  LLMs cannot be authors.
- **Anonymization**: double-blind; identifying information → desk reject.
- **Math density**: medium. Theorems welcome but not required; stated cleanly, proofs in appendix.
- **Empirical bar**: high. Multiple datasets, multiple seeds, baselines from the *last 12 months*. Lacking a recent baseline is a red flag.
- **Reviewer profile**: split between empirical and theoretical; assume the empirical reviewer is dominant. Will ask: "did you compare to method X (current SOTA)?", "is the gain within seed noise?", "what's the compute cost?".
- **Citation convention**: numbered `\cite{}` typical (~30–60 refs); the venue does not mandate a citation style (unverified).
- **Common reviewer red flags**: insufficient ablations, single-seed runs, cherry-picked datasets, missing recent baselines, no compute reporting, vague reproducibility section, unfilled checklist items.

*Sources: neurips.cc/Conferences/2026/CallForPapers + MainTrackHandbook
(as_of 2026-07-10); reviewer persona and red flags: recall/community
experience (unverified).*

## ICML

- **Page limit**: 8 main pages; references, the impact statement, and
  appendices are unlimited (camera-ready gets +1 page).
- **Impact statement**: **required** — "a statement of the potential broader
  impact of their work, including its ethical aspects and future societal
  consequences", placed after the body (with Acknowledgements, before
  References); does not count toward the page limit.
- **LLM/AI policy**: generative-AI assistance allowed; authors take full
  responsibility; notable uses should be explained (encouraged, not a
  mandatory statement).
- **Anonymization**: double-blind; do not advertise the work as an ICML
  submission during review.
- **Reviewer profile**: as NeurIPS but ICML reviewers more frequently push back on novelty vs. recent ArXiv preprints — `novelty-check` mode must include preprints ≤6 months old.
- **Distinct asks**: ICML often expects clearer positioning vs. classical ML literature (not just deep-learning lineage).
- **Citation convention**: author-year via the ICML style file (recall,
  unverified — the CFP does not state it).

*Sources: icml.cc/Conferences/2026/CallForPapers (as_of 2026-07-10);
persona/red flags and bib style: recall (unverified).*

## JMLR

- **Page limit**: no hard limit, but papers **longer than 35 pages**
  (appendices included) review slowly and "may be rejected if an AE and
  reviewers cannot be found"; **above 50 pages** requires justification in
  the cover letter and may be desk rejected.
- **Format**: must be typeset with the JMLR LaTeX style file
  (github.com/JmlrOrg/jmlr-style-file) — "Papers not in the JMLR style file
  will be rejected without review." Abstract ≤ 200 words; running title
  ≤ 50 chars; five keywords; cover-letter disclosures (prior publication,
  co-author consent, conflicts).
- **Section template**: Abstract → Intro → Background → Method → Theory (usually required) → Experiments → Discussion → Conclusion. Appendix integrated; online appendices possible for data/code.
- **Math density**: high. Theorems with full proofs in the main text are expected (community norm).
- **Empirical bar**: rigor matters more than benchmark count. Smaller experiments with thorough analysis OK.
- **Reviewer profile**: theory-heavy. Will scrutinize assumptions (do regularity conditions hold? are they minimal?). `theory-scoping` mode should target *minimax optimality* or *sharp constants* when feasible.
- **Citation convention**: author-year, ~50–100 refs typical (recall, unverified).
- **Distinct asks**: clear discussion of when assumptions fail; honest limitation section is expected.

*Sources: jmlr.org/author-info.html (as_of 2026-07-10); persona,
proofs-in-main norm, and bib style: recall/community experience (unverified).*

## AISTATS

- **Page limit**: **8 pages at submission** (9 for camera-ready), excluding
  references, the reproducibility checklist, and appendices. Appendix must be
  in the same PDF; US Letter; fonts must match the style file.
- **Reproducibility checklist**: part of the submission (excluded from the
  page count) — fill it, don't stub it.
- **LLM/AI policy**: generative-AI assistance allowed with full author
  responsibility; hidden prompts aimed at influencing peer review are
  scientific misconduct.
- **Anonymization**: double-blind; self-citations allowed if anonymity is preserved.
- Position: theory-leaning ML venue, between ICML and JMLR in flavor.
- **Reviewer profile**: expects identifiable theoretical contribution. Pure-engineering papers get desk-rejected. Will probe assumptions hard but accept asymptotic results.
- **Distinct asks**: connection to classical statistics is valued; mention parallels (M-estimation, empirical process, semiparametric efficiency) where relevant.

*Sources: virtual.aistats.org/Conferences/2026/CallForPapers (as_of
2026-07-10); persona and theory expectations: recall/community experience
(unverified).*

## Annals of Statistics

- **Page limit**: none stated by IMS; ~25–35 pages typical (community norm,
  unverified). Supporting technical appendices may be published as electronic
  supplements.
- **Format**: IMS author package (imsart class, per the IMS instructions
  hub; class name from recall).
- **Section template**: Intro → Setup → Main Results → Proofs (or proof sketches with appendix) → Simulations → Real Data → Discussion.
- **Math density**: maximum. The contribution *is* the theorem.
- **Empirical bar**: simulations to corroborate theory. Real-data section helps but not required.
- **Reviewer profile**: pure statisticians. Will challenge assumption minimality, novelty vs. classical literature, and require sharp rates with explicit constants where possible.
- **Distinct asks**: minimax lower bounds expected when claiming optimality. Identifiability and regularity conditions must be stated precisely with citation to standard textbooks.

*Sources: imstat.org (AoS manuscript submission) +
e-publications.org/ims/support/ims-instructions.html (as_of 2026-07-10);
persona, length norm, section template: recall/community experience
(unverified).*

## Generic (used by `peer-reviewer` `/review --venue generic`)

Fallback persona when refereeing a paper for a venue not profiled above (a
workshop, a journal not listed, an unspecified target).

- **Reviewer profile**: a balanced Stats/ML referee weighing five axes equally —
  **correctness, novelty, evidence, clarity, reproducibility**. Neither the
  empirical nor the pure-theory persona dominates; calibrate to whatever the
  paper claims (a theory paper is judged on its theorems, an applied paper on its
  experiments).
- **Empirical bar**: results should support the claims made — appropriate
  baselines, more than one seed/dataset where variance matters, honest ablations.
- **Common reviewer red flags**: claim not supported by the evidence shown,
  missing obvious baseline, single-seed or no variance reporting, novelty not
  delimited against prior work, key assumption unstated, unreproducible setup,
  figures/tables that cannot be read on their own.

---

## Defaults by venue (consumed by paper-writer)

Schema and provenance rules: `shared/prompts/venue_calibration.md`.
`unverified` fields WARN, never FAIL, in `submission-check`;
`must_include_patterns` regexes are passed to `check_tex.py` as
`--pattern token=regex`.

```yaml
neurips:
  as_of: 2026-07-10
  sources:
    - https://neurips.cc/Conferences/2026/CallForPapers
    - https://neurips.cc/Conferences/2026/MainTrackHandbook
  page_limit: 9
  bib_style: numeric
  theory_depth: medium
  ablation_required: true
  seed_count_min: 3
  must_include: [limitations, reproducibility, paper_checklist]
  must_include_patterns:
    paper_checklist: 'paper\s+checklist'
  unverified: [bib_style, theory_depth, ablation_required, seed_count_min]

icml:
  as_of: 2026-07-10
  sources:
    - https://icml.cc/Conferences/2026/CallForPapers
  page_limit: 8
  bib_style: author_year
  theory_depth: medium
  ablation_required: true
  seed_count_min: 3
  must_include: [impact_statement]
  must_include_patterns:
    impact_statement: 'impact\s+statement|broader\s+impact'
  unverified: [bib_style, theory_depth, ablation_required, seed_count_min]

jmlr:
  as_of: 2026-07-10
  sources:
    - https://www.jmlr.org/author-info.html
  page_limit: 35
  bib_style: author_year
  theory_depth: high
  ablation_required: medium
  seed_count_min: 5
  must_include: [proofs_in_main, assumption_discussion]
  unverified: [bib_style, must_include, theory_depth, ablation_required, seed_count_min]

aistats:
  as_of: 2026-07-10
  sources:
    - https://virtual.aistats.org/Conferences/2026/CallForPapers
  page_limit: 8
  bib_style: numeric
  theory_depth: high
  ablation_required: true
  seed_count_min: 3
  must_include: [reproducibility]
  unverified: [bib_style, theory_depth, ablation_required, seed_count_min]

annals_of_statistics:
  as_of: 2026-07-10
  sources:
    - https://imstat.org/journals-and-publications/annals-of-statistics/annals-of-statistics-manuscript-submission/
    - https://www.e-publications.org/ims/support/ims-instructions.html
  page_limit: null
  bib_style: author_year
  theory_depth: maximum
  ablation_required: false
  seed_count_min: 1
  must_include: [main_theorem, proofs_in_main, simulation_section, identifiability]
  unverified: [page_limit, bib_style, must_include, theory_depth, ablation_required, seed_count_min]
```
