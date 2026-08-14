# Mode: citation-audit

**Purpose**: mandatory integrity gate for citation rendering, canonical work
metadata, and passage-level claim support.

Follow `shared/prompts/evidence_grounding.md`. `refs/<slug>.bib` is a generated
view of canonical works; it is not the evidence authority.

## Inputs and gate

- `paper/main.tex` and included section files;
- generated `refs/<slug>.bib`;
- evidence vault/topic plus a validated current packet covering invoked claims;
- a current **self-review artifact** bound to the current draft/upstream hashes;
  it may still be `conditional` because this citation audit is the second half
  of the composite scientific-review gate, but it must have no unresolved
  blocking scientific finding;
- network access for metadata verification when needed.

If the packet is missing/stale, migrate legacy artifacts and run the retrieval
loop before auditing. Do not infer support from model knowledge or abstracts.

## Procedure

### Stage -1 — Regenerate the canonical BibTeX view

Resolve `EVIDENCECTL` to the absolute plugin entrypoint per
`shared/prompts/evidence_grounding.md`; do not assume the research project is the
plugin cwd. Record the previous view hash if present, then run:

```bash
python3 "$EVIDENCECTL" export bibtex --vault "$VAULT" \
  --topic "$TOPIC_ID" --out "refs/<slug>.bib"
```

Recompute the bare SHA-256 into `citations_view_hash` and compare. If the view
changed, explicitly invalidate prior static/metadata audit artifacts and run all
stages below. Never model-generate, hand-merge, or treat the `.bib` as canonical.

### Stage 0 — Static rendering cross-check

Run and paste the real output:

```bash
python3 "$PLUGIN_ROOT/skills/paper-writer/scripts/check_tex.py" \
  paper/main.tex --bib refs/<slug>.bib --json
```

Fix undefined citations/references and missing figures first. This proves only
that keys render; it does not prove existence or support.

### Stage 1 — Canonical metadata verification

Run and paste the real output:

```bash
uv run --project "$PLUGIN_ROOT" python \
  "$PLUGIN_ROOT/skills/paper-writer/scripts/verify_citations.py" \
  --bib refs/<slug>.bib \
  --out .research-state/<slug>-audit.json
```

Classify each rendered work `verified`, `mismatched`, `fabricated`, or
`unreachable`. Reconcile results with canonical vault work IDs/source versions.
If metadata changes, update the canonical work and regenerate BibTeX; do not
hand-edit the generated view as the authority. Retry `unreachable` results and
preserve the query-run rather than dropping them.

### Stage 2 — Atomic claim-to-passage audit

For every citation invocation:

1. Extract the exact substantive sentence and split compound assertions into
   atomic claims.
2. Map each atomic claim to its claim ID and evidence-link IDs in the current
   packet. Confirm the linked canonical work matches the rendered bibkey.
3. Validate the immutable source-version hash, stable locator, excerpt hash, and
   evidence relation. Read the passage—not merely metadata, an abstract, search
   snippet, or “known content.”
4. Classify each claim-link pair with the following **audit-report labels**:
   - `supports` — the inspected passage directly supports the atomic claim;
   - `partial` — supports only a narrower component;
   - `tangential` — relevant topic, not the asserted proposition;
   - `contradicts` — conflicts with the assertion; or
   - `cannot_determine` — source/locator/passage is unavailable or insufficient.
   These are not new evidence-store enums. Persist canonical links only with
   core relations/verdicts: direct support = `supports` + `verified`;
   contradiction = `contradicts` + `verified`; partial/tangential context =
   `relevant_to` or `background` + `provisional`; unavailable support =
   `relevant_to` + `cannot_determine`. Prefer atomizing/narrowing the claim over
   calling partial evidence support.
5. Abstract-only evidence can be a tangential/cannot-determine report item, but
   can never be canonical `verified`, `supports`, or `contradicts` for a
   substantive method, theorem, experiment, or novelty claim.
6. A missing claim, new near-neighbor, or stale source version triggers a
   persisted query, vault-first then external retrieval, new source/link
   records, and a replacement packet before re-audit.

Write a per-invocation report to
`.research-state/<slug>-claim-audit.md`, including claim ID, sentence, bibkey,
work/source-version/link IDs, locator, scope, and verdict.

### Stage 3 — User-facing report

Report totals for rendering, metadata, and **atomic claims** separately. List
blocking action items for fabricated/mismatched works and for every partial,
tangential, contradicts, or cannot-determine claim. Include current packet ID,
hash/status, unresolved query IDs, and whether retrieval changed the draft or
closest-prior set.

## State update and gate

For each `key_claims` entry, retain `claim_id` and `evidence_link_ids`.

- Set `audit_status: verified` only when all rendered metadata is verified and
  every substantive invocation of that claim has a valid `supports` passage
  link in the current packet.
- Use `mismatched` or `fabricated` for those metadata failures.
- Leave `pending` for partial/tangential/cannot-determine or unresolved
  retrieval; record the blocking reason in the audit artifact.

Any `contradicts` result is blocking. The paper cannot advance to `final` while
any invoked substantive claim is ungrounded, the packet is stale, or the latest
metadata audit is not clean.

When all metadata/passage checks pass and the bound self-review has no blocking
finding, append the citation-audit artifact IDs and verdict to the composite
scientific-review artifact, recompute/hash it, and set
`lifecycle_gates.scientific_review.status: pass` with its draft hash, upstream
hashes, and citation-audit artifact IDs. Otherwise keep it `conditional`/`fail`.
This mode never advances directly to submission/final.

## Exit checklist

- [ ] Stage -1 deterministic export ran via absolute evidence CLI; view hash was
      compared/stored and any older audit invalidated on change.
- [ ] Stage 0 ran with pasted output; no undefined keys remain.
- [ ] Stage 1 ran for real; every rendered work maps to a canonical work and is
      classified; unreachable results are queued for retry.
- [ ] Every substantive citation invocation was atomized and mapped to packet
      claim/source-version/link IDs plus a stable locator.
- [ ] Passage text—not abstract/model knowledge—determined support.
- [ ] New gaps/near-neighbors triggered query, retrieval, links, and re-freeze.
- [ ] Per-invocation report and aggregate action list were written.
- [ ] `audit_status: verified` was used only when metadata and all passage links
      passed; any unresolved/contradictory claim blocks `final`.
- [ ] Scientific-review lifecycle gate became `pass` only when its current
      draft/upstream hashes and this clean citation audit all validated.
