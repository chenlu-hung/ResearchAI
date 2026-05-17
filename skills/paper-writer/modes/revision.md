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
   was last written (e.g., new theory targets, new ablation results).

3. **Plan the edit** as a list before writing:
   - What stays (don't gratuitously rewrite)
   - What changes and why
   - What new claims/citations are added → verify in `.bib`
   - Any cross-references that need updating in other sections

4. **Apply edit**. Prefer minimal-diff edits to wholesale rewrites — keeps
   reviewer-response track clean and avoids regenerating bugs.

5. **Coherence check**:
   - Notation still consistent
   - Theorem numbering unchanged unless intentional
   - Bibliography keys all in `.bib`

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

## Output

- Edited section file (minimal diff)
- If reviewer-response: `response.md` with point-by-point reply

## State update

No stage change for routine revision. After full pass of all reviewer
comments, advance `stage` to `revision` → `final`.
