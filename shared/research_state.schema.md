# Research State Schema

Every project this plugin touches keeps a single state file at:

```
<working-dir>/.research-state/<topic-slug>.md
```

This file is the **single source of truth** that connects literature exploration,
algorithm brainstorming, and paper writing across sessions. Each skill reads it
on entry and updates it on exit.

## File Format

YAML frontmatter (machine-readable) + markdown body (human-readable notes).
The frontmatter is authoritative; the body is for narrative.

### Frontmatter

```yaml
---
topic: "Conformal prediction under covariate shift"
slug: conformal-covariate-shift
venue_target: NeurIPS 2026
created: 2026-05-17
updated: 2026-05-17

stage: ideate
# one of:
#   explore | gap | formalize | ideate | novelty | theory
#   | toy | ablation | red-team | outline | drafting | revision | final

# --- artifacts ----------------------------------------------------
literature: docs/survey-conformal-covariate-shift.md
citations:  refs/conformal-covariate-shift.bib
algorithm_card: docs/algo-card-v3.md      # rolling, may be overwritten
draft: paper/main.tex                      # once paper-writer is engaged

# --- formalization (filled by algo-brainstorm `formalize` mode) ---
formalization:
  estimand: "P(Y ∈ C(X) | X ~ Q_target) ≥ 1-α"
  loss: "miscoverage + λ · |C(X)|"
  assumptions:
    - A1: "joint density ratio dQ/dP is bounded and known up to estimation"
    - A2: "exchangeability fails; covariate shift only (no label shift)"
  nuisance: ["density ratio w(x) = dQ/dP"]
  regularity: ["w(x) bounded above by M < ∞"]

# --- candidates (filled by `ideate`) ------------------------------
candidates:
  - id: cand-1
    name: "Weighted split conformal with cross-fitted density ratio"
    core_idea: "Reweight calibration scores by estimated w(x) with cross-fitting"
    primitive: "weighted quantile + DML cross-fitting"
    motivation: theoretical
    status: chosen
  - id: cand-2
    name: ...
    status: dropped
    drop_reason: "Reviewed Tibshirani 2019 — equivalent up to estimator choice"

# --- contribution claims (filled by `novelty-check`) --------------
key_claims:
  - claim: "First finite-sample marginal coverage guarantee under unknown w(x) without exchangeability."
    supporting_refs: [tibshirani2019conformal, lei2018distfree]
    audit_status: pending    # pending | verified | mismatched | fabricated

# --- theory targets (filled by `theory-scoping`) ------------------
theory_targets:
  - kind: coverage
    statement: "P(Y ∈ Ĉ(X)) ≥ 1 - α - O(n^{-1/4})"
    proof_technique: "DML + sample-splitting"
    must_have: true
  - kind: efficiency
    statement: "E[|Ĉ(X)|] → E[|C*(X)|] as n→∞"
    must_have: false

# --- red team findings (filled by `red-team`) --------------------
red_team_findings:
  - finding: "If w(x) estimation error is heavy-tailed, weighted quantile is not consistent."
    severity: high
    mitigation: "Truncate w(x) at quantile-based threshold; report sensitivity."

open_questions:
  - "Does the cross-fitting still work when w is estimated via NN?"
  - "Is there a label-shift extension?"
---
```

### Body (free-form notes)

After the frontmatter, append timestamped narrative entries. Skills append
new entries; they do not rewrite history.

```markdown
## 2026-05-17 — explore

(narrative produced by literature-explorer)

## 2026-05-17 — gap-analysis

(narrative produced by algo-brainstorm)
```

## Rules for Skills

1. **Read before doing**: every skill must read this file on entry. If a needed
   prior stage is empty (e.g., `paper-writer` invoked but `formalization` is
   blank), warn the user and offer to backfill.
2. **Atomic updates**: update only your own section. Never overwrite another
   skill's section without explicit user instruction.
3. **Stage transitions**: only advance `stage` when the user confirms.
4. **No silent deletion**: if dropping a candidate or claim, move it to a
   `dropped:` subsection with `drop_reason`, do not delete.
5. **Cross-references**: `audit_status` on `key_claims` is set by paper-writer's
   `citation-audit` mode; brainstorm modes must not touch it.

## Slug rules

- Lowercase, hyphen-separated
- Derived from topic; max 50 chars
- If collision, append `-v2`, `-v3`
