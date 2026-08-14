# Mode: ideate

**Purpose**: generate diverse candidate algorithms from a formalized problem,
then retrieve targeted prior art before ranking or handing them to novelty
review. Generated candidates are speculative until their evidence packets are
current.

## Inputs and grill

Require a non-empty `formalization:` block **and** a `corpus_manifest:` pointer
whose artifact hash validates. Read state before questioning; if the
formalization is absent, refuse and run `formalize`.

**Corpus gate.** Without a corpus manifest, refuse to start and offer to run
`literature-explorer` in `corpus-prefetch` mode first (one-time per topic,
`skills/literature-explorer/corpus-prefetch.md`); refresh the recent-work axis
if its `gathered:` date is more than 6 months old. Every candidate this mode
generates is a new algorithmic component entering the discussion, so the novelty
reflex in `skills/algo-brainstorm/SKILL.md` Hard discipline #2 fires on each
one: name its nearest corpus neighbor before it reaches the pool table, and
treat an out-of-envelope primitive as a retrieval to run now, not at
`novelty-check`. A corpus hit is alarm evidence — it can kill a candidate's
ranking only after step 5's grounded retrieval confirms it.

Then follow `shared/prompts/grill_protocol.md`. Use the host's interactive
question mechanism (not a host-specific API contract), one question at a time:

1. preferred primitive, grounded in `loss:`/`nuisance:`;
2. contribution type (theoretical / empirical / methodological);
3. hard constraints/no-go zones (free form); and
4. diversity target (max diversity / deep dive / mixed).

Persist `interview_ideate:` on confirmation; skip when already present.

## Procedure

1. **Generate a speculative pool.** Produce 3–5 candidates, each with name,
   one-sentence core idea, algorithmic primitive/components, motivation,
   objective/estimand, data regime/assumptions, claimed delta, expected
   trade-off, and cost class. Model or panel output is a hypothesis—not novelty
   evidence.

2. **Enforce diversity.** Normally require ≥1 theoretically motivated and ≥1
   empirically motivated candidate, with no duplicate (primitive, motivation)
   pair. Apply the confirmed deep-dive exception explicitly.

3. **Reject non-contributions.** Drop cosmetic backbone swaps, unjustified
   regularizer/kernel/Bayesian relabels, and “same method on a new
   application/domain/dataset.” The last is an application delta, not method
   novelty, unless a changed primitive/objective/regime creates a defensible
   methodological claim.

4. **Register before searching.** Create a canonical candidate record for each
   survivor. Persist its component/primitives hash, objective/estimand hash,
   data-regime hash, and atomic claim IDs. Mirror only IDs/hashes in research
   state.

5. **Targeted retrieval per candidate.** For “has someone done this?” and “why
   has this not been done?”, generate explicit queries, query the vault first,
   and retrieve externally for remaining gaps. Inspect passages and persist
   prior-art, limitation, and delta links. Weaknesses alone cannot satisfy this
   prior-art pressure.

6. **Loop on near-neighbors.** A new competing primitive, formulation, or gap
   becomes another query. Update claims and repeat retrieval; any material
   candidate change makes its old packet stale.

7. **Freeze before ranking.** Freeze/validate a candidate-specific evidence
   packet for every candidate to be ranked or handed off. If a packet cannot be
   completed, show that candidate only in an **unranked speculative queue** with
   the unresolved queries—it cannot receive `likely_novel`.

8. **Rank grounded candidates.** Output:

   ```markdown
   | # | Name | Primitive | Objective/regime | Motivation | Trade-off | Cost | Packet | Evidence status |
   |---|------|-----------|------------------|------------|-----------|------|--------|-----------------|
   ```

   State what retrieved evidence changed or eliminated. Better two grounded
   candidates than five padded ones.

## Council panel (opt-in)

With `--council`, provide the formalization and interview constraints and take
the union of candidate hypotheses. Apply the same filters, registration,
targeted retrieval, and packet gates to panel and chair candidates. Member
agreement is never prior-art evidence. Follow `shared/prompts/council_panel.md`.

## State update

```yaml
stage: ideate
research_phase: prior_art_audit
candidates:
  - id: cand-1
    evidence_candidate_id: candidate-cand-1
    name: "..."
    core_idea: "..."
    primitives: ["..."]
    objective: "..."
    data_regime: "..."
    component_hash: "<64-char-lowercase-sha256-hex>"
    objective_hash: "<64-char-lowercase-sha256-hex>"
    data_regime_hash: "<64-char-lowercase-sha256-hex>"
    claim_ids: [claim-...]
    evidence_packet_id: packet-...
    evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
    evidence_packet_status: current
    novelty: pending   # placeholder, never a verdict; only novelty-check may
                       # replace it with novel | incremental | subsumed
    status: active
```

Append the ranked table, speculative queue, and retrieval summary under
`## <date> — ideate`. Do not advance to `theory-scoping`; hand current packets
to `novelty-check` next.

## Exit checklist

- [ ] Corpus manifest validated (and refreshed if >6 months old), or the mode
      refused and offered `corpus-prefetch`.
- [ ] Every surviving candidate named its nearest corpus neighbor with a
      one-line same/different statement; out-of-envelope primitives triggered
      immediate retrieval and a manifest extension.
- [ ] No candidate was ranked, promoted, or dropped on a corpus hit alone.
- [ ] Formalization exists; grill ran or its persisted-answer skip was stated.
- [ ] All candidate fields and diversity constraints are satisfied.
- [ ] Cosmetic/application-only deltas were rejected as method novelty.
- [ ] Each survivor was registered with primitives/objective/regime/claim hashes.
- [ ] Vault-first targeted prior-art retrieval ran per survivor.
- [ ] New near-neighbors triggered another retrieval iteration.
- [ ] Only candidates with validated current packets were ranked/handed off.
- [ ] Unresolved candidates are visibly speculative and unranked.
- [ ] State contains canonical IDs/hashes/status, not duplicated evidence.
- [ ] Lifecycle points to `prior_art_audit`; no method-freeze gate was claimed
      before novelty review and candidate selection.
