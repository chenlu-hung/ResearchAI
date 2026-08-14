# Anti-Hallucination Protocol

Applied across all skills. Use it with
`shared/prompts/evidence_grounding.md`, which defines the canonical retrieval,
claim-linking, packet, freshness, and migration rules.

## Hard rules

1. **Model knowledge is not evidence.** Parametric recall—including agreement
   among council members—may generate a hypothesis, candidate work name, or
   search query only. It cannot support a novelty verdict, top-gap ranking, or
   draft claim.

2. **No fabricated citations.** A bibliographic mention or `\cite{...}` must
   resolve to a canonical vault work. A substantive attributed claim additionally
   needs an atomic claim-to-passage link in a current evidence packet. A BibTeX
   key or metadata match alone is not claim support.

3. **No fabricated theorem names or results.** Do not write "by Smith (2019)
   we have..." without a passage-grounded source. Re-derive the result inline or
   mark it `[VERIFY]`; mark an unproved proposed result
   `[CONJECTURE — not yet proved]`.

4. **No fabricated benchmark numbers.** Every number needs a stable passage,
   table, dataset, or experiment artifact and provenance. A number recalled from
   training data remains a query, not a qualified fact. Expected curves and
   pre-run hypotheses never become observed results; empirical numbers must
   trace to the frozen protocol, result manifest/artifact hash, and evidence audit.

5. **Keep inference and evidence distinct.** Label derived reasoning as a
   derivation. Label recalled or panel-suggested facts `[VERIFY]` and persist a
   query-run. Never let polished prose erase that distinction.

## Sanity checks before output

- [ ] The evidence vault was queried before external sources.
- [ ] Every cited work is canonical and every substantive attributed claim has
      a source version, locator/passage, and evidence link.
- [ ] The candidate-specific packet is current for the exact primitives,
      objective/estimand, data regime, and claim set.
- [ ] Abstract-only material is used only for metadata/context, not `supports`.
- [ ] Every theorem name and numerical claim is traceable or explicitly
      unverified/conjectural.
- [ ] New gaps and near-neighbors were converted into queries and the packet was
      refreshed before the verdict or prose changed.

## When verification is impossible

Persist `[VERIFY: <atomic claim>]` and the attempted/no-result query-run, then
report the missing source or passage. Do not silently omit the issue and do not
cross an evidence gate. Offline mode can produce a search plan, hypothesis list,
or clearly speculative derivation—but not a positive novelty verdict, top-gap
ranking, or supported literature claim.

## Skill-specific gates

- `gap-analysis`: an unverified item cannot be a top gap.
- `ideate`: generated candidates are speculative until targeted retrieval
  produces a current packet.
- `novelty-check`: requires a current candidate packet. Weaknesses do not
  substitute for grounded prior-art comparisons; an application-only delta is
  not method novelty.
- `theory-scoping`: unproved statements remain conjectures.
- `paper-writer`: `citation-audit` may mark a claim `verified` only after both
  metadata validation and passage-level support validation. `.bib` is a
  generated canonical-work view, never the evidence authority.
