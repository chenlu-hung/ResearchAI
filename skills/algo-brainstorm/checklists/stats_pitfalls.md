# Statistical Pitfalls Checklist

Applied by `red-team` mode, and surfaced reactively across other modes
when the user's algorithm touches inference. These are the things that
get JMLR / AISTATS / Annals reviewers (and increasingly NeurIPS reviewers)
to reject papers.

## 1. Post-selection inference

**Pitfall**: select a model (or hyperparameter, or test) based on data,
then compute a CI / p-value using the same data as if no selection happened.

**Reflexive checks**:
- Did the user run cross-validation to pick hyperparameters? If so, do they
  report a CI computed on the same fold? → invalid.
- Did the user pick a "winning" baseline comparison post-hoc?
- Is there a "we noticed X in the data and then tested for X" step?

**Mitigations**: sample-splitting, selective inference (Lee-Sun-Sun-Taylor),
data carving, conformal where applicable.

## 2. Multiple testing / FWER / FDR

**Pitfall**: report a "significant" finding among many tests without correction.

**Reflexive checks**:
- How many hypotheses were tested in the experiment?
- Are p-values reported without correction?
- Is the user comparing $K$ methods on $D$ datasets and quoting "wins"?

**Mitigations**: Bonferroni (conservative, simple), Benjamini-Hochberg (FDR),
Romano-Wolf (FWER with dependence), Westfall-Young permutation.

## 3. Identifiability

**Pitfall**: claim to estimate a parameter that cannot be recovered from
the observable distribution.

**Reflexive checks** (especially for causal / latent variable methods):
- Can two distinct parameter values produce the same observable
  distribution? If yes, parameter is unidentified.
- Are there standard identifying assumptions invoked (positivity,
  no-unmeasured-confounding, anchor variables, instrumental variables)?
- Is partial identifiability acknowledged where full identifiability fails?

## 4. Regularity conditions

**Pitfall**: state a theorem that requires conditions the user did not
verify in their setting.

**Reflexive checks**:
- Does the proof technique require Donsker? VC class? Bracketing entropy
  bound? Lipschitz? Twice-differentiable?
- For empirical process arguments: function class complexity sublinear?
- For M-estimation: identifiability + continuity of $\theta \mapsto \mathbb{E}\ell$?
- For asymptotic normality: Hessian non-singular at $\theta^*$?

For each assumption: state it explicitly in the paper, in plain words,
with one example of when it fails.

## 5. Data leakage

**Pitfall**: information from the test set leaks into training or
calibration.

**Reflexive checks**:
- Is normalization (mean/std) computed on the full dataset before splitting?
  → leakage
- Is feature selection done on full dataset? → leakage
- Is the nuisance estimator (e.g., propensity, density ratio) fit on
  the same data as the calibration set? → breaks coverage unless cross-fit
- For time series: are folds time-respecting?

## 6. p-hacking surface

**Pitfall**: many free design choices, each made post-hoc on the test set,
each silently improving headline numbers.

**Reflexive checks**: count the discrete decisions made *after* seeing test
performance. Examples:
- Hyperparameter grid expanded after seeing initial run
- Outlier removal / filtering criterion adjusted
- Metric definition refined
- Dataset subset selected

Pre-registration (even informal: a frozen plan document) is the cleanest
remedy.

## 7. Selection bias / non-representative sampling

**Pitfall**: training data is not representative of deployment distribution
and this gap is unacknowledged.

**Reflexive checks**:
- Where did the data come from? What was excluded?
- For benchmarks: are the test cases representative of real use?
- For social science / medical: differential measurement / non-response?

## 8. Heavy-tail blindness

**Pitfall**: assume sub-Gaussian / bounded when data is heavy-tailed
($t_3$, Pareto, log-normal). Concentration breaks; rates change.

**Reflexive checks**:
- Plot the empirical residual distribution. Is it heavy-tailed?
- Are concentration bounds in the proof tight under heavy tail, or only
  sub-Gaussian?
- For high-stakes domains (finance, insurance): is the worst case bounded?

## 9. Asymptotic vs. finite-sample gap

**Pitfall**: cite an asymptotic theorem to justify behavior at $n = 100$.

**Reflexive checks**: is there a finite-sample version of the result, even
with worse constants? Even simulations corroborating the asymptotic
prediction at the operational $n$?

## 10. Sample splitting / cross-fitting hygiene

**Pitfall**: in DML / two-step procedures, reuse the same data for nuisance
estimation and final estimation — breaks the orthogonality / Neyman-orthogonal
remainder argument.

**Reflexive checks**:
- Are nuisance fits and target evaluation on disjoint folds?
- Is cross-fitting properly $K$-fold (each $i$ scored by nuisance fit on
  data not containing $i$)?
- For prediction-set methods: is the calibration set disjoint from
  nuisance training?

## 11. Coverage ≠ conditional coverage

**Pitfall**: claim "valid prediction intervals" when only marginal coverage
holds, while implying conditional validity.

**Reflexive checks**:
- Is the guarantee $\Pr(Y \in \hat{C}(X))$ (marginal) or
  $\Pr(Y \in \hat{C}(X) \mid X)$ (conditional)?
- Be explicit. Conditional validity in nonparametric settings is generally
  impossible (Barber et al. 2020).

## 12. Calibration vs. accuracy confusion

**Pitfall**: well-calibrated ≠ accurate. A method can be perfectly
calibrated and useless (constant prediction).

**Reflexive checks**: report both calibration and sharpness/efficiency.
For prediction sets: coverage AND average length. For probabilities:
calibration AND proper scoring rule (log loss, Brier).

---

## How `algo-brainstorm` uses this

- `red-team` walks all 12, marks each ✅/⚠️/❌/N-A
- Other modes surface relevant items reactively (e.g., `theory-scoping`
  surfaces #4 regularity; `ablation-plan` surfaces #2 and #10)
- The list is **not** to make the user fill out a bureaucratic form —
  it's a *prompt* for honest self-attack
