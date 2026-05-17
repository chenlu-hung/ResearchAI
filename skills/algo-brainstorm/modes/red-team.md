# Mode: red-team

**Purpose**: adversarial self-review of the full algorithm + theory + experiments
package before paper writing. Pretend you are the meanest reviewer at the
target venue and try to break the contribution.

## Inputs

- Full research state through `ablation-plan`
- `venue_target` (loads venue profile for tailored attacks)

## Procedure

Run all six attacks. Do not skip.

### Attack 1: Reviewer red-flags (venue-specific)

Load the venue profile from `shared/venue_profiles.md`. List the venue's
"common reviewer red flags". For each, check your work and rate:

- ✅ addressed
- ⚠️ partially addressed — what's missing
- ❌ not addressed — concrete remediation needed

Example for NeurIPS:

| Red flag | Status | Notes |
|----------|--------|-------|
| Insufficient ablations | ✅ | 5 rows, see `ablation-plan` |
| Single-seed runs | ⚠️ | 3 seeds on main; toy has 30 |
| Missing recent baselines | ❌ | Need to add [Smith 2026] preprint |
| No compute reporting | ❌ | Add wall-clock + GPU spec |
| Vague reproducibility | ⚠️ | Code TBD; data setup spec is solid |
| Limitations section missing | ❌ | Must write |
| Broader impact missing | ❌ | Must write |

### Attack 2: Degenerate / edge cases

For statistical algorithms, hit these specifically:

- **High dimension regime**: $n < d$, $n = d$, $n \ll d$
- **Heavy-tailed inputs**: Pareto, Cauchy — what breaks?
- **Discrete / mixed-type covariates**: if assumption is continuous density
- **Collinearity / rank deficiency**: $\mathrm{rank}(X^TX) < d$
- **Support mismatch**: $\mathrm{supp}(Q) \not\subset \mathrm{supp}(P)$ —
  density ratio undefined
- **Non-stationarity / temporal dependence**: if exchangeability assumed
- **Class imbalance / rare events**: $\Pr(Y=1) < 0.01$
- **Distribution shift beyond the modeled type**: covariate-shift method
  on a label-shift problem

For each that applies: write what happens (gracefully degrades? silently
broken? throws error?) and a one-line mitigation if any.

### Attack 3: Statistical pitfalls

From `checklists/stats_pitfalls.md`, walk through:

- **Post-selection inference**: do you select a model and then compute a CI
  on the same data? If so, is the CI valid?
- **Multiple testing**: how many hypotheses are tested? Bonferroni / BH /
  Romano-Wolf applied?
- **Data leakage**: train/calibration/test split — any quantity shared?
  (cross-fitting handles this; vanilla split-conformal handles this; many
  ML papers don't)
- **Selection bias / nuisance estimation reuse**: estimating $w$ on the
  same data used for calibration breaks coverage unless cross-fit
- **p-hacking surface**: how many design choices were made post-hoc on
  the test data?
- **Identifiability**: if a latent parameter, is it identifiable from
  the observable distribution?
- **Regularity conditions**: list each assumption; is each minimal?

### Attack 4: Computational reality

- At $n = 10^6$: what's wall-clock? Does the method still run?
- At $d = 10^4$: does memory blow up?
- Parallelizable? GPU-friendly? (matters for ML venues)
- What's the dominant cost — nuisance estimation? quantile? optimization?

### Attack 5: Sycophancy check on yourself

The single most important attack. Read your contribution statement aloud
and ask:

- Would I find this convincing if I had not done the work?
- Is the Δ vs. closest prior art *actually* important, or am I padding it?
- Is the theorem statement *clean* or is it festooned with caveats
  that make it nearly vacuous?
- If a colleague pitched this to me at NeurIPS, would I be excited or
  would I think "small delta, why didn't they just cite Smith 2026"?

Write the honest answer. If the answer is "padded", *go back to ideate*
or sharpen the contribution.

### Attack 6: Pre-mortem

Imagine the paper is rejected. Write the 2–3 most likely reasons in the
reviewer's voice. Then for each, check whether the current research state
addresses it. If not, plan the fix.

## Output

```markdown
### Red team: <slug>

**Venue red flags** (NeurIPS):
<table>

**Edge cases**:
| Case | Effect | Mitigation |
|------|--------|------------|

**Statistical pitfalls** (relevant subset):
- Post-selection inference: <status>
- ...

**Compute reality**: <summary>

**Sycophancy check**: <honest verdict>

**Pre-mortem — most likely rejection reasons**:
1. ...
2. ...
3. ...

**Action items before paper-writer can engage**:
- [ ] ...
- [ ] ...
```

## State update

```yaml
stage: red-team
red_team_findings:
  - finding: "..."
    severity: high | medium | low
    mitigation: "..."
    blocking: true   # blocks paper-writer if true
```

If any `blocking: true` finding exists, `paper-writer` should refuse to
emit a full draft until resolved (it can still produce outline).
