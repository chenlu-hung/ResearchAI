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

## Council panel (opt-in)

When invoked with `--council`, widen the failure-mode search with a multi-model panel
before building the gap table — diversity surfaces gaps one model misses. Follow
`shared/prompts/council_panel.md`.

- **Panel prompt**: the restated method (Step 1) plus the failure-mode axes (Step 2),
  asking each member to **independently list distinct gaps / failure regimes / broken
  assumptions**, one per line with the regime where each bites. No ranking — you want the
  union.
- **Synthesis**: merge member gaps into the Step 3 gap table, dedup (note convergence,
  e.g. "3/4 flagged heavy-tail miscalibration"), and tag panel-sourced rows `source:
  panel`. Every panel gap enters "Supporting evidence" as `[VERIFY]` with a search query —
  a member is **not** a citation source. Then run the Anti-sycophancy prior-art check below
  on the merged set before picking the top 3.

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

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Step 1 restatement is ≤3 sentences and names what the method computes,
      its inputs, and its claimed guarantee — or you refused and asked.
- [ ] Every Step 2 axis has ≥1 failure mode or an explicit `N/A — <reason>`.
- [ ] Every gap-table row's "Supporting evidence" is a verified bibkey or
      `[VERIFY]` + a concrete search query.
- [ ] Prior-art check ran on each candidate gap; unresolved ones are flagged
      *novelty uncertain*, not presented as open.
- [ ] Top-3 gaps each meet all three criteria and carry an attack sketch.
- [ ] State updated: body entry + `stage` / `open_questions` per Output.
