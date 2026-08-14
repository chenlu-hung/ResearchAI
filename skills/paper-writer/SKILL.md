---
name: paper-writer
description: Venue-aware academic paper drafting for Stats/ML algorithm papers. Modes for positioning-skeleton (write the intro, related work, and empty result-table shells before running experiments), outline, full-draft, revision, citation-audit, post-mortem (turn a rejection's reviews into lifecycle-gate fixes), and grant-nstc (國科會專題研究計畫 CM03 proposals). Loads venue profiles (NeurIPS, ICML, JMLR, AISTATS, Annals of Stats) for style and reviewer-expectation tailoring. Includes a Semantic-Scholar-based citation auditor that flags fabricated or mismatched references before submission.
---

# paper-writer

## Plugin-root contract

Resolve the absolute path of this already loaded `SKILL.md`, then set
`PLUGIN_ROOT` to the directory two levels above its containing skill directory
(`.../skills/paper-writer/../..`). Never infer the plugin location from the
user's working directory and do not `cd` into the plugin. Resolve `shared/...`
and `skills/...` resources against `$PLUGIN_ROOT`; resolve bare `modes/...`,
`scripts/...`, and `style/...` paths against this skill directory. Project
artifacts such as `.research-state/`, `docs/`, `paper/`, `refs/`, and `results/`
remain relative to the user's project. Dependency-bearing Python scripts use
`uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`; stdlib-only
scripts use `python3 "$PLUGIN_ROOT/<path>"`; invoke bundled shell scripts by
their absolute `$PLUGIN_ROOT/...` path.

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
- "幫我寫國科會計畫書" / "Draft my NSTC proposal"
- Claude Code: `/research-assistant:write <mode>`
- Codex: invoke `$research-ai:paper-writer` and name the mode

## When NOT to invoke

- Idea is not yet formalized → run `algo-brainstorm` first
- Need new literature → `literature-explorer`

## Modes

| Mode | Purpose | Mode file |
|------|---------|-----------|
| `positioning-skeleton` | Intro/related/contributions + empty result-table shells, **before** experiments | `modes/positioning-skeleton.md` |
| `outline` | Section-by-section outline tailored to venue | `modes/outline.md` |
| `full-draft` | Section-by-section draft from algorithm card + outline | `modes/full-draft.md` |
| `revision` | Targeted edits to a specific section | `modes/revision.md` |
| `citation-audit` | Verify each citation exists and supports the claim | `modes/citation-audit.md` |
| `self-review` | One-pass venue-reviewer critique of the draft | `modes/self-review.md` |
| `submission-check` | Submission-readiness gate before `final` | `modes/submission-check.md` |
| `venue-calibration` | Add or re-verify a venue profile from official sources + optional exemplar papers | `modes/venue-calibration.md` |
| `post-mortem` | Turn a rejection's reviews into gate attributions and pipeline changes | `modes/post-mortem.md` |
| `grant-nstc` | Draft/revise an NSTC (國科會) 專題研究計畫 CM03 — vision + feasibility register, review-weight-aware | `modes/grant-nstc.md` |

## Hard discipline

0. **Execution discipline**: follow `shared/prompts/execution_discipline.md`
   in every mode — steps in order, Exit checklist before emitting, scripts
   run for real (never simulated), exhaustive checklist walks.
   Literature-backed prose also follows
   `shared/prompts/evidence_grounding.md`: vault first, external retrieval
   second, atomic claim-to-passage links, then a current packet.

1. **Pre-flight check**: on entry, read research state. Refuse to emit
   a positioning outline or full draft if:
   - `algorithm_card` is missing
   - `red-team` mode has any `blocking: true` finding unresolved
   - For experimental claims: `toy-design` or `ablation-plan` missing
   - The candidate/claim evidence packet is missing, stale, invalid, or does
     not match current primitives, objective/estimand, data regime, and claims
   - Any required lifecycle gate through `lifecycle_gates.evidence_audited` and
     `lifecycle_gates.results_red_team` is missing/stale/failing, or its artifact hash does not
     match. Validate `shared/prompts/research_lifecycle.md`; empirical work needs
     real ingested results, while theory-only work needs valid N/A rationale and
     audited proof artifacts.

   **`positioning-skeleton` exemption**: that mode — and only that mode — is
   exempt from the results-gate bullet above (experiment contract, protocol,
   results ingest, evidence audit, results-aware red team). It is the one mode
   that legally runs before results exist, and it pays for that by being
   forbidden a results section and any numeric cell. Every other pre-flight
   condition (method freeze frozen with a spine, current packet, synced `.bib`,
   no unresolved blocking red-team finding) applies to it in full. `outline` and
   `full-draft` gating is unchanged.

   Beyond that exemption, `outline` mode's
   paper artifact cannot pass its lifecycle gate until method/result evidence
   and results-aware red team pass. Legacy survey or `.bib` paths trigger
   additive migration; they never clear a gate alone.

2. **Venue conformance**: read `shared/venue_profiles.md`. The profile
   dictates page limit, bib style, theory depth, required sections.
   No profile for `venue_target` → offer `venue-calibration` before
   drafting (`shared/prompts/venue_calibration.md`); fields listed in a
   profile's `unverified:` never hard-FAIL a gate (WARN + re-calibrate).

3. **Canonical citations**: `refs/<slug>.bib` is a generated view of canonical
   vault works. Every `\cite{key}` must resolve in that view, but key existence
   is necessary only for rendering—not evidence of claim support. Regenerate
   the view deterministically after canonical work metadata changes; never use
   model generation or hand editing as the authority. Resolve `EVIDENCECTL` to
   the absolute plugin entrypoint as specified in `evidence_grounding.md`, then run:

   ```bash
   python3 "$EVIDENCECTL" export bibtex --vault "$VAULT" \
     --topic "$TOPIC_ID" --out "refs/<slug>.bib"
   ```

   Recompute `citations_view_hash` and compare it with state before drafting or
   audit; any change makes prior static/metadata audit output stale.

4. **Citation-claim consistency**: every substantive cited sentence must map
   to an atomic claim and stable locator/passage in the current packet.
   Abstract-only material cannot receive `verified`, `supports`, or
   `contradicts`. `citation-audit` is the
   gate that checks both metadata/rendering and those links.

5. **Math notation consistency**: maintain a notation table at the top
   of the draft (`docs/notation-<slug>.md`); reuse symbols across sections.

6. **Prose hygiene (no AI tells)**: on every drafted or edited prose
   section, before saving, run the `stop-slop` skill if available, then
   the academic overlay `shared/prompts/prose_hygiene.md` (adds ML/Stats
   tells and the exceptions that stop stop-slop's essay rules from harming
   a paper — passive voice, technical adverbs, three-item lists). The
   overlay is self-contained, so the pass still works when `stop-slop` is
   absent. This catches the structural "AI smell" (binary contrasts, false
   agency, vague declaratives) and the format-level smell (§F list budget:
   bullets only in conventional slots, no pseudo-list `\paragraph` runs),
   not just filler words. The mechanical subset is verified by
   `scripts/check_prose.py`, not by eye — paste its result line per section.

7. **Submission gate**: never advance `stage` to `final` until
   `submission-check` passes, the latest `citation-audit` is clean, and a
   scientific-review artifact bound to the current draft and upstream hashes
   has verdict `pass`.

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

After API verification, the claim-support pass resolves each invoked atomic
claim to its exact canonical source version and locator/passage. It validates
the persisted evidence link; model knowledge and abstracts are insufficient.

## Scripts

- `scripts/verify_citations.py` — dependency-bearing citation audit (above):
  `uv run --project "$PLUGIN_ROOT" python
  "$PLUGIN_ROOT/skills/paper-writer/scripts/verify_citations.py" ...`.
- `scripts/check_tex.py` — static cross-checks, no LaTeX needed: every
  `\cite` resolves in the `.bib`, every `\ref` has a `\label`, figure files
  exist, venue `must_include` tokens present, and — with
  `--abstract-word-limit N` from the venue's `abstract_word_limit` — the
  abstract is within its word budget. Stage 0 of `citation-audit`;
  evidence source for `submission-check`; run after every draft/revision.
- `scripts/check_prose.py` — deterministic prose-format lint (the
  mechanical subset of `prose_hygiene.md`): §F list budget and density,
  pseudo-list `\paragraph`/bold-label runs, §A banned phrases, em-dash
  rate, rhythm-uniformity warnings. Evidence for the per-section hygiene
  pass, `self-review`'s AI-tell scan, and `submission-check` item 9; run
  alongside `check_tex.py` after every draft/revision. Both are stdlib-only:
  `python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/<script>.py" ...`.
- `scripts/figs.py` — one colorblind-safe, vector-PDF figure style for
  experiment/ablation plots; import and adapt to real results, never invent
  numbers. `uv run --project "$PLUGIN_ROOT" --extra figures python
  "$PLUGIN_ROOT/skills/paper-writer/scripts/figs.py"` (needs the `figures`
  extra).
- `scripts/build_paper.sh` — `compile` (build gate; non-zero if it won't
  build) and `docx` (lossy LaTeX→DOCX export for co-authors via pandoc); invoke
  as `"$PLUGIN_ROOT/skills/paper-writer/scripts/build_paper.sh" <mode> ...`.
- `scripts/check_venues.py` — consistency check for the venue-knowledge
  triple (`venue_profiles.md` Defaults ↔ prose sections ↔ `style/` files ↔
  `check_tex.py` tokens) + provenance (`as_of`/`sources`) and staleness.
  Run after every `venue-calibration`; evidence for `submission-check`.

## Drafting aids

- **Style calibration** (recommended): `shared/prompts/style_calibration.md` —
  `full-draft` matches your voice and rhythm anchors from 1–3 prior papers;
  the strongest positive lever against AI-flavored prose (soft guidance,
  never overrides venue style or anti-hallucination).
- **Prose hygiene**: `shared/prompts/prose_hygiene.md` — AI-tell checklist
  applied per section (see hard discipline #6).

## State integration

Writes:

- `paper/main.tex` (and `paper/sections/*.tex`), `paper/figures/*.pdf`
- `docs/notation-<slug>.md`
- `style_profile:` (if style calibration run)
- Updates `draft:` field in research state
- Reads/writes packet/link IDs and status, without duplicating vault evidence
- Flips `key_claims[*].audit_status` to `verified` only after metadata and
  passage-support audit
- Writes hashed draft/scientific-review/submission lifecycle gate pointers;
  every revision invalidates review/submission bound to the old draft hash
- `paper/skeleton/` + the hashed `positioning_skeleton` gate (directory hash)
- `docs/post-mortem-<slug>-<date>.md` and an **append-only** `post_mortems:`
  entry; `post-mortem` may also move `research_phase` backwards out of `final`
  to the earliest gate its findings invalidate (the one sanctioned post-final
  transition — see `shared/prompts/research_lifecycle.md`)

Reads everything else.

## Council panel (opt-in)

`outline` and `self-review` can convene a multi-model panel — Codex, Gemini, Claude, and
DeepSeek, each reached through its **own subscription/sign-in CLI** (no API keys), with this
session as chair. Pass `--council` (for example, Claude Code
`/research-assistant:write self-review --council`, or ask
`$research-ai:paper-writer` for `self-review` with a council in Codex) to turn
`self-review` into a real multi-reviewer panel, or `outline` into a structure bake-off;
without the flag both run single-model as documented above. Protocol and guardrails:
`$PLUGIN_ROOT/shared/prompts/council_panel.md` (engine:
`$PLUGIN_ROOT/shared/council.py`, stdlib-only —
`python3 "$PLUGIN_ROOT/shared/council.py"`).

**Requires** the member CLIs on PATH and signed in (`codex`, `agy`, `claude`, `opencode`);
missing ones drop out. The panel never bypasses evidence discipline: any work,
claim, or citation it proposes is stripped to a query/hypothesis and must complete
the vault-first retrieval/link/packet loop before it enters an outline or draft.
