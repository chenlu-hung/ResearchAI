# Execution Discipline

These skills run on whatever Claude model the user has that day. A top-tier
model follows a long mode file reliably; a smaller one drops steps, softens
adversarial passes, and trusts its memory of files it read long ago. The rules
below make step-following **mechanical**, so output quality is set by the mode
files, checklists, and scripts — not by the running model's attention. Every
rule binds on every model; on a top-tier model exactly two of them run in a
relaxed *form* (see **Strong-model tier** below) — the obligation never drops.

## Rules

1. **Steps are a contract.** Run a mode's numbered Procedure steps in order.
   To skip one, write `Skipped step N: <reason>` in the output. A silent skip
   is a defect, not a shortcut.

2. **Two-pass emission.** Draft the mode's output, then re-read the mode
   file's **Exit checklist** and fix every violation *before* showing the
   user anything. End the output with one line: `Exit checklist: N/N` (or
   `N-1/N — <which item and why>` when an item genuinely cannot pass).

3. **Checklists are exhaustive.** When a mode lists axes, attacks, or
   red flags to cover, produce a finding for each **or** an explicit
   `N/A — <one-line reason>`. An axis with neither is unfinished work.

4. **Scripts over recall.** If a bundled script covers a step — retrieval,
   dedup/ranking, citation audit, injection scan, `\cite`/`\ref` cross-check,
   compile — run it and paste its real output. Never simulate a script's
   result by reasoning; a plausible-looking simulated result is worse than an
   error message.

5. **Re-anchor before long output.** Immediately before generating anything
   longer than ~300 words, restate in ≤3 lines the binding constraints: the
   venue/persona in force, the claim this output serves, and where citations
   are allowed to come from. Then generate.

6. **Fresh reads on resume.** After a context compaction, a session resume,
   or any gap where files may have changed, re-read
   `.research-state/<slug>.md` and the active mode file from disk before
   continuing. Remembered contents are stale by default.

7. **Judgment calls are visible.** When you make a choice the mode file
   leaves open (which gap to rank first, which persona, which baseline),
   name the choice and give a one-line reason in the output, so a wrong call
   is visible and cheap to correct.

8. **Minimum counts are floors, met honestly.** "≥3 weaknesses" means three
   real ones. If, after attacking every listed axis, you genuinely cannot
   reach the floor, say so explicitly — padding with invented findings is a
   worse failure than an honest shortfall.

## Strong-model tier

Two of the rules above are *process scaffolding* — they compensate for a
smaller model's drift over long procedures. On a top-tier model their form
relaxes; every other rule, and every deterministic script gate, is identical
on every tier.

**Tier check.** Decide once per skill invocation from the model named in
your system prompt: Mythos-class (Fable, Mythos) or a newer top tier →
**strong**; Opus-tier and below, or any doubt → **standard**. Declare it in
the first mode output of the session (`Discipline tier: strong` or
`standard`); an undeclared tier is standard.

**Relaxed on strong (form changes, obligation doesn't):**

- Rule 2 — the separate draft-then-re-read pass may collapse to one pass:
  verify each Exit-checklist item while writing. The closing
  `Exit checklist: N/N` line stays mandatory, with misses declared the
  same way.
- Rule 5 — the ≤3-line re-anchor may stay silent instead of being emitted —
  except immediately after a compaction or resume, where it is emitted on
  every tier (staleness does not shrink with capability).

**Never relaxed, on any tier:** rules 1, 3, 4, 6, 7, 8. Scripts over recall
(4) and fresh reads on resume (6) guard against hallucination and staleness,
which are behavioural, not capability, failures. Implementer subagents under
`model_dispatch.md` always run standard, whatever their model.
