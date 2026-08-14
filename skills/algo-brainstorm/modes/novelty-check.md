# Mode: novelty-check

**Purpose**: compare each active candidate against passage-grounded prior art
and articulate its exact methodological delta.

## Hard input gate

For every candidate require:

- a canonical candidate ID;
- explicit primitives/components, objective/estimand, data regime/assumptions,
  and atomic claim IDs; and
- a validated `current` candidate-specific evidence packet whose fingerprint
  matches those fields.

Legacy `literature:`/`citations:` paths or a `.bib` alone do not satisfy this
gate. Migrate/import them, ground claims, and freeze a packet first. If a packet
is missing/stale, do the retrieval loop or refuse to issue a novelty verdict.
Follow `shared/prompts/evidence_grounding.md`.

## Procedure

For each active candidate:

1. **Validate identity and freshness.** Recompute/compare the primitives,
   objective, data-regime, and claim basis. Any material change invalidates the
   packet; persist the reason and refresh before continuing.

2. **Find nearest prior art.** Query the vault first for the same problem,
   primitive, objective, assumptions, and claimed delta. Persist each query-run.
   Retrieve externally only for uncovered axes, including recent preprints.
   When cited-by/reference traversal is available, persist those graph searches
   as query-runs too; do not assume a particular search script implements them.

3. **Structural-isomorphism search (mandatory).** Write the candidate as a
   **domain-free mathematical skeleton**: strip every application noun, dataset
   name, and field-specific term, leaving only objects, operators, objective,
   and regime — e.g. "a ridge-learned linear map aligning PCA latent spaces of
   two related representations". Query the vault and then external providers on
   that skeleton **across fields** (at minimum: computer vision, signal
   processing, reduced-order modeling, multivariate statistics, plus any field
   the skeleton's primitives came from) **and across decades, explicitly
   including pre-2015 classic literature**. Reuse and extend the
   math-skeleton axis of `docs/corpus-manifest-<slug>.md`
   (`skills/literature-explorer/corpus-prefetch.md`); persist every run as a
   query-run. Record in the prior-art audit and method-freeze artifacts: the
   skeleton text verbatim, the queried fields, the year coverage per field, and
   every structural query left unresolved. A skeleton match is prior art even
   when no vocabulary overlaps.

4. **Ground comparison claims.** Inspect primary passages and create atomic
   evidence links for what each work actually computes, assumes, and proves.
   Search metadata/abstracts may prioritize reading but cannot support a
   Same/Different/Δ row. Corpus-manifest hits are alarm evidence only
   (`shared/prompts/evidence_grounding.md`, two-fidelity rule): they justify a
   query, never a row or a verdict.

5. **Loop on discoveries.** Every new near-neighbor or competing formulation
   becomes a query. Add its source version and links, invalidate the old packet,
   then freeze/validate a replacement before continuing.

6. **Write a Same/Different/Δ table** from the refreshed packet:

   ```markdown
   | Related work | What's the same | What's different | The Δ | Evidence links |
   |--------------|-----------------|------------------|-------|----------------|
   | work-... | ... | ... | ... | claim-... → evidence-... |
   ```

7. **Classify the delta.** Compare algorithmic primitives, objective/estimand,
   data regime, assumptions, guarantee, and computation. Moving an existing
   method to a new application/domain/dataset is **application novelty only**
   and can never by itself receive a `novel` method verdict.

8. **Compositional-novelty test (mandatory).** When the candidate is a
   composition of standard components, decompose it into its parts and answer,
   per part, "does this already exist?" with grounded evidence; then answer for
   the composition itself: "is the composition non-obvious **and** necessary —
   would the naive combination fail, and why?" Record both answers. A
   composition whose parts all exist and whose glue is routine **cannot receive
   `novel`**; at best it is `incremental`. Naming the composition is not an
   argument for it.

9. **Issue a verdict only after the gate:**
   - `novel` — a material method delta remains after grounded comparison;
   - `incremental` — a real but small method delta remains; or
   - `subsumed` — prior work already implements or proves the claim in essence.

   A `novel` verdict requires at least three grounded closest works and a delta
   against each, a completed structural-isomorphism search (step 3), and a
   passed compositional-novelty test (step 8). “Nothing found” is a retrieval
   failure, not evidence of novelty. If coverage is insufficient, report
   unresolved queries and **issue no verdict** — absence of a verdict is itself
   a blocking state downstream, not a neutral one.

10. **Persist disposition.** Keep subsumed candidates in `dropped:` with a
    passage-grounded `drop_reason`; never delete them. Freeze the final packet and
    write its ID/hash/status into state.

11. **Prior-art audit + method freeze.** Persist a canonical `audit_verdict` for
    the final packet and update `lifecycle_gates.prior_art_audit`. A `conditional`
    verdict needs explicit user acceptance. Require exactly one chosen candidate
    before freezing the method; if several survive, hard-stop for the choice.

    **Minimum verdict for freeze**, checked before anything is written:

    - `novel` — may freeze;
    - `incremental` — may freeze **only** with a persisted
      `incremental_accepted: true` plus a one-line user rationale
      (`incremental_acceptance_rationale:`) in state, obtained from the user in
      this session or already recorded; without both fields, hard-stop;
    - `subsumed` — can **never** freeze; the candidate goes to `dropped:`;
    - no verdict issued (insufficient coverage) — can never freeze; hard-stop
      with the unresolved queries.

    **Freeze the contribution spine.** Before writing the artifact, choose from
    `docs/claim-map-<slug>.md` **exactly one primary claim** and **at most three
    supporting claims**, each named by claim ID — never by prose restatement. The
    spine is what the paper is about; everything downstream binds to it:
    experiments map to spine claims (`toy-design.md`), outline bullets tag the
    spine claim they advance (`paper-writer/modes/outline.md`), and `self-review`
    audits whether the written paper's apparent contribution still matches the
    primary claim. A candidate that cannot name one primary claim is not ready to
    freeze — say so and hard-stop rather than freezing a diffuse spine. More than
    three supporting claims means the paper is two papers; make the user choose.

    Then write/hash `docs/method-freeze-<slug>.md` with the candidate/method IDs,
    primitives/components, objective/estimand, regime/assumptions, claim IDs and
    dependency hashes, the domain-free skeleton text with its queried fields and
    year coverage, the compositional-novelty decomposition and verdict, the
    contribution spine (primary + supporting claim IDs), the recorded novelty
    verdict (plus acceptance rationale when `incremental`), and
    final packet/audit IDs, then set
    `lifecycle_gates.method_freeze.status: frozen`. Follow
    `shared/prompts/research_lifecycle.md`.

## Anti-sycophancy

Always state substantive weaknesses **and** run grounded prior-art pressure
before endorsing a contribution. Weaknesses cannot substitute for prior art.
The intro-ready contribution statement must be traceable sentence-by-sentence
to the final packet.

## Council panel (opt-in)

With `--council`, give members the bounded candidate plus current packet and ask
them to attack the delta. Always include this fixed question verbatim, in
addition to the mode's own attack prompts:

> In what other field has this exact mathematical structure already been done?

Give members the domain-free skeleton from step 3 alongside the candidate so the
question is answerable. Every named work or objection is a hypothesis: persist
it as a query, run vault-first/external retrieval, inspect the passage, refresh
the packet, and only then let it change a verdict. Follow
`shared/prompts/council_panel.md`; no verdict flips on model agreement or say-so.

## State update

```yaml
stage: novelty
candidates:
  - id: cand-1
    evidence_candidate_id: candidate-cand-1
    evidence_packet_id: "<packet-id-returned-by-evidencectl>"
    evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
    evidence_packet_status: current
    novelty: novel          # novel | incremental | subsumed
                            # when no verdict was issued, leave `ideate`'s
                            # `pending` placeholder in place — never invent one
    # required only when novelty: incremental and the candidate is to be frozen
    incremental_accepted: true
    incremental_acceptance_rationale: "<one line, user's own words>"
    structural_skeleton: "<domain-free mathematical skeleton, one sentence>"
    skeleton_fields_queried: ["computer vision", "signal processing", "..."]
    skeleton_year_coverage: "1970–2026"
    compositional_test: non_obvious   # non_obvious | routine_composition
    contribution_statement: "..."
spine:
  primary: claim-novelty-1          # exactly one
  supporting: [claim-limit-1, claim-theory-2]   # 0–3, all from the claim map
  frozen_with: docs/method-freeze-<slug>.md
    closest_prior:
      - work_id: work-...
        claim_ids: [claim-...]
        evidence_link_ids: [evidence-...]
        delta: "..."
key_claims:
  - claim_id: claim-novelty-1
    claim: "..."
    evidence_link_ids: [evidence-...]
    supporting_refs: [generated-bibkey]
    audit_status: pending
lifecycle_gates:
  prior_art_audit:
    status: pass
    candidate_id: candidate-cand-1
    evidence_packet_id: "<packet-id-returned-by-evidencectl>"
    evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
    audit_id: "<audit-id-returned-by-evidencectl>"
  method_freeze:
    status: frozen
    artifact: docs/method-freeze-<slug>.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    candidate_id: candidate-cand-1
    novelty_verdict: novel        # novel | incremental (with acceptance); never subsumed
research_phase: method_frozen
```

`paper-writer citation-audit` later checks rendering metadata and whether each
invoked sentence is supported by these passages; it does not manufacture the
evidence here.

## Exit checklist

- [ ] Exact candidate has a validated current packet; legacy `.bib` alone was rejected.
- [ ] Vault-first retrieval covered primitive, objective, regime, claim, and recent work.
- [ ] Domain-free mathematical skeleton written verbatim into the prior-art
      audit and method-freeze artifacts.
- [ ] Cross-field and pre-2015 coverage recorded per queried field; unresolved
      structural queries listed, not silently dropped.
- [ ] Compositional-novelty test run: per-component existence answered and the
      composition judged non-obvious **and** necessary, or `novel` refused.
- [ ] Every comparison row has primary-passage evidence links; no row rests on a
      corpus-manifest hit alone.
- [ ] New near-neighbors triggered query/link/re-freeze before the verdict.
- [ ] `novel` has ≥3 grounded closest works and explicit deltas.
- [ ] Application-only change was not labeled method novelty.
- [ ] Subsumed candidates were moved, not deleted, with grounded reasons.
- [ ] Panel items changed results only after evidence verification; the fixed
      cross-field structure question was asked when `--council` ran.
- [ ] Final packet ID/hash/status and claim/link IDs were written to state.
- [ ] Canonical prior-art audit persisted; conditional status explicitly accepted.
- [ ] Contribution spine frozen: exactly one primary claim ID and ≤3 supporting
      claim IDs, all drawn from the claim map, written to `spine:` and into the
      method-freeze artifact.
- [ ] Method freeze cleared the minimum-verdict rule: `novel`, or `incremental`
      with persisted `incremental_accepted: true` + rationale. `subsumed` or
      no-verdict hard-stopped instead of freezing.
- [ ] Exactly one chosen candidate has a hashed method-freeze artifact, or the
      mode hard-stopped for selection.
