# Mode: ablation-plan

**Purpose**: decompose the algorithm into components and design the ablation
table that will appear in the paper. The goal is to identify which
components are *necessary* vs. *helpful*, and pre-empt reviewer complaints.

## Inputs

- The chosen candidate
- Toy + theory results (so ablation runs target the *right* metrics)

## Procedure

1. **List components** of the algorithm — be aggressive in decomposing:

   - Pre-processing (normalization, feature engineering)
   - Architecture choice (if any — backbone, depth, width)
   - Loss term (main objective)
   - Regularization (each penalty as a separate component)
   - Optimization choice (cross-fitting, sample-splitting, sieve)
   - Nuisance estimator (each nuisance separately)
   - Calibration / post-processing
   - Hyperparameters that have a non-trivial effect

   Each component should be ablatable — there is a meaningful "without
   this" version.

2. **Necessary vs. helpful triage**:

   - **Necessary**: without it, the algorithm fails its core claim
     (e.g., coverage drops below $1-\alpha$, or rate degrades to slower
     than baseline)
   - **Helpful**: without it, performance worsens but the claim still
     holds qualitatively

   Reviewers should walk away convinced that *every component flagged
   necessary is actually necessary*. Optional components should be
   honestly labeled.

3. **Ablation table**:

   ```markdown
   | Variant | Component removed | Expected effect | Claim about role |
   |---------|-------------------|-----------------|------------------|
   | Full | (nothing) | (reference) | (reference) |
   | -CF | No cross-fitting (use plug-in) | Coverage drops by ~5pp | CF is necessary for marginal coverage |
   | -DML | Use sample-split instead of DML | Slower rate ($n^{-1/6}$) | DML helpful, not necessary |
   | -w-clip | No density-ratio clipping | Higher variance, occasional failure | Clipping helpful |
   | naive  | Unweighted (assume no shift) | Coverage breaks at shift > 2× | Baseline reference |
   ```

4. **Baseline selection** (this is where reviewer fights happen):

   - **Closest prior art** from `novelty-check` (mandatory)
   - **A strong recent method** in the same problem space (≤12 months)
   - **A simple "no-method" baseline** (e.g., constant prediction set)
   - **An oracle baseline** (if a meaningful oracle exists)
   - For ML venues: **at least one method from the past 6 months** — ICML
     reviewers will check ArXiv

   For each baseline: specify the *exact version* and hyperparameter
   tuning protocol. "We used the original paper's hyperparameters" is
   only acceptable if the paper provides them; otherwise specify a tuning
   budget identical to your method.

5. **Metric specification**:

   - Primary metric (the one tied to the theorem)
   - Secondary metrics (efficiency, runtime, robustness)
   - **Multiple seeds**: minimum 3 (NeurIPS/ICML), 5 (JMLR/AISTATS),
     30 for toy
   - **Significance testing**: paired test on per-seed differences. Use
     bootstrap or permutation; report CIs. **No bare mean tables.**

6. **Hyperparameter protocol**:

   - For your method: state the tuning grid and selection criterion
     (validation set? cross-validation?)
   - For each baseline: identical tuning budget. Document.

## Anti-sycophancy

- Pre-commit to which components you *expect* to be necessary, before
  running. If the run reveals a component you thought was necessary is
  not (or vice versa) — that itself is a paper-worthy finding, do not
  hide it.
- Listing more ablation rows is not virtue. Each row must answer a
  specific reviewer question. If a row is just "we tried X, also worked",
  cut it.

## Output

```markdown
### Ablation plan: <slug>

**Components identified**: N

**Ablation table**: <see above>

**Baselines**:
| Baseline | Version | Tuning | Why included |
|----------|---------|--------|--------------|
| ... | v1.2 (paper code) | grid search, val set | closest prior art |

**Primary metric**: ...
**Significance protocol**: paired bootstrap, 1000 resamples, per-seed differences

**Pre-commit**: I expect <component A> to be necessary; <component B> to be
helpful but not necessary.
```

## State update

```yaml
stage: ablation
ablation_plan:
  components: [...]
  baselines: [...]
  pre_commit:
    necessary: [cross_fitting, weighted_quantile]
    helpful: [clipping, DML]
```

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Every listed component has a meaningful "without this" variant.
- [ ] Pre-commit written: which components you expect necessary vs. helpful,
      before any results exist.
- [ ] Baselines include the closest prior art, a ≤12-month method, and a
      no-method baseline — each with exact version and tuning protocol.
- [ ] Primary metric tied to a theorem/claim; seeds meet the venue minimum;
      significance protocol stated (no bare mean tables).
- [ ] Every ablation row answers a specific reviewer question; rows that
      didn't were cut.
- [ ] State updated: `ablation_plan:` block + body entry.
