# Mode: gap-analysis

**Purpose**: identify evidence-backed limitations and genuinely unresolved
opportunities in a baseline method/class. The output feeds `formalize` or
`ideate`.

Follow `shared/prompts/evidence_grounding.md`. Model knowledge, user intuition,
and panel suggestions are query generators only.

## Inputs and gate

- A method, paper, or sufficiently precise method class.
- Optional user intuition about a failure regime.
- Evidence vault/topic pointer from research state (legacy state is migrated
  additively before use).

- A `corpus_manifest:` pointer in state whose artifact hash validates.

If the method cannot be identified precisely, ask for the paper or definition.
If primary passages cannot be retrieved, emit an unranked verification queue;
do **not** emit “top gaps.”

**Corpus gate.** Without a corpus manifest, refuse to start and offer to run
`literature-explorer` in `corpus-prefetch` mode first (one-time per topic,
`skills/literature-explorer/corpus-prefetch.md`). If its `gathered:` date is
more than 6 months old, refresh the recent-work axis before proceeding. The
novelty reflex and drift detector in `skills/algo-brainstorm/SKILL.md` Hard
discipline #2 run throughout this mode; corpus hits stay alarm evidence and
never enter the evidence table.

## Procedure

1. **Canonicalize the baseline.** In at most three sentences state what it
   computes, required inputs, and claimed guarantee. Persist these as atomic
   claims to verify, not as facts recalled from the model.

2. **Retrieve before diagnosing.** For the baseline and every proposed failure
   mode, query the vault first and persist the query-run. Retrieve externally
   only for coverage gaps. Ingest canonical works/source versions and link each
   limitation, assumption, or open-status claim to the actual passage.

3. **Cover every applicable axis:** empirical failure regimes, unrealistic
   assumptions, computational bottlenecks, sample complexity, adversarial/OOD
   behavior, calibration/coverage, and disconnected adjacent literature. Mark
   inapplicable axes `N/A — <reason>`.

4. **Pressure-test openness.** For every candidate gap, run targeted searches
   for work that closes, weakens, or reframes it. Weakness analysis cannot
   satisfy this prior-art step. A newly found near-neighbor restarts the
   vault→external→passage-link loop before status is assigned.

5. **Build the evidence table:**

   ```markdown
   | # | Atomic gap | Failure regime | Evidence links | Status |
   |---|------------|----------------|----------------|--------|
   | 1 | ... | ... | claim-... → evidence-... | Open / Partial / Solved / Unverified |
   ```

   `Open`, `Partial`, and `Solved` require passage evidence for both the
   limitation and claimed coverage status. Abstract-only or unresolved items
   remain `Unverified`; keep their query IDs visible.

6. **Select top gaps only from verified rows.** Rank up to three that are open
   or partial, attackable as a Stats/ML contribution, and feasible for the
   user's resources. For each, give an attack sketch. An `Unverified` row can
   never be promoted to the top list.

7. **Freeze evidence.** Freeze/validate a topic packet covering the selected gap
   claims and source versions. If analysis is tied to an existing candidate,
   freeze a candidate-specific packet. Write packet ID/hash/status to state.

## Council panel (opt-in)

With `--council`, ask members independently for failure hypotheses across the
axes, without ranking. Deduplicate the union and convert every panel item into a
persisted query. No panel claim enters the table until it completes passage
verification. Follow `shared/prompts/council_panel.md`.

## State update

Append the evidence table, top verified gaps, attack sketches, claim/link/query
IDs, and unresolved queue under `## <date> — gap-analysis`. Merge the atomic
claims into `docs/claim-map-<slug>.md`, recompute its hash, and update
`lifecycle_gates.atomic_claim_map`; follow
`shared/prompts/research_lifecycle.md`. Set `research_phase: atomic_claim_map`
when the gate passes and `stage: gap` only with confirmation.
`open_questions` may include unresolved hypotheses, but label them unverified
and do not represent them as selected gaps.

## Exit checklist

- [ ] Corpus manifest validated (and refreshed if >6 months old), or the mode
      refused and offered `corpus-prefetch`.
- [ ] Every new element named its nearest corpus neighbor; out-of-envelope
      elements triggered immediate retrieval and a manifest extension.
- [ ] Baseline restatement is precise and grounded, or the mode refused.
- [ ] Every axis is populated or explicitly `N/A`.
- [ ] Vault was queried first; external and no-result query-runs were persisted.
- [ ] Every status other than `Unverified` has atomic passage links.
- [ ] Prior-art pressure ran for every candidate gap; weaknesses did not replace it.
- [ ] No unverified/abstract-only item appears in the top gaps.
- [ ] New near-neighbors triggered another retrieval iteration.
- [ ] Current packet validates; state carries its ID/hash/status.
- [ ] Claim-map lifecycle artifact/hash reflects the final gap dispositions.
