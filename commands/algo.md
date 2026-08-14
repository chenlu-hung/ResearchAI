---
description: Run a mode of the algo-brainstorm skill for developing new Stats/ML algorithms.
argument-hint: <mode> [--council]
---

Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
it is the absolute parent of the file's `commands/` directory. Never derive it
from the user's working directory. Resolve every `skills/...`, `shared/...`, or
other plugin resource below as `$PLUGIN_ROOT/<path>`. Dependency-bearing Python
scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Invoke the `algo-brainstorm` skill in the mode specified by the first
argument: $ARGUMENTS

Valid modes (see `skills/algo-brainstorm/SKILL.md`):

- `gap-analysis` — find what's wrong/missing in an existing method
- `formalize` — turn intuition into precise math (loss, assumptions, estimand)
- `ideate` — generate 3–5 candidate algorithmic approaches
- `novelty-check` — compare candidates against prior art; articulate Δ
- `theory-scoping` — enumerate theorems and proof techniques
- `toy-design` — design minimal synthetic experiment
- `ablation-plan` — design ablation table and baseline protocol
- `red-team` — adversarial self-review before paper writing

Follow the procedure in `skills/algo-brainstorm/modes/<mode>.md`. Read
research state on entry; update on exit. Apply anti-sycophancy and
statistical-rigor protocols as documented in the SKILL.md. For `gap-analysis`,
`ideate`, and `novelty-check`, also apply
`shared/prompts/evidence_grounding.md`: vault-first retrieval, passage links,
candidate-specific packets, and stale-on-change semantics.

Hard gates: unverified items cannot be top gaps; speculative candidates require
targeted retrieval and a current packet before ranking; novelty-check refuses a
missing/stale packet; application-only deltas are not method novelty. Weaknesses
never replace grounded prior-art pressure. Novelty verdicts are exactly
`novel | incremental | subsumed`; method freeze needs `novel`, or `incremental`
with a persisted `incremental_accepted: true` plus a one-line user rationale —
`subsumed` and "no verdict issued" can never freeze. `gap-analysis`,
`formalize`, and `ideate` additionally refuse to start without a corpus manifest
for the topic (run `/research-assistant:explore corpus-prefetch` first).

Also follow `shared/prompts/research_lifecycle.md`: novelty-check persists the
prior-art audit and method freeze; toy-design freezes the experiment contract;
ablation-plan freezes an executable protocol; then the pipeline hard-stops for a
real results manifest. Red-team first audits those results/proofs and is
results-aware—an experiment plan or expected curve cannot satisfy it.

If the arguments include `--council` (supported by `gap-analysis`, `ideate`,
`novelty-check`, and `red-team`), additionally run the multi-model panel in
`shared/prompts/council_panel.md` after the mode's gating — fan out to
Codex / Gemini / Claude / DeepSeek via
`python3 "$PLUGIN_ROOT/shared/council.py"`, then
chair the synthesis. For `gap-analysis`/`ideate` the panel is divergence (union of
ideas); for `novelty-check`/`red-team` it is adversarial cross-examination (members
attack, then a conditional single rebuttal round) and every attack is a hypothesis the
chair must turn into a persisted query and verify through a refreshed packet before it
changes a verdict. Without `--council`, run the mode single-model; the same evidence gates apply.
