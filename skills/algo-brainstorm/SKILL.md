---
name: algo-brainstorm
description: Develop new Statistics/ML algorithms from rough intuition to submission-ready contribution. Eight modes (gap-analysis, formalize, ideate, novelty-check, theory-scoping, toy-design, ablation-plan, red-team) that can be invoked independently or chained. Use when the user has an idea for a new method, wants to refine an existing method, or needs adversarial review of their algorithm.
---

# algo-brainstorm

## Plugin-root contract

Resolve the absolute path of this already loaded `SKILL.md`, then set
`PLUGIN_ROOT` to the directory two levels above its containing skill directory
(`.../skills/algo-brainstorm/../..`). Never infer the plugin location from the
user's working directory and do not `cd` into the plugin. Resolve `shared/...`
and `skills/...` resources against `$PLUGIN_ROOT`; resolve bare `modes/...` and
`checklists/...` paths against this skill directory. Project artifacts such as
`.research-state/`, `docs/`, `paper/`, `refs/`, and `results/` remain relative
to the user's project. Dependency-bearing Python scripts use
`uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`; stdlib-only
scripts use `python3 "$PLUGIN_ROOT/<path>"`.

The core skill of this plugin. Targeted at researchers whose primary output is
**new algorithms** (not applied work, not surveys). Borrows the staged-pipeline
+ integrity-gate idea from ARS, but rewritten for algorithm development and
implemented entirely from scratch.

## When to invoke

- "I have an idea for a new method"
- "Help me sharpen this algorithm"
- "Is this novel?"
- "What could break this?"
- "What theorems should I aim for?"
- Claude Code: `/research-assistant:algo <mode>`
- Codex: invoke `$research-ai:algo-brainstorm` and name the mode

## When NOT to invoke

- Topic survey → `literature-explorer`
- Writing a section of a paper → `paper-writer`
- Implementing the algorithm → general coding (this skill is design-only)

## Modes

Set the mode in the conversation. Claude Code may use
`/research-assistant:algo <mode>`; Codex may invoke
`$research-ai:algo-brainstorm` and state the mode in the same message.

| Mode | Purpose | Mode file |
|---|---|---|
| `gap-analysis` | Find what's wrong/missing in existing methods | `modes/gap-analysis.md` |
| `formalize` | Turn intuition into math: loss, assumptions, estimand | `modes/formalize.md` |
| `ideate` | Generate 3–5 candidate algorithmic approaches | `modes/ideate.md` |
| `novelty-check` | Compare candidates against prior art; articulate Δ | `modes/novelty-check.md` |
| `theory-scoping` | What theorems should this paper prove? | `modes/theory-scoping.md` |
| `toy-design` | Design the toy and freeze the experiment contract | `modes/toy-design.md` |
| `ablation-plan` | Design ablations and freeze the executable protocol | `modes/ablation-plan.md` |
| `red-team` | Audit actual results/proofs, then adversarially review them | `modes/red-team.md` |

## Typical chain

```
gap-analysis → formalize → ideate → novelty-check
                              ↓ method freeze + contribution spine
                    paper-writer positioning-skeleton (empty table shells)
                                              ↓
                       theory-scoping → toy-design (experiment contract)
                                              ↓
                                  ablation-plan (protocol freeze)
                                              ↓
                          external runs → results ingest → evidence audit
                                              ↓
                                  results-aware red-team → paper-writer
```

At method freeze, `novelty-check` also freezes the **contribution spine** —
exactly one primary claim plus at most three supporting claims, by ID, written to
`spine:` in state. Everything downstream binds to it: every experiment maps to a
spine claim, `positioning-skeleton` writes its contribution statements from it,
outline bullets tag one, and `self-review`'s focus audit checks that the drafted
paper still argues the primary claim.

Each mode updates `research_state` and the `algorithm_card.md`.
Lifecycle advancement additionally requires the hashed artifacts and hard stops
in `shared/prompts/research_lifecycle.md`; the legacy stage chain never treats an
experiment plan as observed results.

## Hard discipline

Applied to **every mode**:

### 0. Execution discipline

Follow `shared/prompts/execution_discipline.md`: numbered Procedure steps
run in order (skips are declared, never silent), output is emitted only
after the mode's **Exit checklist** passes, checklist axes are answered
exhaustively, and bundled scripts are run for real — never simulated.
For literature-dependent modes also follow
`shared/prompts/evidence_grounding.md`: model knowledge generates queries or
hypotheses only; retrieval is vault-first; answers come from a current,
candidate-specific evidence packet.

### 1. Anti-sycophancy

Before any positive response, list substantive weaknesses. Whenever the response
judges novelty, recommends/ranks a candidate, or endorses a contribution, also
retrieve and compare **≥2 closely related prior works** through passage-grounded
evidence (or report that the evidence gate is blocked). Weaknesses never
substitute for prior art. No "great idea!" openers or reassurance without
grounding.

### 2. Novelty reflex (corpus-first)

Novelty is checked **during every algorithm discussion**, not once at the
`novelty-check` gate.

**Reflex.** Whenever a new algorithmic component, objective, or design choice
enters the discussion, immediately name its nearest neighbor **from the local
corpus** — a vault query against `docs/corpus-manifest-<slug>.md`'s works, **no
network** — and state in one line what is the same and what differs. If nothing
in the corpus is close, say that explicitly. Do this before evaluating the idea,
not after.

**Drift detection.** If the new element's terms match none of the manifest's
covered axes, declare **"out of corpus envelope"**, run a targeted retrieval for
that element *now*, persist the results to the vault, and extend the manifest
with the new axis terms and date. Interrupt and retrieve; do not defer to a
later gate.

**Two-fidelity rule.** Corpus hits are **alarm evidence only**. They justify a
warning and a query — never a novelty verdict, a claim link, a Same/Different/Δ
row, or a paper sentence. Promoting an idea to a registered candidate, or
changing anything about a frozen method, still requires passage-level grounding
through the full loop in `shared/prompts/evidence_grounding.md`. The reflex
widens what you notice; it does not lower what counts as evidence.

**Entry hook.** `gap-analysis`, `formalize`, and `ideate` refuse to start
without a corpus manifest for the topic; offer to run
`literature-explorer` in `corpus-prefetch` mode first (one-time,
`skills/literature-explorer/corpus-prefetch.md`). A manifest whose `gathered:`
date is more than 6 months old triggers an incremental refresh of its
recent-work axis before heavy use — refresh that axis, not the whole sweep.

### 3. Fingerprint staleness check on entry (mutation hook)

This runs **first** on entry, ahead of #2's corpus-manifest entry hook: a stale
fingerprint changes which corpus terms are even the right ones to check.

On entry to **every** mode, before anything else: recompute the live candidate
fingerprint — primitives/components, objective/estimand, data regime/assumptions,
claim IDs — and compare it with the evidence packet's basis and the method-freeze
artifact. On a material mismatch, mark the packet and every downstream lifecycle
gate stale per `shared/prompts/research_lifecycle.md` **before** doing any mode
work, and say so in one line.

This is the same rule as the "Mutation hook" in
`skills/research-conductor/routing.md`, stated here so it also fires in ad-hoc
single-mode sessions where no conductor is running. The two copies must stay in
agreement; if they ever disagree, the lifecycle contract decides.

### 4. Statistical rigor reflex

If the user is doing anything that touches inference, surface relevant
pitfalls from `checklists/stats_pitfalls.md`:

- Multiple testing / FWER / FDR
- Post-selection inference
- Identifiability / regularity conditions
- Data leakage / train-test split correctness
- Selection bias
- p-hacking risk surface

If the user is doing pure ML (no inference claims), skip this.

### 5. No fabricated math

Follow `shared/prompts/anti_hallucination.md`. Do not invent theorem names,
do not cite "by X (2019) we have..." unless X 2019 is verified. Mark
conjectured statements with `[CONJECTURE — not yet proved]`.

### 6. Algorithm card hygiene

Each mode updates `docs/algo-card-<slug>.md` with the schema from
`checklists/algorithm_card.md`. The card is the single-page summary you
take into your next conversation, your advisor meeting, or paper outline.

## Output discipline

- Every mode produces **structured output** (markdown sections per the
  mode file), not free-form prose.
- Numerical claims must have provenance.
- Reference to a paper requires a canonical work; every substantive attributed
  claim also requires an atomic claim/passage link in the current packet. A
  generated BibTeX key is necessary for LaTeX rendering, not sufficient evidence.

## State integration

On entry: read `.research-state/<slug>.md` and its evidence pointers. If the relevant prior stage is
empty (e.g., `novelty-check` invoked but `candidates:` is empty), refuse
and suggest running `ideate` first. If an evidence-gated mode has a missing or
stale packet, run the migration/retrieval loop before proceeding; legacy
`literature:`/`citations:` fields alone do not satisfy the gate.

On exit: update the relevant field per the mode file. Advance `stage`
only with user confirmation.

Before persisting any change to candidate primitives/components,
objective/estimand, data regime/assumptions, or material claim text/IDs, mark
the referenced evidence packet stale and record the reason in the canonical
vault. No downstream mode may reuse it; targeted retrieval must freeze a
replacement. Cosmetic renames that leave the fingerprint unchanged are exempt.

## Venue awareness

If `venue_target` is set in research state, `theory-scoping` and `red-team`
load `shared/venue_profiles.md` to tailor expectations.

## Council panel (opt-in)

`gap-analysis`, `ideate`, `novelty-check`, and `red-team` can widen their search with a
multi-model panel — Codex, Gemini, Claude, and opencode, each reached through its **own
subscription/sign-in CLI** (no API keys), merged by this session as chair. Pass `--council`
(for example, Claude Code `/research-assistant:algo ideate --council`, or ask
`$research-ai:algo-brainstorm` for `red-team` with a council in Codex) to
convene it; without the flag
the mode runs single-model exactly as before. Two flavors:

- **Divergence** (`gap-analysis`, `ideate`) — fan out and take the union of ideas.
- **Adversarial cross-examination** (`novelty-check`, `red-team`) — members attack the Δ /
  the contribution, then a *conditional single rebuttal round* on real disagreement. Every
  attack is a **hypothesis the chair must verify** through vault-first retrieval and a
  refreshed packet before it changes a verdict — see the Cross-examination section.

Protocol and guardrails: `$PLUGIN_ROOT/shared/prompts/council_panel.md` (engine:
`$PLUGIN_ROOT/shared/council.py`, stdlib-only —
`python3 "$PLUGIN_ROOT/shared/council.py"`).

**Requires** the member CLIs you want on PATH and signed in (`codex`, `agy`, `claude`,
`opencode`); any that are missing simply drop out of the panel. Panel output is **ideation
only**: every citation, theorem name, or number it produces is a query/hypothesis and must
pass `shared/prompts/evidence_grounding.md` and `shared/prompts/anti_hallucination.md`
before entering evidence state. A panel member is never a source for novelty claims.
