# Mode: full-draft

**Purpose**: produce a complete LaTeX draft from the algorithm card and
outline. This is the heaviest mode; expect to iterate.

## Inputs

- Outline (required — run `outline` first if missing)
- Algorithm card
- Validated current evidence packet(s) for the selected candidate/key claims
- `refs/<slug>.bib` (generated view of packet canonical works)
- Notation file `docs/notation-<slug>.md` (will create if absent)

## Pre-flight

Refuse if:

- `red-team` has `blocking: true` findings unresolved
- Outline does not exist
- Evidence packet is missing/stale/invalid or mismatches the current candidate
- Any lifecycle gate through evidence audit/results-aware red team is
  missing/stale/failing or has a mismatched artifact hash
- Generated `refs/<slug>.bib` does not exist or is out of sync with canonical works

Before the grill, run the deterministic `export bibtex` command in
`paper-writer/SKILL.md` via the absolute `$EVIDENCECTL`, recompute
`citations_view_hash`, and invalidate prior citation/static audits if it changed.

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
   phrasing: synthesize a single sentence from `key_claims:` whose claim ID and
   passage links occur in the current packet. Prefer an already-audited claim
   when available. If no grounded key claim exists, recommendation = "No
   grounded basis in state; retrieve evidence before drafting."
2. **Intended reader** — use the host's interactive question mechanism,
   header "Reader". Options:
   theorists / applied ML practitioners / domain statisticians / mixed.
   Recommended = inferred from `venue_target:` — NeurIPS/ICML → applied
   ML practitioners; JMLR/AoS → theorists; AISTATS → mixed.
3. **Tone / framing** — use the host's interactive question mechanism,
   header "Tone". Options:
   formal-proof-heavy / empirical-results-forward / framework-paper /
   hybrid. Recommended = inferred from the ratio of `theory_targets:`
   (with `must_have: true`) to the number of distinct experiments in
   `toy-design` + `ablation-plan` outputs. Theory-dominant → formal-proof;
   experiment-dominant → empirical-results; roughly equal → hybrid.
4. **Proactive weaknesses** — free-form. Recommended phrasing: list the
   top 1–3 `red_team_findings:` with `severity: high` (or
   `severity: medium` if no high-severity findings exist), plus any
   `reviewer_intel:` objection that applies to this paper, as the
   default answer. User can replace.

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
   Do not emit all sections in one pass; bounded checkpoints protect
   cross-section consistency and make evidence changes visible.

2. **Per-section protocol**:
   - Restate the outline bullets for this section.
   - Decompose proposed substantive sentences into atomic claim IDs. Resolve
     each to evidence-link/source-version IDs in the current packet, then map
     canonical works to display bibkeys in the generated `.bib`.
   - For experimental/numeric claims, resolve each to the audited result
     manifest's run/artifact hashes, metric, split/population, estimate and
     uncertainty, and frozen decision rule. Expected curves are never prose
     evidence.
   - If a needed claim/link is missing or a new near-neighbor appears, stop the
     section: persist a query, run vault-first then external retrieval, inspect
     passages, and freeze a replacement packet. Never fill the gap from memory.
   - Draft the section **as connected prose**. The outline's bullets are a
     content checklist, not a paragraph plan: merge, reorder, and connect
     them so transitions carry the argument. Do not expand one bullet into
     one paragraph in order, and do not let bullets survive as `itemize` —
     list environments only in the §F slots of `prose_hygiene.md`
     (Intro contributions, enumerated assumptions, pseudocode).
   - Run a self-check:
     - Every `\cite{key}` resolves in `.bib` — verify with the script, not
       by eye: `python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_tex.py"
       paper/main.tex --bib refs/<slug>.bib` (rule 4 of
       `execution_discipline.md`; paste its result line)
     - Every substantive citing sentence maps to an atomic claim and stable
       passage link in the refreshed packet; abstract-only is not `supports`
     - Every empirical claim maps to the current manifest/evidence-audit entry;
       no selective omission of failed/excluded runs or protocol deviations
     - Every named theorem either proved here or cited
     - Notation consistent with `docs/notation-<slug>.md` (add new symbols
       to the notation file as introduced)
     - Prose hygiene pass — `stop-slop` skill if available, then the
       academic overlay `shared/prompts/prose_hygiene.md`. Kill the
       structural AI tells (binary contrasts, false agency like "the data
       reveals", vague declaratives) and the §F format tells (lists outside
       the allowed slots, pseudo-list `\paragraph` runs, outline residue),
       not just filler words. Mechanical subset via script, not by eye:
       `python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_prose.py"
       paper/sections/<n>-<name>.tex` — paste its result line; fix blocking
       findings or state the waiver (e.g. "Intro contribution bullets, §F
       slot") before saving.
   - Save as `paper/sections/<n>-<name>.tex`.

3. **Section ordering** (for efficiency):
   1. **Notation + Setup** (Section 2) — most constrained, foundational
   2. **Method** (Section 3) — directly from algorithm card. For ML venues
      (NeurIPS/ICML/AISTATS) a **method/architecture figure** is required: draw
      it, reference it in the text, and place it before the pseudocode.
      Reviewers read the figure before the prose; its absence costs clarity
      scores. Flag to the user if the outline did not plan one.
   3. **Theory** (Section 4) — from `theory-scoping`
   4. **Experiments** (Section 5) — from `toy-design` + `ablation-plan`;
      generate plots with `uv run --project "$PLUGIN_ROOT" --extra figures
      python "$PLUGIN_ROOT/skills/paper-writer/scripts/figs.py"` (consistent
      vector-PDF style; plot only real results, never invented numbers)
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
   - Weaknesses do not replace grounded closest-prior comparisons
   - Application-only deltas are described as application contributions, never
     method novelty

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

Before declaring the write phase complete, in order:

1. Run `python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_tex.py"
   paper/main.tex --bib refs/<slug>.bib` and
   `"$PLUGIN_ROOT/skills/paper-writer/scripts/build_paper.sh" compile
   paper/main.tex`; fix
   static/rendering failures before scientific review.
2. Run `self-review` against the current draft/upstream hashes. It creates the
   scientific-review artifact as `conditional` (or `fail`) and routes blocking
   findings through `revision`.
3. Run `citation-audit` against that current self-review artifact and draft. It
   completes the composite scientific-review gate only when metadata and every
   invoked substantive claim's passage support are clean.
4. Run `submission-check` only after the composite scientific-review gate is
   `pass`; this is the gate to `final`.

## State update

```yaml
stage: drafting
research_phase: drafting
draft: paper/main.tex
evidence_packet_id: packet-...
evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
evidence_packet_status: current
lifecycle_gates:
  draft:
    status: pass
    artifact: paper/main.tex
    artifact_hash: "<64-char-lowercase-sha256-hex>"
  scientific_review:
    status: stale
```

When all sections are checkpointed and the draft/static checks pass:
```yaml
stage: revision
```

## Exit checklist

Verify each item before declaring the draft done; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Grill ran or the skip notice shown; style calibration offered once.
- [ ] Current packet matches the candidate primitives, objective/estimand,
      data regime, and claims; generated BibTeX view is synchronized.
- [ ] Lifecycle method/protocol/result/audit/red-team gates revalidated against
      their artifact hashes; real results or valid theory-only proof audit exist.
- [ ] Every section drafted via the Step 2 per-section protocol,
      checkpointed with the user, and saved under `paper/sections/`.
- [ ] `check_tex.py` ran on the full draft with real output pasted — no
      undefined cites/refs, no missing figures.
- [ ] ML venue: method/architecture figure drawn, placed in Method, and
      referenced in the text — or its absence flagged to the user.
- [ ] Per-phase complexity from the card's Cost section landed in the section
      the outline assigned it; no aggregate-only bound.
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
- [ ] Every substantive literature-backed sentence has atomic claim,
      source-version, locator, and evidence-link provenance; new claims or
      near-neighbors triggered retrieval and a replacement packet.
- [ ] Every empirical/numeric sentence traces to audited result artifact hashes,
      metric/split/uncertainty and protocol rule; expected outcomes were not drafted as results.
- [ ] The After-full-draft sequence (audit → compile → self-review →
      submission-check) was scheduled with the user.
- [ ] State updated: `stage: drafting`, `draft: paper/main.tex`.
- [ ] Draft hash recorded; scientific-review/submission gates marked stale until rerun.
