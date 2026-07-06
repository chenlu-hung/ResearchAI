# Execution Discipline

These skills run on whatever Claude model the user has that day. A top-tier
model follows a long mode file reliably; a smaller one drops steps, softens
adversarial passes, and trusts its memory of files it read long ago. The rules
below make step-following **mechanical**, so output quality is set by the mode
files, checklists, and scripts — not by the running model's attention. Every
rule is mandatory on every model; a stronger model simply clears them faster.

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
