# Mode: gap-analysis

**Purpose**: given a baseline method (or SOTA paper, or class of methods),
identify *where it fails*, *what assumptions are unrealistic*, and *what's
missing*. The output feeds `formalize` or `ideate`.

## Inputs

- A method name, paper, or class (e.g., "split conformal prediction",
  "Tibshirani 2019", "weighted ERM under covariate shift")
- Optional: the user's intuition about where it might fail

## Procedure

1. **Restate the method** in 3 sentences. Include: what it computes, what
   inputs it needs, what guarantee it claims. If you cannot restate it
   confidently, refuse and ask the user to clarify or point to the paper.

2. **Enumerate failure modes** across these axes (skip axes that don't
   apply):

   - **Empirical failure regimes**: data scales, distributions, dimensions
     where the method underperforms or breaks
   - **Unrealistic assumptions**: i.i.d., bounded, Gaussian noise,
     stationarity, exchangeability, identifiability, density support
   - **Computational bottleneck**: time/memory/communication cost; what
     happens at $n=10^6$, $d=10^5$
   - **Sample complexity**: how much data does it need? Hidden constants?
   - **Adversarial / OOD behavior**: distribution shift, noise, adversarial
     perturbation
   - **Calibration / coverage** (if uncertainty quantification): what gets
     miscalibrated and when
   - **Connection failures**: areas where this method is conceptually
     disconnected from related literature it should engage with

3. **Gap table** — produce a markdown table:

   ```markdown
   | # | Gap | Failure regime | Supporting evidence | Open? |
   |---|-----|----------------|---------------------|-------|
   | 1 | Exchangeability assumed | Time series, covariate shift | Tibshirani 2019 §3; Barber 2023 | Partially addressed |
   | 2 | Heavy-tail miscalibration | Pareto-tailed residuals | own intuition; verify | Open |
   ```

   - "Supporting evidence" must be a bibkey from the verified set or marked
     `[VERIFY]` with a search query to confirm.
   - "Open?" = `Open` / `Partially addressed` / `Solved` (with citation).

4. **Pick top 3 gaps** that are simultaneously:
   - genuinely open (not fully solved by an existing paper)
   - amenable to a Stats/ML contribution
   - feasible to attack with the user's resources

   For each, write a one-paragraph "attack sketch": what would a new method
   need to address to close this gap?

## Anti-sycophancy

Required before emitting any "this is a promising gap" assessment:

- For each candidate gap, **search for prior work that may have closed it**
  (via `literature-explorer` or recall + [VERIFY]).
- If you cannot rule out that the gap is already closed, flag it as
  *novelty uncertain* — `novelty-check` will resolve it later.

## Output (written to research_state)

Append to body of `.research-state/<slug>.md`:

```markdown
## <date> — gap-analysis

**Method analyzed**: <name>

**Gap table**:
<table>

**Top 3 candidate gaps**:
1. ...
2. ...
3. ...
```

And set:

```yaml
stage: gap   # if not further along
open_questions:
  - <gap 1>
  - <gap 2>
  - <gap 3>
```

## Failure conditions (refuse to emit)

- Method too vaguely specified → ask for clarification
- No retrieved literature available → suggest running `literature-explorer` first
  (you can proceed but only with heavy `[VERIFY]` flagging)
