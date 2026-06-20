# Conductor bootstrap

Turn a fresh idea (no existing state file) into a `.research-state/<slug>.md` plus
a starting stage, then hand back to the conductor loop. Follow
`shared/research_state.schema.md` exactly.

## 1. Topic + slug

- `topic` = the idea, cleaned into a noun phrase.
- `slug` per the schema "Slug rules": lowercase, hyphen-separated, derived from the
  topic, ≤ 50 chars. On collision append `-v2`, `-v3`.
- If `.research-state/<slug>.md` **already exists**, this is not a new idea — load
  it and return to the loop. Do **not** bootstrap over it.

## 2. One framing question: venue

Ask `venue_target` once, via `AskUserQuestion` (recommended option first, per
`shared/prompts/grill_protocol.md`). Options from `shared/venue_profiles.md`
(NeurIPS / ICML / JMLR / AISTATS / Annals of Statistics). "Decide later" is
available via Other → set `venue_target: TBD`.

Do **not** ask anything else here. In particular do not ask the
empirical-vs-theoretical question — `ideate`'s grill (`interview_ideate`) captures
`contribution_type`, and routing only needs it later at the `theory` stage.
Pre-asking another mode's question violates `grill_protocol.md`.

## 3. Choose the start stage

- **Default `explore`** — a fresh topic. Grounds `novelty-check` and citation
  discipline.
- **`gap` instead** — only when the idea is explicitly a refinement or critique of
  a **named** method or paper (e.g. "fix the exchangeability assumption in split
  conformal"). `gap-analysis` can run on it directly. `explore` still runs before
  `novelty` (routing's bib precondition).

Announce the choice in one line: "Starting at `<stage>` because <reason>."

## 4. Write the initial state file

Create `.research-state/<slug>.md`:

```yaml
---
topic: "<topic>"
slug: <slug>
venue_target: <venue or TBD>
created: <today>
updated: <today>
stage: <chosen start>
---
```

Body: a single bootstrap note (`## <today> — bootstrap` + one line). Leave all
mode-owned sections (`formalization:`, `candidates:`, `literature:`, …) **absent**
— the modes fill them. The conductor writes nothing else for the rest of the run.

## 5. Hand back

Return the chosen start stage to the loop. Because that stage's mode has not
produced output yet, the conductor runs it next (per routing's completeness rule),
rather than skipping to its successor.
