---
description: Survey a Stats/ML research topic via the literature-explorer skill. Generates multi-perspective outline + BibTeX.
argument-hint: <topic>
---

Invoke the `literature-explorer` skill on the topic: $ARGUMENTS

Follow the full pipeline in `skills/literature-explorer/SKILL.md`:

1. Create or load the research-state file for this topic
2. Generate 3–5 perspectives (see `perspectives.md`)
3. Run retrieval via the bundled scripts under `skills/literature-explorer/scripts/` (arXiv + Semantic Scholar + OpenAlex). If the optional external `literature-review-ml` skill is installed in this environment, prefer delegating to it — it adds dedup, PRISMA tracking, and ML-specific metadata. Otherwise the bundled scripts are sufficient.
4. Build hierarchical outline
5. Run two-persona expert dialogue per section (see `expert-dialogue.md`)
6. Emit `docs/survey-<slug>.md` and `refs/<slug>.bib`
7. Update research state

Anti-hallucination: every citation must come from retrieval; no fabricated bibkeys.
