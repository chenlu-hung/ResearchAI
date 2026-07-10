# Style: NeurIPS

## Section template

1. **Abstract** (~150 words): problem, approach, contribution (with one
   number if possible), implication. No equations.
2. **Introduction** (1.0 pp): hook → gap → contribution bullets (3–5) → roadmap.
3. **Related Work** (0.5–1.0 pp): organized by topic, not chronology. Each
   paragraph ends with the Δ against the cited cluster.
4. **Setup / Problem** (0.5–1.0 pp): notation, assumptions, formal goal.
5. **Method** (1.5–2.5 pp): intuition → pseudocode → justification.
6. **Theory** (1.0–2.0 pp, optional): theorems with proof sketch; full proofs in appendix.
7. **Experiments** (1.5–2.5 pp): toy, real data, ablations.
8. **Discussion + Limitations** (0.3–0.5 pp): honest, specific.
9. **Paper checklist** (mandatory, after references; not counted): every
   item answered honestly — reviewers read it. A separate "Broader Impacts"
   section is **not required** (as of 2026); cover societal impact where the
   checklist probes it.

Budget: 9 content pages at submission (figures/tables count; references,
appendices, checklist do not). Camera-ready gets +1.

## Tone

- Active voice, direct. "We propose..." not "It is proposed that..."
- Hedge sparingly. If you're confident, say so.
- No "to the best of our knowledge" — say what's new by Δ to prior work.
- Number every contribution bullet in the intro and use those numbers
  consistently (C1, C2, ...) in the rest of the paper.

## Reviewer expectations

- Will check arXiv for recent baselines (≤6 months). Include them.
- Will demand multi-seed empirical results with statistical significance.
- Will examine the ablation table for completeness.
- Limitations discussion must be specific (checklist probes it). Generic
  "could be misused" societal-impact boilerplate → automatic complaint.

## Don'ts

- No "novel" without scope (novel-relative-to-what?)
- No bare-number tables without significance testing
- No "we believe" / "we feel" — show, don't assert
- No more than 3 acronyms before they all blur
- No bulleted Related Work, Discussion, or Limitations — paragraphs;
  bullets only in the §F slots of `prose_hygiene.md` (intro contributions,
  enumerated assumptions, pseudocode)

## Compute reporting

State explicitly: GPU type + count, wall-clock per experiment, total
compute for the paper (the paper checklist asks for it; norm, unverified
as a standalone requirement).

## LLM / AI use (2026 policy)

If LLMs/agents are an important, original, or non-standard component of
the **method**, describe that in the experimental setup. Routine writing,
editing, and basic code assistance need no statement. LLMs cannot be
authors. Do not hide material use.
