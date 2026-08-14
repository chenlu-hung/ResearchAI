# Mode: revision

**Purpose**: targeted edits to a specific section. Used during iteration
(self-review, advisor feedback) and after reviewer comments.

## Inputs

- Path to the section file (e.g., `paper/sections/03-method.tex`)
- Edit intent (paraphrased): "tighten", "respond to reviewer concern about X",
  "add a missing baseline discussion", "fix theorem statement"

## Procedure

1. **Read the section + surrounding context** (the section file plus the
   sections immediately before and after, so cross-references stay valid).

2. **Read research state** so you know what has changed since the section
   was last written (e.g., new theory targets, new ablation results). Validate
   the current evidence packet against the candidate fingerprint and claim set.

3. **Plan the edit** as a list before writing:
   - What stays (don't gratuitously rewrite)
   - What changes and why
   - What new atomic claims/citations are added → run
     `shared/prompts/evidence_grounding.md`; a `.bib` lookup is not support
   - Any cross-references that need updating in other sections

4. **Ground before applying.** Query the vault first for every new/changed
   literature claim and retrieve externally only for gaps. Persist source
   versions and passage links, then freeze a replacement packet. If the edit
   changes candidate primitives/components, objective/estimand, data regime,
   assumptions, or material claim text, mark the old packet stale immediately.
   A new/changed empirical claim must map to an existing audited result artifact,
   metric/split/uncertainty, and frozen decision rule. If it does not, do not
   write it: return to the experiment/protocol/results lifecycle gate and
   invalidate downstream artifacts.

5. **Apply edit**. Prefer minimal-diff edits to wholesale rewrites — keeps
   reviewer-response track clean and avoids regenerating bugs.

6. **Coherence check**:
   - Notation still consistent
   - Theorem numbering unchanged unless intentional
   - Bibliography keys all in the generated `.bib`, with every substantive
     citing sentence linked to a current packet passage
   - Prose hygiene pass on edited text — `stop-slop` skill if available,
     then the academic overlay `shared/prompts/prose_hygiene.md` (structural
     AI tells and §F format tells, not just filler); mechanical subset via
     `python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_prose.py"
     <edited-file>` — paste its result line

## Reviewer-response sub-mode

When the edit intent is "respond to reviewer X":

1. Extract the specific reviewer concerns as bullet points
2. For each, decide: do we (a) edit the paper, (b) write a rebuttal
   response, (c) both?
3. Edit minimally; track edits in a `response.md` keyed by reviewer comment
4. The response should *acknowledge specifically* — never use generic
   "we have improved..." filler

## Anti-sycophancy

- Do not capitulate to a reviewer concern that is wrong. If the reviewer
  is wrong, the response must be a polite rebuttal with evidence (cite,
  quote your own paper, point to an experiment). Caving with sloppy
  edits hurts the paper.
- Equally: do not stubbornly defend something that is wrong. If reviewer
  caught a real issue, acknowledge and fix.
- Weaknesses or reviewer agreement cannot substitute for grounded prior art
  when a revision changes a novelty/contribution claim.

## Output

- Edited section file (minimal diff)
- If reviewer-response: `response.md` with point-by-point reply

## State update

No stage change for routine revision. After a full pass, keep/set
`stage: revision`, then re-run self-review, citation-audit, and
submission-check. Only submission-check may advance to `final`.

After every edit, recompute the draft hash and update
`lifecycle_gates.draft`. Mark `scientific_review` and `submission` stale even
when the edit is prose-only, because both bind the prior draft hash. Apply the
broader upstream invalidation rules in `shared/prompts/research_lifecycle.md`
when scientific content changed.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Step 3 edit plan (stays / changes / new claims / cross-refs) was
      written *before* the file was touched.
- [ ] Diff is minimal — untouched prose preserved verbatim.
- [ ] Citations still resolve after the edit: `python3
      "$PLUGIN_ROOT/skills/paper-writer/scripts/check_tex.py" paper/main.tex --bib
      refs/<slug>.bib` is clean (pasted, not eyeballed).
- [ ] New/changed claims completed vault-first retrieval and passage linking;
      any material candidate/claim change invalidated and replaced the packet.
- [ ] Draft hash updated; scientific-review/submission gates marked stale, plus
      all scientifically affected upstream/downstream gates invalidated.
- [ ] Coherence check ran: notation, theorem numbering, prose hygiene on
      the edited text (`check_prose.py` on the edited file, result line
      pasted; blocking findings fixed or waived as a §F slot).
- [ ] Reviewer-response: every comment has an (a)/(b)/(c) decision and a
      `response.md` entry; no "we have improved…" filler; no capitulation
      without evidence and no stonewalling on a real issue.
