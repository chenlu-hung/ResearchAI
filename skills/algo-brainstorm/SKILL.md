---
name: algo-brainstorm
description: Develop new Statistics/ML algorithms from rough intuition to submission-ready contribution. Eight modes (gap-analysis, formalize, ideate, novelty-check, theory-scoping, toy-design, ablation-plan, red-team) that can be invoked independently or chained. Use when the user has an idea for a new method, wants to refine an existing method, or needs adversarial review of their algorithm.
---

# algo-brainstorm

The core skill of this plugin. Targeted at researchers whose primary output is
**new algorithms** (not applied work, not surveys). Borrows the staged-pipeline
+ integrity-gate idea from ARS, but rewritten for algorithm development and
implemented entirely from scratch.

## When to invoke

- "I have an idea for a new method"
- "Help me sharpen this algorithm"
- "Is this novel?"
- "What could break this?"
- "What theorems should I aim for?"
- `/algo <mode>` slash command

## When NOT to invoke

- Topic survey → `literature-explorer`
- Writing a section of a paper → `paper-writer`
- Implementing the algorithm → general coding (this skill is design-only)

## Modes

Invoke with `/algo <mode>` or by setting the mode in the conversation.

| Mode | Purpose | Mode file |
|---|---|---|
| `gap-analysis` | Find what's wrong/missing in existing methods | `modes/gap-analysis.md` |
| `formalize` | Turn intuition into math: loss, assumptions, estimand | `modes/formalize.md` |
| `ideate` | Generate 3–5 candidate algorithmic approaches | `modes/ideate.md` |
| `novelty-check` | Compare candidates against prior art; articulate Δ | `modes/novelty-check.md` |
| `theory-scoping` | What theorems should this paper prove? | `modes/theory-scoping.md` |
| `toy-design` | Design minimal experiment that proves the idea works | `modes/toy-design.md` |
| `ablation-plan` | Design ablation table; which components are necessary? | `modes/ablation-plan.md` |
| `red-team` | Adversarial review: what reviewers will object to | `modes/red-team.md` |

## Typical chain

```
gap-analysis → formalize → ideate → novelty-check
                              ↓
                       theory-scoping → toy-design → ablation-plan → red-team
                                                                       ↓
                                                            (paper-writer outline)
```

Each mode updates `research_state` and the `algorithm_card.md`.

## Hard discipline

Applied to **every mode**:

### 1. Anti-sycophancy

Before any positive response to a user proposal, you must list:

- **≥2 substantive weaknesses** of the proposal, OR
- **≥2 closely related prior works** with summary of what they did.

No "great idea!" openers. No reassurance without grounding.

### 2. Statistical rigor reflex

If the user is doing anything that touches inference, surface relevant
pitfalls from `checklists/stats_pitfalls.md`:

- Multiple testing / FWER / FDR
- Post-selection inference
- Identifiability / regularity conditions
- Data leakage / train-test split correctness
- Selection bias
- p-hacking risk surface

If the user is doing pure ML (no inference claims), skip this.

### 3. No fabricated math

Follow `shared/prompts/anti_hallucination.md`. Do not invent theorem names,
do not cite "by X (2019) we have..." unless X 2019 is verified. Mark
conjectured statements with `[CONJECTURE — not yet proved]`.

### 4. Algorithm card hygiene

Each mode updates `docs/algo-card-<slug>.md` with the schema from
`checklists/algorithm_card.md`. The card is the single-page summary you
take into your next conversation, your advisor meeting, or paper outline.

## Output discipline

- Every mode produces **structured output** (markdown sections per the
  mode file), not free-form prose.
- Numerical claims must have provenance.
- Reference to a paper requires a bibkey from the verified set (i.e., from
  `literature-explorer` output).

## State integration

On entry: read `.research-state/<slug>.md`. If the relevant prior stage is
empty (e.g., `novelty-check` invoked but `candidates:` is empty), refuse
and suggest running `ideate` first.

On exit: update the relevant field per the mode file. Advance `stage`
only with user confirmation.

## Venue awareness

If `venue_target` is set in research state, `theory-scoping` and `red-team`
load `shared/venue_profiles.md` to tailor expectations.
