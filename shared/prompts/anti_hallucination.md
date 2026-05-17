# Anti-Hallucination Protocol

Applied across all skills. Skills should reference this file rather than
duplicating the rules.

## Hard rules

1. **No fabricated citations.** Every `\cite{...}` or bibliographic mention
   must correspond to a paper you have either (a) been given by the user, or
   (b) verified via Semantic Scholar / arXiv / OpenAlex within this session.
   If unsure, say "I don't have a verified source for this claim" rather than
   inventing.

2. **No fabricated theorem names or results.** Do not write "by Smith (2019)
   we have..." unless Smith 2019 is in the verified-citations set. Do not
   invent named lemmas (e.g., "Choquet-Hahn inequality"). When attributing
   a result, default to the textbook attribution you are certain of, or
   describe the technique without attribution and flag for verification.

3. **No fabricated benchmark numbers.** Never state "X achieves 87.3% on
   CIFAR-10" unless given that number or verified from a primary source.
   If recalled from training data, qualify: "I recall something near 87%
   but treat as unverified."

4. **Distinguish recall vs. derivation.** Mark conclusions reached by
   reasoning differently from recalled facts:
   - Recalled: "Tibshirani's 2019 conformal-shift paper introduces weighted
     quantile reweighting [VERIFY]"
   - Derived: "Under A1, the estimator is unbiased — see derivation above"

## Sanity checks before output

Before producing a draft section, mentally check:

- [ ] Every cited paper is in the verified set or marked `[VERIFY]`
- [ ] Every named theorem traceable to a source or rederived inline
- [ ] No numerical claim without provenance
- [ ] No "well-known result" hand-wave; either prove inline or cite verifiably

## When verification is impossible

If running offline or without API access, output `[VERIFY: <claim>]` inline
and produce a verification queue at the end of the document. **Do not silently
omit citations.**

## For algo-brainstorm specifically

- `novelty-check` must use real search results. If `literature-explorer` has
  not been run, refuse to claim novelty — instead, list candidate-prior-art
  search queries the user should run.
- `theory-scoping` may suggest proof techniques speculatively, but must mark
  any specific theorem statement as `[CONJECTURE — not yet proved]` if a
  proof has not been written.

## For paper-writer specifically

- `citation-audit` mode is the gate that flips `audit_status: pending` →
  `verified` in `research_state`. Until then, treat all citations as suspect.
