# research-assistant

A Claude Code plugin for Stats/ML researchers whose core output is **developing new algorithms**.

Three skills, each independently usable:

| Skill | Purpose | Trigger |
|---|---|---|
| `literature-explorer` | Multi-perspective survey of a topic; produces hierarchical outline + BibTeX. Uses bundled arXiv / Semantic Scholar / OpenAlex scripts; if the external `literature-review-ml` skill is installed, will prefer it. | `/explore <topic>` |
| `algo-brainstorm` | Eight-mode pipeline for going from "I have an idea" to "I have a contribution worth submitting". Modes: `gap-analysis`, `formalize`, `ideate`, `novelty-check`, `theory-scoping`, `toy-design`, `ablation-plan`, `red-team`. | `/algo <mode>` |
| `paper-writer` | Venue-aware drafting (NeurIPS, ICML, JMLR, AISTATS) with stage checkpoints and citation auditing via Semantic Scholar. | `/write <mode>` |

State carries across skills and sessions via `.research-state/<topic-slug>.md` (schema in `shared/research_state.schema.md`).

## Install

This plugin ships its own local marketplace. From inside Claude Code:

```text
/plugin marketplace add /Users/chenlu-hung/Documents/Projects/ResearchAI
/plugin install research-assistant@research-assistant
```

(Substitute your own absolute path to this repo, or a Git URL once published.)

Then install the Python dependencies used by the retrieval and citation-audit
scripts:

```bash
uv sync
# Optional: STORM backend for heavy auto-surveys
uv sync --extra storm
```

### Optional external skill

`literature-explorer` will automatically prefer an external skill named
`literature-review-ml` for retrieval **if** it is installed in your Claude
environment. If it is not present, the bundled scripts under
`skills/literature-explorer/scripts/` are used instead — no configuration
needed.

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
