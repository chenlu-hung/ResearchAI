# Mode: theory-scoping

**Purpose**: for the chosen candidate, enumerate which theorems the paper
should aim to prove, the proof technique each requires, and which are
must-haves vs. nice-to-haves given the venue.

## Inputs

- A chosen candidate from `novelty-check` (must have `status: chosen`)
- `venue_target` from research state (loads `shared/venue_profiles.md`)

## Procedure

1. **Enumerate possible theorem types** relevant to Stats/ML:

   | Type | Statement form | When relevant |
   |---|---|---|
   | Consistency | $\hat{\theta}_n \to \theta^*$ in probability | Any estimator paper |
   | Convergence rate | $\|\hat{\theta}_n - \theta^*\| = O_P(r_n)$ | Most theory papers |
   | Asymptotic normality | $\sqrt{n}(\hat{\theta}_n - \theta^*) \Rightarrow N(0, \Sigma)$ | Inference / CI |
   | Minimax lower bound | $\inf_{\hat{\theta}} \sup_P R(\hat{\theta}, P) \geq c r_n$ | Optimality claims |
   | Sample complexity | $n \geq c \cdot \varepsilon^{-d/\beta}$ to achieve $\varepsilon$ | Learning theory |
   | Coverage / calibration | $\Pr(Y \in \hat{C}(X)) \geq 1 - \alpha$ | Uncertainty quantification |
   | Identifiability | Parameter recoverable from observable distribution | Causal / latent variable |
   | Generalization bound | $R(\hat{f}) - \hat{R}(\hat{f}) \leq B$ | PAC / Rademacher |
   | Regret bound | $\sum_t \ell_t(\hat{a}_t) - \min_a \sum_t \ell_t(a) \leq R_T$ | Online / bandit |
   | Stability | Algorithmic stability + generalization | Connecting alg → generalization |
   | Robustness | $\sup_{Q \in B_\varepsilon(P)} R(\hat{\theta}, Q)$ bounded | Distribution shift |

2. **For each type relevant to the candidate**:

   - Write a **target statement** (specific to this problem)
   - Identify the **proof technique** likely to work:
     - empirical process (Donsker, Glivenko-Cantelli, bracketing entropy)
     - U-/V-statistic theory
     - influence function / one-step debiasing
     - double machine learning (Neyman orthogonality + cross-fitting)
     - concentration (Bernstein, Talagrand, McDiarmid)
     - chaining / Dudley
     - stability arguments (Bousquet-Elisseeff, Hardt-Recht-Singer)
     - PAC-Bayes
     - direct calculation / closed-form
     - reduction to a known result
   - Flag any **non-standard ingredient** the proof needs (e.g., "needs a
     uniform LLN for indexed by a VC class of dimension $d$")

3. **Triage by must-have vs. nice-to-have** using venue profile:

   ```markdown
   | Theorem | Statement | Technique | Status | Must-have? |
   |---------|-----------|-----------|--------|------------|
   | Coverage | $\Pr(Y \in \hat{C}(X)) \geq 1-\alpha - O(n^{-1/4})$ | DML + cross-fitting | conjecture | yes (NeurIPS) |
   | Efficiency | $\mathbb{E}|\hat{C}(X)| \to \mathbb{E}|C^*(X)|$ | empirical process | conjecture | no, nice-to-have |
   | Minimax LB | Matching $n^{-1/4}$ for any estimator | Fano + LeCam | conjecture | yes (JMLR), no (NeurIPS) |
   ```

4. **For each must-have**: produce a **proof sketch outline** (5–10 bullet
   points) including key lemmas and where each ingredient comes from. Mark
   conjectures clearly.

5. **For pure-empirical algorithms** (e.g., a new transformer training
   trick) where formal theorems are not the contribution:

   - Specify the **empirical guarantee** structure expected by reviewers:
     scaling law, transfer to ≥3 architectures, ≥3 model sizes,
     statistical significance of improvement (paired bootstrap on per-seed
     differences), ablation completeness
   - Cite venue profile expectations

## Anti-sycophancy

For each theorem you propose, list:

- The **closest existing theorem** in the literature and the technical gap
  between it and what you propose
- One **specific reason the proof might fail** — e.g., "DML requires
  Neyman orthogonality; need to verify $\partial_w \mathcal{L}|_{w^*} = 0$"

## State update

```yaml
stage: theory
theory_targets:
  - kind: coverage
    statement: "..."
    technique: "DML + cross-fitting"
    must_have: true
    status: conjecture
    proof_sketch_ref: docs/proof-sketch-coverage.md
  - kind: efficiency
    ...
```

If proof sketches are produced, save them to `docs/proof-sketch-<kind>.md`
(separate file per theorem so they can be edited in isolation later by
paper-writer).

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Every theorem type in the Step 1 table was considered — proposed or
      `N/A — <reason>`; none silently ignored.
- [ ] Each proposed theorem has a target statement specific to this problem,
      a named proof technique, and any non-standard ingredient flagged.
- [ ] Must-have vs. nice-to-have justified against a named line of the venue
      profile, not taste.
- [ ] Each must-have has a 5–10 bullet proof sketch saved to
      `docs/proof-sketch-<kind>.md`.
- [ ] Each theorem lists the closest existing theorem + one concrete reason
      the proof might fail (Anti-sycophancy).
- [ ] Every unproved statement is marked `[CONJECTURE — not yet proved]`.
- [ ] State updated: `theory_targets:` with `must_have`/`status` + body entry.
