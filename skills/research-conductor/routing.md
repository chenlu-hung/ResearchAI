# Conductor routing

The `stage → next mode` state machine the conductor follows. Backbone = the
"Typical chain" in `skills/algo-brainstorm/SKILL.md`. Read `stage` from
`.research-state/<slug>.md`; pick the next mode here; load and run its file.

## Primary routing: lifecycle gate → action

Read `shared/prompts/research_lifecycle.md` first. `research_phase` names the
current gate. Verify its artifact/status/hash; if accepted, advance to the next
phase below. If not, run its owner or hard-stop. The legacy `stage` tables later
in this file select a mode within a phase but cannot waive a lifecycle gate.

| `research_phase` | Gate owner / next action | Accepted status |
|---|---|---|
| `intake_import` | bootstrap or `literature-explorer`; link external vault topic and import/queue sources | `pass` |
| `atomic_claim_map` | `literature-explorer` + `gap-analysis`/`formalize`; write hashed claim map | `pass` |
| `prior_art_audit` | `ideate` → `novelty-check`; current candidate packet + canonical audit | `pass`, or user-accepted `conditional` |
| `method_frozen` | `novelty-check` method-freeze handoff; exactly one chosen candidate whose verdict clears the minimum-verdict rule, plus a frozen contribution spine | `frozen` |
| `positioning_skeleton` | `paper-writer positioning-skeleton`; intro/related/contributions from the spine + empty table shells, no results section | `pass` |
| `experiment_contract` | `theory-scoping` + `toy-design`; write claims/metrics/decision-rule contract covering every promised table row | `frozen` or valid `not_applicable` |
| `protocol_frozen` | `ablation-plan`; lock code/data/environment/seeds/analysis before confirmatory runs | `frozen` or valid `not_applicable` |
| `results_ingested` | **external-run hard stop** until manifest exists; conductor validates JSON, protocol and artifact hashes, and the per-run `method_variant`/`param_count`/`adaptation`/`resolution_direction` fields against the contract's parity matrix and calibration budget | `pass` or valid `not_applicable` |
| `evidence_audited` | `red-team` preflight audits claim↔protocol↔result/proof evidence and persists verdict | `pass`, or explicitly accepted `conditional` |
| `results_red_team` | `red-team` reads audited actual results/proofs and deviations | `pass` with `blocking: false` |
| `drafting` | `paper-writer outline` → `full-draft` | `pass` |
| `scientific_review` | `self-review` + `citation-audit`, bound to current draft hash | `pass` |
| `submission` | `submission-check` | `pass` |
| `final` | summarize only after all prior hashes/statuses revalidate; a rejection re-opens the pipeline via `paper-writer post-mortem`, which moves the phase back to the earliest gate its findings invalidate | `pass` |

On the external-run stop, state the exact missing manifest path and schema from
the lifecycle contract. Never generate plausible numbers, mark absent runs
complete, or advance because expected curves look reasonable.

## Stage → mode file

The `--economy` column marks stages the conductor may delegate to a cheaper
implementer subagent — **only** when the conductor was invoked with `--economy`, per
`shared/prompts/model_dispatch.md` (preconditions, brief, acceptance).
Unmarked stages always run inline: they are grill-, verdict-, or
review-bearing, or too small to repay a subagent's overhead.

| `stage` | Skill / mode file | `--economy` |
|---|---|---|
| explore | `literature-explorer` pipeline (its `SKILL.md`) | ✓ |
| *(corpus precondition, no stage)* | `skills/literature-explorer/corpus-prefetch.md` | ✓ |
| gap | `skills/algo-brainstorm/modes/gap-analysis.md` | |
| formalize | `skills/algo-brainstorm/modes/formalize.md` | |
| ideate | `skills/algo-brainstorm/modes/ideate.md` | |
| novelty | `skills/algo-brainstorm/modes/novelty-check.md` | |
| *(positioning gate, no legacy stage)* | `skills/paper-writer/modes/positioning-skeleton.md` | |
| theory | `skills/algo-brainstorm/modes/theory-scoping.md` | |
| toy | `skills/algo-brainstorm/modes/toy-design.md` | |
| ablation | `skills/algo-brainstorm/modes/ablation-plan.md` | |
| red-team | `skills/algo-brainstorm/modes/red-team.md` | |
| outline | `skills/paper-writer/modes/outline.md` | |
| drafting | `skills/paper-writer/modes/{full-draft,self-review,citation-audit}.md` (sub-steps, see below) | full-draft ✓, citation-audit ✓; self-review inline |
| revision | `skills/paper-writer/modes/revision.md` | ✓ |
| *(post-final / retrofit+reviews, no stage)* | `skills/paper-writer/modes/post-mortem.md` | |
| final | — (done; summarize artifacts) | |

## Routing table

| Current `stage` | Next (default) | Branch / loop-back |
|---|---|---|
| *(bootstrap, no state)* | explore | start at `gap` instead if the idea is a refinement of a **named** method (bootstrap decides). Evidence gates still apply. |
| *(bootstrap, no state, existing draft)* | see "Retrofit entry" below | `entry_mode: retrofit`; never route from the fact that a finished draft exists |
| explore | gap | entering `gap` requires a `corpus_manifest:` in state; absent → run `literature-explorer` `corpus-prefetch` first (see below) |
| gap | formalize | same corpus-manifest precondition on entry |
| formalize | ideate | same corpus-manifest precondition on entry |
| ideate | novelty | needs ≥1 live candidate with a validated current candidate packet; grill `interview_ideate` is a hard stop if absent |
| novelty | positioning-skeleton → theory | after method freeze, run `paper-writer positioning-skeleton` (lifecycle gate `positioning_skeleton`) before `theory`/`toy`; its `handoff.md` is the experiment contract's input spec. **halt if the chosen candidate's verdict is `subsumed`, if no verdict was issued (insufficient coverage), or if the verdict is `incremental` without persisted `incremental_accepted: true` + a one-line user rationale.** Verdicts are exactly `novel \| incremental \| subsumed`. Missing/stale packet → run the evidence detour below. |
| theory | toy *(if experiments needed)* else red-team evidence/proof audit | see "Experiments-needed"; no direct jump to outline |
| toy | ablation | |
| ablation | external results-ingest stop | require frozen experiment contract + protocol and real manifest before red-team |
| red-team | outline | requires `lifecycle_gates.evidence_audited` pass/accepted conditional and results-aware red-team `blocking: false`; otherwise loop back |
| outline | drafting → full-draft | grill `interview_drafting` is a hard stop if absent |
| drafting | self-review → citation-audit → submission-check | sub-step order below; loop to `revision` on issues |
| revision | back to self-review / citation-audit | re-loop until clean |
| submission-check | final *(pass)* / revision *(fail)* | |
| final | — | summarize artifacts: survey, bib, algorithm card, draft, audit. On a rejection, `post-mortem` re-opens the pipeline at the earliest gate its findings invalidate |

## Completeness rule (which mode runs next)

Modes set `stage` to their own name **on completion**, so normally `stage` = the
last completed stage and you run its **successor** above. The one exception is a
freshly bootstrapped (or crash-interrupted) file: if the mode named by `stage` has
**not** produced its output yet — no `## <date> — <stage>` body entry and its
artifact field is empty — run **that** mode, not the successor. The evidence
precondition below is the safety net if this is ever misjudged.

This rule is subordinate to lifecycle routing: if `stage` appears later than the
earliest missing/stale gate, backfill that gate first. Never infer
method/protocol/results/review completion from a stage label.

## Retrofit entry (`entry_mode: retrofit`)

State created by `bootstrap.md`'s retrofit branch carries gates with status
`backfill_needed` (defined in `shared/prompts/research_lifecycle.md`). Route it
like this, and re-evaluate the order on every hop:

1. **Reviews first.** If `retrofit_source.reviews` is present, run
   `paper-writer post-mortem` (`skills/paper-writer/modes/post-mortem.md`)
   before any backfill: its gate attribution tells you which gates the findings
   invalidate, and backfilling first would waste the work. The mode sets
   `research_phase` back to the earliest invalidated gate, which is where step 2
   resumes.
2. **Otherwise, earliest `backfill_needed` gate wins.** Walk the ordered
   lifecycle table top-down and run the owner of the first gate whose status is
   `backfill_needed` — claim map → `literature-explorer`/`gap-analysis`;
   prior-art audit and method freeze → `ideate` → `novelty-check`; experiment
   contract → `toy-design`; protocol → `ablation-plan`; results → the
   external-run stop. The legacy `stage` label is ignored while any
   `backfill_needed` gate remains.
3. **No shortcut.** `backfill_needed` blocks advancement exactly like `missing`.
   A reconstructed claim map or method-freeze artifact is an input to the owning
   mode, not a substitute for it: claims still need passage grounding, and the
   method freeze still needs a novelty verdict that clears the minimum-verdict
   rule. Never promote `backfill_needed` to `pass`/`frozen` because the paper
   already asserts the thing.

## Hard precondition: corpus manifest before discussion modes

Before `gap`, `formalize`, and `ideate`, check `corpus_manifest:` in state. If
it is absent, run `literature-explorer` in `corpus-prefetch` mode
(`skills/literature-explorer/corpus-prefetch.md`) first — one broad shallow
sweep across its four mandatory axes, emitting a hashed
`docs/corpus-manifest-<slug>.md`. This is one-time per topic, not per mode.

If the manifest's `gathered:` date is more than 6 months old, run the
recent-work refresh described in that file before the discussion mode, not the
full sweep. Recompute the manifest hash after any refresh or drift extension and
compare it with state.

The manifest is a precondition, not a lifecycle gate: it occupies no
`research_phase`, and it never substitutes for an evidence packet. Its records
are abstract-scope alarm evidence — the packet precondition below is unchanged
and unweakened by its presence.

## Hard precondition: current evidence packet before novelty/writing

Before `novelty`, validate a candidate-specific packet whose fingerprint matches
the live candidate's primitives/components, objective/estimand, data regime,
and atomic claim set. Before `outline`, `full-draft`, and `citation-audit`,
validate current packet coverage for every substantive claim they invoke.

If missing or stale:

1. For legacy state, import/deduplicate `literature:` and `citations:` into the
   vault; these paths remain compatibility views and do not prove support.
2. Run the applicable mode's vault-first targeted retrieval, inspect primary
   passages, persist query-runs/source versions/claims/evidence links, and freeze
   a replacement packet.
3. Re-read state and validate its packet ID/hash/status before returning to the
   blocked stage.

If retrieval cannot clear the gap, hard-stop with the unresolved queries. Never
advance on a `.bib`, abstract-only evidence, or model recall. `gap-analysis` may
emit an unranked query queue without a packet, but cannot publish top gaps.

### Mutation hook

This is the conductor-side copy of the same rule that
`skills/algo-brainstorm/SKILL.md` Hard discipline #3 applies on entry to every
mode — so it also fires in ad-hoc single-mode sessions with no conductor. Keep
the two in agreement; the lifecycle contract decides if they ever diverge.

After any loop-back, revision, red-team mitigation, or user edit, compare the
candidate fingerprint with the packet basis. A material change to primitives,
objective/estimand, data regime/assumptions, or claim text/IDs marks the old
packet stale immediately. Route through targeted retrieval and re-freeze before
resuming; also mark method freeze and every downstream lifecycle gate stale per
`research_lifecycle.md`. Do not let a later stage silently inherit the old
verdict, protocol, results, or review.

## Experiments-needed branch

Read `interview_ideate.contribution_type` (`theoretical` | `empirical` | `both`)
and `venue_target` (+ `shared/venue_profiles.md`).

- **Run `toy` → `ablation`** when contribution is `empirical` or `both`, or the
  venue expects experiments (NeurIPS / ICML / AISTATS). This is the default —
  when unsure, include them.
- **Skip to `outline` after `theory`** only for an explicitly pure-theory paper:
  `contribution_type: theoretical` **and** a theory-leaning venue (e.g. Annals of
  Statistics) **and** no empirical `key_claims`. Mark experiment/protocol/results
  gates `not_applicable` only with the lifecycle contract's proof-artifact
  rationale. Evidence/proof audit and results-aware red-team still run before
  `outline` in this branch (theory → evidence audit → red-team → outline).

## Write-phase entry hook: reviewer intel

On transitioning **into `red-team`** (either branch), check research state:
`venue_target` has public reviews (OpenReview venue) and `reviewer_intel:`
absent → run `shared/prompts/reviewer_intel.md` first. The dossier is a
project artifact — gather without asking; only the venue-profile upgrade
it may offer needs user confirmation. No public reviews (JMLR, AoS) →
skip with one line. Consumers: `red-team`, `self-review`, `full-draft`.

## Write-phase sub-steps (`stage: drafting` / `revision`)

The `stage` enum does not split the write phase, so detect sub-progress from
artifacts instead of `stage` alone. Run in this order, skipping any already done:

1. **full-draft** — done when `draft:` exists, `paper/sections/*` populated, and
   the body has a `full-draft` entry. (Hard stop on its `interview_drafting` grill
   and the `paper-writer` pre-flight/current-packet gate.) Recompute the draft
   hash and set the `draft` lifecycle gate; a stage/body entry alone is not done.
2. **self-review** — done when the body has a `self-review` entry dated at/after
   the latest draft **and** the scientific-review artifact binds the current
   method/protocol/result/audit/draft hashes. Major issues → `revision`, then
   re-run self-review.
3. **citation-audit** — done when the latest `.research-state/<slug>-audit-<date>.json`
   is clean (no `fabricated`/`mismatched`), all substantive cited claims have
   valid passage links in a current packet, and cited `key_claims` are
   `audit_status: verified`. **Any metadata or passage-support failure →
   `revision`**, then re-audit/retrieve.
4. **submission-check** — when 1–3 are clean. Pass → set `stage: final`. Fail →
   `revision`, then loop back to the failing sub-step. Set `research_phase:
   final` only after submission and every upstream lifecycle gate revalidate.

## Notes

- `--council` is opt-in per mode and orthogonal to routing; the conductor does not
  add it automatically. The user can pass it to a specific mode by hand.
- Never skip a mode's own gating, grill, or state-write. The conductor only
  chooses *which* mode runs next.
