# research-assistant

A Claude Code plugin for Stats/ML researchers whose core output is **developing new algorithms**.

Three skills, each independently usable:

| Skill | Purpose | Trigger |
|---|---|---|
| `literature-explorer` | Multi-perspective survey of a topic; produces hierarchical outline + BibTeX. Calls `literature-review-ml` skill for retrieval. | `/explore <topic>` |
| `algo-brainstorm` | Eight-mode pipeline for going from "I have an idea" to "I have a contribution worth submitting". Modes: `gap-analysis`, `formalize`, `ideate`, `novelty-check`, `theory-scoping`, `toy-design`, `ablation-plan`, `red-team`. | `/algo <mode>` |
| `paper-writer` | Venue-aware drafting (NeurIPS, ICML, JMLR, AISTATS) with stage checkpoints and citation auditing via Semantic Scholar. | `/write <mode>` |

State carries across skills and sessions via `.research-state/<topic-slug>.md` (schema in `shared/research_state.schema.md`).

## Install

From the repo root:

```bash
# As a local plugin
ln -s "$(pwd)" ~/.claude/plugins/research-assistant

# Python deps (citation audit + retrieval scripts)
uv sync
# Optional: STORM backend for heavy auto-surveys
uv sync --extra storm
```

## Quickstart

```text
/explore conformal prediction under covariate shift
/algo gap-analysis
/algo formalize
/algo ideate
/algo novelty-check
/algo red-team
/write outline --venue neurips
/write citation-audit
```

## Design Philosophy

- **Bias toward developing new algorithms**, not surveying or applying.
- **Statistical rigor by default**: post-selection inference, identifiability, multiple testing, regularity conditions are surfaced in `red-team` and `stats_pitfalls.md`.
- **Anti-sycophancy**: every brainstorm response must list ≥2 weaknesses or related prior work before any positive feedback.
- **MIT-licensed throughout**; no copyleft or non-commercial dependencies.
- Borrows design ideas from STORM (Stanford OVAL) and ARS (Imbad0202), but contains no copied prompts or code.

## License

MIT. See [LICENSE](LICENSE).
