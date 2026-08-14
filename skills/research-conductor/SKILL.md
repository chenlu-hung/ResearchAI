---
name: research-conductor
description: Autopilot that drives a Stats/ML research idea from rough intuition to a submission-ready paper by sequencing literature-explorer, algo-brainstorm, and paper-writer over the shared evidence-store core. Reads the research-state stage machine and calls the right mode next, looping until the paper is done. Use when the user says "I have an idea, take it to a paper", "drive the whole pipeline", "from idea to paper", "把這個想法做成論文", "幫我從頭跑到投稿", invokes Claude Code /research-assistant:research, or invokes the Codex $research-ai:research-conductor skill. NOT for running a single isolated mode — use the corresponding workflow skill for that.
---

# research-conductor

## Plugin-root contract

Resolve the absolute path of this already loaded `SKILL.md`, then set
`PLUGIN_ROOT` to the directory two levels above its containing skill directory
(`.../skills/research-conductor/../..`). Never infer the plugin location from
the user's working directory and do not `cd` into the plugin. Resolve
`shared/...` and `skills/...` resources against `$PLUGIN_ROOT`; resolve bare
`bootstrap.md` and `routing.md` against this skill directory. Every delegated
skill and mode inherits this same absolute plugin root. Project artifacts such
as `.research-state/`, `docs/`, `paper/`, `refs/`, and `results/` remain relative
to the user's project. Dependency-bearing Python scripts use
`uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`; stdlib-only
scripts use `python3 "$PLUGIN_ROOT/<path>"`.

The **conductor** for this plugin. The three workflow skills each do one stage of
research over the shared evidence-store core; this one *sequences* them. You start from an idea, and it decides which
skill/mode to invoke next, runs it, and loops — so you complete a paper without
hand-driving every step.

It is a thin orchestration layer. It **never** re-implements mode logic, **never**
writes a mode-owned section of research-state, and **never** bypasses a gate. It
reads the `stage` that modes already write and delegates execution back to them.
It also validates the evidence control plane on each evidence-dependent hop;
`shared/prompts/evidence_grounding.md` is binding across all delegated hosts.
`shared/prompts/research_lifecycle.md` is the authoritative gate order. Legacy
`stage` chooses a compatible mode; `research_phase` and hashed gate artifacts
decide whether scientific advancement is allowed.

## When to invoke

- "I have an idea for a new method — help me take it all the way to a paper"
- "Drive the pipeline", "what's the next step?", "keep going"
- Claude Code: `/research-assistant:research <idea>` (new) or
  `/research-assistant:research` (resume)
- Codex: invoke `$research-ai:research-conductor` with an idea or ask it to
  resume

## When NOT to invoke

- One isolated stage → invoke `literature-explorer`, `algo-brainstorm`, or
  `paper-writer` directly.
- The user is mid-discussion inside a single mode and just wants that mode.

## The loop

```
1. Resolve project:
     - new idea with no state  → run bootstrap.md (create state, pick start stage)
     - existing draft/PDF (± a decision/reviews file) with no state → run
       bootstrap.md's retrofit branch (entry_mode: retrofit, then its backfill
       sequence), and route per routing.md's "Retrofit entry"
     - existing .research-state/<slug>.md → load it
2. Render the roadmap from `research_phase`/lifecycle gates, using legacy
   `stage` only as a compatibility routing hint (see "Roadmap" below).
3. Pick the next mode from routing.md (stage → next, with branches/loop-backs).
4. Announce the hop in ONE line: "▶ <stage> → <next mode> (<why>)".
5. Load and execute that mode file (skills/<skill>/modes/<mode>.md or the
   literature-explorer pipeline). The mode owns its own grill, gating, and
   state-writes — let it run exactly as if invoked directly.
   *Economy branch (`--economy` only):* if routing.md marks the stage `✓`
   and the preconditions in `shared/prompts/model_dispatch.md` hold, run the
   mode in an implementer subagent per that file instead of inline, then
   apply its Acceptance section before step 6. Otherwise inline as above.
6. When the mode finishes, re-read research-state, validate any referenced
   evidence packet from the canonical vault, and recompute hashes for every
   gate artifact the mode claims to have completed.
     - hard stop hit?  → halt, hand control to the user (see "Hard stops").
     - else            → go to 2.
7. Stop only when `research_phase: final`, `stage: final`, and every lifecycle
   gate/hash revalidates (then summarize artifacts), or when a hard stop fires.
   A legacy `stage: final` by itself is never a completion signal.
   `final` rests, it does not terminate: a rejection re-opens the run via
   `paper-writer post-mortem`, which moves `research_phase` back to the earliest
   gate its findings invalidate.
```

The substance of steps 1 and 3 lives in the two sub-files — read them when you
reach those steps:

- `bootstrap.md` — turn a fresh idea, or an existing paper (retrofit entry),
  into a state file and a starting stage.
- `routing.md` — the `stage → next mode` table, branch rules, loop-backs, and the
  packet-before-novelty and writing preconditions.
- `shared/prompts/research_lifecycle.md` — ordered phase gates, artifact
  schemas, result-ingest stop, validation, invalidation, and legacy mapping.

### Hop checklist (every loop iteration)

Verify before each hop — per `shared/prompts/execution_discipline.md`
(rule 6 especially; the loop runs long and memory of state goes stale):

- [ ] `.research-state/<slug>.md` re-read from disk **this turn**, not
      recalled from earlier context.
- [ ] `research_phase` and `lifecycle_gates` checked against
      `shared/prompts/research_lifecycle.md`; any legacy state routed to the
      earliest unmet backfill gate.
- [ ] Referenced vault/topic/candidate/packet IDs validated; packet freshness
      checked against primitives, objective/estimand, data regime, and claims.
- [ ] Completeness rule applied (routing.md): the stage's own mode runs iff
      its output is missing; otherwise its successor.
- [ ] Hard-stop list scanned against the fresh state; none firing.
- [ ] Roadmap printed; hop announced in one line.

## Autonomy

Default: **full auto until blocked.** Auto-chain stage→stage; only the hard stops
below (or the user) pause the run. Two opt-down flags on a conductor request:

- `--gates` — also pause for a one-line go/no-go at high-leverage gates: candidate
  pick (after `ideate`), novelty verdict, red-team triage, before `full-draft`,
  before `submission-check`.
- `--step` — pause before every mode.

A third flag changes *where* modes run, not when they pause:

- `--economy [model]` — delegate the token-heavy, judgment-light stages
  (marked `✓` in routing.md) to a cheaper implementer subagent per
  `shared/prompts/model_dispatch.md`; default = the host-configured economy
  model (legacy Claude Code setups may resolve it to `sonnet`). Routing,
  grills, verdicts, and acceptance stay in this session. Composes freely
  with `--gates`/`--step`.

Full auto is **not silent**: announce every hop (step 4) so the user can interject.

### Standing-confirmation semantics

Schema rule #3 (`shared/research_state.schema.md`) says advance `stage` only on
user confirmation. A conductor run supplies that confirmation **once, up front**:
during the run, modes may advance `stage` without re-asking. This override is
scoped to the conductor and applies to stage advancement **only** — it does not
touch grills or any hard stop.

## Hard stops (halt even in full auto)

Halt, state why in one line, and hand control back when:

- A mode needs its grill (`shared/prompts/grill_protocol.md`) and no
  `interview_<mode>:` block exists yet → let the mode run its interview; the
  conductor waits for the user, then resumes.
- A refuse-if-blank precondition fails and can't be auto-backfilled (e.g.
  `paper-writer` pre-flight, `gap-analysis` "no method specified").
- A discussion mode (`gap-analysis`, `formalize`, `ideate`) is next and
  `corpus_manifest:` is absent — run `literature-explorer` `corpus-prefetch`
  first; halt only if that sweep cannot complete.
- A required evidence packet is missing/stale/invalid after attempted legacy
  migration or retrieval; a generated `.bib` never clears this stop.
- A lifecycle artifact is absent/empty, its recomputed hash differs, or its
  status is missing/draft/stale/fail/cannot-determine. (`backfill_needed` also
  blocks advancement, but is **not** a halt: route it through the retrofit
  backfill in `routing.md` instead of handing control back.)
- Method freeze, experiment contract, or protocol freeze is not current for its
  upstream dependency hashes.
- Confirmatory runs have not been ingested into a valid result manifest, or its
  run/artifact hashes do not match the frozen protocol, or its per-run
  `method_variant`/`param_count`/`adaptation`/`resolution_direction` fields do
  not cover the contract's parity matrix and calibration budget (a claim-bearing
  asymmetry whose equalized-variant runs are absent is a stop). The conductor
  never fabricates results to continue.
- Evidence audit or results-aware red team is absent/stale/blocking before drafting.
- `gap-analysis` would promote an unverified or abstract-only item to a top gap.
- The chosen candidate's `novelty-check` verdict is `subsumed`; or no verdict
  was issued because coverage was insufficient (field absent, or still carrying
  `ideate`'s `pending` placeholder); or the verdict is `incremental` without a
  persisted `incremental_accepted: true` and a one-line user rationale. The
  verdict vocabulary is exactly `novel | incremental | subsumed`
  (`skills/algo-brainstorm/modes/novelty-check.md`); treat any other value in
  state as a corrupt gate and halt.
- `red-team` has a `blocking: true` / high-severity finding → do **not** advance to
  `outline`; route back per routing.md.
- `citation-audit` returns any `fabricated`, `mismatched`, or substantive claim
  without a valid passage link.
- `submission-check` fails.
- An API/tool failure (`unreachable`), or an anti-hallucination `[VERIFY]` that
  gates an irreversible step (`shared/prompts/anti_hallucination.md`).
- The user types `stop` / `pause` / "等一下" — halt immediately after the current
  mode; the persisted `stage` lets the next conductor request resume.

After any halt, the user resolves the issue (answers the grill, fixes a finding,
re-runs a mode by hand) and asks the conductor to continue.

## Roadmap

At step 2, print a compact checklist derived from lifecycle gates (the source of
truth), with the legacy mode beneath it when useful. Mark `✅` done, `▶`
current, `⬜` pending, and `⛔` blocked. Example:

```
intake ✅  claims ✅  prior-art ✅  method-freeze ✅
experiment-contract ▶  protocol ⬜  results ⬜  evidence-audit ⬜
results-red-team ⬜  draft ⬜  scientific-review ⬜  submission ⬜
```

Show only the branch that applies (theory vs toy/ablation) per routing.md.

## State discipline

The conductor writes research-state during bootstrap (topic / slug / venue /
initial `stage`/`research_phase` and evidence pointers) and may validate/update
only lifecycle gate status/pointers that no mode owns (notably externally
produced result manifests). It may advance `research_phase` to the next ordered
value only after the current gate validates. Mode-owned scientific content remains owned by the
modes. It must obey atomic-update/append-only rules and must not duplicate a
mode's grill.

Legacy state without evidence pointers remains resumable: route through the
additive import/backfill/freeze migration in `evidence_grounding.md` before the
first evidence-gated stage. Never infer a current packet from legacy survey or
BibTeX paths.
