# Mode: ideate

**Purpose**: given a formalized problem, generate 3–5 distinct candidate
algorithmic approaches. Force diversity — empirical vs. theoretical
motivation, different primitives.

## Inputs

- A `formalize` block from research state (required)
- Optional: user's preferred direction or constraint

## Pre-flight grill

Run the interview protocol in `shared/prompts/grill_protocol.md` **after**
Step 1 below (state read + refuse-if-blank check) and **before** Step 2
(candidate generation). If `interview_ideate:` is already present in the
research-state frontmatter, skip the interview and proceed.

**Essentials** (ask in this order, one at a time):

1. **Algorithmic primitive preference** — `AskUserQuestion`, header
   "Primitive". Options drawn from Step 2's primitive list: proximal /
   score-matching / conformal / DML / variational / Bayesian /
   sampling-based. Recommended = the primitive most consistent with the
   formalization's `loss:` and `nuisance:` fields (cite the grounding in
   the option's `description`).
2. **Contribution type** — `AskUserQuestion`, header "Contribution".
   Options: theoretical (target theorem in mind) / empirical (fixing
   observed failure) / methodological (new framework). Recommended =
   `theoretical` if `theory_targets:` is non-empty, else `empirical` if
   `gap-analysis` has populated failure modes, else `methodological`.
3. **Hard constraints / no-go zones** — free-form. Recommended phrasing:
   "Candidates must not rely on knowing the nuisance exactly; must
   remain valid at finite-sample n." User can replace, extend, or accept.
4. **Diversity target** — `AskUserQuestion`, header "Diversity".
   Options: max diversity across primitives / deep dive within one
   primitive / mixed (2 primitives, 2 variants each). Recommended = max
   diversity (default, matches Step 3's existing diversity requirement).

On `Proceed`, append an `interview_ideate:` block to research-state
frontmatter per the protocol's persistence rules. Use the answers to
constrain Step 2: the primitive answer narrows the primitive list, the
contribution-type answer biases each candidate's `motivation:` field,
constraints filter the candidate set, and diversity target shapes the
spread (Step 3's `≥1 theoretical`, `≥1 empirical` requirements still
apply under "max diversity"; under "deep dive" relax the
distinct-primitive rule but keep the motivation diversity).

## Procedure

1. **Read the formalization**. If `formalization:` is empty in research
   state, refuse and run `formalize` first.

2. **Generate candidates** — 3–5, each with:

   - **Name**: 3–7 words
   - **Core idea** (one sentence): the *single* algorithmic primitive that
     drives this approach
   - **Primitive** (pick one or compose): proximal / score matching /
     conformal / debiased ML / cross-fitting / sample splitting /
     pseudo-labeling / two-stage / EM / variational / MCMC / kernel /
     RKHS / influence function / one-step bias correction / sieve /
     penalty / projection / online / bandit / RL
   - **Motivation type**: `theoretical` (has a target theorem in mind) /
     `empirical` (driven by observed failure) / `analogy` (porting from
     adjacent field)
   - **Expected trade-off**: what does this candidate give up to gain?
     (e.g., "trades sample efficiency for distribution-free coverage")
   - **Cost class**: $O(n)$ / $O(n \log n)$ / $O(n^2)$ / $O(n^3)$ / iterative

3. **Required diversity**: across the 3–5 candidates:

   - **≥1 candidate motivated theoretically** (you can already imagine the
     proof technique)
   - **≥1 candidate motivated empirically** (driven by a specific failure
     mode from `gap-analysis`)
   - **Distinct primitives** — no two candidates may share both primitive
     and motivation

4. **Forbidden "candidates"**:

   - "Same method but with a transformer/attention/diffusion backbone" —
     not an algorithmic contribution
   - "Same method with $L_2 \to L_1$ regularization" — only counts if there
     is a *specific* analytic or empirical reason
   - "Same method but Bayesian" — only counts if the prior structure does
     real work in the analysis
   - "Same method but with kernel" — only counts if the kernel choice
     is principled (eigenfunction, RKHS embedding, etc.)

5. **Output as ranked candidate table**:

   ```markdown
   | # | Name | Core idea | Primitive | Motivation | Trade-off | Cost |
   |---|------|-----------|-----------|------------|-----------|------|
   | 1 | Cross-fitted weighted conformal | Use DML to estimate w(x), then weighted quantile | weighted quantile + cross-fitting | theoretical | Needs $w$ estimation; gets $n^{-1/4}$ remainder | $O(n)$ + nuisance |
   | 2 | ...
   ```

## Anti-sycophancy

For each candidate, **before** writing it, briefly check (one sentence
each):

- "Has someone done this?" — if you cannot rule out prior art with
  reasonable confidence, mark `novelty: uncertain` next to the candidate
- "Why hasn't this been done?" — if the answer is "it's obviously
  worse than the existing approach", drop the candidate

If you cannot generate 3 candidates that pass these checks, say so.
Better to deliver 2 strong candidates than 5 weak ones.

## State update

```yaml
stage: ideate
candidates:
  - id: cand-1
    name: "..."
    core_idea: "..."
    primitive: "..."
    motivation: theoretical
    trade_off: "..."
    cost: "O(n)"
    novelty: uncertain   # uncertain | likely_novel | known_prior_art
    status: active
  - id: cand-2
    ...
```

Append to body under `## <date> — ideate`.

## Hand-off

After ideate completes, the immediate next step is `novelty-check`, which
resolves the `novelty: uncertain` flags. Do not advance to `theory-scoping`
without a novelty pass.
