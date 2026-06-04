# Mode: self-review

**Purpose**: simulate one venue reviewer reading the *drafted manuscript* and
produce actionable comments. This is distinct from `algo-brainstorm`'s
`red-team`:

- `red-team` attacks whether the **method/claims are valid**.
- `self-review` attacks whether the **manuscript persuades this venue** —
  completeness, positioning, evidence, clarity. It assumes the method is sound.

Single pass, single reviewer persona. No multi-agent panel.

## Inputs

- Draft (`paper/main.tex` or section files) — required
- `venue_target` — required (sets the reviewer persona)

## Procedure

1. Read the full draft and the venue's profile in `shared/venue_profiles.md`
   (reviewer profile + red-flag list) plus the matching `style/<venue>.md`.
2. Adopt the venue's **dominant** reviewer persona (e.g. NeurIPS → empirical
   reviewer; AoS → pure statistician).
3. Produce a review with these parts:
   - **Summary** (3–4 sentences, as a reviewer would write it): what the paper
     claims and does.
   - **Recommendation**: map to the venue scale (e.g. accept / weak accept /
     borderline / reject) with a one-line reason.
   - **Major comments**: substantive — unsupported claim, missing recent
     baseline, assumption not discussed, theory–experiment mismatch, novelty
     not delimited. Each tied to a section.
   - **Minor comments**: clarity, notation, figure/table issues.
   - **Red-flag check**: go down the venue's `Common reviewer red flags` list
     and mark each present / absent / N/A.

## Anti-sycophancy

- Surface **≥3 concrete weaknesses**. "Strong paper, minor polish" is not a
  valid output for a draft.
- Every comment cites a section/line. No generic praise.
- Do not invent flaws either — if the draft genuinely covers a red flag, say so.

## Output

`.research-state/<slug>-selfreview-<date>.md`. Feed findings into `revision`.

## State update

No stage change. Surface to the user; they decide what to act on.
