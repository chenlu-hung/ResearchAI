---
name: paper-writer
description: Venue-aware academic paper drafting for Stats/ML algorithm papers. Modes for outline, full-draft, revision, and citation-audit. Loads venue profiles (NeurIPS, ICML, JMLR, AISTATS, Annals of Stats) for style and reviewer-expectation tailoring. Includes a Semantic-Scholar-based citation auditor that flags fabricated or mismatched references before submission.
---

# paper-writer

Borrows the staged-pipeline + integrity-gate concept from ARS, rewritten
from scratch (no copied prompts or code). Tightly integrated with
`algo-brainstorm` — refuses to emit a full draft if `red-team` flagged
blocking findings.

## When to invoke

- "Draft my method section for X"
- "Outline a NeurIPS paper from my algorithm card"
- "Audit my citations"
- "Help me revise the intro"
- `/write <mode>` slash command

## When NOT to invoke

- Idea is not yet formalized → run `algo-brainstorm` first
- Need new literature → `literature-explorer`

## Modes

| Mode | Purpose | Mode file |
|------|---------|-----------|
| `outline` | Section-by-section outline tailored to venue | `modes/outline.md` |
| `full-draft` | Section-by-section draft from algorithm card + outline | `modes/full-draft.md` |
| `revision` | Targeted edits to a specific section | `modes/revision.md` |
| `citation-audit` | Verify each citation exists and supports the claim | `modes/citation-audit.md` |

## Hard discipline

1. **Pre-flight check**: on entry, read research state. Refuse to emit
   a full draft if:
   - `algorithm_card` is missing
   - `red-team` mode has any `blocking: true` finding unresolved
   - For experimental claims: `toy-design` or `ablation-plan` missing

   Outline mode is more permissive (can run after `formalize` + `novelty-check`).

2. **Venue conformance**: read `shared/venue_profiles.md`. The profile
   dictates page limit, bib style, theory depth, required sections.

3. **No fabricated citations**: every `\cite{key}` must be in the
   `refs/<slug>.bib` file produced by `literature-explorer`. If a
   key is not in the bib, refuse to use it or mark `[BIBKEY MISSING — verify]`.

4. **Citation-claim consistency**: when citing a paper to support a
   claim, the cited paper must actually contain the claim. The
   `citation-audit` mode is the gate that verifies this.

5. **Math notation consistency**: maintain a notation table at the top
   of the draft (`docs/notation-<slug>.md`); reuse symbols across sections.

## Style files

`style/neurips.md`, `style/icml.md`, `style/jmlr.md`, `style/aistats.md`
— each has section templates, prose tone, and venue-specific dos/don'ts.

## Citation audit

`scripts/verify_citations.py` reads a `.bib` file, queries Semantic Scholar
for each entry, and reports:

- `verified` — paper exists with matching title + first author + year
- `mismatched` — paper exists but metadata differs (likely wrong key or
  typo)
- `fabricated` — no paper matches; suspect hallucination
- `unreachable` — API failure, retry

Output JSON to `.research-state/<slug>-audit-<date>.json`.

After API verification, the LLM does a second pass: for each `verified`
citation that is invoked in the draft, check whether the *paper's
abstract or known content* actually supports the *claim it is cited for*.
Flag mismatches.

## State integration

Writes:

- `paper/main.tex` (and `paper/sections/*.tex`)
- `docs/notation-<slug>.md`
- Updates `draft:` field in research state
- Flips `key_claims[*].audit_status` to `verified` after citation audit

Reads everything else.
