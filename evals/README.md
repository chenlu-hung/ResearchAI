# Evals

## Why this directory exists

The Python test suite covers the deterministic scripts: regexes fire, JSON
parses, exit codes are right. None of it touches the judgments that actually
gate the research — whether `novelty-check` was right to say `subsumed`,
whether the prose pass flagged the correct sentence, whether a mode refused a
claim it should have refused. Those are model judgments, and until they are
measured, "the gate works" means "the gate ran".

This is a small held-out set for the subset of those judgments whose correct
answer follows from a written rule.

## Ground-truth isolation

An agent that can see the answer key while producing the answer optimizes
against the key rather than the task, and the resulting score does not
transfer. This is architectural, not a matter of intent, so the key never
enters the run:

1. `scripts/eval_pack.py --out <dir>` writes prompts, the allowed answers, and
   the rule files to load. It never writes `answer` or `because`, and it
   re-reads its own output to confirm that before exiting.
2. The runner answers from the pack directory alone, filling in `answers.json`.
3. `scripts/eval_score.py --answers <file> --pack <dir>` scores against
   `evals/cases/`, which the runner never opened.

The pack records a digest of the case files. Scoring refuses to run if the
cases changed after the pack was built, so an edited case cannot be used to
explain away a wrong answer afterwards. Rationales print only for cases
answered wrongly — a scoring run is not a side channel for reading the key of
the cases you skipped.

If you run this yourself in a session that already has the repo open, you have
already broken isolation. Use a fresh session, or a subagent given the pack
directory and nothing else.

## What is covered

| Surface | Cases | Where the label comes from |
|---|---|---|
| `evidence-gating` | 12 | The refusal rules in `shared/prompts/evidence_grounding.md`, `shared/prompts/research_lifecycle.md`, `shared/firm_rules.md`, and `skills/research-conductor/routing.md` |
| `prose-hygiene` | 7 | `shared/prompts/prose_hygiene.md`, concentrating on what `check_prose.py` documents it cannot judge — §E exceptions and §F slot legitimacy |

These labels are **definitional**: the rule says X, the case does X, so the
answer follows. Nothing here rests on an empirical fact about the world, which
is why it could be authored without new fieldwork.

Answers are deliberately mixed within each surface. Three of the seven prose
cases are §E exceptions that must **not** be flagged, and five of the twelve
gating cases are ones where proceeding is correct. A set where refusing is
always right would be aced by a model that always refuses, and over-refusal is
a real failure: a gate that blocks legitimate progress, or flags legitimate
academic prose, is a gate that gets bypassed — and a bypassed gate catches
nothing.

## What is not covered

These need ground truth this repo cannot generate, and are deliberately empty
rather than filled with plausible guesses:

- **Novelty verdicts.** Whether `subsumed` was correct requires real candidates,
  real prior art, and a human who knows the answer. Seed it from resolved cases
  in your own history — a candidate you later confirmed was subsumed, one you
  confirmed was not — one case per resolved decision, with the resolution date.
- **Grill quality.** Whether `interview_ideate` asked the question that
  mattered. Judgable only after the project resolves.
- **Red-team catch rate.** Requires runs with known planted flaws.
- **Venue calibration.** Requires an official CFP as ground truth; the
  provenance fields already carry it, so this is buildable — it just isn't
  built.

Adding a surface: one JSON file in `evals/cases/`, same shape as the existing
two. `tests/test_evals.py` validates the shape and the isolation property.

## Running

```bash
uv run --project . python3 scripts/eval_pack.py --out /tmp/pack
# hand /tmp/pack to a fresh session; it fills in /tmp/pack/answers.json
uv run --project . python3 scripts/eval_score.py \
    --answers /tmp/pack/answers.json --pack /tmp/pack
```

`--min-accuracy` turns the score into a pass/fail gate. There is deliberately
no scheduled job running this: an eval that runs itself against the model that
authored the cases measures very little.

## What a score here does and does not mean

Nineteen cases is a smoke test. It can show that a rule is being applied
backwards; it cannot estimate how often the gate is right in practice, and a
percentage from this set has no useful confidence interval. Report it as
"16/19, these three wrong", never as an accuracy figure with a decimal point.
