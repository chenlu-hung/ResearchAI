# Prose Hygiene

Run on every prose section after drafting/editing, **before saving**. Cheap,
mechanical, catches the AI-tell tax reviewers notice — the "this reads like it
was generated" smell that costs credibility even when the science is sound.

**Engine vs. overlay.** If the `stop-slop` skill is available, invoke it on the
section first — it is the general AI-tell engine. This file is the **academic
overlay**: it (a) carries the same checks so the pass works even when `stop-slop`
is absent, (b) adds ML/Stats-specific tells, and (c) lists the stop-slop rules to
**relax** for academic register (§ Academic exceptions). Where they conflict, the
exceptions here win — `stop-slop` is tuned for blog/essay prose, not papers.

---

## A. Phrase-level cuts

- **Hedge filler**: "it is worth noting (that)", "it should be noted", "it is
  important to note", "importantly", "notably", "interestingly", "arguably",
  "we believe / feel". Delete, or replace with the claim itself.
- **Throat-clearing openers**: "In this section, we will…", "It is important to
  understand…", "To begin with…". Start with the content.
- **AI-tell vocabulary**: "delve", "crucial", "pivotal", "leverage" (verb; use
  "use"/"exploit"), "rich tapestry", "showcase", "underscore", "realm",
  "harness", "intricate", "seamless", "robustly" (when not a robustness claim),
  "holistic". Use plain words.
- **Empty intensifiers**: "very", "highly", "extremely", "remarkably",
  "significantly" (unless reporting statistical significance — then give the test
  and p-value/CI), "substantially" (give the number instead).
- **Unscoped superlatives**: no "novel / first / state-of-the-art / superior"
  without explicit scope (novel *relative to what?* SOTA *on which benchmark, as
  of when?*).
- **Em-dashes**: ≤ 2 per page; prefer commas, parentheses, or a period.

## B. Structural tells (the strongest "AI smell")

These are the patterns reviewers subconsciously flag as machine-written. They
survive a vocabulary pass, so check them explicitly.

- **Binary contrast / telegraphed reversal**: "not because X, but because Y",
  "the problem is not X; it is Y", "it is not just X, but also Y", "X is not the
  bottleneck, Y is". State Y directly.
  - ✗ "The gain comes not from more parameters but from the orthogonalization."
  - ✓ "The orthogonalization step (Eq. 4), not parameter count, drives the gain
    (Table 3)."
- **False agency** (inanimate subject + human verb — AI's favorite dodge for
  naming the actor): "the data reveals / tells us", "the results speak for
  themselves", "the ablation tells a clear story", "the theory suggests" (unless
  it is a literal theorem), "the loss landscape decides".
  - ✗ "The ablation tells a clear story."
  - ✓ "Removing the regularizer raises test error from 4.1% to 7.8% (Table 2)."
  - (ML idioms where the model is the genuine actor — "the network learns to…",
    "the estimator converges" — are fine.)
- **Negative listing / rhetorical striptease**: "Not an X. Not a Y. A Z." State Z.
- **Dramatic fragmentation**: "We trained one model. One. And it won." or
  "[Noun]. That's the key idea." Use complete sentences; trust the content.
- **Rhetorical setups**: "What if we could…?", "Here's the key insight:", "What
  makes this work is…". Make the point. "What makes the estimator unbiased is the
  cross-fitting" → "Cross-fitting (§3.2) removes the first-order bias."
- **Vague declaratives**: "The implications are significant", "This has profound
  consequences", "the reasons are structural". Name the specific implication.
  - ✓ "This implies √n-consistency holds under model misspecification (Cor. 2)."
- **Narrator-from-a-distance / Wh- openers as a crutch**: "What makes this hard
  is…", "This is why…". Lead with the subject. ("The constraint is…", or name it.)

## C. Rhythm

- Do not make every paragraph or sentence the same length; vary 2–8 sentences per
  paragraph and mix short claims with longer compound ones.
- Do not end every paragraph on a punchy one-liner — that cadence reads as
  generated. Some paragraphs should end on a qualification or a forward pointer.
- Do not stack three short staccato sentences for emphasis.

## D. ML / Stats-specific

- No "outperforms / improves / achieves SOTA" without numbers **and**
  seed/variance (or a CI / significance test).
- No "well-known that / it is clear that / obviously" hand-waves — cite verifiably
  or prove inline.
- **Voice**: active for claims and contributions ("We prove…", "We propose…");
  past tense for what was done ("We trained…", "We evaluated…").
- Drop "to the best of our knowledge"; state the Δ to specific prior work instead.

## E. Academic exceptions (relax these stop-slop rules)

`stop-slop` is written for essays. Do **not** carry these rules into a paper:

- **Passive voice is allowed** where the actor is conventional or irrelevant:
  "Samples were drawn i.i.d. from $P$", "The model was trained for 100 epochs."
  Prefer active only for *claims and contributions*. Do not hunt down every passive.
- **Keep technical adverbs**: "asymptotically", "almost surely", "uniformly",
  "jointly", "marginally", "i.i.d.", "in probability". Cut only empty
  intensifiers (§A). Do not blanket-delete "-ly" words.
- **No second person.** Never use "you" or "put the reader in the room" — academic
  register is first-person-plural / third-person. This stop-slop rule is inverted
  here.
- **Three-item lists are fine** (three contributions, three assumptions). Ignore
  stop-slop's "two beats three."
- **Em-dashes**: ≤ 2 per page, not a total ban.

## Per-section checklist (fast pass)

1. Any phrase from §A? Cut or replace.
2. Any "not X, but Y" / "the data reveals" / "what makes this work is…"? Restructure (§B).
3. Any superlative or improvement claim without scope/numbers? Add them or soften.
4. Do three paragraphs in a row have the same length or punchy ending? Break the pattern (§C).
5. Active voice for our claims (§D); passive only where conventional (§E).

## Precedence

`anti_hallucination.md` and the venue `style/` file **override** anything here —
never trade correctness or venue conformance for fluency. `style_calibration.md`
sits **below** this file: a calibrated voice is a tie-breaker, it never reinstates
an AI tell.
