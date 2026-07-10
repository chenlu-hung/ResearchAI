# Style: JMLR

## Section template

- Page policy (author guide): >35 pp (appendices included) reviews slowly
  and may be rejected for lack of reviewers; >50 pp needs cover-letter
  justification and risks desk rejection. Target ≤35 pp.
- **JMLR style file mandatory** — papers not in it are rejected without
  review. Abstract ≤200 words; running title ≤50 chars; five keywords.
- More expansive sections, proofs in main text
- Sections: Introduction → Background → Method → Theory → Experiments →
  Discussion → Conclusion. Appendix integrated; online appendices possible
  for data/code.

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
- No bulleted Related Work or Discussion — JMLR expects flowing prose;
  enumerate only assumptions (A1, A2, …) and algorithm steps.
