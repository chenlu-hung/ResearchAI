# Algorithm Card Schema

A single-page snapshot of an algorithm under development. Lives at
`docs/algo-card-<slug>.md` and is updated by every `algo-brainstorm` mode.
Bring this to advisor meetings, take it into your paper outline, paste
the relevant rows into the paper's Method section.

## Template

```markdown
# Algorithm Card: <Name> (v<rev>)

**Slug**: <slug>
**Last updated**: <YYYY-MM-DD>
**Stage**: <stage from research_state>
**Venue target**: <venue>

## One-line description

<single sentence: what does it do, in one breath>

## Problem (from `formalize`)

- **Setup**: $(X, Y) \sim P$, $n$ i.i.d. samples
- **Estimand**: $\theta^* = ...$ (or $C^*$, $f^*$)
- **Loss / construction**: $\hat{\theta} = \arg\min ...$
- **Assumptions**:
  - (A1) ...
  - (A2) ...

## Algorithm (from `ideate` + chosen candidate)

- **Core idea** (1 sentence): ...
- **Primitive**(s): cross-fitting / weighted quantile / DML / ...
- **Steps**:
  1. ...
  2. ...
  3. ...
- **Hyperparameters**: $\alpha, K, ...$

## Contribution (from `novelty-check`)

- **Closest prior**: [bibkey1, bibkey2, bibkey3]
- **Δ in one paragraph**: ...

## Guarantees (from `theory-scoping`)

| Theorem | Statement | Technique | Status |
|---------|-----------|-----------|--------|
| Coverage | ... | DML | conjecture |
| Rate | ... | empirical process | proof outline |

## Cost

- Time: $O(...)$
- Memory: $O(...)$

## Empirical plan (from `toy-design` + `ablation-plan`)

- **Toy**: <ref to toy spec>
- **Real data**: <list>
- **Baselines**: ...
- **Primary metric**: ...
- **Seeds**: ...

## Open risks (from `red-team`)

- [ ] ...
- [ ] ...

## Decisions log

| Date | Decision | Why |
|------|----------|-----|
| 2026-05-17 | Picked candidate 1 over candidate 3 | Theory cleaner; toy expected to work |
```

## Rules

1. **Always one page**. Edit ruthlessly. If it doesn't fit on one screen,
   you don't yet understand the contribution well enough.
2. **Newer revisions**: append a new section "## Revision history" at the
   bottom; do not overwrite without a record.
3. **One card per chosen candidate**. If you pursue two candidates,
   maintain two cards (e.g., `algo-card-<slug>-A.md`, `-B.md`) until one
   is dropped.
4. **Cross-link with research_state**: the `algorithm_card:` field in
   research_state always points to the current canonical card.
