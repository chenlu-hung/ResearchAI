# Style: JMLR

## Section template

- Page limit: none (typical 25–40 pp)
- More expansive sections, proofs in main text
- Sections: Introduction → Background → Method → Theory → Experiments →
  Discussion → Conclusion. Appendix integrated.

## Tone

- More formal than NeurIPS/ICML. Mathematical statements are the load-bearing
  content.
- "We" allowed but used sparingly; passive acceptable in technical sections.

## Reviewer expectations

- **Theorems with full proofs in main text**, not in appendix. Proof
  sketches in main + full proofs in appendix is acceptable only for
  long results.
- **Assumption minimality** is scrutinized. For each assumption: when
  does it fail? Is there a weaker version?
- **Sharp rates and constants** valued. Aim for minimax-style results
  when possible.
- Empirical section can be smaller than NeurIPS/ICML, but rigor (multi-seed,
  significance, ablation) is unchanged.

## Distinct dos

- State minimax / lower bound if available
- Provide assumption discussion: each (A1, A2, ...) gets a paragraph
  explaining when it holds and when it fails, with examples
- For semiparametric work: cite the classical statistics literature
  (Bickel, Pfanzagl, Tsiatis, van der Vaart)

## Don'ts

- No proof-by-citation for the main theorem. Reviewers want to see it.
- No vague "regularity conditions" — list them.
