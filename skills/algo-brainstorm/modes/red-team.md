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

Load the venue profile from `shared/venue_profiles.md`. If research state
has `reviewer_intel:` (`shared/prompts/reviewer_intel.md`), read the
dossier too and rate against its observed objections where they apply —
evidence beats persona. (The conductor gathers it on entry when the venue
has public reviews; standalone runs may proceed without.) List the
venue's "common reviewer red flags". For each, check your work and rate:

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
reviewer's voice — when `reviewer_intel:` exists, ground them in its
observed objections (cite the quote a reason echoes). Then for each,
check whether the current research state addresses it. If not, plan the
fix.

## Council panel (opt-in)

The six attacks above are one model red-teaming itself. When invoked with `--council`,
convene a **real adversarial panel**: each member plays the meanest reviewer at the target
venue against the full contribution, then you chair the merge. Follow
`shared/prompts/council_panel.md` (this is a **critique mode** → cross-review applies, and
red-team is an **adversarial mode** → conditional cross-examination applies).

- **Panel prompt**: the contribution statement + theory + experiment plan from research
  state, plus the venue's `Common reviewer red flags` from `shared/venue_profiles.md`. Ask
  each member for objections in the six-attack frame (venue red flags, edge cases,
  statistical pitfalls, compute reality, sycophancy, pre-mortem rejection reasons), each
  tied to a specific part of the work.
- **Cross-review**: anonymize the reviews and have members rank which objections are most
  damaging — this surfaces where reviewers disagree on severity.
- **Cross-examination (conditional)**: when reviewers split on whether an objection is fatal,
  run **one** rebuttal round per `council_panel.md` — send the contested objection back to
  its author to substantiate (concrete edge case / pitfall / missing baseline) or concede.
  An objection counts only if it is **checkable against the work or the venue red-flag list**;
  a member's unverified "reviewers will hate this" is a hypothesis, not a finding.
- **Synthesis → six-attack output**: fold surviving objections into the sections below,
  deduping and noting agreement ("3/4 reviewers flag single-seed runs" → high severity).
  Every panel-originated attack is `[VERIFY]`-flagged and run through the
  Anti-hallucination guardrails before it becomes a finding. The chair owns correctness —
  discard stale or out-of-scope attacks and say why in one line.

Without `--council`, run the six attacks single-model exactly as above.

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

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] All six attacks have content or an explicit `N/A — <reason>`;
      none skipped silently.
- [ ] Venue red-flag table rates **every** flag ✅/⚠️/❌ with a note;
      `reviewer_intel:` dossier read and cited where it applies
      (if present).
- [ ] Every finding carries severity + mitigation + `blocking:` bool
      in state.
- [ ] Sycophancy check answered honestly in ≥1 full sentence; if the verdict
      is "padded", the output routes back to `ideate`, not forward.
- [ ] Pre-mortem lists ≥2 rejection reasons in the reviewer's voice, each
      mapped to addressed / action item.
- [ ] Action items emitted; user told paper-writer is gated if any
      `blocking: true` finding exists.
- [ ] (`--council`) surviving objections passed the evidence gate; discarded
      ones noted with a one-line reason.
