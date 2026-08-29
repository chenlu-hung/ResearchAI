# Mode Registry

Single source of truth for every mode in the suite. **22 modes across 4
workflow skills**; `research-conductor` and `evidence-store` ship no modes.

The mode surface is declared in four places that must agree: the files on disk,
each skill's own `## Modes` table, the conductor's `routing.md`, and this
registry. When they disagree the failure is silent — the conductor routes to a
mode file that no longer exists, or a mode ships that the conductor can never
reach. `scripts/check_mode_registry.py` fails CI on any of those.

**When adding, renaming, or removing a mode, edit this table first**, then the
owning `SKILL.md`, then `routing.md`.

| Skill | Mode | File | Purpose | Lifecycle phase(s) owned |
|---|---|---|---|---|
| literature-explorer | `survey` *(default)* | `skills/literature-explorer/SKILL.md` | Deep, passage-grounded survey → claim map, evidence packet, BibTeX view | `intake_import`, `atomic_claim_map` |
| literature-explorer | `corpus-prefetch` | `skills/literature-explorer/corpus-prefetch.md` | One broad shallow abstract-level sweep → hashed corpus manifest | none — precondition for the discussion modes |
| algo-brainstorm | `gap-analysis` | `skills/algo-brainstorm/modes/gap-analysis.md` | Find what's wrong/missing in existing methods | `atomic_claim_map` |
| algo-brainstorm | `formalize` | `skills/algo-brainstorm/modes/formalize.md` | Turn intuition into math: loss, assumptions, estimand | `atomic_claim_map` |
| algo-brainstorm | `ideate` | `skills/algo-brainstorm/modes/ideate.md` | Generate 3–5 candidate algorithmic approaches | `prior_art_audit` |
| algo-brainstorm | `novelty-check` | `skills/algo-brainstorm/modes/novelty-check.md` | Compare candidates against prior art; articulate Δ; issue the verdict | `prior_art_audit`, `method_frozen` |
| algo-brainstorm | `theory-scoping` | `skills/algo-brainstorm/modes/theory-scoping.md` | Decide what theorems the paper should prove | `experiment_contract` |
| algo-brainstorm | `toy-design` | `skills/algo-brainstorm/modes/toy-design.md` | Design the toy and freeze the experiment contract | `experiment_contract` |
| algo-brainstorm | `ablation-plan` | `skills/algo-brainstorm/modes/ablation-plan.md` | Design ablations and freeze the executable protocol | `protocol_frozen` |
| algo-brainstorm | `red-team` | `skills/algo-brainstorm/modes/red-team.md` | Audit actual results/proofs, then adversarially review them | `evidence_audited`, `results_red_team` |
| paper-writer | `positioning-skeleton` | `skills/paper-writer/modes/positioning-skeleton.md` | Intro/related/contributions + empty result-table shells, before experiments | `positioning_skeleton` |
| paper-writer | `outline` | `skills/paper-writer/modes/outline.md` | Section-by-section outline tailored to venue | `drafting` |
| paper-writer | `full-draft` | `skills/paper-writer/modes/full-draft.md` | Section-by-section draft from algorithm card + outline | `drafting` |
| paper-writer | `revision` | `skills/paper-writer/modes/revision.md` | Targeted edits to a specific section | none — loop-back within a phase |
| paper-writer | `citation-audit` | `skills/paper-writer/modes/citation-audit.md` | Verify each citation exists and supports the claim | `scientific_review` |
| paper-writer | `self-review` | `skills/paper-writer/modes/self-review.md` | One-pass venue-reviewer critique of the draft | `scientific_review` |
| paper-writer | `submission-check` | `skills/paper-writer/modes/submission-check.md` | Submission-readiness gate before `final` | `submission` |
| paper-writer | `venue-calibration` | `skills/paper-writer/modes/venue-calibration.md` | Add or re-verify a venue profile from official sources + exemplars | none — maintains `shared/venue_profiles.md` |
| paper-writer | `post-mortem` | `skills/paper-writer/modes/post-mortem.md` | Turn a rejection's reviews into gate attributions and pipeline changes | none — re-opens the earliest invalidated gate |
| paper-writer | `grant-nstc` | `skills/paper-writer/modes/grant-nstc.md` | Draft/revise an NSTC (國科會) 專題研究計畫 CM03 | none — proposal track, outside the paper lifecycle |
| peer-reviewer | `report` | `skills/peer-reviewer/modes/report.md` | Full referee report on someone else's manuscript (default) | none — needs no `.research-state` |
| peer-reviewer | `triage` | `skills/peer-reviewer/modes/triage.md` | Fast desk-screen: scope fit + fatal flaw + novelty smell | none — needs no `.research-state` |

## Skills with no modes

| Skill | Why | Entry files |
|---|---|---|
| `research-conductor` | Orchestrator. It selects and runs other skills' modes and never implements one. | `bootstrap.md`, `routing.md` |
| `evidence-store` | Library skill wrapping `evidencectl`. Invoked by modes, not selected as one. | `SKILL.md` |

## Flags are not modes

`--depth quick\|standard\|deep` and `--council` scale `peer-reviewer report`;
`--step`, `--gates`, and `--economy` scale the conductor. They vary how a mode
runs, so they carry no registry row and no lifecycle phase.

## Phase ownership is not a routing table

The right-hand column says which lifecycle gate a mode can satisfy, not when it
runs. Ordering, preconditions, branches, and loop-backs live in
`skills/research-conductor/routing.md`; the gates themselves are defined in
`shared/prompts/research_lifecycle.md`. A mode owning no phase is not optional —
it means the mode satisfies no gate by running.
