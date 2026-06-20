# Conductor routing

The `stage → next mode` state machine the conductor follows. Backbone = the
"Typical chain" in `skills/algo-brainstorm/SKILL.md`. Read `stage` from
`.research-state/<slug>.md`; pick the next mode here; load and run its file.

## Stage → mode file

| `stage` | Skill / mode file |
|---|---|
| explore | `literature-explorer` pipeline (its `SKILL.md`; entry `/explore`) |
| gap | `skills/algo-brainstorm/modes/gap-analysis.md` |
| formalize | `skills/algo-brainstorm/modes/formalize.md` |
| ideate | `skills/algo-brainstorm/modes/ideate.md` |
| novelty | `skills/algo-brainstorm/modes/novelty-check.md` |
| theory | `skills/algo-brainstorm/modes/theory-scoping.md` |
| toy | `skills/algo-brainstorm/modes/toy-design.md` |
| ablation | `skills/algo-brainstorm/modes/ablation-plan.md` |
| red-team | `skills/algo-brainstorm/modes/red-team.md` |
| outline | `skills/paper-writer/modes/outline.md` |
| drafting | `skills/paper-writer/modes/{full-draft,self-review,citation-audit}.md` (sub-steps, see below) |
| revision | `skills/paper-writer/modes/revision.md` |
| final | — (done; summarize artifacts) |

## Routing table

| Current `stage` | Next (default) | Branch / loop-back |
|---|---|---|
| *(bootstrap, no state)* | explore | start at `gap` instead if the idea is a refinement of a **named** method (bootstrap decides). `explore` must still run before `novelty`. |
| explore | gap | |
| gap | formalize | |
| formalize | ideate | |
| ideate | novelty | needs ≥1 candidate with `status: chosen`/live; grill `interview_ideate` is a hard stop if absent |
| novelty | theory | **halt if verdict is "not novel" / "novelty uncertain" unresolved.** If `literature:`+`citations:` missing → detour to `explore` first (precondition below). |
| theory | toy *(if experiments needed)* else outline | see "Experiments-needed" |
| toy | ablation | |
| ablation | red-team | |
| red-team | outline | **if any `blocking: true` / high-severity finding → back to `formalize` (assumption flaw) or `ideate` (approach flaw); do not advance** |
| outline | drafting → full-draft | grill `interview_drafting` is a hard stop if absent |
| drafting | self-review → citation-audit → submission-check | sub-step order below; loop to `revision` on issues |
| revision | back to self-review / citation-audit | re-loop until clean |
| submission-check | final *(pass)* / revision *(fail)* | |
| final | — | summarize artifacts: survey, bib, algorithm card, draft, audit |

## Completeness rule (which mode runs next)

Modes set `stage` to their own name **on completion**, so normally `stage` = the
last completed stage and you run its **successor** above. The one exception is a
freshly bootstrapped (or crash-interrupted) file: if the mode named by `stage` has
**not** produced its output yet — no `## <date> — <stage>` body entry and its
artifact field is empty — run **that** mode, not the successor. The bib
precondition below is the safety net if this is ever misjudged.

## Hard precondition: bib before novelty

`novelty-check` and all `\cite{...}` discipline depend on retrieved literature.
Before running `novelty`, verify `literature:` and `citations:` in frontmatter
point to existing non-empty files. If not, run `explore` first, then return to
`novelty`. (`gap-analysis` may run without a bib, but only with heavy `[VERIFY]`
flagging — not a hard stop.)

## Experiments-needed branch

Read `interview_ideate.contribution_type` (`theoretical` | `empirical` | `both`)
and `venue_target` (+ `shared/venue_profiles.md`).

- **Run `toy` → `ablation`** when contribution is `empirical` or `both`, or the
  venue expects experiments (NeurIPS / ICML / AISTATS). This is the default —
  when unsure, include them.
- **Skip to `outline` after `theory`** only for an explicitly pure-theory paper:
  `contribution_type: theoretical` **and** a theory-leaning venue (e.g. Annals of
  Statistics) **and** no empirical `key_claims`. `red-team` still runs before
  `outline` in this branch (theory → red-team → outline).

## Write-phase sub-steps (`stage: drafting` / `revision`)

The `stage` enum does not split the write phase, so detect sub-progress from
artifacts instead of `stage` alone. Run in this order, skipping any already done:

1. **full-draft** — done when `draft:` exists, `paper/sections/*` populated, and
   the body has a `full-draft` entry. (Hard stop on its `interview_drafting` grill
   and the `paper-writer` pre-flight.)
2. **self-review** — done when the body has a `self-review` entry dated at/after
   the latest draft. Major issues → `revision`, then re-run self-review.
3. **citation-audit** — done when the latest `.research-state/<slug>-audit-<date>.json`
   is clean (no `fabricated`/`mismatched`) and cited `key_claims` are
   `audit_status: verified`. **Any `fabricated`/`mismatched` → `revision`** (fix
   cites), then re-audit.
4. **submission-check** — when 1–3 are clean. Pass → set `stage: final`. Fail →
   `revision`, then loop back to the failing sub-step.

## Notes

- `--council` is opt-in per mode and orthogonal to routing; the conductor does not
  add it automatically. The user can pass it to a specific mode by hand.
- Never skip a mode's own gating, grill, or state-write. The conductor only
  chooses *which* mode runs next.
