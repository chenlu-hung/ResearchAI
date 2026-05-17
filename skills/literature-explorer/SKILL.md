---
name: literature-explorer
description: Multi-perspective survey of a Statistics/ML research topic. Generates structured outline grounded in arXiv / Semantic Scholar / OpenAlex retrieval, with simulated expert dialogue to deepen each section. Outputs markdown survey + BibTeX. Use when starting a new topic, scoping a literature review, or feeding prior-art into algo-brainstorm's novelty-check.
---

# literature-explorer

Borrows the *multi-perspective question generation* and *simulated expert
discourse* patterns from Stanford STORM, but adapted for Stats/ML and
implemented as prompt orchestration (no STORM dependency required).

## When to invoke

- User says: "survey X", "what's known about X", "literature review on X",
  "what's the prior art for X", `/explore <topic>`.
- `algo-brainstorm`'s `novelty-check` mode requests prior art.

## When NOT to invoke

- User wants a specific paper read → use general read tools.
- User wants brainstorming, not survey → use `algo-brainstorm`.
- Heavy automated Wikipedia-style report needed → consider falling back to
  the `knowledge-storm` Python package (optional dep) for the empirical retrieval pass,
  then reformat with this skill.

## Pipeline

1. **Slug + state file**: derive slug from topic, create or load
   `.research-state/<slug>.md` per `shared/research_state.schema.md`.

2. **Generate perspectives** (3–5). For each, write a one-line motivation
   and a list of 5–10 search queries. See `perspectives.md` for the prompt
   pattern and defaults for Stats/ML.

3. **Retrieval**. Run the three retrieval scripts in parallel:
   - `scripts/search_arxiv.py "<query>"` — arXiv API
   - `scripts/search_semantic_scholar.py "<query>"` — Semantic Scholar Graph API
   - `scripts/search_openalex.py "<query>"` — OpenAlex

   The bundled scripts are the default and require only the Python deps
   from `pyproject.toml`. **Optional**: if a `literature-review-ml` skill
   is independently installed in the environment, prefer delegating
   retrieval to it — it adds dedup, PRISMA tracking, and ML-specific
   metadata. It is *not* a hard dependency of this plugin; do not assume
   its presence.

4. **Dedup + rank**. Merge by normalized title + first author + year.
   Rank by (citations × recency-decay × perspective-match).

5. **Build hierarchical outline**. Top level = perspectives; second level =
   sub-themes within each perspective; leaves = paper bundles (3–8 papers
   each).

6. **Simulated expert dialogue** per section (see `expert-dialogue.md`).
   Two personae argue/refine for ~6 turns, then converge to a 1-paragraph
   synthesis with inline citations.

7. **Emit artifacts**:
   - `docs/survey-<slug>.md` — full survey
   - `refs/<slug>.bib` — verified BibTeX
   - Update `research_state` `literature:` and `citations:` paths; advance
     `stage` from `explore` to whatever comes next when user confirms.

## Output discipline

- Every claim cited; no `[citation needed]` placeholders.
- Mark recent preprints (≤6 months) with `[PREPRINT]` flag — they are
  important for `novelty-check` but unstable.
- Cap survey body at ~3000 words. Detail goes into the outline tree, not
  prose.

## Files

- `perspectives.md` — perspective archetypes and prompt template.
- `expert-dialogue.md` — two-persona dialogue protocol.
- `scripts/search_arxiv.py`, `scripts/search_semantic_scholar.py`,
  `scripts/search_openalex.py` — retrieval helpers.

## Anti-hallucination

Follow `shared/prompts/anti_hallucination.md`. Specifically: no `\cite{...}`
to a paper not in this session's retrieved set. If a famous result feels
relevant but you cannot retrieve it, add to a `[VERIFY]` queue at the end.
