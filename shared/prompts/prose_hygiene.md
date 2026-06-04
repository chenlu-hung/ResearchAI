# Prose Hygiene

Run on every prose section after drafting/editing, before saving. If the
`stop-slop` skill is available, invoke it on the section; otherwise apply this
checklist. Cheap, mechanical, catches the AI-tell tax reviewers notice.

## Cut / fix

- **Hedge filler**: "it is worth noting", "it should be noted", "importantly",
  "arguably", "we believe/feel". Delete or replace with the claim itself.
- **Throat-clearing openers**: "In this section, we will…", "It is important to
  understand…". Start with the content.
- **AI-tell vocabulary**: "delve", "crucial", "pivotal", "leverage" (verb),
  "rich tapestry", "showcase", "underscore", "realm". Use plain words.
- **Em-dashes**: ≤ 2 per page.
- **Rhythm**: do not make every paragraph the same length; vary 2–8 sentences.
- **Empty intensifiers**: "very", "highly", "significantly" (unless statistical).
- **Unscoped superlatives**: no "novel / first / state-of-the-art" without an
  explicit scope (novel *relative to what?*).

## ML-specific

- No "outperforms / improves" without numbers **and** seed/variance.
- No "well-known / it is clear that" hand-waves — cite verifiably or prove inline.
- Active voice for contributions ("We prove…"), past tense for what was done
  ("We evaluated…").

Precedence on conflict: `anti_hallucination.md` and the venue `style/` file
override stylistic preferences here; never trade correctness for fluency.
