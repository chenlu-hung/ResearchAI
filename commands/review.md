---
description: Peer-review someone else's paper as a venue reviewer. Plug-and-play — point at a PDF / .tex / arXiv id and get a referee report. Modes: report (default), triage.
argument-hint: <paper-path|arxiv-id|url> [--venue neurips|icml|jmlr|aistats|aos|generic] [--depth quick|standard|deep] [--council]
---

Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
it is the absolute parent of the file's `commands/` directory. Never derive it
from the user's working directory. Resolve every `skills/...`, `shared/...`, or
other plugin resource below as `$PLUGIN_ROOT/<path>`. Dependency-bearing Python
scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Invoke the `peer-reviewer` skill: $ARGUMENTS

This is the **plug-and-play** entry for reviewing *other people's* manuscripts.
Unlike `/research-assistant:write self-review` (which critiques *your own* draft
and assumes `.research-state`), `/research-assistant:review` takes an external
artifact and needs **no project state** — just a file and, ideally, a target
venue.

Modes (see `skills/peer-reviewer/SKILL.md`):

- `report` (default) — full referee report: summary, recommendation on the
  venue scale, method-validity attacks, novelty positioning, evidence/clarity
  comments, claim/citation sanity, AI-tell scan, red-flag checklist.
- `triage` — fast desk-screen (scope fit + fatal-flaw + novelty smell) for an
  AC or a quick first pass.

Flags:

- `--venue` — sets the reviewer persona and red-flag list from
  `shared/venue_profiles.md`. `generic` if the venue is not profiled.
- `--depth quick|standard|deep` — review thoroughness (default `standard`).
- `--council` — convene a multi-model **multi-reviewer panel** and chair a
  meta-review (`report` only), per `shared/prompts/council_panel.md`.

**Before doing anything else**, the skill runs the review-ethics gate
(`skills/peer-reviewer/checklists/review_ethics.md`): confidentiality, conflict
of interest, and the venue's LLM-in-reviewing policy. Many venues prohibit
uploading submissions to LLMs or submitting machine-written reviews — the output
is a **draft to inform the human reviewer**, never a review to submit verbatim.
