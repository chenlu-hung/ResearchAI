# Research Lifecycle Contract

This contract sits above the legacy `stage` machine. `stage` remains readable for
backward compatibility and UI routing; `research_phase` plus validated gate
artifacts determine whether the pipeline may advance. A stage name is never
proof that its scientific gate passed.

`research_phase` names the gate currently being satisfied (or just satisfied).
After that gate validates, the conductor advances it to the next ordered value;
it never skips directly to the phase implied by a later legacy `stage`.

Use the phase→gate-key mapping in `shared/research_state.schema.md` exactly.
Notably, phases `results_ingested` and `evidence_audited` use identically named
gate keys; do not invent `results_ingest` or `evidence_audit` variants.

Use `shared/prompts/evidence_grounding.md` for literature evidence. Project
method/experiment/result artifacts live in the project and are content-hashed;
canonical works, passages, claims, methods, datasets, packets, queries, and
audit verdicts live in the user-selected external evidence vault.

## Ordered lifecycle

| `research_phase` | Required gate | Default owner |
|---|---|---|
| `intake_import` | topic/state linked to external vault; legacy sources imported or queued | conductor bootstrap / literature-explorer |
| `atomic_claim_map` | atomic problem, limitation, contribution, and evaluation claims mapped to IDs/links/queries | literature-explorer / gap-analysis / formalize |
| `prior_art_audit` | current candidate packet + audit verdict; nearest prior art pressure complete | ideate / novelty-check |
| `method_frozen` | one chosen candidate; method-freeze artifact, contribution spine, and candidate fingerprint frozen | novelty-check |
| `positioning_skeleton` | intro/related/contributions drafted and empty result-table shells promised, before any run | paper-writer positioning-skeleton |
| `experiment_contract` | claims→datasets→metrics→baselines→decision rules contract, covering every promised table row | toy-design |
| `protocol_frozen` | executable protocol, code/data/environment versions, seeds, and analysis locked | ablation-plan |
| `results_ingested` | real run/result manifest with immutable artifact hashes | external run + conductor validation |
| `evidence_audited` | protocol/result/claim consistency audit passes or is explicitly conditional | red-team preflight |
| `results_red_team` | adversarial review reads actual audited results/deviations; no blocking finding | red-team |
| `drafting` | outline/draft claims trace to literature passages or result artifacts | paper-writer |
| `scientific_review` | scientific self-review + citation/passage audit current for draft hash | self-review / citation-audit |
| `submission` | venue/reproducibility/submission checks pass | submission-check |
| `final` | all prior gates current | conductor |

Theory-only work may mark experiment/protocol/results gates `not_applicable`
only with a persisted rationale, venue fit, proof-artifact paths/hashes, and a
scientific audit of the theorem/proof claims. “No experiments planned” is not a
sufficient rationale at an empirical venue.

## Gate artifact schemas

Research state stores these pointers/hashes under `lifecycle_gates:`. Detailed
content lives in the referenced artifact; do not paste raw evidence or results
into frontmatter.

### Claim map

`docs/claim-map-<slug>.md` records each atomic claim ID, type
(`problem|limitation|method|theory|experiment|novelty`), current evidence-link
IDs, unresolved query-run IDs, and disposition. Unverified claims may remain in
the queue but cannot satisfy a top-gap or contribution gate.

Claims extracted from an existing paper by the retrofit entry route carry
`retrofit: true` and `evidence: pending`. They are the queue, not the answer: a
claim the paper asserts is a claim to be verified.

### Corpus manifest (precondition, not a phase gate)

`docs/corpus-manifest-<slug>.md` is content-hashed and pointed at by
`corpus_manifest:` in state (artifact, hash, `gathered:` date, axes,
`works_total`). It is written by `literature-explorer` in `corpus-prefetch` mode
and extended in place by `algo-brainstorm`'s drift detector.

It sits **outside** the ordered lifecycle: it occupies no `research_phase`, and
its absence never marks a gate `missing`. What it does gate is *discussion* —
`gap-analysis`, `formalize`, and `ideate` refuse to start without it, and a
manifest older than 6 months triggers a recent-work refresh before heavy use.

Its records are abstract-scope. They are **alarm evidence only** and can never
ground a claim, a Same/Different/Δ row, or a verdict; see the two-fidelity rule
in `shared/prompts/evidence_grounding.md`. Recompute its hash whenever the
manifest is extended.

### Method freeze

`docs/method-freeze-<slug>.md` records candidate ID, method IDs, exact
primitives/components, objective/estimand, data regime/assumptions, claim IDs,
their dependency hashes, the validated evidence packet/audit IDs, the
domain-free mathematical skeleton with its queried fields and year coverage,
the compositional-novelty decomposition and its outcome, and the **contribution
spine**. It is
`frozen` only when exactly one candidate is chosen, its prior-art audit is
`pass` or an explicitly user-accepted `conditional`, **and** its novelty verdict
clears the minimum-verdict rule below.

**Contribution spine.** Frozen with the method: **exactly one primary claim** and
**at most three supporting claims**, each named by claim ID from
`docs/claim-map-<slug>.md`, mirrored to `spine:` in state. The spine is what the
paper is about, and it binds downstream:

- every experiment in the experiment contract maps to a spine claim; one that
  serves no spine claim is cut or carries a written one-line justification;
- every outline section bullet tags the spine claim it advances;
- `positioning-skeleton` writes its contribution statements from the spine;
- `self-review`'s focus audit checks that the drafted paper's apparent
  contribution is still the primary claim.

A spine change is a method change: it invalidates the experiment contract and
every downstream gate per the invalidation chain.

**Minimum verdict for freeze.** The verdict vocabulary is exactly
`novel | incremental | subsumed` (`skills/algo-brainstorm/modes/novelty-check.md`).

| Verdict | May freeze? |
|---|---|
| `novel` | yes |
| `incremental` | only with `incremental_accepted: true` **and** a one-line `incremental_acceptance_rationale:` in state |
| `subsumed` | never |
| absent (coverage insufficient, no verdict issued) | never |

Mirror the frozen verdict as `lifecycle_gates.method_freeze.novelty_verdict`.
A gate carrying any other verdict string is corrupt: halt rather than interpret it.

### Positioning skeleton

`paper/skeleton/` holds `intro.tex`, `related.tex`, `contributions.tex`,
`tables/*.tex` (empty shells), and `handoff.md`. Owner:
`skills/paper-writer/modes/positioning-skeleton.md`.

The gate is `pass` only when: contribution statements come one-per-spine-claim
from the frozen spine; every quantitative self-claim in the prose is marked
`[HYPOTHESIS — pending results]`; **no results section exists**; and every
promised table/figure shell has complete headers, method rows, and regimes with
**every numeric cell literally empty**. A filled cell is a fabricated result and
fails the gate.

Its `artifact_hash` is a directory hash: `sha256` over the newline-joined,
lexicographically sorted `<relative-path>:<file-sha256>` lines, trailing newline
included.

This is the one phase that legally precedes results, so `paper-writer`'s
pre-flight exempts **this mode only** from the results-gate requirement.
`outline` and `full-draft` gating is unchanged. `handoff.md`'s promised-row list
is the input spec for the experiment contract below.

### Experiment contract

`docs/experiment-contract-<slug>.md` records:

- method-freeze hash and testable claim IDs;
- dataset IDs/versions and train/calibration/validation/test roles;
- primary/secondary metrics and estimands;
- exact closest-prior, simple, and oracle baselines where applicable;
- comparison unit, seed count, uncertainty/significance analysis;
- success, failure, stopping, exclusion, and missing-data rules;
- compute budget plus expected/smoke-test outcomes written before runs;
- the convention-survey and follow/deviate decision tables, and the
  domain-regime stress row (`skills/algo-brainstorm/modes/toy-design.md`);
- the **parity matrix** and **calibration/adaptation budget** below.

Every empirical claim must map to at least one metric and decision rule. Every
experiment must map to a `spine:` claim or carry a written justification, and
every table/figure row promised in `paper/skeleton/handoff.md` must have an
experiment that fills it.

**Parity matrix** (mandatory). Rows = every compared method, own variants and
baselines. Columns = parameter count, training data, target-resolution labels
consumed, fine-tuning allowed?, adaptation/residual correction?, tuning budget.

For a **claim-bearing comparison** — any comparison cited by a spine claim — an
asymmetric cell **requires an equalized baseline variant**; a written
justification alone is insufficient, because the asymmetry, not the method, may
be producing the gap. For non-claim-bearing side comparisons a recorded
justification may suffice.

**Nonlinear-baseline rule**: a claim about a nonlinear component requires at
least one strong nonlinear alternative as a baseline. A linear strawman alone
fails the contract.

**Calibration/adaptation budget**: record the exact number and provenance of
target-resolution samples/labels each calibration step or adapter consumes,
including whether ground-truth high-resolution labels are required, plus one
budget-response experiment (few-shot → full curve).

### Protocol freeze

`docs/protocol-freeze-<slug>.md` records experiment-contract hash, code commit or
immutable archive hash, environment/lockfile hash, dataset content hashes,
splits, preprocessing, hyperparameter grids/tuning budgets, seeds, analysis
code hash, and expected result-manifest schema. `TBD` in any claim-critical
field blocks `frozen` status. Freeze before any confirmatory run.

### Results manifest

`results/<slug>/manifest.json` is generated by or from real experiment runs:

```json
{
  "schema_version": 1,
  "protocol_hash": "<64-char-lowercase-sha256-hex>",
  "code_version": "commit-or-64-char-sha256-hex",
  "environment_hash": "<64-char-lowercase-sha256-hex>",
  "dataset_versions": [{"dataset_id": "dataset-...", "content_hash": "<64-char-lowercase-sha256-hex>"}],
  "runs": [{
    "run_id": "run-...",
    "seed": 1,
    "status": "complete",
    "method_variant": "ours-full",
    "param_count": 1200000,
    "adaptation": {
      "fine_tuned": false,
      "labels_used": 64,
      "budget": "64 target-resolution labels, ground truth"
    },
    "resolution_direction": "coarse_to_fine",
    "artifacts": [{"uri": "results/...", "content_hash": "<64-char-lowercase-sha256-hex>"}]
  }],
  "created_at": "RFC3339 timestamp"
}
```

`method_variant`, `param_count`, and `adaptation` are required on every run so
that parity and budget coverage are **mechanically checkable** against the
contract's parity matrix rather than argued in prose. `resolution_direction`
(`coarse_to_fine` | `fine_to_coarse`) is required wherever the claims involve a
transfer direction and omitted otherwise.

The manifest must enumerate failed/excluded runs too, with reasons fixed by the
contract. Do not copy large artifacts into the evidence vault; store stable
URIs/paths and hashes. The conductor validates existence, JSON fields, protocol
hash, required run coverage, and artifact hashes. It additionally checks the new
per-run fields **against the frozen contract**: every parity-matrix row has runs,
every claim-bearing asymmetry has its equalized-variant runs present, and the
recorded `adaptation.labels_used` matches the contract's budget. A mismatch is a
gate failure, not a note. It never fabricates or silently fills results.

### Evidence audit and results red team

`docs/evidence-audit-<slug>.md` maps every empirical claim to result artifact,
metric, population/split, estimate/uncertainty, protocol decision rule, and
verdict (`pass|conditional|fail|cannot_determine`). It lists protocol deviations,
missing/failed runs, post-hoc analyses, and literature packet ID/hash. Persist a
canonical `audit_verdict` and mirror its ID in state.

`.research-state/<slug>-results-red-team-<date>.md` must use the audited result
manifest—not expected curves—to attack robustness, leakage, selection,
statistics, compute, negative results, and claim scope. Blocking findings stop
drafting; changing the method/claims/protocol invalidates downstream gates.

### Scientific review

`.research-state/<slug>-scientific-review-<date>.md` is a composite artifact.
First, `self-review` records the draft hash, method/protocol/result/evidence-audit
hashes, every major scientific objection and disposition, and a
`conditional`/`fail` verdict. Then `citation-audit` verifies canonical metadata
and passage support, appends its artifact IDs/verdict, and may promote the gate
to `pass`. Venue-style review alone is insufficient; a clean citation audit
alone is also insufficient.

## Validation and invalidation

Before each hop, the conductor must:

1. re-read state and the lifecycle contract;
2. verify every required artifact exists and is non-empty;
3. recompute SHA-256 hashes and compare them with state;
4. validate referenced vault records/packet dependency hashes with the bundled
   evidence-store tooling; and
5. refuse advancement on `missing`, `backfill_needed`, `draft`, `stale`,
   `invalidated`, `fail`, or `cannot_determine` gates.

### `backfill_needed`

A gate status used by the retrofit entry route
(`skills/research-conductor/bootstrap.md`, section 5). It means: an artifact was
reconstructed from an existing paper, or is known to be absent with its gap
enumerated, and the gate's owning mode has not yet run.

- It **blocks advancement exactly like `missing`** — nothing downstream may
  proceed, and it never satisfies a dependency hash.
- It differs from `missing` in what the conductor does next: `missing` on a
  normal run means run the owner in the usual order; `backfill_needed` means run
  the retrofit routing in `skills/research-conductor/routing.md` — go to the
  **earliest** such gate — rather than hard-stopping for the user.
- Its optional fields are `retrofit: true` (the artifact was reconstructed from
  the paper, evidence pending) and `missing:` (a list naming exactly what is
  absent). A `backfill_needed` gate with neither is malformed.
- It clears only by the owning mode running for real and the gate reaching its
  own accepted status. A retrofit artifact is an input to that mode, never its
  output. Retrofit waives no evidence discipline: backfilled claims need passage
  grounding before the novelty and drafting gates pass.

Every present verified content/artifact hash is stored as bare lowercase
64-character hexadecimal text, without a prefix. Schema-declared unknown
dataset, provider-response, and unverified-excerpt hashes may remain empty but
cannot satisfy a gate. Metadata/abstract discovery fingerprints are never
treated as byte-content hashes.

Invalidation propagates forward:

- primitives/objective/regime/claims change → prior-art packet, method freeze,
  experiment contract, protocol, results, audits, red team, and reviews stale;
- experiment contract changes → protocol and every downstream artifact stale;
- protocol/code/data version changes → results and downstream audits/reviews stale;
- result manifest changes → evidence audit, results red team, draft claim audit,
  and scientific review stale;
- draft changes → scientific review, citation audit, and submission stale.

Cosmetic prose changes that leave scientific claims and draft hash consumers
unchanged may avoid upstream invalidation, but still invalidate review artifacts
that explicitly bind the old draft hash.

## Post-final transition (post-mortem)

`final` is a resting state, not a terminal one. A real rejection re-opens the
pipeline through exactly one sanctioned route:
`skills/paper-writer/modes/post-mortem.md`.

- **When**: after `final`/rejection, or on a retrofit entry
  (`entry_mode: retrofit`) where a decision/reviews file was supplied. Routing
  sends a retrofit-with-reviews here **before** any backfill, because the gate
  attribution decides which gates are worth backfilling.
- **Effect**: the mode sets `research_phase` back to the **earliest gate any
  finding invalidates**, and marks that gate plus every downstream gate `stale`
  by the chain above — a novelty objection returns the project to
  `prior_art_audit`, not to `drafting`. Findings that are all `reviewer-error`
  or `uncatchable` move nothing; the artifact is recorded regardless.
- **Artifact**: `docs/post-mortem-<slug>-<date>.md`, content-hashed, recorded in
  the append-only `post_mortems:` list in state.
- **Constraints**: superseded artifacts are retained for provenance, never
  deleted. Venue-wide lessons route through `venue-calibration` as `unverified`
  single-paper evidence; `shared/venue_profiles.md` is never edited from the
  post-mortem. Re-reaching `final` requires every gate to revalidate through
  `submission-check` exactly as the first time.

## Legacy mapping

For old state without `research_phase`/`lifecycle_gates`, infer the earliest
plausible phase from `stage` only to choose the next migration action:

| Legacy `stage` | Resume no later than |
|---|---|
| `explore|gap|formalize` | `atomic_claim_map` |
| `ideate|novelty|theory` | `prior_art_audit` |
| `toy|ablation` | `experiment_contract` |
| `red-team|outline` | `protocol_frozen` (then require real results/audit unless valid N/A) |
| `drafting|revision|final` | `scientific_review` after backfilling every earlier gate |

Inference never marks a gate passed. Backfill artifacts and hashes additively,
preserve legacy fields, and do not silently advance `stage` or
`research_phase`.
