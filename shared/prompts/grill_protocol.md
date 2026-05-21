# Grill Protocol

Applied by modes that need to anchor generation on user intent **before**
expensive output. Modes should reference this file rather than duplicating
the rules.

## Purpose

Generation that drifts from user intent is the dominant failure mode of
divergent steps (`ideate`, `full-draft`). One round of targeted questioning
— recommended answer first, one question at a time — costs ~4 turns and
saves a whole regeneration cycle. Use this protocol whenever a mode is
about to produce output that is expensive to undo.

## When to run

After the calling mode has:

1. Read `.research-state/<slug>.md` on entry.
2. Run any refuse-if-blank gating (e.g., `formalize` complete,
   `outline` exists, `bib` exists).

Run the grill **after** the cheap fails so the interview only happens when
the mode would otherwise proceed.

## Skip rule

If `.research-state/<slug>.md` frontmatter already contains an
`interview_<mode>:` block (e.g., `interview_ideate:` for the `ideate`
mode), **skip the entire interview** and proceed to the mode's Procedure.
State the skip explicitly to the user in one line:

> Interview answers found in state (`interview_ideate`, asked
> 2026-05-21). Skipping grill.

The skip is unconditional — answers stay frozen until the user deletes
the block manually. This is intentional. Iteration happens at the mode
level (re-running `ideate` on a fresh slug or a `-v2` slug), not at the
interview level.

## Question format

### Discrete answer (2–4 options)

Use `AskUserQuestion`. Constraints:

- **Recommended option first**, labeled with `(Recommended)` suffix.
- Header ≤ 12 characters.
- 2–4 options total. `"Other"` is added automatically — do **not**
  enumerate it explicitly.
- The recommended option's `description` field must state the *reason*
  for the recommendation in one sentence, grounded in research-state
  fields if possible (e.g., "Inferred from `theory_targets:` already
  having two entries").

### Open-ended answer (free-form prose)

Print the question in chat, then a single sentence labeled
`Recommended:` that Claude would write if the user said "use yours",
then wait for user reply. Example:

> **Q3. Hard constraints / no-go zones?**
>
> Recommended: "Candidates must not rely on knowing the nuisance exactly;
> must remain valid at finite-sample n."

User can accept ("yes" / "use yours"), edit, or replace.

## Pacing rules

- **One question at a time.** Never batch.
- **Essentials first, in the order the calling mode specifies.**
- **Follow-up rule**: after each essential, judge whether the answer is
  specific enough to anchor downstream work. If not, ask **one**
  follow-up. Hard cap: **3 follow-ups total** across the interview.
- **Short-circuit**: if the user replies "go", "enough", "stop grilling",
  "skip", or equivalent, stop questioning immediately. Proceed to the
  summary step with whatever answers exist; mark missing ones as
  `unspecified`.

## Anti-sycophancy in the interview itself

- Do **not** prefix the recommended answer with "Great question",
  "Excellent intuition", or similar. State the recommendation flatly.
- Recommendations must cite the grounding (state field, prior stage
  output, venue, etc.) — not "based on best practices".
- If you cannot find grounding for a recommendation in research-state,
  say so: "No basis in state for a recommendation; user pick is
  authoritative."

## Summary + confirm (last step)

After all essentials are answered (or short-circuited):

1. Print a summary, **one line per essential**, in the order asked. Use
   the exact answer text the user supplied (or the recommended phrasing
   if they accepted it).
2. Ask via `AskUserQuestion`:
   - Header: "Confirm"
   - Options (≤ 4 per call): `Proceed` *(Recommended)* /
     `Edit answer 1` / `Edit answer 2` / `Edit answer 3`.
     If 4 essentials, drop the lowest-leverage edit and add it on a
     follow-up call if the user picks "Other → edit answer 4".
   - Plus `Cancel` if it fits within 4; else expose via "Other".
3. On `Edit N`: re-ask only question N, then re-print summary and
   re-ask confirm.
4. On `Cancel`: abort the calling mode entirely. **Do not** write the
   interview block to state.
5. On `Proceed`: append the `interview_<mode>:` block to the frontmatter
   of `.research-state/<slug>.md` (see schema), then return control to
   the calling mode's Procedure.

## Persistence format

Append to YAML frontmatter under the key `interview_<mode>:` where
`<mode>` matches the calling mode name (`ideate`, `drafting`, ...).
Fields are mode-defined. Always include `asked_at:` with today's date
and `follow_ups:` (list, possibly empty) of any dynamic follow-ups
asked and their answers. Do not delete or overwrite an existing block —
modes skip-if-exists, so a second write should not happen.

## Failure modes to avoid

- **Drilling on already-answered fields**: if research-state has
  `venue_target: NeurIPS 2026`, do not ask "which venue?". Read state
  first; ask only what's missing.
- **Asking for things the next mode will ask anyway**: don't pre-ask
  `theory-scoping` questions inside `ideate`'s grill. Each mode grills
  for its **own** output, not the pipeline's.
- **Open-ended sprawl**: every free-form question must have a
  recommended phrasing. If you can't write one, the question is too
  vague to ask.
