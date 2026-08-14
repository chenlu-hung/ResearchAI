# Simulated Expert Dialogue Protocol

For each section of the outline, run a short two-persona dialogue. The point
is to surface *disagreements* and *missing context* that a single-voice
summary would miss.

## Personae

For each section, pick two personae whose views are likely to conflict:

| Pair | When to use |
|---|---|
| Theorist ↔ Empiricist | Method papers (will fight over what counts as "evidence") |
| Methodologist ↔ Critic | Algorithmic sections (will fight over what's actually new) |
| Bayesian ↔ Frequentist | Inference / uncertainty sections |
| Classical statistician ↔ ML practitioner | Anything involving rates, regularity, or "sufficient" sample sizes |

## Turn structure (6 turns total)

```
Turn 1 — Persona A opens: "What does this section conclude, and why?"
  (1–2 sentences, must cite at least one claim/passage link from the packet)

Turn 2 — Persona B objects: list the strongest counter-argument or missing
  context. Must cite a different claim/passage link.

Turn 3 — Persona A concedes one point, doubles down on another.

Turn 4 — Persona B narrows: identifies the *real* point of disagreement and
  what evidence would resolve it.

Turn 5 — Both agree on a synthesis: "The honest summary is..."

Turn 6 — Both flag what remains *open*: questions for future work or for
  the user's brainstorm session.
```

## Hard rules

- Every factual turn must reference atomic claim/passage links from the current
  evidence packet. A rendered bibkey alone is insufficient.
- No persona is allowed to "win". Synthesis must integrate both views.
- Turn 6's open questions feed into `algo-brainstorm`'s `gap-analysis` —
  preserve them in the section frontmatter as `open_questions: [...]`, persist
  them as queries, and run vault-first retrieval before any is called a gap.
- Persona/model additions are hypotheses only. A newly named near-neighbor must
  complete the retrieval/link/freeze loop before changing the synthesis.

## Dialogue health check (per ARS-inspired design)

Before emitting the synthesis, verify:

- [ ] At least 2 substantive disagreements were raised
- [ ] No turn consisted of "great point, I agree" with no new content
- [ ] At least 4 distinct passage links were cited across the 6 turns
- [ ] Synthesis takes a *position* — not "it depends" without specifics

If any check fails, regenerate that section's dialogue with stricter prompt.

## Output (per section)

```markdown
### <Section title>

<3–5 sentence synthesis with inline citations generated from packet-grounded claims>

**Open questions** (carried forward to algo-brainstorm):
- ...
- ...
```

Dialogue transcripts are *not* emitted to the final survey by default —
they live in `.research-state/dialogues/<slug>-<section>.md` for debugging.
