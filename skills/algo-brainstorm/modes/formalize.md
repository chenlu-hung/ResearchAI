# Mode: formalize

**Purpose**: turn a rough algorithmic intuition into a precise mathematical
object that can be analyzed, compared to prior art, and proven about.

## Inputs

- Either: a gap from `gap-analysis` the user wants to attack
- Or: a free-form "I want to do X" idea the user types
- Plus: a `corpus_manifest:` pointer in state whose artifact hash validates

**Corpus gate.** Without a corpus manifest, refuse to start and offer to run
`literature-explorer` in `corpus-prefetch` mode first (one-time per topic,
`skills/literature-explorer/corpus-prefetch.md`); refresh the recent-work axis
if its `gathered:` date is more than 6 months old. Formalization is where the
objective and regime get their final wording, so the novelty reflex in
`skills/algo-brainstorm/SKILL.md` Hard discipline #2 applies to every term you
commit to here: name the nearest corpus neighbor for each, and treat an
out-of-envelope term as a retrieval to run now.

## Procedure

Produce all of the following. Each piece must be precise enough that a
referee could rederive it.

### 1. Setup

- **Random variables**: $(X, Y)$ or just $X$; spaces ($\mathcal{X}, \mathcal{Y}$); dimensions.
- **Data**: sample size $n$, i.i.d.? exchangeable? time series? what dependence?
- **Population / generative assumption**: $X \sim P$; if there is shift, $P$ vs $Q$.

### 2. Estimand / target

What does the algorithm output, in mathematical terms?

- $\hat{\theta} \in \Theta$? Parameter vector?
- $\hat{f}: \mathcal{X} \to \mathcal{Y}$? Function?
- $\hat{C}(x) \subset \mathcal{Y}$? Prediction set?
- $\hat{p}(y \mid x)$? Conditional density?

Distinguish:

- **Estimand**: the true target ($\theta^*$, $f^*$, $C^*$).
- **Estimator**: the algorithm's output.
- **Target functional** (if estimand is itself a functional, e.g., ATE).
- **Nuisance**: any quantity that needs to be estimated to compute the
  estimator but is not itself the goal (propensity score, density ratio,
  variance function).

### 3. Loss / objective

If the algorithm optimizes something, write it out:

$$\hat{\theta} = \arg\min_{\theta \in \Theta} \mathcal{L}(\theta; \mathcal{D}) + \lambda \cdot R(\theta)$$

Specify: $\mathcal{L}$ (empirical risk? log-likelihood?), $R$ (regularizer), $\Theta$ (constraint set), $\lambda$ (tuning).

If the algorithm is not optimization-based (e.g., method of moments,
empirical Bayes, conformal), describe the construction step-by-step.

### 4. Assumptions

List with standard textbook names where possible:

- (A1) Exchangeability / i.i.d.
- (A2) Bounded support / sub-Gaussian noise
- (A3) Identifiability of $\theta^*$
- (A4) Regularity: $\mathcal{L}$ is twice differentiable, ...
- (A5) Smoothness: Hölder/Sobolev class
- (A6) Density: $p(x) > 0$ on supp
- (A7) Margin / noise condition (Tsybakov, etc.)

For each: cite the textbook source if you know it; flag `[VERIFY]` if not certain.

### 5. Quantities of interest

What scalars/functions do you want to control or compute?

- $\text{Risk}(\hat{f}) = \mathbb{E}[\ell(\hat{f}(X), Y)]$
- $\text{Coverage}(\hat{C}) = \Pr(Y \in \hat{C}(X))$
- $\text{Length}(\hat{C}) = \mathbb{E}[|\hat{C}(X)|]$
- $\text{Bias}(\hat{\theta}) = \mathbb{E}[\hat{\theta}] - \theta^*$
- etc.

### 6. Headline terms

Every term the paper will lean on in its title, abstract, or contribution
statements — "operator", "cross-resolution", "invariance", "scalable",
"consistent" — is a **promise to a reviewer**, and gets pinned down here rather
than at drafting time, when the wording is already load-bearing.

For each headline term, write an atomic claim with formal content:

| Term | What it formally promises | Claim ID | Delimited to |
|---|---|---|---|
| operator | maps between function spaces, not fixed discretizations; discretization consistency as $h \to 0$ | claim-term-1 | uniform grids only |
| cross-resolution | **both** transfer directions: coarse→fine and fine→coarse | claim-term-2 | — |

Rules:

- State the promise a hostile reader would extract, not the weakest reading you
  could defend. "Operator" promises discretization consistency; if the method is
  grid-locked, either establish the consistency or drop the word.
- A promise you will not demonstrate must be **explicitly delimited** in the
  claim text ("uniform grids only"), never left ambient.
- Propagate: each term claim enters `docs/claim-map-<slug>.md`, is available to
  the contribution spine at method freeze, and any term claim the spine adopts
  must have an experiment or a proof bound to it in the experiment contract.
- `self-review`'s headline-term audit later checks each promise against the
  written paper. A term with no claim here becomes an unfalsifiable boast there.

### 7. Output: LaTeX-ready problem statement

Emit a block ready to paste into Section 2 of a paper:

```latex
\paragraph{Setup.} Let $(X_i, Y_i)_{i=1}^n$ be i.i.d. draws from $P$ on $\mathcal{X} \times \mathcal{Y}$, where ...

\paragraph{Target.} We aim to construct $\hat{C}: \mathcal{X} \to 2^{\mathcal{Y}}$ such that
\[
\Pr(Y_{n+1} \in \hat{C}(X_{n+1})) \geq 1 - \alpha
\]
where $(X_{n+1}, Y_{n+1}) \sim Q$ and $Q$ admits density $q$ with $\mathrm{d}Q/\mathrm{d}P = w$ for some bounded $w$.

\paragraph{Assumptions.}
\begin{enumerate}
\item[(A1)] $w$ is bounded above by $M < \infty$.
\item[(A2)] ...
\end{enumerate}
```

## Anti-sycophancy

After producing the formalization, **before** asking the user if it's right,
list:

- ≥1 ambiguity that the user's intuition did not specify and you had to
  fill in (so they can correct it)
- ≥1 standard textbook setup that almost-but-not-quite matches this, and
  why this isn't just a special case

## State update

```yaml
stage: formalize
formalization:
  estimand: "..."
  loss: "..."
  assumptions: [A1, A2, ...]
  nuisance: [...]
  regularity: [...]
```

Append the LaTeX block to body under `## <date> — formalize`.

Update `docs/claim-map-<slug>.md` with the atomic estimand, assumption,
target, and **headline-term** claims and recompute
`lifecycle_gates.atomic_claim_map.artifact_hash` per
`shared/prompts/research_lifecycle.md`. Unverified attributions remain query
items; the claim map can pass only when every item needed for the next gate has
a disposition.

If this revises an existing candidate's objective/estimand, data regime, or
assumptions, mark every affected evidence packet stale with a reason before
writing state. Downstream evidence-gated modes must retrieve and freeze a
replacement; legacy survey/BibTeX artifacts do not preserve freshness.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Corpus manifest validated (and refreshed if >6 months old), or the mode
      refused and offered `corpus-prefetch`.
- [ ] Each committed objective/regime/assumption term named its nearest corpus
      neighbor; out-of-envelope terms triggered retrieval and a manifest extension.
- [ ] All seven Procedure outputs present: setup, estimand/target,
      loss/construction, assumptions, quantities of interest, headline terms,
      LaTeX block.
- [ ] Every headline term the paper will lean on has an atomic claim stating
      what it formally promises, with undemonstrated promises explicitly
      delimited; each term claim is in the claim map.
- [ ] Estimand vs. estimator vs. target functional vs. nuisance explicitly
      distinguished — a referee could not confuse them.
- [ ] Every assumption carries a textbook name + source or `[VERIFY]`.
- [ ] Every symbol in the LaTeX block is introduced in it or in Setup;
      none appears from nowhere.
- [ ] Anti-sycophancy done: ≥1 filled-in ambiguity and ≥1 almost-matching
      textbook setup listed, with why this isn't a special case.
- [ ] State updated: `formalization:` block + body entry.
- [ ] Claim-map lifecycle artifact/hash updated with formalization claims.
- [ ] Any affected existing candidate packet was marked stale after a material
      objective/regime/assumption change.
