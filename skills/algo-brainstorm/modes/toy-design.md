# Mode: toy-design

**Purpose**: design the smallest synthetic experiment that demonstrates
the algorithm does what it claims. The toy is the first thing you'll run
and the first thing reviewers will ask about.

For statistical algorithms especially, a well-designed toy catches most
bugs *before* you spend time on real-data experiments.

## Inputs

- A chosen candidate from `novelty-check`
- Theory targets from `theory-scoping` (so the toy can corroborate them)
- A validated `lifecycle_gates.method_freeze` artifact/hash

## Procedure

0. **Validate method freeze.** Recompute its hash and confirm candidate,
   primitives, objective/regime, claims, packet, and prior-art audit are current.
   Missing/stale method freeze blocks experiment design. Read
   `shared/prompts/research_lifecycle.md`.

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

## Benchmark design (mandatory before the contract freezes)

Steps 1–7 design the *toy*. A toy alone does not carry an empirical paper: no
other mode owns real-benchmark breadth, so it is owned here. Run steps 8–10
before writing the experiment contract.

8. **Convention survey.** Pull the ≥3 closest works from the novelty packet
   (already required there) plus any strong recent baseline papers, and
   **tabulate their experimental designs** — read the papers, do not recall them:

   | Work | Datasets / benchmarks | Scale + resolution regime | Spatial dim | Mesh / geometry variability | History dependence | Metrics | Baselines | Seeds | Tuning budget | Compute reported |
   |---|---|---|---|---|---|---|---|---|---|---|
   | work-... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

   This table is what tells you what the field considers a complete evaluation.
   A design that silently omits a column every neighbor fills is the reviewer
   complaint you will get.

9. **Decision table + grill.** Propose this project's design as one row per
   design choice: **follow convention / deviate**, plus a one-line rationale.

   | Design choice | Convention (from step 8) | Ours | Follow / deviate | Rationale |
   |---|---|---|---|---|
   | Benchmark set | 3 standard + 1 hard | 2 standard | deviate | compute budget; hard case covered by toy |

   Deviating is allowed; deviating *silently* is not. Put the table to the user
   for adjudication through `shared/prompts/grill_protocol.md` — one question at
   a time, recommended option first. Persist the rulings as
   `interview_toy_design:` in state; skip the grill if that block already exists.

10. **Domain-regime stress row.** Explicitly decide and record coverage for each
    axis below. Each is either **covered** by a planned experiment or
    **explicitly delimited** in the claim text — never left ambient:

    - spatial dimension (1D / 2D / 3D);
    - structured vs unstructured meshes;
    - per-sample geometry variability;
    - temporal / history dependence;
    - **both transfer directions**: coarse→fine and fine→coarse.

    An axis the method cannot handle is a scope limit to write into the claim,
    not a gap to leave for a reviewer to find.

## Parity matrix and calibration budget (mandatory)

11. **Parity matrix.** Rows = **every** compared method, own variants and
    baselines. Columns = parameter count, training data, target-resolution labels
    consumed, fine-tuning allowed?, adaptation/residual correction?, tuning budget.

    | Method | Params | Training data | Target-res labels | Fine-tuned? | Adaptation? | Tuning budget |
    |---|---|---|---|---|---|---|
    | Ours (full) | 1.2M | D_train | 64 | no | residual head | 20 trials |
    | Baseline A | 0.3M | D_train | 0 | no | none | 20 trials |
    | Baseline A + adapter | 0.35M | D_train | 64 | no | residual head | 20 trials |

    For a **claim-bearing comparison** — any comparison a spine claim cites — an
    asymmetric cell **requires an equalized baseline variant**, as in the third
    row above. A written justification is *not* sufficient: if our method sees 64
    target-resolution labels and the baseline sees none, the comparison measures
    the labels, not the method. For a non-claim-bearing side comparison, a
    recorded one-line justification may suffice.

12. **Nonlinear-baseline rule.** A claim about a nonlinear component requires at
    least one **strong nonlinear alternative** as a baseline. A linear strawman
    alone fails the contract — beating linear does not establish that *this*
    nonlinearity is the right one.

13. **Calibration / adaptation budget.** Record the exact number and provenance
    of target-resolution samples or labels each calibration step or adapter
    consumes, including whether ground-truth high-resolution labels are needed
    and where they come from. Include **one budget-response experiment**: few-shot
    through to the full curve, so the reader sees how the method degrades as the
    budget shrinks. "Uses a few samples" is not a budget.

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

Also write/hash `docs/experiment-contract-<slug>.md`. It binds the method-freeze
hash to testable claim IDs, dataset IDs/versions and split roles, primary and
secondary metrics/estimands, grounded baselines, comparison unit/seeds,
uncertainty/significance analysis, success/failure/stopping/exclusion rules,
compute budget, and the pre-run expected/smoke-test outcomes above — plus the
convention-survey and decision tables, the domain-regime stress row, the parity
matrix, and the calibration/adaptation budget from steps 8–13. Every
empirical claim maps to a metric and decision rule.

**Spine binding**: every experiment maps to a claim in `spine:`. An experiment
serving no spine claim is cut, or carries a written one-line justification in
the contract. **Promised-row binding**: every table/figure row promised by
`paper/skeleton/handoff.md` (the positioning skeleton) has an experiment that
fills it; a promised row with no experiment is an unkeepable promise — cut the
row or add the experiment before freezing. Set:

```yaml
research_phase: experiment_contract
lifecycle_gates:
  experiment_contract:
    status: frozen
    artifact: docs/experiment-contract-<slug>.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    method_freeze_hash: "<64-char-lowercase-sha256-hex>"
```

Do not run experiments in this mode. Any later contract change invalidates the
protocol/results/audit/red-team/review gates.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] The toy demonstrates ≥1 named theory target or an explicit Step 1 goal
      (sanity / graceful failure / outperform / phase transition / rate).
- [ ] Data spec fully explicit: distribution, $d$, $n$ grid, noise model,
      ≥30 seeds, and a closed-form/oracle truth.
- [ ] Oracle and optimal baselines defined; the proposed→oracle convergence
      expectation is stated.
- [ ] Expected curves written *before* any implementation discussion.
- [ ] ≥2 smoke tests with numeric thresholds (the "⇒ bug" form).
- [ ] ≥1 non-trivial baseline (not just "no method").
- [ ] Compute estimate present; state updated (`toy_design:` +
      `docs/toy-spec-<slug>.md`).
- [ ] Convention survey tabulates ≥3 closest works from the novelty packet on
      every column — read, not recalled.
- [ ] Decision table adjudicated through the grill; rulings persisted in
      `interview_toy_design:` (or the existing-block skip was stated).
- [ ] Domain-regime stress row decided on every axis — spatial dimension,
      structured/unstructured mesh, per-sample geometry, history dependence,
      and **both** transfer directions — each covered or delimited in a claim.
- [ ] Parity matrix complete for every compared method; every claim-bearing
      asymmetry has an **equalized baseline variant**, not a justification.
- [ ] Any nonlinear-component claim has ≥1 strong nonlinear baseline; no
      linear-strawman-only comparison.
- [ ] Calibration/adaptation budget records exact label counts and provenance;
      a budget-response (few-shot → full) experiment is in the contract.
- [ ] Every experiment maps to a spine claim, or carries a written justification.
- [ ] Every row promised in `paper/skeleton/handoff.md` has an experiment.
- [ ] Method freeze revalidated; hashed experiment contract covers every field
      in the lifecycle schema and every empirical claim has a decision rule.
