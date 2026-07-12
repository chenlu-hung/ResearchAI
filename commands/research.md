---
description: Autopilot from a research idea to a submission-ready paper. Sequences explore → algo → write automatically via the research-conductor skill.
argument-hint: [idea] [--step | --gates] [--economy [model]]
---

Invoke the `research-conductor` skill on: $ARGUMENTS

The conductor drives the whole pipeline so you don't hand-call each mode:

- **New idea** (`/research <idea>`): bootstrap a `.research-state/<slug>.md` and
  start the pipeline (see `skills/research-conductor/bootstrap.md`).
- **Resume** (`/research` with no idea): load the current project's state and
  continue from its `stage`.

Follow the loop in `skills/research-conductor/SKILL.md`: read research-state →
render the roadmap → pick the next mode from `skills/research-conductor/routing.md`
→ run that mode (it owns its own grill, gating, and state-writes) → repeat until
`stage: final` or a hard stop.

Autonomy (default **full auto until blocked**):

- no flag — auto-chain stage→stage; pause only on a hard stop or a mode's grill.
- `--gates` — also pause for a go/no-go at high-leverage gates (candidate pick,
  novelty verdict, red-team triage, before full-draft, before submission).
- `--step` — pause before every mode.
- `--economy [model]` — run the token-heavy, judgment-light stages (explore,
  full-draft, revision, citation-audit) in a cheaper implementer subagent
  (default `sonnet`) per `shared/prompts/model_dispatch.md`; grills, verdicts,
  and acceptance stay in the main session. Composes with `--gates`/`--step`.

The conductor never bypasses a gate, never duplicates a mode's grill, and writes
research-state only during bootstrap. `--council` is not applied automatically;
pass it to a specific mode by hand if you want a panel.
