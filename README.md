# research-assistant

A host-portable research-agent plugin for Stats/ML researchers whose core output
is **developing new algorithms**. Its prompts and persisted evidence workflow do
not depend on a Codex-only or Claude-only API.

What it refuses to do — and what kind of change would cross each of those
lines — is recorded in [POSITIONING.md](POSITIONING.md). The mode surface is
indexed in [shared/mode_registry.md](shared/mode_registry.md).

## Evidence before answers

Literature-dependent modes use one ordered loop: model knowledge proposes
queries/hypotheses → query the user-selected external Obsidian vault → retrieve externally
only for gaps → persist query-runs, immutable source versions, atomic claims, and
passage links → freeze a candidate-specific packet → answer from that packet.
A new gap or near-neighbor restarts the loop. Changes to primitives, objective,
data regime, or material claims make the packet stale.

`.research-state/<slug>.md` is the workflow control plane; `evidence_vault`
points to the external Obsidian vault root, which is the canonical evidence data
plane; `refs/<slug>.bib` is only a generated view of canonical works. The
vault's `.evidence/` directory is internal metadata—not the root and not a
project-local evidence store. A BibTeX key or abstract does not establish claim support.
See `shared/prompts/evidence_grounding.md`.

### Corpus prefetch and the novelty reflex

Novelty is checked during **every** algorithm discussion, not once at a gate.
`literature-explorer` has a `corpus-prefetch` mode that runs one broad, shallow
sweep up front — metadata and abstracts for 100–300 works across four mandatory
axes: the application field, the **mathematical skeleton** (the method stripped
of application vocabulary, searched across fields and across decades including
pre-2015), adjacent fields, and history. It writes a hashed
`docs/corpus-manifest-<slug>.md`. From then on, whenever a new component or
design choice enters an `algo-brainstorm` discussion, the mode names its nearest
neighbour from that local corpus — no network — and says in one line what is the
same and what differs. Terms outside the manifest's covered axes trigger an
immediate targeted retrieval that extends the manifest. Corpus hits are **alarm
evidence only**: they justify a warning and a query, never a verdict, a claim
link, or a Same/Different/Δ row. `gap-analysis`, `formalize`, and `ideate`
refuse to start without a manifest.

## Autopilot: idea → paper

Start from a rough idea and let the **`research-conductor`** skill drive the whole
pipeline — it reads the shared research-state, decides which skill/mode to call
next, and loops until you have a submission-ready paper:

Claude Code:

```text
/research-assistant:research conformal prediction under covariate shift
```

Codex:

```text
Use $research-ai:research-conductor to take "conformal prediction under
covariate shift" from idea to a submission-ready paper.
```

It runs **full auto until blocked**: it auto-chains the stages below and only
pauses when a real gate needs you — a mode's grill, a `subsumed` novelty verdict
(or an `incremental` one you have not explicitly accepted), a
red-team blocking finding, missing/stale evidence packet, ungrounded claim,
fabricated citation, or a failed submission check. Add
`--gates` to also pause at high-leverage decision points, or `--step` to confirm
before every mode. It never bypasses a gate; it sequences the three workflow
skills over the shared evidence-store core, all independently usable below.

The backward-compatible `stage` label does not waive scientific gates. The
conductor advances `research_phase` only through: intake/import → atomic claim
map → prior-art audit → method freeze → positioning skeleton → experiment
contract → protocol freeze →
real runs/results ingest → evidence audit → results-aware red team → draft →
scientific review → submission. Each gate has a content-hashed artifact; a
missing/stale hash or missing real result manifest hard-stops the run. See
`shared/prompts/research_lifecycle.md`.

### Positioning skeleton: write half the paper first

Between method freeze and the experiment contract sits one phase that runs
*before* any experiment: `paper-writer positioning-skeleton`. It drafts the
intro, related work, and contribution statements (taken from the frozen
contribution spine — one primary claim plus at most three supporting claims,
each by ID), plus **empty** result-table and figure shells with every header,
compared method, and dataset named and every numeric cell literally blank.
Quantitative claims about your own method are marked
`[HYPOTHESIS — pending results]`; a results section is forbidden outright. Those
promised table rows then become the input spec for the experiment contract, so
what you run is decided by what the paper needs to say. It is the one mode
exempt from the results-gate pre-flight, and it pays for that by being unable to
print a number.

### Parity matrix and calibration budget

The experiment contract now freezes a **parity matrix**: one row per compared
method, with parameter count, training data, target-resolution labels consumed,
fine-tuning, adaptation, and tuning budget. For any comparison a spine claim
cites, an asymmetric cell **requires an equalized baseline variant** — a written
justification is not enough, because the asymmetry rather than the method may be
producing the gap. A claim about a nonlinear component needs a strong nonlinear
baseline, not a linear strawman. The contract also records exactly how many
target-resolution labels each calibration step or adapter consumes and where
they come from, plus one budget-response experiment from few-shot to the full
curve. The results manifest carries `method_variant`, `param_count`,
`adaptation`, and `resolution_direction` per run, so the conductor and
`red-team`'s Gate 0 can check parity mechanically instead of arguing it in prose.

### Retrofit: entering with a paper you already have

A finished or rejected paper used to have no legal way into the pipeline —
bootstrap only made blank state, and `paper-writer` refused to draft without the
upstream gates. Point the conductor at an existing draft (optionally with a
decision/reviews file) and it takes the **retrofit** entry: it extracts the
paper's claims into a claim map marked `retrofit: true` with evidence pending,
reconstructs a method-freeze artifact from the paper's own method section, and
marks the experiment/protocol/results gates `backfill_needed` — importing real
artifacts where the project has them and otherwise listing exactly what is
missing. `backfill_needed` blocks advancement like `missing` but routes to the
backfill rather than hard-stopping. Retrofit is a legal entry route, not a
shortcut: backfilled claims still need passage grounding before the novelty and
drafting gates pass.

### Post-mortem: learning from a real rejection

`paper-writer post-mortem` turns a decision-and-reviews file into pipeline
changes. It injection-scans the reviews first (they are third-party text),
decomposes them into atomic objections classified by kind, and then does the
part that matters: **gate attribution** — for each objection, which lifecycle
gate should have caught it and why it did not (missing check, check too weak,
pipeline not run, genuinely uncatchable), with a proposed change to that gate's
owning mode, artifact schema, exit checklist, or hard-stop list. "Add a red
flag" is not an acceptable proposal on its own; the objection already proved a
reminder was not enough. Lessons that generalize route through
`venue-calibration` as `unverified` single-paper evidence, never as direct edits
to the venue profile; paper edits go to `revision`'s reviewer-response sub-mode.
It runs after `final`/rejection or on a retrofit entry, and sets
`research_phase` back to the earliest gate its findings invalidate — so a
novelty objection reopens prior-art audit rather than the draft.

Add `--economy [model]` to cut usage via an architect/implementer split: the
token-heavy, judgment-light stages (`explore`, `full-draft`, `revision`,
`citation-audit`) run in a cheaper implementer subagent (the host-configured
economy model; legacy Claude Code setups may default to `sonnet`)
under a DONE/CONSULT protocol, while routing, grills, verdicts, and a
non-skippable acceptance gate (re-running the machine checks on the
implementer's output) stay in the main session. Protocol and delegation rules:
`shared/prompts/model_dispatch.md`. Composes with `--gates`/`--step`; without
the flag, everything runs inline exactly as before.

## The workflow skills (each independently usable)

Claude Code installs the five command wrappers under the manifest namespace
`research-assistant`. Codex does not load `commands/`; invoke the shared skills
by natural language or their installed, namespaced skill names.

| Skill | Purpose | Claude Code | Codex |
|---|---|---|---|
| `research-conductor` | Autopilot from a rough idea to a submission-ready paper. | `/research-assistant:research <idea>` | `$research-ai:research-conductor` |
| `evidence-store` | Host-neutral canonical evidence layer in an external Obsidian vault: works, source versions, readings, passages, atomic claims/links, methods, candidates, query runs, packets, and audit verdicts. | Invoked automatically, or ask for evidence-vault maintenance | `$research-ai:evidence-store` |
| `literature-explorer` | Multi-perspective, vault-first survey; persists passage-grounded claims and a validated packet, then produces an outline + generated BibTeX view. A `corpus-prefetch` mode builds the local corpus that algorithm discussion runs against. Uses bundled arXiv / Semantic Scholar / OpenAlex discovery scripts; optionally delegates external retrieval to `literature-review-ml`. | `/research-assistant:explore <topic>` | `$research-ai:literature-explorer` |
| `algo-brainstorm` | Eight-mode pipeline for going from "I have an idea" to "I have a contribution worth submitting". Modes: `gap-analysis`, `formalize`, `ideate`, `novelty-check`, `theory-scoping`, `toy-design`, `ablation-plan`, `red-team`. | `/research-assistant:algo <mode>` | `$research-ai:algo-brainstorm` |
| `paper-writer` | Venue-aware drafting with packet-gated, atomic claim-to-passage support. BibTeX metadata audit remains, but a clean key is insufficient without passage evidence. Includes positioning-skeleton/outline/draft/revision/audit/review/submission, post-mortem, and venue/grant modes. | `/research-assistant:write <mode>` | `$research-ai:paper-writer` |
| `peer-reviewer` | Stateless, ethics-gated review of someone else's manuscript. | `/research-assistant:review <paper>` | `$research-ai:peer-reviewer` |

State carries across skills and sessions via `.research-state/<topic-slug>.md`
and stable IDs into the configured external vault (schema in
`shared/research_state.schema.md`).
Legacy survey/`.bib` state is read and migrated additively before an evidence
gate; it is never silently treated as a current packet.

Two `paper-writer` modes work out-of-band of the paper pipeline:
`venue-calibration` adds or re-verifies a venue profile from official
sources with provenance, and `grant-nstc` drafts an NSTC (國科會)
專題研究計畫 CM03 into your own LaTeX template — proposal register
(vision + feasibility), review-weight-aware, no research state required.

## Reviewing other people's papers

The workflow skills above critique *your own* work. To referee *someone else's*
manuscript, use the standalone, **stateless** `peer-reviewer` skill:

Claude Code:

```text
/research-assistant:review path/to/manuscript.pdf --venue neurips
```

Codex:

```text
Use $research-ai:peer-reviewer to review path/to/manuscript.pdf for NeurIPS.
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

The canonical repository contains both `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json`. Both hosts consume the same `skills/`, `shared/`,
evidence CLI/core, and schemas; synchronize one canonical checkout rather than
letting the two deployments diverge.

### Claude Code

This plugin ships its own local marketplace. From inside Claude Code:

```text
/plugin marketplace add <absolute-path-to-canonical-checkout>
/plugin install research-assistant@research-assistant
```

(Substitute your own absolute path to this repo, or a Git URL once published.)

### Codex

Codex reads `.codex-plugin/plugin.json`. Keep the canonical checkout as the
source of truth and synchronize it into the personal-plugin deployment. The
official `plugin-creator` helper creates the default personal marketplace entry
and its `~/plugins/research-ai` target; do not hand-edit
`~/.agents/plugins/marketplace.json`.

For a first installation, set `CANONICAL_REPO` to this checkout and
`PLUGIN_CREATOR_ROOT` to the installed official `plugin-creator` skill:

```bash
CANONICAL_REPO="<absolute-path-to-canonical-checkout>"
PLUGIN_CREATOR_ROOT="${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator"
PLUGIN_ROOT="$HOME/plugins/research-ai"

python3 "$PLUGIN_CREATOR_ROOT/scripts/create_basic_plugin.py" \
  research-ai --with-marketplace
rsync -az --exclude '.git/' "$CANONICAL_REPO/" "$PLUGIN_ROOT/"
python3 "$PLUGIN_CREATOR_ROOT/scripts/validate_plugin.py" "$PLUGIN_ROOT"
python3 "$PLUGIN_CREATOR_ROOT/scripts/read_marketplace_name.py"
codex plugin add research-ai@personal
```

The marketplace-name helper normally prints `personal`; if it prints another
name, use that exact name after `@`. The default personal marketplace is
discovered automatically, so do not run `codex plugin marketplace add` for it.

For later updates, synchronize again, use the official cachebuster helper, and
reinstall. Keep the deployment generated-only. The normal sync is deliberately
non-destructive; remove stale deployment files only as an explicit maintenance
action. This keeps the existing personal deployment flow reproducible without
modifying marketplace JSON by hand:

```bash
rsync -az --exclude '.git/' "$CANONICAL_REPO/" "$PLUGIN_ROOT/"
python3 "$PLUGIN_CREATOR_ROOT/scripts/update_plugin_cachebuster.py" "$PLUGIN_ROOT"
python3 "$PLUGIN_CREATOR_ROOT/scripts/validate_plugin.py" "$PLUGIN_ROOT"
python3 "$PLUGIN_CREATOR_ROOT/scripts/read_marketplace_name.py"
codex plugin add research-ai@personal
```

Start a new Codex task after installation so it loads the new plugin snapshot.
Do not maintain a separate evidence implementation for Codex—the same
host-neutral `$PLUGIN_ROOT/shared/evidencectl.py` and
`$PLUGIN_ROOT/skills/evidence-store/` are the shared core.

Then install the Python dependencies used by the retrieval and citation-audit
scripts:

```bash
uv sync --project "$PLUGIN_ROOT"
# Optional: STORM backend for heavy auto-surveys
uv sync --project "$PLUGIN_ROOT" --extra storm
# Optional: matplotlib + numpy for paper-writer figures
uv sync --project "$PLUGIN_ROOT" --extra figures
```

### Optional external skill

`literature-explorer` will automatically prefer an external skill named
`literature-review-ml` for external retrieval **if** it is installed in the host
environment. If it is not present, the bundled scripts under
`skills/literature-explorer/scripts/` are used instead — no configuration
needed.

### Council panel (opt-in multi-model)

Four modes — `algo gap-analysis`, `algo ideate`, `write outline`, `write
self-review` — accept a `--council` flag that convenes a multi-model panel
(Codex, Gemini, Claude, opencode), each reached through its **own
subscription/sign-in CLI** rather than an API key, with the running session as
chair. It widens divergent search (more gaps, more candidate algorithms) and
turns `self-review` into a real multi-reviewer meta-review. Inspired by
[karpathy/llm-council](https://github.com/karpathy/llm-council).

- Engine: `$PLUGIN_ROOT/shared/council.py` (stdlib-only). Protocol +
  anti-hallucination guardrails:
  `$PLUGIN_ROOT/shared/prompts/council_panel.md`.
- The engine is **vendored** from the [`llm-council`
  skill](https://github.com/chenlu-hung/my-skills/tree/main/llm-council) — the
  plugin ships it because it installs where that checkout doesn't exist. Don't
  edit `shared/council.py`: change it upstream, then run
  `shared/vendor-council.sh`, which refetches it (and its schema) by URL. No
  local copy of the upstream is required; set `COUNCIL_UPSTREAM` to one only if
  you want to vendor work that isn't pushed yet.
- Needs the member CLIs on PATH and signed in (`codex`, `agy`, `claude`,
  `opencode`); any missing one drops out of the panel. Without `--council`,
  every mode runs single-model exactly as before.
- Panel output is **ideation/critique only** — citations and prior-art claims
  become persisted queries and must complete vault-first retrieval plus passage
  verification before entering an evidence packet or changing a verdict.

## Quickstart

### Claude Code

Let the conductor drive the whole thing:

```text
/research-assistant:research conformal prediction under covariate shift
```

…or hand-drive the stages yourself:

```text
/research-assistant:explore conformal prediction under covariate shift
/research-assistant:explore corpus-prefetch conformal prediction under covariate shift
/research-assistant:algo gap-analysis
/research-assistant:algo formalize
/research-assistant:algo ideate --council
/research-assistant:algo novelty-check
/research-assistant:write positioning-skeleton --venue neurips
/research-assistant:algo theory-scoping
/research-assistant:algo toy-design
/research-assistant:algo ablation-plan
# Run the frozen protocol externally and ingest results/<slug>/manifest.json
/research-assistant:algo red-team
/research-assistant:write outline --venue neurips
/research-assistant:write full-draft
/research-assistant:write self-review --council
/research-assistant:write citation-audit
/research-assistant:write submission-check
# If it comes back rejected:
/research-assistant:write post-mortem review.md
```

### Codex

Let the conductor drive the workflow by saying:

```text
Use $research-ai:research-conductor to take "conformal prediction under
covariate shift" from idea to paper. Continue until a hard gate needs me.
```

To hand-drive it, invoke the namespaced skill and state the mode in the same
message, for example:

```text
Use $research-ai:literature-explorer on conformal prediction under covariate shift.
Use $research-ai:algo-brainstorm in gap-analysis mode.
Use $research-ai:algo-brainstorm in ideate mode with a council.
Use $research-ai:paper-writer in outline mode for NeurIPS.
Use $research-ai:paper-writer in submission-check mode.
```

## Design Philosophy

- **Bias toward developing new algorithms**, not surveying or applying.
- **Statistical rigor by default**: post-selection inference, identifiability, multiple testing, regularity conditions are surfaced in `red-team` and `stats_pitfalls.md`.
- **Anti-sycophancy**: weaknesses are mandatory design pressure, but never replace grounded prior-art retrieval when novelty or contribution is judged.
- **Model-robust by construction**: output quality tracks persisted evidence, checklists, and deterministic scripts—not the host model's confidence. `dedupe_rank.py` handles literature merge/rank, `verify_citations.py` + `check_tex.py` handle metadata/rendering integrity, and passage links handle claim support. Council agreement remains a hypothesis until retrieval.
- **MIT-licensed throughout**; no copyleft or non-commercial dependencies.
- Borrows design ideas from STORM (Stanford OVAL) and ARS (Imbad0202), but contains no copied prompts or code.

## License

MIT. See [LICENSE](LICENSE).
