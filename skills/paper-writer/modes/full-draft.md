# Mode: full-draft

**Purpose**: produce a complete LaTeX draft from the algorithm card and
outline. This is the heaviest mode; expect to iterate.

## Inputs

- Outline (required — run `outline` first if missing)
- Algorithm card
- `refs/<slug>.bib` (citations must be in here)
- Notation file `docs/notation-<slug>.md` (will create if absent)

## Pre-flight

Refuse if:

- `red-team` has `blocking: true` findings unresolved
- Outline does not exist
- `refs/<slug>.bib` does not exist

## Pre-flight grill

After the refuse-if checks pass, offer **style calibration** once
(`shared/prompts/style_calibration.md`) — match the user's voice from 1–3 prior
papers. Recommend accepting: a calibrated voice with rhythm anchors is the
strongest positive lever against AI-flavored prose. The user may still skip. Then run the interview protocol in
`shared/prompts/grill_protocol.md` before Step 1 of Procedure. If
`interview_drafting:` is already present in research-state frontmatter,
skip the interview and proceed.

**Essentials** (ask in this order, one at a time):

1. **One-sentence contribution claim** — free-form. Recommended
   phrasing: synthesize a single sentence from `key_claims:`. Prefer the
   first claim with `audit_status: verified`; otherwise the first claim
   in the list. If `key_claims:` is empty, recommendation = "No basis in
   state; user pick is authoritative."
2. **Intended reader** — `AskUserQuestion`, header "Reader". Options:
   theorists / applied ML practitioners / domain statisticians / mixed.
   Recommended = inferred from `venue_target:` — NeurIPS/ICML → applied
   ML practitioners; JMLR/AoS → theorists; AISTATS → mixed.
3. **Tone / framing** — `AskUserQuestion`, header "Tone". Options:
   formal-proof-heavy / empirical-results-forward / framework-paper /
   hybrid. Recommended = inferred from the ratio of `theory_targets:`
   (with `must_have: true`) to the number of distinct experiments in
   `toy-design` + `ablation-plan` outputs. Theory-dominant → formal-proof;
   experiment-dominant → empirical-results; roughly equal → hybrid.
4. **Proactive weaknesses** — free-form. Recommended phrasing: list the
   top 1–3 `red_team_findings:` with `severity: high` (or
   `severity: medium` if no high-severity findings exist) as the default
   answer. User can replace.

On `Proceed`, append an `interview_drafting:` block to research-state
frontmatter per the protocol's persistence rules. Use the answers as
drafting context throughout Procedure:

- The contribution claim becomes the thesis sentence reused verbatim or
  near-verbatim in Abstract, Introduction (opening + contributions
  bullets), and Conclusion.
- Reader controls jargon level and what gets defined vs assumed.
- Tone controls per-section voice (formal-proof → more
  `\begin{theorem}`-driven prose; empirical-results-forward → results
  tables introduced earlier and more prominently; framework-paper →
  Method section emphasizes the framework's interfaces).
- Proactive weaknesses seed the Limitations section — written as
  paragraphs, one per failure case (prose_hygiene §F; not a bullet
  dump) — and may also trigger defensive moves in Method / Experiments
  (e.g., a stated failure case becomes an explicit subsection rather
  than a glossed caveat).

## Procedure

1. **One section at a time**. Emit, checkpoint with the user, then next.
   Do not emit all sections in one pass — Claude's coherence degrades and
   you will end up rewriting.

2. **Per-section protocol**:
   - Restate the outline bullets for this section.
   - Identify which bibkeys are needed; verify each is in the `.bib`.
   - Draft the section **as connected prose**. The outline's bullets are a
     content checklist, not a paragraph plan: merge, reorder, and connect
     them so transitions carry the argument. Do not expand one bullet into
     one paragraph in order, and do not let bullets survive as `itemize` —
     list environments only in the §F slots of `prose_hygiene.md`
     (Intro contributions, enumerated assumptions, pseudocode).
   - Run a self-check:
     - Every `\cite{key}` resolves in `.bib` — verify with the script, not
       by eye: `uv run python skills/paper-writer/scripts/check_tex.py
       paper/main.tex --bib refs/<slug>.bib` (rule 4 of
       `execution_discipline.md`; paste its result line)
     - Every named theorem either proved here or cited
     - Notation consistent with `docs/notation-<slug>.md` (add new symbols
       to the notation file as introduced)
     - Prose hygiene pass — `stop-slop` skill if available, then the
       academic overlay `shared/prompts/prose_hygiene.md`. Kill the
       structural AI tells (binary contrasts, false agency like "the data
       reveals", vague declaratives) and the §F format tells (lists outside
       the allowed slots, pseudo-list `\paragraph` runs, outline residue),
       not just filler words. Mechanical subset via script, not by eye:
       `uv run python skills/paper-writer/scripts/check_prose.py
       paper/sections/<n>-<name>.tex` — paste its result line; fix blocking
       findings or state the waiver (e.g. "Intro contribution bullets, §F
       slot") before saving.
   - Save as `paper/sections/<n>-<name>.tex`.

3. **Section ordering** (for efficiency):
   1. **Notation + Setup** (Section 2) — most constrained, foundational
   2. **Method** (Section 3) — directly from algorithm card
   3. **Theory** (Section 4) — from `theory-scoping`
   4. **Experiments** (Section 5) — from `toy-design` + `ablation-plan`;
      generate plots with `scripts/figs.py` (consistent vector-PDF style;
      plot only real results, never invented numbers)
   5. **Related Work** — after Method so positioning is clear
   6. **Introduction** — after the body; hooks land cleaner
   7. **Abstract** — last
   8. **Discussion + Limitations** — from `red-team`

4. **Math discipline**:
   - Numbered theorems, lemmas, corollaries with consistent prefixes
     (`thm:coverage`, `lem:dml-orthogonal`)
   - Equations numbered only if cross-referenced; otherwise unnumbered
   - Notation collected in `docs/notation-<slug>.md`; reuse, don't reintroduce

5. **Voice**:
   - Active voice for *what we do*: "We prove that..."
   - Past tense for *what we did*: "We evaluated on..."
   - Avoid "to the best of our knowledge" hedging; use specific
     references to prior art
   - Avoid AI-typical hedge stacks ("It is worth noting that..."); cut
     wherever possible

6. **Anti-sycophancy in draft itself**:
   - Limitations section must mention concrete failure cases (from
     `red-team`), not generic "future work" filler
   - Related work must articulate Δ, not just enumerate citations
   - No "novel" or "first" without specific scope

## Output

`paper/main.tex` glue file + `paper/sections/*.tex` per section.

Glue:
```latex
\documentclass{neurips_2026}    % or icml, jmlr, etc.
\usepackage{...}
\input{sections/01-introduction}
\input{sections/02-setup}
\input{sections/03-method}
\input{sections/04-theory}
\input{sections/05-experiments}
\input{sections/06-related}
\input{sections/07-discussion}
\bibliography{../refs/<slug>}
```

## After full draft

Before declaring "draft done", in order:

1. `citation-audit` — must be clean (no `fabricated` / `contradicts`);
   its Stage 0 static check (`check_tex.py`) must also be clean.
2. `scripts/build_paper.sh compile paper/main.tex` — the draft must build.
3. `self-review` — one venue-reviewer pass; feed findings into `revision`.
4. `submission-check` — the gate to `final`.

## State update

```yaml
stage: drafting
draft: paper/main.tex
```

When all sections checkpointed and `citation-audit` clean:
```yaml
stage: revision
```

## Exit checklist

Verify each item before declaring the draft done; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Grill ran or the skip notice shown; style calibration offered once.
- [ ] Every section drafted via the Step 2 per-section protocol,
      checkpointed with the user, and saved under `paper/sections/`.
- [ ] `check_tex.py` ran on the full draft with real output pasted — no
      undefined cites/refs, no missing figures.
- [ ] Notation file carries every symbol introduced; no symbol was
      reintroduced with a different meaning.
- [ ] Prose-hygiene pass ran per section (stop-slop if available, then
      `prose_hygiene.md`), and `check_prose.py` ran per section with its
      result line pasted — every blocking finding fixed or explicitly
      waived as a §F slot.
- [ ] No section is a bullet-expansion of its outline: outline bullets were
      dissolved into connected paragraphs; lists appear only in §F slots.
- [ ] Limitations names concrete failure cases from `red-team`; Related
      Work articulates Δ per work; no unscoped "novel"/"first".
- [ ] The After-full-draft sequence (audit → compile → self-review →
      submission-check) was scheduled with the user.
- [ ] State updated: `stage: drafting`, `draft: paper/main.tex`.
