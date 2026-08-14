# Mode: positioning-skeleton

**Purpose**: write half the paper **before** running the experiments — intro,
related work, contribution statements, and empty result-table shells — so the
positioning is fixed while it can still change what you run, and so the promised
tables become the input spec for the experiment contract.

This is the one paper-writer mode that legally runs before results exist. It buys
that privilege by being forbidden to write a results section at all.

## Where it sits

Lifecycle phase `positioning_skeleton`, between `method_frozen` and
`experiment_contract` (`shared/prompts/research_lifecycle.md`). Method freeze —
including the contribution spine — must be `frozen` first; the experiment
contract (`toy-design`) consumes this mode's table shells afterward.

## Inputs

- `lifecycle_gates.method_freeze.status: frozen` with a matching artifact hash
- `spine:` in state — the primary claim and ≤3 supporting claims
- `venue_target` and its profile in `shared/venue_profiles.md`
- A validated current evidence packet for every claim the intro and related work
  will invoke

## Pre-flight

This mode is **exempt** from `paper-writer` Hard discipline #1's results-gate
requirement (experiment contract, protocol, results ingest, evidence audit,
results-aware red team) — it runs before those exist by design. Every other
pre-flight condition still applies in full:

- method freeze frozen and current, with a spine;
- evidence packet current and matching the candidate fingerprint;
- generated `refs/<slug>.bib` in sync with canonical works;
- no unresolved `blocking: true` red-team finding from any earlier run.

The exemption is scoped to this mode alone. `outline` and `full-draft` gating is
unchanged: they still require the full results chain.

## Procedure

1. **Validate and read.** Recompute the method-freeze hash, read `spine:`, load
   the venue profile and `style/<venue>.md`. Missing spine ⇒ stop; positioning
   without a frozen contribution is what this mode exists to prevent.

2. **Draft the intro.** Standard shape: problem, why existing work does not
   solve it, what we do, contributions. Every quantitative or comparative
   assertion about *our own* results is marked inline
   `[HYPOTHESIS — pending results]` — no exceptions, including "outperforms",
   "achieves state of the art", "reduces error by", "scales to". Claims about
   *prior* work follow the normal evidence rules and must be passage-grounded.

3. **Draft related work.** Positioning against the closest prior art from the
   novelty packet, articulating Δ per work — not an enumeration of citations.
   This is where the structural-isomorphism findings from `novelty-check` step 3
   get written down: a cross-field near neighbor the reviewer knows and the paper
   ignores is a rejection.

4. **Write the contribution statements from the spine.** One statement per spine
   claim, primary first, each tagged with its claim ID. The statements are the
   spine in prose; if a statement needs content the spine does not contain, the
   spine is wrong — go back to method freeze rather than widening the prose.

5. **Build empty result-table and figure shells.** For every table and figure the
   paper promises, write the complete structure with **every numeric cell
   literally empty**:

   - column headers: metrics, with units and the uncertainty format intended;
   - rows: every compared method, own variants and baselines, named exactly;
   - the datasets/benchmarks, resolutions, or regimes each block covers;
   - the caption, stating what the table is meant to show and which spine claim
     it serves.

   ```latex
   \begin{tabular}{lccc}
   \toprule
   Method & RMSE ($\pm$ s.e.) & Params & Wall-clock (s) \\
   \midrule
   Ours (full)        &  &  &  \\
   Ours (-adaptation) &  &  &  \\
   Baseline A [cite]  &  &  &  \\
   Baseline B [cite]  &  &  &  \\
   \bottomrule
   \end{tabular}
   % Serves: claim-novelty-1. Cells intentionally empty until results ingest.
   ```

   A shell with a filled cell is a fabricated result. Never write a placeholder
   number, not even `0.00` or `X.XX` — an empty cell cannot be mistaken for data.

6. **Emit the handoff list.** Enumerate every promised table/figure row as a line
   item for the experiment contract: which experiment must run to fill it, and
   which spine claim it serves. This list is the input spec `toy-design` consumes.

## Hard prohibitions

- **No results section.** Not empty, not stubbed, not "to be completed". If the
  draft needs one, this mode is being used to write the paper, which it is not.
- **No numbers from anywhere** — not from the toy design's expected curves, not
  from a pilot run, not from a prior paper's table. Expected curves are
  predictions; this mode does not print predictions as cells.
- **No unmarked quantitative self-claim** in the intro or abstract.
- The artifact is a *skeleton*: `full-draft` writes the real paper later and
  supersedes it.

## Output

`paper/skeleton/` containing:

- `intro.tex`, `related.tex`, `contributions.tex`
- `tables/*.tex` — the empty shells
- `handoff.md` — the promised-rows list from step 6

**Directory hash.** The gate stores one hash over the whole directory:
`sha256` of the newline-joined, lexicographically sorted lines
`<path-relative-to-paper/skeleton>:<file-sha256>`, one per file, with a trailing
newline. Record it as bare lowercase 64-hex per the schema's hash rule.

## State update

```yaml
research_phase: positioning_skeleton
lifecycle_gates:
  positioning_skeleton:
    status: pass
    artifact: paper/skeleton/
    artifact_hash: "<64-char-lowercase-sha256-hex>"   # directory hash, above
    method_freeze_hash: "<64-char-lowercase-sha256-hex>"
    spine_primary: claim-novelty-1
    promised_tables: [tab-main, tab-ablation, fig-scaling]
```

Append a body entry under `## <date> — positioning-skeleton`. Do not set
`draft:`; this is not the draft, and `outline`/`full-draft` own that pointer.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Method freeze revalidated and `spine:` read from state; missing spine
      stopped the mode.
- [ ] Intro, related work, and contribution statements drafted; **no results
      section exists** in any form.
- [ ] One contribution statement per spine claim, primary first, each tagged
      with its claim ID; no statement exceeds the spine.
- [ ] Every quantitative claim about our own method in intro/abstract carries
      `[HYPOTHESIS — pending results]`.
- [ ] Every prior-work assertion is passage-grounded in a current packet.
- [ ] Every promised table/figure shell has complete headers, method rows,
      datasets/regimes, and a caption naming the spine claim it serves.
- [ ] **Every numeric cell is literally empty** — no placeholder digits, no
      expected values, no pilot numbers.
- [ ] `handoff.md` lists every promised row with its experiment and spine claim.
- [ ] Directory hash computed per the stated rule and written to the gate with
      `research_phase: positioning_skeleton`.
