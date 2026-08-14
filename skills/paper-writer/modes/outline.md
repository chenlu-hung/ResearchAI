# Mode: outline

**Purpose**: produce a section-by-section outline for the target venue,
populated with the algorithm-card contents.

## Inputs

- `algorithm_card` from research state (required)
- `venue_target` (required)
- A validated current evidence packet for the selected candidate and key claims
- Optional: target subsection length budget

## Procedure

0. **Validate evidence state.** Follow
   `shared/prompts/evidence_grounding.md` and
   `shared/prompts/research_lifecycle.md`. The packet fingerprint must match the
   selected candidate's primitives, objective/estimand, data regime, and claim
   set. Method freeze, applicable experiment/protocol/results ingest, evidence
   audit, and results-aware red-team artifacts/hashes must pass (or carry valid
   theory-only N/A status). Migrate legacy artifacts additively; do not treat
   them as proof. Missing/stale gates block the paper outline artifact.

1. **Load venue profile**. Section template + page budget determines the
   skeleton. If `venue_target` has no profile in `shared/venue_profiles.md`,
   stop and offer `venue-calibration` first; proceed unprofiled only if the
   user explicitly declines (then say every venue field is unverified).

2. **Map algorithm card → sections**. Each part of the card should land in
   a specific section:

   | Card section | Paper section |
   |---|---|
   | One-line description | Abstract opener; Intro paragraph 1 |
   | Problem (formalize) | Section 2 (Setup) |
   | Algorithm (ideate + chosen) | Section 3 (Method) |
   | Contribution (novelty-check) | Intro paragraph 3; Related Work |
   | Guarantees (theory) | Section 4 (Theory) |
   | Cost (per-phase complexity) | Section 5 (Experiments) or a dedicated complexity subsection |
   | Empirical plan | Section 5 (Experiments) |
   | Open risks (red-team) | Limitations section |

   No card section may be left homeless — including **Cost**. The card's
   per-phase complexity (preprocessing/decomposition, training,
   calibration/adaptation, inference, plus the untested scaling regime) needs a
   named home in the paper, not a sentence dropped into Method.

3. **Produce outline**: nested markdown with bullets per section. For each
   subsection: 2–4 bullets describing what content goes there.

   **Every bullet tags the spine claim it advances** — `[S:claim-novelty-1]` for
   the primary, `[S:claim-limit-1]` for a supporting claim, read from `spine:` in
   state. A bullet that advances no spine claim is either cut or carries
   `[S:none — <one-line justification>]`. Untagged bullets are how a paper drifts
   away from its own contribution; the tags make the drift visible here rather
   than at review. If `spine:` is absent, stop: method freeze did not complete.

   For ML venues (NeurIPS / ICML / AISTATS), a **method/architecture figure** is
   a required outline element — name it, place it in a section, and budget its
   space. Its absence is flagged to the user as a venue risk, not silently
   accepted; `submission-check` later verifies it exists and is referenced.

   Every external
   or novelty-positioning bullet records its atomic claim ID and evidence-link
   IDs; its display citation comes from the generated BibTeX view. If outlining
   exposes a new claim or near-neighbor, persist a query, retrieve vault-first,
   and refresh the packet before keeping the bullet. Every empirical/result
   bullet instead records its evidence-audit entry and immutable result artifact
   hash; expected outcomes cannot populate a results bullet.

4. **Page budget allocation**: distribute the venue's page limit across
   sections, with rationale.

## Output

```markdown
# Outline: <Title> (target: NeurIPS 2026)

## Notation
- $X, Y$, $\mathcal{X}, \mathcal{Y}$, ...

## Page budget
- Abstract: 0.2pp
- Intro: 1.0pp
- Related Work: 0.8pp
- Setup: 1.0pp
- Method: 2.0pp
- Theory: 2.0pp
- Experiments: 1.5pp
- Discussion + Limitations: 0.5pp
- Total: 9pp

## Sections

### 1. Introduction
- Hook: the open problem in 2 sentences. [cite Tibshirani 2019, ...] [S:claim-novelty-1]
- What we do: 2-sentence summary. [S:claim-novelty-1]
- Contribution bullets:
  - C1: ... [S:claim-novelty-1]
  - C2: ... [S:claim-limit-1]
  - C3: ... [S:claim-theory-2]
- Roadmap: 1 sentence. [S:none — navigational]

### 2. Setup
- Notation as in `formalize` block. [S:none — shared machinery]
- Assumptions A1–A3, each in plain English then math. [S:claim-theory-2]

### 3. Method
- 3a. Intuition (½ page) [S:claim-novelty-1]
- 3b. Figure 1: method/architecture diagram (required for ML venues) [S:claim-novelty-1]
- 3c. Algorithm 1 (pseudocode) [S:claim-novelty-1]
- 3d. Why this construction works in 1 paragraph [S:claim-novelty-1]

### 4. Theory
- Thm 4.1 (Coverage): ... [S:claim-theory-2]
- Proof in Appendix A; sketch here. [S:claim-theory-2]
- Discussion of assumptions. [S:claim-theory-2]

### 5. Experiments
- 5a. Toy (corroborates Thm 4.1) [S:claim-theory-2]
- 5b. Real data: ... [S:claim-novelty-1]
- 5c. Ablations: <table from `ablation-plan`> [S:claim-limit-1]
- 5d. Cost: per-phase complexity + the untested scaling regime [S:claim-novelty-1]

### 6. Discussion + Limitations
- Open risks from `red-team`. [S:none — required venue section]
```

## Council panel (opt-in)

When invoked with `--council`, get alternative structures from a multi-model panel before
committing to one outline. Follow `shared/prompts/council_panel.md`.

- **Panel prompt**: the venue + page budget + the algorithm-card → section mapping (Step 2),
  asking each member to propose a **section-by-section skeleton with a page-budget split**
  and a one-line rationale for any non-obvious ordering. Strip citations and convert any
  new factual/prior-art suggestion into a query before use.
- **Cross-review**: this is a ranking mode — run the anonymized review pass so members rank
  each other's skeletons for venue fit and narrative flow.
- **Synthesis**: produce one outline that takes the best structural choices, justified
  against the venue profile (not member popularity). Apply the Anti-sycophancy thin/overflow
  flags below to the *merged* outline. Citations and claims stay packet-grounded; panel
  skeletons contribute structure only.

## Anti-sycophancy

After producing outline, list:

- **≥1 section where content is thin** — content from the card doesn't
  cover the page budget; flag for the user to add experiments or theory
- **≥1 section where content is overflowing** — too much for the budget;
  flag what should move to appendix

## State update

```yaml
stage: outline
research_phase: drafting
draft: paper/outline.md
evidence_packet_id: packet-...
evidence_packet_hash: "<64-char-lowercase-sha256-hex>"
evidence_packet_status: current
lifecycle_gates:
  draft:
    status: draft
    artifact: paper/outline.md
    artifact_hash: "<64-char-lowercase-sha256-hex>"
```

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Venue profile loaded; the skeleton matches its section template.
- [ ] Exact candidate/claims packet is validated current; legacy `.bib` alone
      was not accepted.
- [ ] Every lifecycle gate through results-aware red team passed and artifact
      hashes match; valid theory-only N/A gates include audited proof artifacts.
- [ ] Every algorithm-card section is mapped to a paper section
      (Step 2 table complete — no card content homeless), **including Cost**.
- [ ] Every outline bullet carries a spine tag `[S:<claim-id>]` or an explicit
      `[S:none — <justification>]`; `spine:` was read from state, not invented.
- [ ] ML venue: a method/architecture figure is named, placed, and budgeted —
      or its absence was flagged to the user as a venue risk.
- [ ] Page budget allocated per section and sums to the venue limit.
- [ ] Every external/novelty-positioning bullet carries atomic claim and
      passage-link IDs; display bibkeys resolve in the generated view.
- [ ] Every empirical/result bullet maps to audited manifest artifacts and
      uncertainty; no expected curve is presented as an observation.
- [ ] New claims/near-neighbors triggered vault-first retrieval and packet refresh.
- [ ] ≥1 thin section and ≥1 overflowing section flagged (Anti-sycophancy).
- [ ] State updated: `stage: outline`, `draft: paper/outline.md`.
