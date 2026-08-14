---
description: Autopilot from a research idea to a submission-ready paper. Sequences explore → algo → write automatically via the research-conductor skill.
argument-hint: [idea | existing draft path] [--step | --gates] [--economy [model]]
---

Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
it is the absolute parent of the file's `commands/` directory. Never derive it
from the user's working directory. Resolve every `skills/...`, `shared/...`, or
other plugin resource below as `$PLUGIN_ROOT/<path>`. Dependency-bearing Python
scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Invoke the `research-conductor` skill on: $ARGUMENTS

The conductor drives the whole pipeline so you don't hand-call each mode:

- **New idea** (`/research-assistant:research <idea>`): bootstrap a
  `.research-state/<slug>.md` and
  start the pipeline (see `skills/research-conductor/bootstrap.md`).
- **Retrofit** (`/research-assistant:research <path to draft or PDF>
  [reviews file]`, no state yet): import an existing or rejected paper via
  bootstrap's retrofit branch — reconstruct the claim map and method freeze from
  the paper, mark the experiment/protocol/results gates `backfill_needed` with
  exactly what is missing, then route to the earliest such gate. A legal entry
  route, not a shortcut: backfilled claims still need passage grounding.
- **Resume** (`/research-assistant:research` with no idea): load the current
  project's state and
  continue from its lifecycle gates, using `stage` only as a compatibility
  routing hint.

Follow the loop in `skills/research-conductor/SKILL.md`: read research-state →
validate its vault/packet pointers → render the roadmap → pick the next mode from `skills/research-conductor/routing.md`
→ run that mode (it owns its own grill, gating, and state-writes) → repeat until
both `research_phase: final` and `stage: final` revalidate against every gate,
or a hard stop.

Autonomy (default **full auto until blocked**):

- no flag — auto-chain stage→stage; pause only on a hard stop or a mode's grill.
- `--gates` — also pause for a go/no-go at high-leverage gates (candidate pick,
  novelty verdict, red-team triage, before full-draft, before submission).
- `--step` — pause before every mode.
- `--economy [model]` — run the token-heavy, judgment-light stages (explore,
  full-draft, revision, citation-audit) in a cheaper implementer subagent
  (host-configured economy default; an explicit model may be supplied) per
  `shared/prompts/model_dispatch.md`; grills, verdicts,
  and acceptance stay in the main session. Composes with `--gates`/`--step`.

The conductor never bypasses a gate or duplicates a mode's grill. It writes
bootstrap fields and may validate/advance non-mode lifecycle pointers (notably a
real external results manifest), but never writes mode-owned scientific content.
Missing/stale evidence packets, unverified
top gaps, application-only novelty claims, and ungrounded draft claims are hard
stops. It also enforces `shared/prompts/research_lifecycle.md`: claim map →
prior-art audit → method freeze → experiment contract → protocol freeze → real
results ingest → evidence audit → results-aware red team → draft → scientific
review → submission. A missing/mismatched artifact hash or absent real result
manifest stops the run; expected curves never count as results. Legacy
survey/`.bib`/`stage` state is migrated/backfilled before proceeding; a
BibTeX file alone never clears an evidence gate. `--council` is not applied automatically;
pass it to a specific mode by hand if you want a panel.
