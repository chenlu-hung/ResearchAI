# Model dispatch — economy delegation

Architect/implementer split for the conductor. The main session (the
strongest model) keeps routing, grills, verdicts, and acceptance; token-heavy
but judgment-light modes run in a subagent on a cheaper model. Active **only**
when the user passed `--economy` to `/research` — never delegate by default.

Two things this buys: the delegated mode's tokens bill at the cheaper model's
rate, and its bulk reading / long output never enters the main session's
context, so every later conductor turn stays small.

## Delegable stages

Only stages marked `✓` in the `--economy` column of routing.md's Stage → mode
table: `explore`, `full-draft`, `revision`, `citation-audit`. Everything else
runs inline, no exceptions — grills and verdicts need the user or the
strongest model, and small modes don't repay a subagent's startup overhead.
For `explore`, the "mode file" below is the whole
`skills/literature-explorer/SKILL.md` pipeline.

## Preconditions (all must hold, else run inline and say why in one line)

1. The mode's grill (if it has one) is already satisfied — its
   `interview_<mode>:` block exists in research-state. A subagent cannot
   interview the user; a pending grill is a hard stop for the conductor
   first, delegation after.
2. No hard stop currently firing.
3. The Agent tool is available and the spawn succeeds.

## Spawning

`Agent` with `subagent_type: "general-purpose"` and `model:` the economy
model — default `sonnet`; the user may name another (`--economy haiku`).
**One implementer per mode, never parallel**: research-state is a shared
file and concurrent writers corrupt it.

Announce the hop with the model: `▶ <stage> → <mode> (economy: sonnet)`.

## Implementer brief (template — fill every <blank>; all paths absolute)

```text
You are the implementer for one research-pipeline mode: <mode name>,
project <topic slug>, working directory <absolute project root>.

Read these in full, in order, before doing anything:
1. <path to shared/prompts/execution_discipline.md> — binding rules.
2. <path to the mode file> — the procedure you execute.
3. <path to .research-state/<slug>.md> — project state.
Plus every file the mode file itself tells you to load (venue profiles,
prose_hygiene.md, checklists).

Rules:
1. Execute the mode file exactly as written — its Procedure order, gates,
   scripts, state-writes, and Exit checklist are binding. This brief adds
   process only; it never overrides the mode.
2. You cannot talk to the user. Any step needing user input, and any
   trigger in rule 3, ends the run with a CONSULT block instead of a guess.
3. CONSULT when: research-state is ambiguous or contradicts the mode's
   preconditions; a verdict-level judgment appears (novelty call,
   blocking-severity finding, dropping or changing a key claim); a citation
   cannot be verified against any real source (never invent one); or a
   mode-mandated approach or script fails after one honest attempt.
4. Scripts over recall: run the real script, paste its real output.
   A simulated result is a defect, not a shortcut.
5. Your discipline tier is standard, whatever model you run on — never
   apply the strong-model relaxations in execution_discipline.md.
6. End the run with exactly one of these blocks and nothing after it:

   DONE
   stage written: <the stage value you set in research-state>
   artifacts: <paths written or updated>
   gates: <verbatim result line of each script/gate the mode ran>
   Exit checklist: N/N   (or N-1/N — <item and why>)
   deviations: <list, or "none">

   CONSULT
   mode: <mode name>
   question: <one sentence>
   context: <what you read/tried; verbatim output if a script failed>
   options: A) <option> B) <option> — my lean: <A/B, one-line why>
```

## Consult loop

On CONSULT, rule decisively — decision, why, what it forecloses. Answer the
design question; don't do the mode's work for it. Reply with **SendMessage**
to the same agent so its context survives; never spawn a fresh agent to
continue a delegated mode. Relay each consult and ruling to the user in 1–2
lines. Ruling format:

```text
RULING: <decision in one sentence>
why: <one line>
implies: <what this forecloses or forces downstream>
Continue the mode.
```

Escalation: a 3rd CONSULT from the same mode, or two failed attempts at the
same step, means the split isn't paying — take the mode over and run it
inline yourself.

## Acceptance (conductor, non-skippable — never accept DONE blind)

1. Re-read `.research-state/<slug>.md` from disk; confirm the mode wrote its
   stage and body entry (routing.md completeness rule).
2. Confirm every artifact the DONE block names exists and is non-empty.
3. Re-run the stage's machine gates yourself and paste the result lines:
   `full-draft` / `revision` → `check_prose.py` + `check_tex.py`;
   `citation-audit` → read the audit JSON (any `fabricated`/`mismatched` is
   the usual hard stop); `explore` → literature + bib artifacts exist,
   `[VERIFY]` flags preserved on unaudited claims.
4. `Exit checklist: N/N` line present in the DONE block; a shortfall names
   its item and reason, or the run goes back via SendMessage.
5. Judgment spot-check: skim for silently dropped claims, softened findings,
   or invented citations — architecture-level deviations go back to the
   implementer citing the mode file; small mechanical slips you fix inline.

Only after 1–5 does the conductor advance to the next hop.
