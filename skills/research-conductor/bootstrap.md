# Conductor bootstrap

Turn a fresh idea, or an existing paper with no state, into a
`.research-state/<slug>.md` plus a starting stage, then hand back to the
conductor loop. Follow `shared/research_state.schema.md` exactly.

## 0. Entry mode

Decide once, before anything else, and state the choice in one line:

- **`new`** — the user brings an idea and there is no draft. Run sections 1–4,
  skip section 5.
- **`retrofit`** — the user points at an existing draft (`paper/*.tex`, another
  `.tex`, or a PDF), optionally with a decision/reviews file, and there is no
  `.research-state/<slug>.md`. Run sections 1–4 with the retrofit deltas noted
  there, then run the backfill sequence in section 5.

Retrofit is a **legal entry route, not a shortcut**. It waives no evidence
discipline: backfilled claims still need passage grounding before the novelty
and drafting gates can pass, and a reconstructed artifact is never a passed
gate. Its only privilege is that the pipeline may be entered from the middle
instead of refusing outright.

If a state file already exists, this is not a bootstrap at all — load it and
return to the loop (legacy migration is `shared/prompts/evidence_grounding.md`,
not this file).

## 1. Topic + slug

- `topic` = the idea, cleaned into a noun phrase. On retrofit, derive it from the
  draft's title/abstract instead of asking.
- `slug` per the schema "Slug rules": lowercase, hyphen-separated, derived from the
  topic, ≤ 50 chars. On collision append `-v2`, `-v3`.
- If `.research-state/<slug>.md` **already exists**, this is not a new idea — load
  it and return to the loop. Do **not** bootstrap over it.

## 2. One framing question: venue

On **retrofit**, read `venue_target` off the draft (template, `\documentclass`,
submission footer) or the decision file and state it in one line; ask only when
the draft is silent.

Ask `venue_target` once via the host's interactive question mechanism
(recommended option first, per `shared/prompts/grill_protocol.md`). Options from `shared/venue_profiles.md`
(NeurIPS / ICML / JMLR / AISTATS / Annals of Statistics). Via Other the user
can answer "decide later" → set `venue_target: TBD`, or name an unprofiled
venue → set it verbatim and note in one line that `outline` will require
run `paper-writer` in `venue-calibration` mode first
(`shared/prompts/venue_calibration.md`).

Do **not** ask anything else here. In particular do not ask the
empirical-vs-theoretical question — `ideate`'s grill (`interview_ideate`) captures
`contribution_type`, and routing only needs it later at the `theory` stage.
Pre-asking another mode's question violates `grill_protocol.md`.

## 3. Choose the start stage

- **Default `explore`** — a fresh topic. Builds the canonical topic evidence
  base used by later candidate packets.
- **`gap` instead** — only when the idea is explicitly a refinement or critique of
  a **named** method or paper (e.g. "fix the exchangeability assumption in split
  conformal"). `gap-analysis` can run on it directly. `explore` still runs before
  `novelty` unless targeted retrieval has already produced a valid candidate
  packet (routing's evidence precondition).
- **Retrofit overrides both.** Set `stage: novelty` and
  `research_phase: prior_art_audit` and let routing.md's retrofit rule pick the
  actual next hop from the `backfill_needed` gates — never infer a late stage
  from the fact that a finished draft exists.

Announce the choice in one line: "Starting at `<stage>` because <reason>."

## 4. Initialize evidence + write state

Resolve the user's external Obsidian vault root from existing configuration; if
none is configured, ask once for its absolute path. Never silently create a
project-local `.evidence` vault. Use the bundled evidence-store workflow to
initialize/validate that root and create the canonical topic record. The vault's
internal `.evidence/` directory is metadata, not the root. This is host-neutral
persisted work; do not depend on a Codex-only or Claude-only API. Keep the
returned topic ID.

Create `.research-state/<slug>.md`:

```yaml
---
topic: "<topic>"
slug: <slug>
venue_target: <venue or TBD>
created: <today>
updated: <today>
entry_mode: new          # new | retrofit
stage: <chosen start>
research_phase: intake_import
evidence_vault: "/absolute/path/to/Obsidian Research Vault"
evidence_topic_id: <canonical topic ID>
evidence_packet_status: missing
lifecycle_gates:
  intake_import:
    status: pass
    topic_id: <canonical topic ID>
    imported_source_version_ids: []
    unresolved_query_run_ids: []
  atomic_claim_map: {status: missing}
  prior_art_audit: {status: missing}
  method_freeze: {status: missing}
  experiment_contract: {status: missing}
  protocol_freeze: {status: missing}
  results_ingested: {status: missing}
  evidence_audited: {status: missing}
  results_red_team: {status: missing}
  draft: {status: missing}
  scientific_review: {status: missing}
  submission: {status: missing}
---
```

Body: a single bootstrap note (`## <today> — bootstrap` + one line). Leave all
mode-owned sections (`formalization:`, `candidates:`, `literature:`, …) **absent**
— the modes fill them. The conductor writes nothing else for the rest of the run.

**Retrofit deltas to the block above** — set `entry_mode: retrofit`, add the
imported pointers, and mark the gates that section 5 will backfill:

```yaml
entry_mode: retrofit
stage: novelty
research_phase: prior_art_audit
retrofit_source:
  draft: paper/main.tex          # or the PDF / .tex the user pointed at
  draft_hash: "<64-char-lowercase-sha256-hex>"
  reviews: review.md             # omit when absent
  reviews_hash: "<64-char-lowercase-sha256-hex>"
  imported_on: <today>
lifecycle_gates:
  intake_import: {status: pass, topic_id: <canonical topic ID>, imported_source_version_ids: [], unresolved_query_run_ids: []}
  atomic_claim_map: {status: backfill_needed, artifact: docs/claim-map-<slug>.md, artifact_hash: null, retrofit: true}
  prior_art_audit: {status: backfill_needed, retrofit: true}
  method_freeze: {status: backfill_needed, artifact: docs/method-freeze-<slug>.md, artifact_hash: null, retrofit: true}
  experiment_contract: {status: backfill_needed, retrofit: true, missing: ["..."]}
  protocol_freeze: {status: backfill_needed, retrofit: true, missing: ["..."]}
  results_ingested: {status: backfill_needed, retrofit: true, missing: ["..."]}
  evidence_audited: {status: missing}
  results_red_team: {status: missing}
  draft: {status: missing, artifact: paper/main.tex, artifact_hash: "<64-char-lowercase-sha256-hex>"}
  scientific_review: {status: missing}
  submission: {status: missing}
```

The `draft` gate stays `missing` even though the file exists: a hash records
what was imported, not that the drafting gate passed.

## 5. Retrofit backfill sequence (retrofit only)

Run these in order, immediately after writing state. Each step produces a real
artifact marked `retrofit: true`; none of them passes a gate.

1. **Claim extraction.** Read the draft's abstract, intro contribution
   statements, theorem statements, and results discussion. Write
   `docs/claim-map-<slug>.md` per the lifecycle contract's claim-map schema,
   with every claim carrying `retrofit: true` and `evidence: pending`. Hash it
   and record the hash; the gate stays `backfill_needed` until each claim has a
   passage-grounded evidence link through the normal loop
   (`shared/prompts/evidence_grounding.md`). A claim the paper asserts is a
   claim to be verified, never a verified claim.

2. **Method-freeze reconstruction.** From the paper's method section, write
   `docs/method-freeze-<slug>.md` with `retrofit: true`, filling
   primitives/components, objective/estimand, and data regime/assumptions
   **from the paper's own description**, and compute the candidate fingerprint
   from that reconstruction. Where the paper is silent, write
   `UNDERSPECIFIED — <what is missing>` rather than inventing a value; the
   fingerprint then covers only what the paper actually states. Status stays
   `backfill_needed`: a reconstruction is not a novelty verdict, and
   `novelty-check` still has to run before the gate can reach `frozen`.

3. **Experiment / protocol / results import.** For each of the three gates, look
   for the real artifact in the project — a result manifest, a protocol or
   experiment description, config/seed files. Import and hash what exists per
   the lifecycle contract's schemas. Where nothing exists, keep the gate
   `backfill_needed` and populate its `missing:` list with **exactly** what is
   absent (e.g. `results/<slug>/manifest.json`, per-run seeds, environment
   hash). Never reconstruct a number, a seed, or a run from the paper's tables:
   a printed table is a claim about results, not a result manifest.

4. **Reviews, if supplied.** Record the decision/reviews file and its hash in
   `retrofit_source`. Do **not** read the reviews closely here — they are
   third-party text needing an injection scan first, and routing.md hands them
   to `paper-writer post-mortem`, which runs before any backfill.

Report the backfill as one table (gate → artifact written → what is still
missing) and hand back.

## 6. Hand back

Return the chosen start stage to the loop. Because that stage's mode has not
produced output yet, the conductor runs it next (per routing's completeness rule),
rather than skipping to its successor.

On **retrofit**, return `entry_mode: retrofit` with the backfill table instead;
routing.md sends the conductor to `paper-writer post-mortem` first when reviews
were supplied, and otherwise to the earliest `backfill_needed` gate.

On resume, lifecycle routing—not the initial stage label—determines every later
advance. Read `shared/prompts/research_lifecycle.md` before the first hop.
