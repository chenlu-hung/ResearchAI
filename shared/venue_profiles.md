# Venue Profiles

Style parameters per submission target. `paper-writer` loads the relevant
profile when the user sets `venue_target`. `algo-brainstorm`'s `red-team` mode
uses these to predict reviewer concerns.

---

## NeurIPS

- **Page limit**: 9 main + unlimited references + appendix.
- **Section template**: Abstract → Intro → Related Work → Method → Theory (optional) → Experiments → Discussion → Limitations + Broader Impact (mandatory).
- **Math density**: medium. Theorems welcome but not required; reviewers expect them stated cleanly with proofs in appendix.
- **Empirical bar**: high. Multiple datasets, multiple seeds, baselines from the *last 12 months*. Lacking a recent baseline is a red flag.
- **Reviewer profile**: split between empirical and theoretical; assume the empirical reviewer is dominant. Will ask: "did you compare to method X (current SOTA)?", "is the gain within seed noise?", "what's the compute cost?".
- **Citation convention**: numbered, `\cite{}` with NeurIPS bibstyle. ~30–60 refs typical.
- **AI disclosure**: NeurIPS 2024+ requires LLM-use statement.
- **Common reviewer red flags**: insufficient ablations, single-seed runs, cherry-picked datasets, missing recent baselines, no compute reporting, vague reproducibility section.

## ICML

- **Page limit**: 8 main + unlimited refs + appendix.
- Otherwise broadly similar to NeurIPS, slightly more theory-tolerant.
- **Reviewer profile**: as NeurIPS but ICML reviewers more frequently push back on novelty vs. recent ArXiv preprints — `novelty-check` mode must include preprints ≤6 months old.
- **Distinct asks**: ICML often expects clearer positioning vs. classical ML literature (not just deep-learning lineage).

## JMLR

- **Page limit**: none, but ~25–40 pages typical.
- **Section template**: Abstract → Intro → Background → Method → Theory (usually required) → Experiments → Discussion → Conclusion. Appendix integrated.
- **Math density**: high. Theorems with full proofs in the main text are expected.
- **Empirical bar**: rigor matters more than benchmark count. Smaller experiments with thorough analysis OK.
- **Reviewer profile**: theory-heavy. Will scrutinize assumptions (do regularity conditions hold? are they minimal?). `theory-scoping` mode should target *minimax optimality* or *sharp constants* when feasible.
- **Citation convention**: author-year, ~50–100 refs typical.
- **Distinct asks**: clear discussion of when assumptions fail; honest limitation section is expected.

## AISTATS

- **Page limit**: 9 main + unlimited refs + appendix.
- Position: theory-leaning ML venue, between ICML and JMLR in flavor.
- **Reviewer profile**: expects identifiable theoretical contribution. Pure-engineering papers get desk-rejected. Will probe assumptions hard but accept asymptotic results.
- **Distinct asks**: connection to classical statistics is valued; mention parallels (M-estimation, empirical process, semiparametric efficiency) where relevant.

## Annals of Statistics

- **Page limit**: ~25–35 pages.
- **Section template**: Intro → Setup → Main Results → Proofs (or proof sketches with appendix) → Simulations → Real Data → Discussion.
- **Math density**: maximum. The contribution *is* the theorem.
- **Empirical bar**: simulations to corroborate theory. Real-data section helps but not required.
- **Reviewer profile**: pure statisticians. Will challenge assumption minimality, novelty vs. classical literature, and require sharp rates with explicit constants where possible.
- **Distinct asks**: minimax lower bounds expected when claiming optimality. Identifiability and regularity conditions must be stated precisely with citation to standard textbooks.

---

## Defaults by venue (consumed by paper-writer)

```yaml
neurips:
  page_limit: 9
  bib_style: numeric
  theory_depth: medium
  ablation_required: true
  seed_count_min: 3
  must_include: [limitations, broader_impact, reproducibility, ai_disclosure]

icml:
  page_limit: 8
  bib_style: numeric
  theory_depth: medium
  ablation_required: true
  seed_count_min: 3
  must_include: [limitations, reproducibility]

jmlr:
  page_limit: null
  bib_style: author_year
  theory_depth: high
  ablation_required: medium
  seed_count_min: 5
  must_include: [proofs_in_main, assumption_discussion]

aistats:
  page_limit: 9
  bib_style: numeric
  theory_depth: high
  ablation_required: true
  seed_count_min: 3
  must_include: [theory_contribution, assumption_discussion]

annals_of_statistics:
  page_limit: null
  bib_style: author_year
  theory_depth: maximum
  ablation_required: false
  seed_count_min: 1
  must_include: [main_theorem, proofs, simulation_section, identifiability]
```
