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

## Procedure

1. **One section at a time**. Emit, checkpoint with the user, then next.
   Do not emit all sections in one pass — Claude's coherence degrades and
   you will end up rewriting.

2. **Per-section protocol**:
   - Restate the outline bullets for this section.
   - Identify which bibkeys are needed; verify each is in the `.bib`.
   - Draft the section.
   - Run a self-check:
     - Every `\cite{key}` resolves in `.bib`
     - Every named theorem either proved here or cited
     - Notation consistent with `docs/notation-<slug>.md` (add new symbols
       to the notation file as introduced)
   - Save as `paper/sections/<n>-<name>.tex`.

3. **Section ordering** (for efficiency):
   1. **Notation + Setup** (Section 2) — most constrained, foundational
   2. **Method** (Section 3) — directly from algorithm card
   3. **Theory** (Section 4) — from `theory-scoping`
   4. **Experiments** (Section 5) — from `toy-design` + `ablation-plan`
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

Trigger `citation-audit` mode before declaring "draft done".

## State update

```yaml
stage: drafting
draft: paper/main.tex
```

When all sections checkpointed and `citation-audit` clean:
```yaml
stage: revision
```
