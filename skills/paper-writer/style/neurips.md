# Style: NeurIPS

## Section template

1. **Abstract** (~150 words): problem, approach, contribution (with one
   number if possible), implication. No equations.
2. **Introduction** (1.0 pp): hook → gap → contribution bullets (3–5) → roadmap.
3. **Related Work** (0.5–1.0 pp): organized by topic, not chronology. Each
   paragraph ends with the Δ against the cited cluster.
4. **Setup / Problem** (0.5–1.0 pp): notation, assumptions, formal goal.
5. **Method** (1.5–2.5 pp): intuition → pseudocode → justification.
6. **Theory** (1.0–2.0 pp, optional): theorems with proof sketch; full proofs in appendix.
7. **Experiments** (1.5–2.5 pp): toy, real data, ablations.
8. **Discussion + Limitations** (0.3–0.5 pp): honest, specific.
9. **Broader Impact** (0.1–0.3 pp): mandatory; concrete, not boilerplate.

## Tone

- Active voice, direct. "We propose..." not "It is proposed that..."
- Hedge sparingly. If you're confident, say so.
- No "to the best of our knowledge" — say what's new by Δ to prior work.
- Number every contribution bullet in the intro and use those numbers
  consistently (C1, C2, ...) in the rest of the paper.

## Reviewer expectations

- Will check arXiv for recent baselines (≤6 months). Include them.
- Will demand multi-seed empirical results with statistical significance.
- Will examine the ablation table for completeness.
- Limitations and Broader Impact sections must be specific. Generic
  "could be misused" → automatic complaint.

## Don'ts

- No "novel" without scope (novel-relative-to-what?)
- No bare-number tables without significance testing
- No "we believe" / "we feel" — show, don't assert
- No more than 3 acronyms before they all blur

## Compute reporting (required since NeurIPS 2024)

State explicitly: GPU type + count, wall-clock per experiment, total
compute for the paper.

## AI disclosure (required)

Single sentence stating any LLM use (writing assistance, code generation,
review). Do not hide.
