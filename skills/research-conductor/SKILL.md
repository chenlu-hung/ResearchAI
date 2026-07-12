---
name: research-conductor
description: Autopilot that drives a Stats/ML research idea from rough intuition to a submission-ready paper by automatically sequencing the other three skills (literature-explorer, algo-brainstorm, paper-writer). Reads the research-state stage machine and calls the right mode next, looping until the paper is done. Use when the user says "I have an idea, take it to a paper", "drive the whole pipeline", "from idea to paper", "把這個想法做成論文", "幫我從頭跑到投稿", or invokes /research. NOT for running a single isolated mode — use /explore, /algo, or /write for that.
---

# research-conductor

The **conductor** for this plugin. The other three skills each do one stage of
research; this one *sequences* them. You start from an idea, and it decides which
skill/mode to invoke next, runs it, and loops — so you complete a paper without
hand-driving every step.

It is a thin orchestration layer. It **never** re-implements mode logic, **never**
writes a mode-owned section of research-state, and **never** bypasses a gate. It
reads the `stage` that modes already write and delegates execution back to them.

## When to invoke

- "I have an idea for a new method — help me take it all the way to a paper"
- "Drive the pipeline", "what's the next step?", "keep going"
- `/research <idea>` (new idea) or `/research` (resume current project)

## When NOT to invoke

- One isolated stage → use `/explore`, `/algo <mode>`, `/write <mode>` directly.
- The user is mid-discussion inside a single mode and just wants that mode.

## The loop

```
1. Resolve project:
     - new idea with no state  → run bootstrap.md (create state, pick start stage)
     - existing .research-state/<slug>.md → load it
2. Render the roadmap (checklist from `stage`; see "Roadmap" below).
3. Pick the next mode from routing.md (stage → next, with branches/loop-backs).
4. Announce the hop in ONE line: "▶ <stage> → <next mode> (<why>)".
5. Load and execute that mode file (skills/<skill>/modes/<mode>.md or the
   literature-explorer pipeline). The mode owns its own grill, gating, and
   state-writes — let it run exactly as if invoked directly.
   *Economy branch (`--economy` only):* if routing.md marks the stage `✓`
   and the preconditions in `shared/prompts/model_dispatch.md` hold, run the
   mode in an implementer subagent per that file instead of inline, then
   apply its Acceptance section before step 6. Otherwise inline as above.
6. When the mode finishes, re-read research-state.
     - hard stop hit?  → halt, hand control to the user (see "Hard stops").
     - else            → go to 2.
7. Stop when `stage: final` (summarize artifacts) or a hard stop fires.
```

The substance of steps 1 and 3 lives in the two sub-files — read them when you
reach those steps:

- `bootstrap.md` — turn a fresh idea into a state file and a starting stage.
- `routing.md` — the `stage → next mode` table, branch rules, loop-backs, and the
  bib-before-novelty precondition.

### Hop checklist (every loop iteration)

Verify before each hop — per `shared/prompts/execution_discipline.md`
(rule 6 especially; the loop runs long and memory of state goes stale):

- [ ] `.research-state/<slug>.md` re-read from disk **this turn**, not
      recalled from earlier context.
- [ ] Completeness rule applied (routing.md): the stage's own mode runs iff
      its output is missing; otherwise its successor.
- [ ] Hard-stop list scanned against the fresh state; none firing.
- [ ] Roadmap printed; hop announced in one line.

## Autonomy

Default: **full auto until blocked.** Auto-chain stage→stage; only the hard stops
below (or the user) pause the run. Two opt-down flags from `/research`:

- `--gates` — also pause for a one-line go/no-go at high-leverage gates: candidate
  pick (after `ideate`), novelty verdict, red-team triage, before `full-draft`,
  before `submission-check`.
- `--step` — pause before every mode.

A third flag changes *where* modes run, not when they pause:

- `--economy [model]` — delegate the token-heavy, judgment-light stages
  (marked `✓` in routing.md) to a cheaper implementer subagent per
  `shared/prompts/model_dispatch.md`; default implementer `sonnet`. Routing,
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
- `novelty-check` verdict is *not novel* or *novelty uncertain* unresolved.
- `red-team` has a `blocking: true` / high-severity finding → do **not** advance to
  `outline`; route back per routing.md.
- `citation-audit` returns any `fabricated` or `mismatched`.
- `submission-check` fails.
- An API/tool failure (`unreachable`), or an anti-hallucination `[VERIFY]` that
  gates an irreversible step (`shared/prompts/anti_hallucination.md`).
- The user types `stop` / `pause` / "等一下" — halt immediately after the current
  mode; the persisted `stage` lets the next `/research` resume.

After any halt, the user resolves the issue (answers the grill, fixes a finding,
re-runs a mode by hand) and says "continue" / `/research` to resume.

## Roadmap

At step 2, print a compact checklist derived from `stage` (the source of truth),
so the auto-run stays legible. Mark `✅` done, `▶` current, `⬜` pending. Example:

```
explore ✅  gap ✅  formalize ✅  ideate ▶  novelty ⬜  theory ⬜
toy ⬜  ablation ⬜  red-team ⬜  outline ⬜  draft ⬜  review ⬜
audit ⬜  submission ⬜  final ⬜
```

Show only the branch that applies (theory vs toy/ablation) per routing.md.

## State discipline

The conductor writes research-state **only** during bootstrap (topic / slug /
venue_target / created / initial `stage`). Everything after that is written by the
modes it calls. It must obey the schema's atomic-update and append-only rules and
must not duplicate a mode's grill (see `grill_protocol.md` "Failure modes").
