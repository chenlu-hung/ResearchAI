# Research State Schema

Every project this plugin touches keeps a single state file at:

```
<working-dir>/.research-state/<topic-slug>.md
```

This file is the **workflow control plane** that connects literature exploration,
algorithm brainstorming, and paper writing across sessions. Canonical literature
evidence lives in the evidence vault described by
`shared/prompts/evidence_grounding.md`; state stores stable IDs and snapshot
hashes, never a second copy of the evidence records. Each skill reads state and
the referenced evidence packet on entry and updates only its own fields on exit.

## File Format

YAML frontmatter (machine-readable) + markdown body (human-readable notes).
The frontmatter is authoritative; the body is for narrative.

### Frontmatter

```yaml
---
topic: "Conformal prediction under covariate shift"
slug: conformal-covariate-shift
venue_target: NeurIPS 2026
created: 2026-05-17
updated: 2026-05-17

entry_mode: new
# new | retrofit
# `retrofit` means the project was entered from an existing draft (or a draft
# plus a decision/reviews file) via `skills/research-conductor/bootstrap.md`
# section 0. It changes routing, never evidence discipline. Absent = `new`.

retrofit_source:            # present only when entry_mode: retrofit
  draft: paper/main.tex
  draft_hash: "<64-char-lowercase-sha256-hex>"
  reviews: review.md        # omit when no decision/reviews file was supplied
  reviews_hash: "<64-char-lowercase-sha256-hex>"
  imported_on: 2026-05-17

stage: toy
# one of:
#   explore | gap | formalize | ideate | novelty | theory
#   | toy | ablation | red-team | outline | drafting | revision | final

# `stage` is a backward-compatible routing label. Scientific advancement is
# controlled by `research_phase` + validated lifecycle gates.
research_phase: experiment_contract
# intake_import | atomic_claim_map | prior_art_audit | method_frozen
# | positioning_skeleton | experiment_contract | protocol_frozen
# | results_ingested | evidence_audited | results_red_team | drafting
# | scientific_review | submission | final

lifecycle_gates:
  # status ∈ missing | backfill_needed | draft | frozen | pass | conditional
  #          | stale | invalidated | fail | cannot_determine | not_applicable
  # `backfill_needed` is the retrofit-entry status: it blocks advancement like
  # `missing`, but routes to the retrofit backfill sequence instead of a hard
  # stop. It may carry `retrofit: true` (artifact reconstructed from the paper,
  # evidence pending) and `missing: [...]` (exactly what is absent).
  # See `shared/prompts/research_lifecycle.md`.
  intake_import:
    status: pass
    topic_id: topic-conformal-covariate-shift
    imported_source_version_ids: [source-...]
    unresolved_query_run_ids: []
  atomic_claim_map:
    status: pass
    artifact: docs/claim-map-conformal-covariate-shift.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    claim_ids: [claim-novelty-1, claim-limit-1]
  prior_art_audit:
    status: pass
    candidate_id: candidate-cand-1
    evidence_packet_id: "<packet-id-returned-by-evidencectl>"
    evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
    audit_id: "<audit-id-returned-by-evidencectl>"
  method_freeze:
    status: frozen
    artifact: docs/method-freeze-conformal-covariate-shift.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    candidate_id: candidate-cand-1
    novelty_verdict: novel   # novel | incremental (accepted); never subsumed/absent
    component_hash: "<64-char-lowercase-sha256-hex>"
    objective_hash: "<64-char-lowercase-sha256-hex>"
    data_regime_hash: "<64-char-lowercase-sha256-hex>"
    claim_ids: [claim-novelty-1]
  positioning_skeleton:
    status: pass
    artifact: paper/skeleton/
    artifact_hash: "<64-char-lowercase-sha256-hex>"  # directory hash, see lifecycle
    method_freeze_hash: "<64-char-lowercase-sha256-hex>"
    spine_primary: claim-novelty-1
    promised_tables: [tab-main, tab-ablation]
  experiment_contract:
    status: draft
    artifact: docs/experiment-contract-conformal-covariate-shift.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    method_freeze_hash: "<64-char-lowercase-sha256-hex>"
  protocol_freeze:
    status: missing
    artifact: docs/protocol-freeze-conformal-covariate-shift.md
    artifact_hash: null
    experiment_contract_hash: "<64-char-lowercase-sha256-hex>"
  results_ingested:
    status: missing
    manifest: results/conformal-covariate-shift/manifest.json
    manifest_hash: null
    protocol_hash: null
  evidence_audited:
    status: missing
    artifact: docs/evidence-audit-conformal-covariate-shift.md
    artifact_hash: null
    audit_id: null
    result_manifest_hash: null
  results_red_team:
    status: missing
    artifact: .research-state/conformal-covariate-shift-results-red-team.md
    artifact_hash: null
    blocking: null
  draft:
    status: missing
    artifact: paper/main.tex
    artifact_hash: null
  scientific_review:
    status: missing
    artifact: .research-state/conformal-covariate-shift-scientific-review.md
    artifact_hash: null
    draft_hash: null
    verdict: null
  submission:
    status: missing
    artifact: .research-state/conformal-covariate-shift-submission-check.md
    artifact_hash: null

# --- contribution spine (frozen by `novelty-check` at method freeze) ---
spine:
  primary: claim-novelty-1        # exactly one; the paper's subject
  supporting: [claim-limit-1]     # 0–3 claim IDs, all from the claim map
  frozen_with: docs/method-freeze-conformal-covariate-shift.md
# Binds downstream: experiments map to spine claims, outline bullets tag one,
# positioning-skeleton writes contribution statements from it, self-review's
# focus audit checks the drafted paper still argues `primary`. Changing the
# spine is a method change and invalidates the experiment contract onward.

# --- post-mortems (filled by paper-writer `post-mortem`) ----------
post_mortems:          # APPEND-ONLY: a second rejection appends, never overwrites
  - artifact: docs/post-mortem-conformal-covariate-shift-2026-08-14.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
    venue: NeurIPS 2026
    decision: reject
    received: 2026-08-14
    reviews_source: review.md
    reviews_source_hash: "<64-char-lowercase-sha256-hex>"
    objection_count: 11
    gates_implicated: [prior_art_audit, experiment_contract]
    reverted_phase_to: prior_art_audit
# Written after `final`/rejection or on a retrofit entry. The mode sets
# `research_phase` back to `reverted_phase_to` — the earliest gate any finding
# invalidates — and marks that gate and everything downstream stale. See rule 13
# below and `shared/prompts/research_lifecycle.md`.

# --- corpus (filled by literature-explorer `corpus-prefetch`) -----
corpus_manifest:
  artifact: docs/corpus-manifest-conformal-covariate-shift.md
  artifact_hash: "<64-char-lowercase-sha256-hex>"
  gathered: 2026-05-17          # date of the sweep; >6 months old ⇒ refresh
  axes: [application_field, mathematical_skeleton, adjacent_fields, historical]
  works_total: 214
# Not a lifecycle gate — a precondition for algo-brainstorm's discussion modes
# (`gap-analysis`, `formalize`, `ideate`) and the source for its novelty reflex.
# Its records are abstract-scope alarm evidence and can never ground a claim.
# Ownership exception to rule 2: `literature-explorer corpus-prefetch` creates
# this block; algo-brainstorm's drift detector may APPEND an Extensions row to
# the artifact and update `artifact_hash`, and nothing else.

# --- artifacts ----------------------------------------------------
literature: docs/survey-conformal-covariate-shift.md
citations:  refs/conformal-covariate-shift.bib
citations_view_hash: "<64-char-lowercase-sha256-hex>" # deterministic export
algorithm_card: docs/algo-card-v3.md      # rolling, may be overwritten
draft: paper/main.tex                      # once paper-writer is engaged
reviewer_intel: .research-state/conformal-covariate-shift-reviewer-intel.md
  # optional; topic-scoped review dossier (shared/prompts/reviewer_intel.md)

# --- evidence control plane ---------------------------------------
evidence_vault: "/absolute/path/to/Obsidian Research Vault"
evidence_topic_id: topic-conformal-covariate-shift
evidence_packet_id: "<packet-id-returned-by-evidencectl>"
evidence_packet_hash: "<64-char-lowercase-sha256-hex>" # canonical snapshot_hash
evidence_packet_status: current       # missing | current | stale
evidence_audit_id: "<audit-id-returned-by-evidencectl>"
evidence_packet_basis:
  candidate_id: candidate-cand-1
  component_hash: "<64-char-lowercase-sha256-hex>"  # primitives/components
  objective_hash: "<64-char-lowercase-sha256-hex>"  # objective/estimand
  data_regime_hash: "<64-char-lowercase-sha256-hex>" # assumptions + evaluation regime
  claim_ids: [claim-novelty-1, claim-limit-1]
  query_run_ids: [query-...]
  work_ids: [work-...]
  source_version_ids: [source-...]
  passage_ids: [passage-...]
  dataset_ids: [dataset-...]
# The vault packet is canonical (`frozen` | `invalidated`). State maps a
# validated frozen packet to `current`, and invalidated/mismatched to `stale`.
# These fields are a validated pointer/cache.
# Any material basis change sets status: stale until a replacement is frozen.

# --- formalization (filled by algo-brainstorm `formalize` mode) ---
formalization:
  estimand: "P(Y ∈ C(X) | X ~ Q_target) ≥ 1-α"
  loss: "miscoverage + λ · |C(X)|"
  assumptions:
    - A1: "joint density ratio dQ/dP is bounded and known up to estimation"
    - A2: "exchangeability fails; covariate shift only (no label shift)"
  nuisance: ["density ratio w(x) = dQ/dP"]
  regularity: ["w(x) bounded above by M < ∞"]

# --- candidates (filled by `ideate`) ------------------------------
candidates:
  - id: cand-1
    evidence_candidate_id: candidate-cand-1
    name: "Weighted split conformal with cross-fitted density ratio"
    core_idea: "Reweight calibration scores by estimated w(x) with cross-fitting"
    primitives: ["weighted quantile", "DML cross-fitting"]
    objective: "finite-sample target coverage with efficient set size"
    data_regime: "covariate shift; unknown bounded density ratio"
    component_hash: "<64-char-lowercase-sha256-hex>"
    objective_hash: "<64-char-lowercase-sha256-hex>"
    data_regime_hash: "<64-char-lowercase-sha256-hex>"
    claim_ids: [claim-novelty-1, claim-limit-1]
    evidence_packet_id: "<packet-id-returned-by-evidencectl>"
    evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
    evidence_packet_status: current   # missing | current | stale
    motivation: theoretical
    novelty: novel        # novel | incremental | subsumed
      # Verdicts are set only by `novelty-check`, and these three values are the
      # complete verdict vocabulary — any other string is a corrupt gate.
      # Before a verdict exists the field is either ABSENT or carries the
      # placeholder `pending` written by `ideate`. `pending` is not a verdict:
      # it never satisfies a gate and never clears a hard stop.
    incremental_accepted: true
    incremental_acceptance_rationale: "User accepts the smaller delta: the
      cross-fitting variant is the paper's only defensible claim."
      # Both fields are REQUIRED to freeze a candidate whose verdict is
      # `incremental`. `subsumed` and a missing verdict can never freeze.
    status: chosen
  - id: cand-2
    name: ...
    status: dropped
    drop_reason: "Reviewed Tibshirani 2019 — equivalent up to estimator choice"

# --- contribution claims (filled by `novelty-check`) --------------
key_claims:
  - claim_id: claim-novelty-1
    claim: "First finite-sample marginal coverage guarantee under unknown w(x) without exchangeability."
    evidence_link_ids: [evidence-tibshirani-p4, evidence-lei-p2]
    evidence_scope: full_text  # metadata | abstract | full_text | supplement | dataset
    supporting_refs: [tibshirani2019conformal, lei2018distfree]
    audit_status: pending    # pending | verified | mismatched | fabricated

# --- theory targets (filled by `theory-scoping`) ------------------
theory_targets:
  - kind: coverage
    statement: "P(Y ∈ Ĉ(X)) ≥ 1 - α - O(n^{-1/4})"
    proof_technique: "DML + sample-splitting"
    must_have: true
  - kind: efficiency
    statement: "E[|Ĉ(X)|] → E[|C*(X)|] as n→∞"
    must_have: false

# --- interview answers (filled by grill protocol) -----------------
interview_ideate:
  asked_at: 2026-05-21
  primitive: "conformal"
  contribution_type: theoretical
  constraints: "must work without known shift ratio"
  diversity: max_diversity
  follow_ups: []   # list of {question, answer} pairs for any dynamic follow-ups

interview_toy_design:
  asked_at: 2026-05-22
  # `toy-design`'s benchmark-design decision table: the user's follow/deviate
  # ruling per experimental-design choice, adjudicated via grill_protocol.md.
  rulings:
    - choice: "Benchmark set"
      convention: "3 standard + 1 hard"
      ours: "2 standard"
      decision: deviate
      rationale: "compute budget; hard case covered by the toy"
    - choice: "Seeds"
      convention: "5"
      ours: "5"
      decision: follow
      rationale: "venue minimum"
  follow_ups: []

interview_drafting:
  asked_at: 2026-05-21
  contribution_claim: "First finite-sample marginal coverage guarantee under unknown w(x) without exchangeability."
  reader: applied_ml_practitioners
  tone: formal_proof_heavy
  proactive_weaknesses:
    - "If w(x) estimation error is heavy-tailed, weighted quantile is not consistent."
  follow_ups: []

# --- red team findings (filled by `red-team`) --------------------
red_team_findings:
  - finding: "If w(x) estimation error is heavy-tailed, weighted quantile is not consistent."
    severity: high
    mitigation: "Truncate w(x) at quantile-based threshold; report sensitivity."

open_questions:
  - "Does the cross-fitting still work when w is estimated via NN?"
  - "Is there a label-shift extension?"
---
```

### Body (free-form notes)

After the frontmatter, append timestamped narrative entries. Skills append
new entries; they do not rewrite history.

```markdown
## 2026-05-17 — explore

(narrative produced by literature-explorer)

## 2026-05-17 — gap-analysis

(narrative produced by algo-brainstorm)
```

## Rules for Skills

`research_phase` maps to `lifecycle_gates` keys as follows; conductors must use
this table rather than guessing grammatical variants:

| Phase | Gate key |
|---|---|
| `intake_import` | `intake_import` |
| `atomic_claim_map` | `atomic_claim_map` |
| `prior_art_audit` | `prior_art_audit` |
| `method_frozen` | `method_freeze` |
| `positioning_skeleton` | `positioning_skeleton` |
| `experiment_contract` | `experiment_contract` |
| `protocol_frozen` | `protocol_freeze` |
| `results_ingested` | `results_ingested` |
| `evidence_audited` | `evidence_audited` |
| `results_red_team` | `results_red_team` |
| `drafting` | `draft` |
| `scientific_review` | `scientific_review` |
| `submission` | `submission` |
| `final` | all prior gates |

1. **Read before doing**: every skill must read this file on entry. If a needed
   prior stage is empty (e.g., `paper-writer` invoked but `formalization` is
   blank), warn the user and offer to backfill.
2. **Atomic updates**: update only your own section. Never overwrite another
   skill's section without explicit user instruction.
3. **Stage transitions**: only advance `stage` when the user confirms.
4. **No silent deletion**: if dropping a candidate or claim, move it to a
   `dropped:` subsection with `drop_reason`, do not delete.
5. **Cross-references**: `audit_status` on `key_claims` is set by paper-writer's
   `citation-audit` mode; brainstorm modes must not touch it.
6. **Interview answers are append-only and stage-scoped**. Modes that invoke the
   grill protocol (`shared/prompts/grill_protocol.md`) skip the interview iff an
   `interview_<mode>:` block already exists in the frontmatter. Skills must not
   modify interview blocks belonging to other modes. To re-grill, the user
   deletes the block manually or starts a new slug.
7. **Evidence IDs, not duplicated evidence**: work/source/passage contents live
   only in the vault. State records `evidence_*_id`, link IDs, and validated
   snapshot hashes. `literature:` and `citations:` remain supported as legacy or
   generated-view paths, not proof of coverage or support.
8. **Packet freshness is mandatory**: a material change to a candidate's
   primitives/components, objective/estimand, data regime/assumptions, or claim
   text/IDs immediately sets both the candidate and top-level
   `evidence_packet_status` to `stale` and records the reason in the canonical
   vault packet. No evidence-gated stage may proceed until a replacement packet
   is frozen and its hash copied back to state.
9. **Legacy migration is additive**: old state files without evidence fields
   remain readable. On the first evidence-gated action, import their survey and
   bibliography into the vault, backfill source versions and atomic claim links,
   then freeze a packet. Preserve the old fields; never infer `current` merely
   because a `.bib` exists.
10. **Lifecycle gates outrank `stage`**: follow
    `shared/prompts/research_lifecycle.md`. Before advancing, verify referenced
    artifacts exist, recompute their SHA-256 hashes, validate vault IDs/packet
    dependencies, and require the gate's accepted status. A legacy stage is a
    routing hint only and never auto-passes a gate.
11. **Forward invalidation**: when an upstream dependency changes, mark every
    downstream lifecycle gate `stale` according to the lifecycle contract. Do
    not delete old artifacts; retain them for provenance and replace pointers
    only after a new gate passes.
12. **Hash representation**: every present verified content/artifact SHA-256 is
    bare, lowercase, 64-character hexadecimal text with no prefix. A schema-
    declared unknown dataset, provider response, or unverified excerpt hash may
    be empty but cannot satisfy a gate; metadata/abstract discovery fingerprints
    are not byte-content hashes. Compare gate hashes byte-for-byte with their
    canonical records.
13. **`final` is not terminal — the post-final transition**. `research_phase:
    final` may move **backwards** into a revision cycle, and only two things may
    do it: `paper-writer post-mortem`, or an explicit user instruction. The
    post-mortem sets `research_phase` to the earliest gate its findings
    invalidate, marks that gate and everything downstream `stale`, and appends
    to `post_mortems:`. Ordinary forward advancement is unchanged — nothing else
    may leave `final`, and no mode may re-reach `final` without every gate
    revalidating through `submission-check` as usual. Retain the superseded
    artifacts for provenance; a post-mortem never deletes the paper it examines.

## Slug rules

- Lowercase, hyphen-separated
- Derived from topic; max 50 chars
- If collision, append `-v2`, `-v3`
