---
name: literature-explorer
description: Multi-perspective Stats/ML literature retrieval and survey synthesis. Queries the canonical evidence vault before arXiv / Semantic Scholar / OpenAlex, persists query runs and passage-grounded atomic claims, and emits a survey plus a generated BibTeX view. A second mode, corpus-prefetch, runs one broad shallow abstract-level sweep across application, mathematical-skeleton, adjacent-field, and historical axes to build the local corpus that algorithm discussion runs against. Use when starting a topic, scoping prior art, building the corpus before brainstorming, or preparing evidence for algorithm novelty review.
---

# literature-explorer

## Plugin-root contract

Resolve the absolute path of this already loaded `SKILL.md`, then set
`PLUGIN_ROOT` to the directory two levels above its containing skill directory
(`.../skills/literature-explorer/../..`). Never infer the plugin location from
the user's working directory and do not `cd` into the plugin. Resolve
`shared/...` and `skills/...` resources against `$PLUGIN_ROOT`; resolve bare
`perspectives.md`, `expert-dialogue.md`, `corpus-prefetch.md`, and
`scripts/...` paths against this
skill directory. Project artifacts such as `.research-state/`, `docs/`,
`paper/`, `refs/`, and `results/` remain relative to the user's project.
Dependency-bearing Python scripts use
`uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`; stdlib-only
scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Multi-perspective retrieval and expert disagreement help widen coverage, but
neither model recall nor dialogue is evidence. Follow
`shared/prompts/evidence_grounding.md` and
`shared/prompts/anti_hallucination.md` throughout.

## Modes

| Mode | Purpose | File |
|---|---|---|
| *(default)* survey | Deep, passage-grounded survey → claim map, packet, BibTeX | this file, "Pipeline" below |
| `corpus-prefetch` | One broad shallow sweep (abstracts only) → hashed corpus manifest | `corpus-prefetch.md` |

`corpus-prefetch` is a **precondition for algorithm discussion**, not a survey:
`algo-brainstorm`'s `gap-analysis`, `formalize`, and `ideate` refuse to start
without a corpus manifest for the topic. It produces no survey, no claim map,
and no evidence packet, and satisfies no lifecycle gate. Its records are
abstract-scope alarm evidence only — see the two-fidelity rule in
`shared/prompts/evidence_grounding.md`. Run it once per topic, then the deep
pipeline below when the topic needs grounded claims.

## Pipeline

1. **Load state and vault.** Derive/load `.research-state/<slug>.md`, initialize
   or validate its `evidence_vault` and `evidence_topic_id`, and migrate legacy
   survey/`.bib` paths additively when needed. Do not accept legacy artifacts as
   a current evidence packet.

2. **Generate perspectives and query seeds.** Produce 3–5 perspectives using
   `perspectives.md`. Parametric recall, user suggestions, and panel outputs are
   hypotheses/query seeds only. Persist every executed query-run, including
   zero-result runs.

3. **Query the vault first.** Search canonical works, source versions, claims,
   and prior packets for every perspective. Record coverage and unresolved
   queries before contacting external services.

4. **Retrieve externally for coverage gaps.** For unresolved queries, run the
   bundled arXiv, Semantic Scholar, and OpenAlex search scripts in parallel and
   retain the byte-exact raw response for **each query × provider** (plus a
   perspective aggregation only as a derived file). Compute its bare SHA-256.
   Run each dependency-bearing provider script from the user's project cwd as:

   ```bash
   uv run --project "$PLUGIN_ROOT" python \
     "$PLUGIN_ROOT/skills/literature-explorer/scripts/search_<provider>.py" \
     "$QUERY" --max 25
   ```

   Here `<provider>` is `arxiv`, `semantic_scholar`, or `openalex`; use each
   script's `--help` rather than guessing additional flags.
   An installed `literature-review-ml` skill may replace this external step, but
   not the vault-first or persistence rules.

5. **Persist provenance before filtering/ranking.** Identity-resolve and ingest
   **every raw observation's work** first—not only top/selected/deduplicated
   items—using the absolute evidence CLI resolved per
   `shared/prompts/evidence_grounding.md`:

   ```bash
   python3 "$EVIDENCECTL" work ingest --vault "$VAULT" \
     --title "<title>" --author "<author>" --year <year> \
     --doi "<doi-if-any>" --arxiv-id "<id-if-any>" --url "<url-if-any>" \
     --topic "$TOPIC_ID"
   ```

   Omit absent optional flags; never pass placeholder text as metadata.

   Immediately after each query/provider, persist its full provider order with
   one repeated `--result-work` per canonical work ID, the raw-response hash,
   execution time, filters, and an ordered observation array. Each observation
   includes at least `provider_id`, `rank`, `query`, and resolved `work_id`;
   retain `included_in_rank_view` and `exclusion_reason` so downstream filtering
   is auditable:

   ```bash
   python3 "$EVIDENCECTL" query add --vault "$VAULT" \
     --topic "$TOPIC_ID" --query "$QUERY" --provider "$PROVIDER" \
     --result-work "$WORK_ID_1" --result-work "$WORK_ID_2" \
     --raw-response-hash "$RAW_SHA256" \
     --observations-json "$ORDERED_OBSERVATIONS_JSON" \
     --executed-at "$EXECUTED_AT"
   ```

   Use `--filters-json` when filters were applied. A zero-result/no-result query
   still gets a query-run with empty ordered results/observations. Never rebuild
   this provenance from a ranked view.

6. **Deduplicate and rank as a downstream view.** Run, never simulate:

   ```bash
   python3 "$PLUGIN_ROOT/skills/literature-explorer/scripts/dedupe_rank.py" \
     <perspective>.jsonl ... --out ranked.jsonl --md ranked.md --top 60
   ```

   Paste its `merged N -> M unique papers` summary. This output chooses a reading
   order only; it must not overwrite query runs, provider ranks, raw hashes,
   observations, or exclusions. Search metadata/abstracts establish discovery
   only. Acquire/ingest immutable primary source versions and inspect passages
   before using `supports` + `verified` for a substantive claim.

7. **Ground and synthesize.** Build atomic claims, claim-to-passage evidence
   links, and a hierarchical outline. Run `expert-dialogue.md` against those
   bounded links. A new near-neighbor or open question becomes a query and loops
   back through vault-first retrieval before it enters the synthesis.

8. **Write the claim-map gate.** Emit `docs/claim-map-<slug>.md` with each
   problem/limitation/method/theory/experiment/novelty claim ID, evidence-link
   IDs, unresolved query-run IDs, and disposition. Hash it and update
   `lifecycle_gates.atomic_claim_map` with `status: pass`; set
   `research_phase: atomic_claim_map`. Follow
   `shared/prompts/research_lifecycle.md`; unverified claims stay queued.

9. **Freeze and emit.** Freeze/validate a topic packet, or a candidate-specific
   packet when exploration was requested for a candidate. Emit:
   - `docs/survey-<slug>.md` from packet-grounded claims;
   - `refs/<slug>.bib` via deterministic export, never model generation or hand edit:

     ```bash
     python3 "$EVIDENCECTL" export bibtex --vault "$VAULT" \
       --topic "$TOPIC_ID" --out "refs/<slug>.bib"
     ```

   - state pointers/hashes (`evidence_*`) plus legacy `literature:` and
     `citations:` paths and `citations_view_hash` for compatibility.

Advance `stage` only with user confirmation.

## Output discipline

- Follow `shared/prompts/execution_discipline.md`; scripts run for real and
  skips are explicit.
- Every substantive literature claim must trace to an atomic claim and stable
  passage link in the current packet. A BibTeX key alone is insufficient.
- Mark recent preprints (≤6 months) `[PREPRINT]`; source-version pinning is
  mandatory because they may change.
- Keep the survey body near 3000 words. Preserve unresolved items as persisted
  queries, not confident prose.

## Files

- `perspectives.md` — perspective archetypes and query-generation template.
- `corpus-prefetch.md` — broad shallow sweep across the four mandatory axes;
  emits `docs/corpus-manifest-<slug>.md`.
- `expert-dialogue.md` — bounded two-persona critique protocol.
- `scripts/search_{arxiv,semantic_scholar,openalex}.py` — external discovery;
  run with the `uv run --project "$PLUGIN_ROOT" ...` form above.
- `scripts/dedupe_rank.py` — deterministic stdlib merge/rank; run with the
  absolute `python3 "$PLUGIN_ROOT/..."` form above.
- `scripts/search_openreview.py` — dependency-bearing venue intelligence; run
  with `uv run --project "$PLUGIN_ROOT" python
  "$PLUGIN_ROOT/skills/literature-explorer/scripts/search_openreview.py"`;
  not part of the survey
  retrieval trio.

## Exit checklist

- [ ] 3–5 perspectives with ≤40% query overlap; all executed queries persisted.
- [ ] Vault queried first; external retrieval used only for recorded gaps.
- [ ] Every query×provider raw response was hashed; every raw work was
      identity-resolved/ingested before ranking; ordered work IDs,
      provider/rank/query observations, filters, and exclusions were persisted.
- [ ] Retrieval ran with real output and `dedupe_rank.py` summary was pasted.
- [ ] Canonical works and immutable source versions were persisted.
- [ ] Every emitted substantive claim has a passage-level evidence link;
      abstracts are not marked `verified`, `supports`, or `contradicts`.
- [ ] New gaps/near-neighbors were retrieved or remain explicitly unresolved.
- [ ] Hashed claim-map artifact written; intake/claim-map lifecycle gates updated.
- [ ] Packet validates and is current; its ID/hash/status are in state.
- [ ] Deterministic `export bibtex` ran from canonical works (no model/hand
      BibTeX); survey/view were written and preprints flagged.
