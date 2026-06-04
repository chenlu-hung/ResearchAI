# Style Calibration

Optional. Lets `full-draft` match the user's (or advisor's) writing voice.
**Soft guidance only** — never overrides venue `style/`, `prose_hygiene.md`, or
`anti_hallucination.md`.

## Skip-if-exists

If research-state frontmatter already has a `style_profile:` block, skip and say
so in one line. To recalibrate, the user deletes the block.

## Offer (once, in full-draft pre-flight)

> Provide 1–3 of your prior papers (`.tex` / `.md` / `.pdf`) to match your
> voice? Reply with paths, or "skip".

On "skip": proceed with venue defaults; write nothing.

## Extract (from the provided papers)

Read them and record ~6 soft features:

- Sentence rhythm (avg length; short-punchy vs long-compound).
- Hedging level (assertive vs cautious).
- Citation integration (narrative "Smith (2019) shows…" vs parenthetical).
- Section-opening style (claim-first vs roadmap-first).
- Math exposition (intuition-before-formalism vs formalism-first).
- Lexical tics to keep / avoid.

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
```

Apply during drafting as a tie-breaker on style choices only.
