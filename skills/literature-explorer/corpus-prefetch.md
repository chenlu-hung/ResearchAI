# Mode: corpus-prefetch

**Purpose**: build the **local corpus** that algorithm discussion runs against —
one broad, shallow sweep up front, so `algo-brainstorm`'s novelty reflex can name
a nearest neighbor without touching the network on every turn.

This is a mode of `literature-explorer`, not a separate skill. It reuses the same
scripts, the same vault, and the same persistence rules as the full pipeline in
`SKILL.md`; it differs only in **breadth over depth**. It never produces a
survey, a claim map, or a packet, and it never satisfies an evidence gate.

## Depth contract (read before anything else)

- **Shallow by design**: metadata + abstracts for on the order of **100–300
  works**, ingested as canonical works with source versions at
  `--source-scope abstract`. Do not acquire full text here.
- **Alarm evidence only**: an abstract-scope corpus record can motivate a query
  and raise a warning. It can never be marked `verified`, `supports`, or
  `contradicts`, and can never ground a Same/Different/Δ row, a novelty verdict,
  or a paper sentence. See the two-fidelity rule in
  `shared/prompts/evidence_grounding.md`.
- Everything in `shared/prompts/evidence_grounding.md` still applies: vault
  first, persist every query-run including zero-result runs, no untracked result
  pasted into state or prose.

## Mandatory axes

All four run. An axis with no results is reported as an axis with no results —
it is never dropped.

1. **Application-field axis.** The topic as the user's own field states it. Use
   the standard archetypes in `perspectives.md` (theorist / empiricist /
   methodologist / critic / applied) to generate its query sets.

2. **Mathematical-skeleton axis.** Write the method **domain-free**: strip every
   application noun and field-specific term, leaving objects, operators,
   objective, and regime — e.g. "a ridge-learned linear map aligning PCA latent
   spaces of two related representations". Then search that skeleton
   - **across fields**: at minimum computer vision, signal processing,
     reduced-order modeling, and multivariate statistics, plus any field the
     skeleton's primitives came from; and
   - **across decades, explicitly including pre-2015 classic literature**. A
     provider default that quietly favors recent work is a coverage failure —
     set explicit year windows and record them.

   This axis is the one that catches structural isomorphism, which the
   application-field axis structurally cannot. `novelty-check` step 3 reuses and
   extends it.

3. **Adjacent-fields axis.** The `Adjacent fields` archetype in
   `perspectives.md`, **mandatory here** (it is optional for a normal survey).

4. **Historical axis.** The `Historical` archetype in `perspectives.md`,
   **mandatory here**. Lineage and paradigm shifts, not only the current wave.

The anti-overlap rule in `perspectives.md` applies within an axis, not across
axes: axes are expected to converge on some of the same works, and that
convergence is signal.

## Procedure

1. **Load state and vault.** As `SKILL.md` step 1. Require `evidence_vault` and
   `evidence_topic_id`; initialize them if this is the first run.

2. **Write the axis term lists.** Before retrieving, write out per axis: problem
   formulations, algorithmic primitives, math-skeleton terms, fields, and year
   ranges. These term lists are the manifest's contract — the drift detector in
   `algo-brainstorm` matches new discussion terms against exactly this text, so
   vague terms cost coverage later.

3. **Query the vault first**, per axis, and persist every run.

4. **Retrieve externally, broad and shallow.** Run the bundled providers in
   parallel per query, from the user's project cwd:

   ```bash
   uv run --project "$PLUGIN_ROOT" python \
     "$PLUGIN_ROOT/skills/literature-explorer/scripts/search_<provider>.py" \
     "$QUERY" --max 50
   ```

   `<provider>` is `arxiv`, `semantic_scholar`, or `openalex`. Retain the
   byte-exact raw response per query × provider and compute its bare SHA-256.

5. **Persist provenance before any filtering.** Identity-resolve and ingest
   **every** raw observation's work — not just the interesting ones; a corpus
   whose boring half was dropped cannot answer "is anything close to this?":

   ```bash
   python3 "$EVIDENCECTL" work ingest --vault "$VAULT" \
     --title "<title>" --author "<author>" --year <year> \
     --doi "<doi-if-any>" --arxiv-id "<id-if-any>" --url "<url-if-any>" \
     --topic "$TOPIC_ID" --source-scope abstract
   ```

   Then persist each query × provider run with its ordered work IDs, raw-response
   hash, observations, and filters, exactly as `SKILL.md` step 5 requires.

6. **Count and report per axis.** Works retrieved, works new to the vault, year
   span actually covered. If the math-skeleton axis returned nothing before 2015,
   say so explicitly and re-query with an explicit pre-2015 window before
   concluding the literature is genuinely recent.

7. **Write the manifest** (below), hash it, and update state.

Do **not** run `dedupe_rank.py`, `expert-dialogue.md`, passage inspection, claim
grounding, packet freezing, survey writing, or BibTeX export here. Those belong
to the full pipeline; running them on abstract-scope records would manufacture
support that does not exist.

## Output: `docs/corpus-manifest-<slug>.md`

Content-hashed. Records:

```markdown
# Corpus manifest — <topic>

gathered: <YYYY-MM-DD>
slug: <slug>
topic_id: <canonical topic ID>
works_total: <N>

## Axis: application-field
- problem formulations: [...]
- primitives: [...]
- fields: [...]
- year range: <from>–<to>
- works: <n>   (new to vault: <m>)
- query runs: [query-..., query-...]

## Axis: mathematical-skeleton
- skeleton: "<domain-free one-sentence statement>"
- math-skeleton terms: [...]
- fields searched: [computer vision, signal processing, reduced-order modeling,
  multivariate statistics, ...]
- year range: <from>–<to>   (pre-2015 coverage: yes/no + what was found)
- works: <n>   (new to vault: <m>)
- query runs: [...]

## Axis: adjacent-fields
...

## Axis: historical
...

## Extensions
| date | trigger | axis | terms added | query runs |
|---|---|---|---|---|
| <YYYY-MM-DD> | out-of-envelope: "<element>" | mathematical-skeleton | [...] | [query-...] |

## Unresolved
- <queries that returned nothing or failed, with provider and date>
```

The `Extensions` table is appended by `algo-brainstorm`'s drift detector when a
discussion element falls outside the covered axes; append rows, never rewrite
history. Recompute the hash and update state on every extension.

## State update

```yaml
corpus_manifest:
  artifact: docs/corpus-manifest-<slug>.md
  artifact_hash: "<64-char-lowercase-sha256-hex>"
  gathered: <YYYY-MM-DD>
  axes: [application_field, mathematical_skeleton, adjacent_fields, historical]
  works_total: <N>
```

Append a one-paragraph summary under `## <date> — corpus-prefetch`. Do not touch
`lifecycle_gates`, `evidence_packet_*`, `literature:`, or `citations:` — this
mode owns none of them, and the corpus manifest is not a lifecycle gate.

## Refresh

- **Drift** (during discussion): `algo-brainstorm` extends the manifest in place
  per its novelty reflex. Targeted, immediate, one axis.
- **Staleness**: a manifest whose `gathered:` date is more than **6 months** old
  triggers an incremental refresh of the **recent-work** slice — re-run each
  axis restricted to the window since `gathered:`, append the new works, and
  update `gathered:`. Do not re-run the full sweep; the historical and
  skeleton axes do not decay.
- A material change to the candidate's primitives, objective, or regime is drift,
  not staleness: re-derive the skeleton and extend the skeleton axis.

## Exit checklist

- [ ] All four axes ran; each has an explicit term list, field list, and year range.
- [ ] Math-skeleton axis has a written domain-free skeleton, ≥4 fields, and
      recorded pre-2015 coverage (or an explicit statement that it was queried
      and empty).
- [ ] Adjacent-fields and historical axes ran as mandatory, not optional.
- [ ] Corpus size is in the 100–300 range, or the shortfall is explained per axis.
- [ ] Every query × provider raw response hashed; every raw work identity-resolved
      and ingested before counting; zero-result runs persisted.
- [ ] Source versions are `abstract` scope; nothing was marked `verified`,
      `supports`, or `contradicts`.
- [ ] No survey, packet, claim link, or BibTeX export was produced here.
- [ ] Manifest written and hashed; `corpus_manifest:` pointer/hash/`gathered`
      date in state.
