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

   Save each perspective's results to its own file (e.g.
   `theorist.jsonl`) — step 4 uses the filenames as perspective labels.
   The bundled scripts are the default and require only the Python deps
   from `pyproject.toml`. **Optional**: if a `literature-review-ml` skill
   is independently installed in the environment, prefer delegating
   retrieval to it — it adds dedup, PRISMA tracking, and ML-specific
   metadata. It is *not* a hard dependency of this plugin; do not assume
   its presence.

4. **Dedup + rank** — deterministic, via the bundled script. Do **not**
   merge or rank by hand (rule 4 of
   `shared/prompts/execution_discipline.md`):

   ```bash
   uv run python skills/literature-explorer/scripts/dedupe_rank.py \
     <perspective>.jsonl ... --out ranked.jsonl --md ranked.md --top 60
   ```

   It merges on arXiv id / DOI / normalized title+author, scores by
   citations × recency-decay × perspective-hits (papers surfaced by
   several perspectives rank higher), and prints a
   `merged N -> M unique papers` summary — paste that line.

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

- Execution discipline per `shared/prompts/execution_discipline.md`:
  pipeline steps run in order, scripts over hand-work, and the Exit
  checklist below gates emission.
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
- `scripts/search_openreview.py` — venue-scoped accepted-papers + public-
  reviews fetcher for `shared/prompts/reviewer_intel.md` and
  venue-calibration exemplars; **not** part of the survey retrieval trio
  in step 3.

## Anti-hallucination

Follow `shared/prompts/anti_hallucination.md`. Specifically: no `\cite{...}`
to a paper not in this session's retrieved set. If a famous result feels
relevant but you cannot retrieve it, add to a `[VERIFY]` queue at the end.

## Exit checklist

Verify each item before emitting the survey; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] 3–5 perspectives, each with a motivation + query list; the ≤40%
      query-overlap rule applied.
- [ ] Retrieval actually ran (scripts or `literature-review-ml`) with real
      output; per-perspective JSONL files kept.
- [ ] `dedupe_rank.py` did the merge/rank; its summary line pasted — no
      hand-merged list.
- [ ] Every survey claim cites a bibkey from the retrieved set;
      unretrievable "famous results" sit in the `[VERIFY]` queue instead.
- [ ] Papers ≤6 months old flagged `[PREPRINT]`.
- [ ] Survey body ≤ ~3000 words; each section's dialogue passed the
      health check in `expert-dialogue.md`.
- [ ] `docs/survey-<slug>.md` + `refs/<slug>.bib` written; state updated
      (`literature:`, `citations:`, `stage`).
