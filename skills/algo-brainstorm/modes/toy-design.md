# Mode: toy-design

**Purpose**: design the smallest synthetic experiment that demonstrates
the algorithm does what it claims. The toy is the first thing you'll run
and the first thing reviewers will ask about.

For statistical algorithms especially, a well-designed toy catches most
bugs *before* you spend time on real-data experiments.

## Inputs

- A chosen candidate from `novelty-check`
- Theory targets from `theory-scoping` (so the toy can corroborate them)

## Procedure

1. **What does the toy need to demonstrate?** Pick one or more:

   - The algorithm **works** when its assumptions hold (sanity)
   - The algorithm **fails gracefully** when assumptions are violated
     (calibrated to its own scope)
   - The algorithm **outperforms** a specific baseline in the regime it
     was designed for
   - A **phase transition** predicted by theory matches simulation
   - A **convergence rate** matches the theorem's $n^{-r}$

2. **Synthetic data specification**:

   - **Distribution**: explicit form (e.g., $X \sim N(0, I_d)$, $Y = f(X) + \varepsilon$, $\varepsilon \sim N(0, \sigma^2)$)
   - **Dimension** $d$: pick a low value (5, 10, 20) — toy ≠ large
   - **Sample size** $n$: a grid (e.g., 100, 300, 1000, 3000, 10000) for
     scaling plots
   - **Heterogeneity / shift / noise level**: parameterized so you can
     sweep the difficulty axis
   - **Noise**: i.i.d.? heavy-tail? heteroscedastic?
   - **Truth**: must be a closed-form or oracle quantity you can compute
     analytically — this is the whole point of a toy

3. **Oracle / closed-form baseline**:

   - What does the *optimal* algorithm output, in closed form?
   - What does an *oracle* version of your algorithm output (i.e., your
     algorithm with nuisance known)?
   - Your algorithm should approach the oracle as $n \to \infty$, and
     the oracle should match (or exceed) the optimal up to fundamental
     limits

4. **Metrics**:

   - For each theory target, a corresponding empirical measurement
     (coverage → empirical coverage rate; convergence rate → log-log
     slope of error vs. $n$)
   - Per-seed measurements with ≥30 seeds for tight CIs

5. **Expected curves** (sketch before running):

   - "I expect coverage to be flat at $1-\alpha$ across all $n$"
   - "I expect error to decay like $n^{-1/4}$ on a log-log plot"
   - "I expect baseline X to fail when $w$ is highly skewed (effective
     sample size < 10)"

6. **Failure conditions** (smoke test):

   - "If empirical coverage is below $1 - \alpha - 0.05$ at large $n$,
     the proof is wrong or the implementation is wrong"
   - "If error does not decrease with $n$, something fundamental is broken"
   - "If oracle and estimator don't converge, nuisance estimation is broken"

   Write these *before* implementing — they are your sanity gates.

7. **Estimated compute**: rough wall-clock for the full toy run.

## Output

```markdown
### Toy: <name>

**Question this answers**: <one sentence>

**Data**:
- $X \sim ...$
- $Y = ...$
- $n \in \{100, 300, ...\}$, $d = ...$, repeats = 30 seeds

**Oracle**: <closed-form>

**Algorithms compared**:
- Proposed (full)
- Proposed (oracle nuisance)
- Baseline A (e.g., naive ERM)
- Baseline B (e.g., closest prior art from novelty-check)

**Metrics**: coverage, error norm, set length (if applicable)

**Expected**:
- Proposed (full) converges to oracle as $n \to \infty$
- Coverage flat at $1-\alpha$ for proposed
- Baseline A miscalibrated when shift is large

**Smoke tests** (will reveal bugs):
- Coverage < $1-\alpha - 0.05$ at largest $n$ → bug
- Oracle does not match optimal → setup error
- Log-log slope ≠ predicted rate → either bug or theory wrong

**Compute**: ~<wall-clock estimate>
```

## Anti-sycophancy

- Force a specific **failure prediction** before declaring the toy ready.
  "I have no idea what will happen" is not a good toy — it indicates the
  theory is too weak to predict, which is itself a finding.
- Force comparison to **at least one non-trivial baseline** (not just "no
  method") so the toy can show *relative* benefit, not just absolute.

## State update

```yaml
stage: toy
toy_design:
  spec_ref: docs/toy-spec-<slug>.md
  expected_curves:
    - "coverage flat at 1-α"
    - "error ~ n^{-1/4}"
  smoke_tests:
    - "coverage < 1-α-0.05 at n=10000 ⇒ bug"
```

Save the full toy spec to `docs/toy-spec-<slug>.md`.
