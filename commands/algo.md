---
description: Run a mode of the algo-brainstorm skill for developing new Stats/ML algorithms.
argument-hint: <mode> [extra args]
---

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
statistical-rigor protocols as documented in the SKILL.md.
