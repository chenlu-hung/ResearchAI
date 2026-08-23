# Positioning

## What this is

An evidence-grounded research plugin for Stats/ML researchers whose core output
is **new algorithms**. It runs on two hosts from one core (`skills/`), and it
carries a project from a rough idea to a submission-ready paper.

Its distinguishing bet: the workflow may run unattended, but it may never
advance on an unsupported claim. Autonomy is bounded by evidence, not by
asking permission.

## What this is not

Not a paper generator. Not a substitute for reading the literature — R-EV-1
exists precisely because the store cannot tell whether you read a source
correctly. Not a reviewer of record, and not an authorship claim.

---

## Rejected mechanisms

Each entry states what is refused, why, where the refusal is currently
enforced, and **what kind of change would cross the line**. These are review
criteria for future work, not runtime guarantees: an enforcement point can have
gaps, and saying so is the point of writing them down.

### Corpus hits as proof

An abstract-scope record from `docs/corpus-manifest-<slug>.md` may raise an
alarm and motivate a query. It may never become a novelty verdict, a
claim-to-passage evidence link, a Same/Different/Δ row, or a sentence in the
paper.

Why: the corpus exists so a near neighbour is noticed *during* discussion
rather than at a gate. Letting it also settle questions would create a second,
cheaper standard of proof — and the cheaper standard always wins under time
pressure.

Enforced in: `shared/prompts/evidence_grounding.md` § Two-fidelity rule;
pinned as R-EV-2 in `shared/firm_rules.md`.

Crosses the line: any change letting an abstract-scope record satisfy a gate,
or any new retrieval surface that produces gate-eligible records without
passage inspection.

### Advancing a gate on recall, a `.bib` entry, or an abstract

A BibTeX key proves a work exists. An abstract proves what a paper claims about
itself. Neither proves that a specific passage supports a specific claim.

Why: these are the three cheapest things to mistake for evidence, and all three
are things a language model can produce without reading anything.

Enforced in: `skills/research-conductor/routing.md` § Hard precondition:
current evidence packet; `shared/prompts/evidence_grounding.md`.

Crosses the line: a mode that accepts `literature:` or `citations:` state as
support, or a gate whose accepted status can be reached without a frozen packet.

### Generating results that were never run

Results enter only through an external run manifest. The conductor hard-stops
until one exists and validates protocol and artifact hashes against the frozen
contract.

Why: this is the failure that ends careers, and it is the one an eager
autopilot is structurally most likely to commit — the expected curve is easy to
imagine and the gate is one line of JSON away.

Enforced in: `skills/research-conductor/routing.md` (external-run stop:
"Never generate plausible numbers, mark absent runs complete, or advance
because expected curves look reasonable"); `shared/prompts/research_lifecycle.md`
§ Results manifest.

Crosses the line: any path that writes a results artifact from inside the
plugin, including "illustrative" or "placeholder" numbers in a draft table.

### A conductor that does the work itself

The conductor selects and runs modes. It never re-implements mode logic, never
writes a mode-owned section of research state, and never bypasses a gate.

Why: a gate is only as strong as the narrowest place it is checked. An
orchestrator that can also *do* the step can also skip the check, and nothing
in the state file would show it.

Enforced in: `skills/research-conductor/SKILL.md`; `skills/research-conductor/routing.md`
§ Notes.

Crosses the line: giving the conductor its own analysis, verdict, or
state-writing capability — including "just summarizing" a mode's output into a
field that mode owns.

### Promoting a reconstructed artifact because the paper already says so

Retrofit entry marks gates `backfill_needed`. A reconstructed claim map or
method-freeze artifact is an *input* to the owning mode, never a substitute for
running it.

Why: a finished draft is the strongest possible source of confirmation bias.
Reading the gate's answer off the paper it is supposed to gate is circular.

Enforced in: `skills/research-conductor/routing.md` § Retrofit entry, rule 3;
`shared/prompts/research_lifecycle.md` § `backfill_needed`.

Crosses the line: any status transition from `backfill_needed` to
`pass`/`frozen` that does not run the owning mode.

### Sending someone else's manuscript to an external model without consent

`peer-reviewer --council` fans a manuscript out to other model CLIs. That
transmission needs explicit user confirmation; without it the run downgrades to
a single-model report executed locally.

Why: a manuscript under review is confidential and not the user's to
distribute. Many venues also forbid it outright, and the reviewer — not the
tool — carries that obligation.

Enforced in: `skills/peer-reviewer/SKILL.md` (review-ethics gate and the
council confidentiality downgrade); `skills/peer-reviewer/checklists/review_ethics.md`.

Crosses the line: any default-on fan-out of third-party text, or a confirmation
prompt that does not name where the text is going.

### A host-specific fork of the core

One `skills/` tree serves both Claude Code and Codex. A `.claude/skills/` or
`.codex/skills/` tree is a fork and is rejected mechanically.

Why: two copies of a workflow means two sets of gates, and the weaker set is
the one that gets used.

Enforced in: `scripts/check_host_parity.py` (host-specific skill tree "would
fork the core"), run on every push.

Crosses the line: any host-conditional behaviour that lives outside the thin
wrappers in `commands/` and `.codex-plugin/`.

---

## Recorded scope decisions

Deliberate choices that a reasonable reader might expect to go the other way.
Recorded so the contrast is a decision rather than an oversight.

### Autopilot is in scope; unbounded autonomy is not

`research-conductor` runs full-auto until blocked. Comparable tools (e.g.
Academic Research Skills) reject end-to-end automation outright, on the grounds
that the scholar would become a reviewer of AI output rather than the author.

This repo takes the other route because it binds authority to *evidence* rather
than to *confirmation prompts*: the conductor may take any step whose gate
artifact validates, and may take no step whose gate artifact is missing or
stale. A confirmation prompt asks a tired human to notice a problem; a hash
comparison does not get tired. `--gates` and `--step` exist for users who want
the prompts anyway.

The cost is real and worth stating: this design assumes the gates are correctly
specified. Where a gate is weak, nothing pauses to let a human catch it. That
is what `audits/` is for.

### Evidence persists across papers

The external Obsidian vault is shared across topics and projects, by design —
a source read once is reusable forever, and `.research-state/<slug>.md` is only
the per-topic control plane.

Tools that keep no cross-paper state do so to avoid gates evaluating something
nobody declared this run. The mitigation here is different: vault records are
immutable and versioned, packets are candidate-specific and expire on
fingerprint change, so a reused record cannot silently become support for a
claim it was never linked to.

Crosses the line: any cross-topic state that is *inferred* rather than
explicitly linked — a "related work you probably want" surface that feeds a
gate.

---

## What the gates cannot prove

Stated plainly, because a checklist that looks complete is worse than one that
admits its edges.

- **Not that a source was read correctly.** The store keeps a paraphrase and an
  excerpt hash; it can prove some span was inspected, never that the paraphrase
  reports it faithfully. This is R-EV-1's whole subject.
- **Not that reported results are real.** The manifest gate checks that results
  arrived from a declared external run whose hashes match the frozen protocol.
  Consistently fabricated inputs pass every check in this repo.
- **Not that the mathematics is correct.** `red-team` audits proofs
  adversarially; that is a review, not verification.
- **Not that a novelty verdict is right.** `novelty-check` reports what
  retrieval found. Absence of a near neighbour in the packet is not absence in
  the literature, and no gate here measures how often the verdict is wrong —
  `evals/` exists to start closing that gap and currently covers only part of
  the surface.
- **Not that a gate ever fired.** This repo has no run telemetry. Claims about
  which checks earn their keep rest on recall and git history; see
  `audits/README.md`.
