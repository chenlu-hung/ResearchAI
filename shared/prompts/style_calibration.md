# Style Calibration

**Recommended by default** — a calibrated voice with rhythm anchors is the
strongest *positive* lever against AI-flavored prose: models imitate exemplars
far better than they obey prohibitions, so this complements the negative
checklists in `prose_hygiene.md`. Still **soft guidance only** — never
overrides venue `style/`, `prose_hygiene.md`, or `anti_hallucination.md`.

## Skip-if-exists

If research-state frontmatter already has a `style_profile:` block, skip and say
so in one line. To recalibrate, the user deletes the block.

## Offer (once, in full-draft pre-flight)

> Provide 1–3 of your prior papers (`.tex` / `.md` / `.pdf`) to match your
> voice? Recommended — it is the best single defense against generic AI prose.
> Reply with paths, or "skip".

On "skip": proceed with venue defaults; write nothing.

## Extract (from the provided papers)

Read them and record ~6 soft features:

- Sentence rhythm (avg length; short-punchy vs long-compound).
- Hedging level (assertive vs cautious).
- Citation integration (narrative "Smith (2019) shows…" vs parenthetical).
- Section-opening style (claim-first vs roadmap-first).
- Math exposition (intuition-before-formalism vs formalism-first).
- Lexical tics to keep / avoid.

Then pick **2–3 rhythm anchors**: verbatim paragraphs (≤120 words each) that
typify the author's cadence — ideally one introduction-flavored, one
method/theory-flavored, one results/discussion-flavored. Prefer paragraphs
with varied sentence lengths and real transitions, not boilerplate.

## Persist

Append to research-state frontmatter:

```yaml
style_profile:
  asked_at: <date>
  source: [path1.tex, path2.pdf]
  features:
    rhythm: "short, declarative; avg ~18 words"
    hedging: low
    citation_style: narrative
    section_openings: claim_first
    math: intuition_first
    notes: "avoids 'novel'; prefers 'we show'"
  rhythm_anchors:
    - |
      <verbatim paragraph 1>
    - |
      <verbatim paragraph 2>
```

## Apply

Before drafting each section, re-read the anchors and match their **shape**:
sentence-length spread, transition style, paragraph size, how math is walked
into. **Never reuse an anchor's sentences or distinctive phrases** — that is
text recycling; anchors calibrate rhythm, they are not source material.
Tie-breaker only: a calibrated voice never reinstates an AI tell
(`prose_hygiene.md` precedence) or a venue violation.
