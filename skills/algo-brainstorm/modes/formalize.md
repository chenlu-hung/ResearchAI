# Mode: formalize

**Purpose**: turn a rough algorithmic intuition into a precise mathematical
object that can be analyzed, compared to prior art, and proven about.

## Inputs

- Either: a gap from `gap-analysis` the user wants to attack
- Or: a free-form "I want to do X" idea the user types

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

### 6. Output: LaTeX-ready problem statement

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

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] All six Procedure outputs present: setup, estimand/target,
      loss/construction, assumptions, quantities of interest, LaTeX block.
- [ ] Estimand vs. estimator vs. target functional vs. nuisance explicitly
      distinguished — a referee could not confuse them.
- [ ] Every assumption carries a textbook name + source or `[VERIFY]`.
- [ ] Every symbol in the LaTeX block is introduced in it or in Setup;
      none appears from nowhere.
- [ ] Anti-sycophancy done: ≥1 filled-in ambiguity and ≥1 almost-matching
      textbook setup listed, with why this isn't a special case.
- [ ] State updated: `formalization:` block + body entry.
