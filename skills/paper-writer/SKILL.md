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
- "Review my draft like a reviewer would"
- "Is my paper submission-ready?"
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
| `self-review` | One-pass venue-reviewer critique of the draft | `modes/self-review.md` |
| `submission-check` | Submission-readiness gate before `final` | `modes/submission-check.md` |

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

6. **Prose hygiene (no AI tells)**: on every drafted or edited prose
   section, before saving, run the `stop-slop` skill if available, then
   the academic overlay `shared/prompts/prose_hygiene.md` (adds ML/Stats
   tells and the exceptions that stop stop-slop's essay rules from harming
   a paper — passive voice, technical adverbs, three-item lists). The
   overlay is self-contained, so the pass still works when `stop-slop` is
   absent. This catches the structural "AI smell" (binary contrasts, false
   agency, vague declaratives), not just filler words.

7. **Submission gate**: never advance `stage` to `final` until
   `submission-check` passes and the latest `citation-audit` is clean.

## Style files

`style/neurips.md`, `style/icml.md`, `style/jmlr.md`, `style/aistats.md`
— each has section templates, prose tone, and venue-specific dos/don'ts.

## Citation audit

`scripts/verify_citations.py` reads a `.bib` file and, per entry, queries
Semantic Scholar → OpenAlex → Crossref (a resolving DOI short-circuits to
`verified`; multi-source fallback avoids false `fabricated` on new preprints):

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

## Scripts

- `scripts/verify_citations.py` — citation audit (above). `uv run python ...`.
- `scripts/figs.py` — one colorblind-safe, vector-PDF figure style for
  experiment/ablation plots; import and adapt to real results, never invent
  numbers. `uv run --extra figures python ...` (needs the `figures` extra).
- `scripts/build_paper.sh` — `compile` (build gate; non-zero if it won't
  build) and `docx` (lossy LaTeX→DOCX export for co-authors via pandoc).

## Drafting aids

- **Style calibration** (optional): `shared/prompts/style_calibration.md` —
  `full-draft` can match your voice from 1–3 prior papers (soft guidance,
  never overrides venue style or anti-hallucination).
- **Prose hygiene**: `shared/prompts/prose_hygiene.md` — AI-tell checklist
  applied per section (see hard discipline #6).

## State integration

Writes:

- `paper/main.tex` (and `paper/sections/*.tex`), `paper/figures/*.pdf`
- `docs/notation-<slug>.md`
- `style_profile:` (if style calibration run)
- Updates `draft:` field in research state
- Flips `key_claims[*].audit_status` to `verified` after citation audit

Reads everything else.

## Council panel (opt-in)

`outline` and `self-review` can convene a multi-model panel — Codex, Gemini, Claude, and
DeepSeek, each reached through its **own subscription/sign-in CLI** (no API keys), with this
session as chair. Pass `--council` (e.g. `/write self-review --council`) to turn
`self-review` into a real multi-reviewer panel, or `outline` into a structure bake-off;
without the flag both run single-model as documented above. Protocol and guardrails:
`shared/prompts/council_panel.md` (engine: `shared/council.py`, stdlib-only —
`python3 shared/council.py`).

**Requires** the member CLIs on PATH and signed in (`codex`, `agy`, `claude`, `opencode`);
missing ones drop out. The panel never bypasses citation discipline — members do not share
`refs/<slug>.bib`, so any `\cite{...}` they emit is stripped or marked
`[BIBKEY MISSING — verify]`, per hard-discipline rule 3.
