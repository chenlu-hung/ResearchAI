# Mode: red-team

**Purpose**: adversarial self-review of the full algorithm + theory + experiments
package before paper writing. Pretend you are the meanest reviewer at the
target venue and try to break the contribution.

## Inputs

- Full research state through `ablation-plan`
- `venue_target` (loads venue profile for tailored attacks)
- Current method-freeze, experiment-contract, and protocol hashes
- A validated real results manifest, or valid theory-only N/A gates plus hashed
  proof artifacts

## Procedure

### Gate 0: evidence audit before red team

Follow `shared/prompts/research_lifecycle.md`. Refuse to run a plan-only red team
after the protocol gate: expected curves are not results.

For empirical work, validate the result-manifest JSON, protocol/code/
environment/dataset hashes, required run coverage (including failures and
exclusions), and every referenced artifact. Map each empirical claim to its
actual metric, population/split, estimate/uncertainty, pre-frozen decision rule,
and result artifact. Record protocol deviations and post-hoc analyses. For
theory-only work, audit the hashed proof artifacts against theorem/assumption
claims instead.

**Parity and budget check.** Verify the manifest's per-run `method_variant`,
`param_count`, `adaptation` (fine-tuned?, labels used, budget), and
`resolution_direction` against the frozen contract's parity matrix and
calibration budget. Every parity-matrix row must have runs; every claim-bearing
asymmetry must have its **equalized baseline variant** runs present; recorded
label counts must match the budget. A missing equalized variant makes the
comparison uninterpretable — record it as an evidence failure, not a caveat.

Write/hash `docs/evidence-audit-<slug>.md`, persist a canonical `audit_verdict`,
and update `lifecycle_gates.evidence_audited`. `fail`/`cannot_determine` stops;
`conditional` requires explicit acceptance. Only then run all seven attacks below
against the audited **actual results/proofs**. Do not skip an attack.

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

Also compare the frozen experiment contract with actual run coverage. Missing
registered baselines, datasets, metrics, or seeds are evidence failures, not
mere writing suggestions.

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

Use the result manifest and audit to identify failed/excluded runs, selective
reporting, protocol deviations, multiple-comparison inflation, and claims whose
uncertainty does not support their wording. Negative results remain visible.

### Attack 4: Computational reality

Read the algorithm card's **Cost** section (`checklists/algorithm_card.md`) —
the per-phase entries (preprocessing/decomposition, training,
calibration/adaptation, inference) and the representative scaling regime beyond
the tested one. Attack that artifact, not generic large-$n$ questions.

**Acceptance criterion**: feasibility *relative to the regimes the spine claims
target*. A method whose cost is fine at the tested scale but infeasible in the
regime a spine claim advertises fails this attack — the claim is writing a
cheque the cost analysis cannot cash. Report which phase dominates and at what
scale it becomes infeasible.

- Per phase: what is the wall-clock and memory, and how does each scale?
- At the claimed regime (e.g. 3D, transient, $n = 10^6$, $d = 10^4$): does it
  still run, and what is the memory implication?
- Parallelizable? GPU-friendly? (matters for ML venues)
- What is the dominant cost — decomposition? nuisance estimation? calibration?
- If the card has no per-phase Cost section, that is the finding: send it back
  to be filled before this attack can be answered.

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

### Attack 7: Table interrogation

Attacks 1–6 interrogate the *work*. This one interrogates the **numbers as
printed**. For every results table and figure in the audited results, enumerate
the questions a hostile reviewer could form **purely from the numbers**, without
reading your explanation:

- **Counterintuitive orderings** — a simpler model beating a more complex one; a
  baseline beating an ablation that was supposed to be necessary; a method
  winning on the hard benchmark and losing on the easy one.
- **Outsized variances** — one cell with a standard error several times its
  neighbors'. Why is that configuration unstable?
- **Components useless alone but transformative in combination** — a favorite
  reviewer target, because it is the signature of an accidental interaction or a
  tuning artifact.
- **Gains within seed noise** — any headline improvement whose margin is
  comparable to the reported uncertainty.
- Rows or columns that are conspicuously **absent** from an otherwise
  systematic grid.

Every anomaly gets a **disposition**, and which dispositions are available
depends on what the anomaly contradicts:

- **If it violates a pre-frozen decision rule or contradicts a spine claim**, a
  narrative explanation is **not** an acceptable disposition. Writing a
  paragraph that makes the number sound reasonable is exactly the move this
  attack exists to block. The only outcomes are:
  1. **method mitigation** — change the method and re-run;
  2. **claim narrowing or withdrawal** — the spine claim shrinks to what the
     numbers support; or
  3. gate `fail`.
- **Otherwise**: a written explanation grounded in the audited results, or a
  follow-up experiment.

**Protocol-amendment route.** A follow-up experiment triggered here is
**exploratory**. It cannot become confirmatory evidence by being run and
reported: it must go through a protocol amendment — re-freeze the protocol,
run, re-ingest the manifest, re-audit — per the invalidation chain in
`shared/prompts/research_lifecycle.md`. State this explicitly in the output for
any follow-up you propose, so a post-hoc run cannot be quietly laundered into
the paper as if it had been planned.

## Council panel (opt-in)

The seven attacks above are one model red-teaming itself. When invoked with `--council`,
convene a **real adversarial panel**: each member plays the meanest reviewer at the target
venue against the full contribution, then you chair the merge. Follow
`shared/prompts/council_panel.md` (this is a **critique mode** → cross-review applies, and
red-team is an **adversarial mode** → conditional cross-examination applies).

- **Panel prompt**: the contribution statement + theory + frozen protocol + evidence audit
  + actual result manifest from research state, plus the venue's `Common reviewer red flags`
  from `shared/venue_profiles.md`. Ask
  each member for objections in the seven-attack frame (venue red flags, edge cases,
  statistical pitfalls, compute reality, sycophancy, pre-mortem rejection reasons,
  table interrogation), each
  tied to a specific part of the work.
- **Cross-review**: anonymize the reviews and have members rank which objections are most
  damaging — this surfaces where reviewers disagree on severity.
- **Cross-examination (conditional)**: when reviewers split on whether an objection is fatal,
  run **one** rebuttal round per `council_panel.md` — send the contested objection back to
  its author to substantiate (concrete edge case / pitfall / missing baseline) or concede.
  An objection counts only if it is **checkable against the work or the venue red-flag list**;
  a member's unverified "reviewers will hate this" is a hypothesis, not a finding.
- **Synthesis → seven-attack output**: fold surviving objections into the sections below,
  deduping and noting agreement ("3/4 reviewers flag single-seed runs" → high severity).
  Every panel-originated factual attack becomes a query/check and runs through the
  evidence/protocol artifacts before it becomes a finding. The chair owns correctness —
  discard stale or out-of-scope attacks and say why in one line.

Without `--council`, run the seven attacks single-model exactly as above.

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

**Table interrogation**:
| Table/figure | Anomaly (from the numbers alone) | Contradicts a frozen rule / spine claim? | Disposition |
|---|---|---|---|
| Tab. 2 | -CF ablation beats full model on D2 | yes — claim-novelty-1 | claim narrowed to D1/D3 regime |
| Fig. 3 | s.e. 4× neighbors at n=300 | no | explanation grounded in audited runs |

Any follow-up experiment listed here is **exploratory** and needs a protocol
amendment (re-freeze → run → re-ingest → re-audit) before it can be cited as
confirmatory evidence.

**Action items before paper-writer can engage**:
- [ ] ...
- [ ] ...
```

## State update

```yaml
stage: red-team
research_phase: results_red_team
red_team_findings:
  - finding: "..."
    severity: high | medium | low
    mitigation: "..."
    blocking: true   # blocks paper-writer if true
lifecycle_gates:
  evidence_audited:
    status: pass
    artifact: docs/evidence-audit-<slug>.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    audit_id: audit-...
    result_manifest_hash: "<64-char-lowercase-sha256-hex>"
  results_red_team:
    status: pass
    artifact: .research-state/<slug>-results-red-team-<date>.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    blocking: false
```

If any `blocking: true` finding exists, set the results-red-team gate `fail` and
`paper-writer` must refuse both positioning outline and full draft until the
upstream fix is made, affected gates are invalidated, and audit/red-team rerun.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] All seven attacks have content or an explicit `N/A — <reason>`;
      none skipped silently.
- [ ] Gate 0 validated real result/proof artifacts and hashes; evidence audit
      artifact + canonical verdict exist; fail/cannot-determine stopped the mode.
- [ ] Venue red-flag table rates **every** flag ✅/⚠️/❌ with a note;
      `reviewer_intel:` dossier read and cited where it applies
      (if present).
- [ ] Every finding carries severity + mitigation + `blocking:` bool
      in state.
- [ ] Sycophancy check answered honestly in ≥1 full sentence; if the verdict
      is "padded", the output routes back to `ideate`, not forward.
- [ ] Pre-mortem lists ≥2 rejection reasons in the reviewer's voice, each
      mapped to addressed / action item.
- [ ] Attack 4 was answered against the card's **per-phase** Cost artifact and
      judged feasible relative to every regime a spine claim targets.
- [ ] Attack 7 walked every results table/figure; each anomaly has a
      disposition, and anomalies contradicting a frozen decision rule or a
      spine claim were resolved by method mitigation, claim narrowing, or
      `fail` — never by narrative explanation.
- [ ] Any follow-up experiment from Attack 7 is labelled exploratory with the
      protocol-amendment route stated; no post-hoc run was presented as
      confirmatory.
- [ ] Gate 0's parity/budget check ran: parity-matrix rows covered, every
      claim-bearing asymmetry has equalized-variant runs, label counts match.
- [ ] Action items emitted; user told paper-writer is gated if any
      `blocking: true` finding exists.
- [ ] (`--council`) surviving objections passed the evidence gate; discarded
      ones noted with a one-line reason.
- [ ] Results-red-team artifact binds current method/protocol/manifest/audit
      hashes; any blocking finding prevents drafting.
