# Mode: novelty-check

**Purpose**: for each active candidate from `ideate`, compare against the
most-relevant prior art and write a contribution statement that articulates
exactly what is new (Δ).

## Inputs

- `candidates:` from research state (at least one with `status: active`)
- Retrieved literature from `literature-explorer` — required for honest
  comparison. If unavailable, refuse with: "novelty cannot be claimed
  without retrieval; run `/explore <topic>` first."

## Procedure

For **each active candidate**:

1. **Identify the 3–5 most-similar prior works** via:
   - Direct similarity in the retrieved set (same primitive, same problem)
   - Forward/backward citation chase from those (use Semantic Scholar
     citation graph)
   - Recent preprints (arXiv ≤6 months) — these are easy to miss and ICML
     reviewers will catch you on them

2. **Same/Different/Δ table** per related paper:

   ```markdown
   #### Candidate 1: <name>
   
   | Related work | What's the same | What's different | The Δ |
   |--------------|-----------------|------------------|-------|
   | Tibshirani 2019 | Weighted quantile reweighting | They assume $w$ known | We estimate $w$ via DML with cross-fitting and obtain $n^{-1/4}$ remainder |
   | Barber 2023 | Jackknife+ for non-exchangeable | Different shift model | Their result is conditional; ours marginal under shift |
   | ...
   ```

3. **Contribution statement** (one paragraph, paper-intro ready):

   > Compared to [Tibshirani 2019], who assumes $w$ is known, we propose a
   > cross-fitted DML estimator for $w$ and prove that the resulting
   > prediction set retains marginal coverage with an $O(n^{-1/4})$
   > remainder. Compared to [Barber 2023], who provide conditional
   > validity under non-exchangeability, our result is marginal but
   > applies under a broader class of shift models.

4. **Novelty verdict** per candidate:

   - `novel` — clearly distinct delta, articulated above
   - `incremental` — delta exists but is small; flag for user to decide
     if worth pursuing
   - `subsumed` — at least one prior work already does this, in essence;
     candidate should be dropped or substantially modified

5. **For subsumed candidates**: do not silently delete. Move to
   `dropped:` in research state with `drop_reason` citing the subsuming
   work.

## Citation graph chase

Use this minimum protocol:

- Take each "most similar" paper
- Pull its 5 most-cited references and 5 most-recent citing papers
- Scan for anything that would invalidate the Δ
- If you find something, update the table

Tools: `skills/literature-explorer/scripts/search_semantic_scholar.py`
can fetch by paperId via the `/paper/{id}/citations` and `/paper/{id}/references`
endpoints (add as needed — keep this in mind for ablation-plan stage).

## Anti-sycophancy

Hard rule: you may not declare a candidate `novel` without listing ≥3
related works and articulating Δ against each. Bare "I couldn't find
anything similar" is not acceptable — that's a retrieval failure, not
a novelty result.

## Council panel (opt-in)

When invoked with `--council`, convene a panel to **attack the Δ** before you commit a
verdict. Heterogeneous models surface prior art and subsumption angles a single model
misses. Follow `shared/prompts/council_panel.md` — novelty-check is a **critique** *and*
**adversarial** mode, so cross-review and the conditional cross-examination both apply.

- **Panel prompt**: each active candidate's contribution statement + Same/Different/Δ table,
  asking each member: "Where is this *not* novel? Name the closest prior work and say what
  Δ it kills." Frame it as adversarial — you want the strongest subsumption case, not praise.
- **Cross-examination (conditional)**: when members disagree on a verdict
  (`novel`/`incremental`/`subsumed`), run **one** rebuttal round — send the contested
  candidate back with the strongest "this is subsumed by X" objection and ask the author to
  defend the Δ or concede.
- **Evidence gate — NON-NEGOTIABLE**: a member's "subsumed by X" is a **hypothesis, not a
  result**. You may **not** flip a verdict to `incremental`/`subsumed` on a member's say-so.
  For each proposed prior work, **verify against the retrieved set** (and a citation-graph
  chase via `skills/literature-explorer/scripts/search_semantic_scholar.py`):
  - If X exists and genuinely subsumes the Δ → flip the verdict, cite X from the verified
    bibliography, and record it in `closest_prior`.
  - If X is unretrievable or doesn't actually subsume → **discard the attack**, note why in
    one line. Bare "a model said it's not novel" is a retrieval/verification task, **never**
    a novelty result — the same hard rule as the Anti-sycophancy section above.

  Members reasoning about novelty from parametric memory only converge on shared priors;
  the retrieval gate is exactly what stops a confident hallucinated citation from sinking a
  good candidate. Panel-proposed works enter state only after verification, `[VERIFY]`-clean.

Without `--council`, run novelty-check single-model exactly as above.

## State update

```yaml
stage: novelty
candidates:
  - id: cand-1
    novelty: novel
    contribution_statement: "..."
    closest_prior:
      - ref: tibshirani2019
        delta: "..."
      - ref: barber2023
        delta: "..."
key_claims:
  - claim: "<the contribution statement, distilled>"
    supporting_refs: [tibshirani2019, barber2023, ...]
    audit_status: pending
```

The `audit_status: pending` will be flipped to `verified` once
`paper-writer citation-audit` confirms the citations exist and support
the comparisons made.

## Failure modes

- If no candidates pass novelty: tell the user honestly, offer to return
  to `ideate` with explicit constraints (e.g., "ideate candidates that
  attack a different gap").
- If multiple candidates are equally novel: do not pick a winner. Present
  trade-offs and let the user choose.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Retrieval present (`literature:` + `citations:` non-empty) — or you
      refused with the exact message in Inputs.
- [ ] Every active candidate has ≥3 related works, each with a filled
      Same / Different / Δ row.
- [ ] Citation-graph chase ran per most-similar paper (5 refs + 5 citers),
      or `Skipped step: <reason>` appears in the output.
- [ ] Verdict per candidate ∈ {novel, incremental, subsumed}; `novel` only
      with the ≥3-works rule met — never from "couldn't find anything".
- [ ] Subsumed candidates moved to `dropped:` with `drop_reason` citing the
      subsuming work; nothing silently deleted.
- [ ] `key_claims` written with `supporting_refs` from the verified set and
      `audit_status: pending`.
- [ ] (`--council`) every panel attack was verified against retrieval or
      discarded with a one-line reason; no verdict flipped on say-so.
