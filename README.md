# research-assistant

A Claude Code plugin for Stats/ML researchers whose core output is **developing new algorithms**.

## Autopilot: idea → paper

Start from a rough idea and let the **`research-conductor`** skill drive the whole
pipeline — it reads the shared research-state, decides which skill/mode to call
next, and loops until you have a submission-ready paper:

```text
/research conformal prediction under covariate shift
```

It runs **full auto until blocked**: it auto-chains the stages below and only
pauses when a real gate needs you — a mode's grill, a "not novel" verdict, a
red-team blocking finding, fabricated citations, or a failed submission check. Add
`--gates` to also pause at high-leverage decision points, or `--step` to confirm
before every mode. It never bypasses a gate; it only sequences the three skills,
which all remain independently usable below.

## The three skills (each independently usable)

| Skill | Purpose | Trigger |
|---|---|---|
| `literature-explorer` | Multi-perspective survey of a topic; produces hierarchical outline + BibTeX. Uses bundled arXiv / Semantic Scholar / OpenAlex scripts; if the external `literature-review-ml` skill is installed, will prefer it. | `/explore <topic>` |
| `algo-brainstorm` | Eight-mode pipeline for going from "I have an idea" to "I have a contribution worth submitting". Modes: `gap-analysis`, `formalize`, `ideate`, `novelty-check`, `theory-scoping`, `toy-design`, `ablation-plan`, `red-team`. | `/algo <mode>` |
| `paper-writer` | Venue-aware drafting (NeurIPS, ICML, JMLR, AISTATS, Annals of Stats) with stage checkpoints. Modes: `outline`, `full-draft`, `revision`, `citation-audit`, `self-review`, `submission-check`. Multi-source citation audit (Semantic Scholar → OpenAlex → Crossref + DOI match), publication figures, LaTeX compile gate + DOCX export, AI-tell prose hygiene, optional voice calibration. | `/write <mode>` |

State carries across skills and sessions via `.research-state/<topic-slug>.md` (schema in `shared/research_state.schema.md`).

## Reviewing other people's papers

The three skills above critique *your own* work. To referee *someone else's*
manuscript, use the standalone, **stateless** `peer-reviewer` skill:

```text
/review path/to/manuscript.pdf --venue neurips
```

Plug-and-play: point it at a local PDF / `.tex` (or an arXiv id) and it produces
a venue-tailored referee report — summary, recommendation, method-validity
attacks, novelty positioning, evidence/clarity comments, AI-tell scan, and the
venue's reviewer red-flag checklist. `--depth quick|standard|deep` scales
thoroughness; `--council` convenes a multi-model multi-reviewer panel; `triage`
mode does a fast desk-screen. It needs no `.research-state` and writes to
`reviews/`. It runs a **review-ethics gate first** (confidentiality, conflict of
interest, the venue's LLM-in-reviewing policy) and treats its output as a draft
to inform the human reviewer — never a review to submit verbatim.

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
# Optional: matplotlib + numpy for paper-writer figures
uv sync --extra figures
```

### Optional external skill

`literature-explorer` will automatically prefer an external skill named
`literature-review-ml` for retrieval **if** it is installed in your Claude
environment. If it is not present, the bundled scripts under
`skills/literature-explorer/scripts/` are used instead — no configuration
needed.

### Council panel (opt-in multi-model)

Four modes — `algo gap-analysis`, `algo ideate`, `write outline`, `write
self-review` — accept a `--council` flag that convenes a multi-model panel
(Codex, Gemini, Claude, DeepSeek), each reached through its **own
subscription/sign-in CLI** rather than an API key, with the running session as
chair. It widens divergent search (more gaps, more candidate algorithms) and
turns `self-review` into a real multi-reviewer meta-review. Inspired by
[karpathy/llm-council](https://github.com/karpathy/llm-council).

- Engine: `shared/council.py` (stdlib-only). Protocol + anti-hallucination
  guardrails: `shared/prompts/council_panel.md`.
- Needs the member CLIs on PATH and signed in (`codex`, `agy`, `claude`,
  `opencode`); any missing one drops out of the panel. Without `--council`,
  every mode runs single-model exactly as before.
- Panel output is **ideation/critique only** — citations and prior-art claims
  it produces are `[VERIFY]`-flagged and must pass the normal audit before
  entering research-state.

## Quickstart

Let the conductor drive the whole thing:

```text
/research conformal prediction under covariate shift   # then just say "continue"
```

…or hand-drive the stages yourself:

```text
/explore conformal prediction under covariate shift
/algo gap-analysis
/algo formalize
/algo ideate --council          # optional: multi-model brainstorm
/algo novelty-check
/algo red-team
/write outline --venue neurips
/write full-draft
/write citation-audit
/write self-review --council     # optional: multi-reviewer panel
/write submission-check
```

## Design Philosophy

- **Bias toward developing new algorithms**, not surveying or applying.
- **Statistical rigor by default**: post-selection inference, identifiability, multiple testing, regularity conditions are surfaced in `red-team` and `stats_pitfalls.md`.
- **Anti-sycophancy**: every brainstorm response must list ≥2 weaknesses or related prior work before any positive feedback.
- **Model-robust by construction**: the plugin is written so output quality tracks its checklists and scripts, not the size of the Claude model running it. Mechanical steps are deterministic scripts (`dedupe_rank.py` for literature merge/rank, `verify_citations.py` + `check_tex.py` for citation/TeX integrity, `scan_injection.py` for the review injection scan); every mode ends with an **Exit checklist** enforced by `shared/prompts/execution_discipline.md` (two-pass emission, no silent step-skips, scripts-over-recall). On a smaller model, additionally consider `--council` on the adversarial modes (`novelty-check`, `red-team`, `self-review`, `/review`) — cross-model critique compensates for weaker single-model self-critique.
- **MIT-licensed throughout**; no copyleft or non-commercial dependencies.
- Borrows design ideas from STORM (Stanford OVAL) and ARS (Imbad0202), but contains no copied prompts or code.

## License

MIT. See [LICENSE](LICENSE).
