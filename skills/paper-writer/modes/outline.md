# Mode: outline

**Purpose**: produce a section-by-section outline for the target venue,
populated with the algorithm-card contents.

## Inputs

- `algorithm_card` from research state (required)
- `venue_target` (required)
- Optional: target subsection length budget

## Procedure

1. **Load venue profile**. Section template + page budget determines the
   skeleton.

2. **Map algorithm card → sections**. Each part of the card should land in
   a specific section:

   | Card section | Paper section |
   |---|---|
   | One-line description | Abstract opener; Intro paragraph 1 |
   | Problem (formalize) | Section 2 (Setup) |
   | Algorithm (ideate + chosen) | Section 3 (Method) |
   | Contribution (novelty-check) | Intro paragraph 3; Related Work |
   | Guarantees (theory) | Section 4 (Theory) |
   | Empirical plan | Section 5 (Experiments) |
   | Open risks (red-team) | Limitations section |

3. **Produce outline**: nested markdown with bullets per section. For each
   subsection: 2–4 bullets describing what content goes there, with
   bibkey citations for any external references.

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
- Hook: the open problem in 2 sentences. [cite Tibshirani 2019, ...]
- What we do: 2-sentence summary.
- Contribution bullets:
  - C1: ...
  - C2: ...
  - C3: ...
- Roadmap: 1 sentence.

### 2. Setup
- Notation as in `formalize` block.
- Assumptions A1–A3, each in plain English then math.

### 3. Method
- 3a. Intuition (½ page)
- 3b. Algorithm 1 (pseudocode)
- 3c. Why this construction works in 1 paragraph

### 4. Theory
- Thm 4.1 (Coverage): ...
- Proof in Appendix A; sketch here.
- Discussion of assumptions.

### 5. Experiments
- 5a. Toy (corroborates Thm 4.1)
- 5b. Real data: ...
- 5c. Ablations: <table from `ablation-plan`>

### 6. Discussion + Limitations
- Open risks from `red-team`.
```

## Anti-sycophancy

After producing outline, list:

- **≥1 section where content is thin** — content from the card doesn't
  cover the page budget; flag for the user to add experiments or theory
- **≥1 section where content is overflowing** — too much for the budget;
  flag what should move to appendix

## State update

```yaml
stage: outline
draft: paper/outline.md
```
