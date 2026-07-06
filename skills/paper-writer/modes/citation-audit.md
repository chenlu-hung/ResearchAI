# Mode: citation-audit

**Purpose**: the integrity gate. Verify every citation in the draft (a)
exists, (b) is correctly cited (right paper, right key), and (c) actually
supports the claim it's invoked for.

This is the **mandatory gate** before submission. Borrows the *audit
checkpoint* idea from ARS, but implemented as a two-stage pipeline:
script-based metadata verification + LLM-based claim-support check.

## Inputs

- `paper/main.tex` (or section files) — to extract `\cite{...}` invocations
- `refs/<slug>.bib` — the bibliography
- Internet access for Semantic Scholar API

## Procedure

### Stage 0 — Static cross-check (`scripts/check_tex.py`)

```bash
uv run python skills/paper-writer/scripts/check_tex.py \
  paper/main.tex --bib refs/<slug>.bib --json
```

Catches undefined `\cite` keys, dangling `\ref`s, and missing figure files
*before* any API call. Fix undefined keys first — Stages 1–2 can only audit
keys that resolve. Paste the script's real output (rule 4 of
`execution_discipline.md`); never assert "all cites resolve" from reading.

### Stage 1 — Metadata verification (`scripts/verify_citations.py`)

```bash
uv run python skills/paper-writer/scripts/verify_citations.py \
  --bib refs/<slug>.bib \
  --out .research-state/<slug>-audit.json
```

(`uv run` ensures the project's virtualenv with `httpx`, `tenacity`, and
`pybtex` is used. If running outside `uv`, activate the venv first.)

For each entry in `.bib`:

1. Construct a Semantic Scholar query from title + first author + year
2. Take the top match
3. Compute string similarity (title) + author/year exactness
4. Classify:
   - `verified` — title sim > 0.85, year matches ±1, first author matches
   - `mismatched` — paper exists but metadata differs (probable typo or
     wrong key)
   - `fabricated` — no plausible match in top-K results
   - `unreachable` — API failure, mark for retry

### Stage 2 — Claim-support audit (LLM pass)

For each `verified` citation:

1. Extract the surrounding context: the sentence and 1 sentence before/after
   the `\cite{key}` in the draft.
2. Fetch the cited paper's title + abstract (from Stage 1 result).
3. Ask: "Does this paper's abstract support the specific claim made in
   the citing sentence?"
4. Classify:
   - `supports` — abstract clearly supports the claim
   - `tangential` — paper is on the topic but doesn't directly support
     the specific claim
   - `contradicts` — paper actually says the opposite
   - `cannot_determine` — abstract too generic; needs full-paper read

5. Output a per-citation report to `.research-state/<slug>-claim-audit.md`.

### Stage 3 — User-facing report

Generate a markdown summary:

```markdown
# Citation audit — <slug> — <date>

## Summary
- Total citations: 47
- Verified: 41
- Mismatched: 3 ⚠️
- Fabricated: 1 🚨
- Tangential: 5 ⚠️
- Contradicts: 0

## Action items

### 🚨 Fabricated
- `smith2026foo`: no plausible match. Search alternative: "Smith 2026
  conformal something"
  - Sentence: "Smith (2026) proved minimax optimality..."
  - Verdict: remove or replace before submission.

### ⚠️ Mismatched
- `tibshirani19conformal`: title in .bib says "Conformal prediction under
  covariate shift" but the canonical title is "Conformal Prediction
  Under Covariate Shift" (capitalization). Fix bibkey.
- ...

### ⚠️ Tangential
- `barber2021jackknife`: cited for "marginal coverage under shift", but
  abstract is about conditional coverage. Consider citing different
  paper or rewording claim.
- ...
```

## State update

After audit:

```yaml
key_claims:
  - claim: "..."
    supporting_refs: [tibshirani2019, ...]
    audit_status: verified      # was: pending
```

Set `audit_status: verified` only if Stage 1 returns `verified` and
Stage 2 returns `supports` for all refs.

If any `fabricated` or `contradicts` finding: `audit_status: failed` —
must fix before draft can proceed.

## Hard rule

`paper-writer` modes must not advance `stage` past `revision` (i.e.,
to `final`) unless the most recent audit is clean.

## Limitations

- Stage 2 uses abstracts only; deeper claims may need full-paper read.
  Surface this as `cannot_determine` rather than false negatives.
- Semantic Scholar's coverage is good but not exhaustive for very new
  preprints — for ArXiv-only refs ≤2 weeks old, fall back to arXiv
  metadata.
- Conference proceedings sometimes have different titles than arXiv
  versions; treat title similarity > 0.7 + author + year as soft-match
  and surface for user review.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Stage 0 ran with pasted output; no undefined citation keys remain.
- [ ] Stage 1 script ran (real output, not simulated); every bib entry
      classified verified / mismatched / fabricated / unreachable.
- [ ] Stage 2 claim-support verdict exists for every verified citation
      invoked in the draft; `unreachable` queued for retry, not dropped.
- [ ] Stage 3 report written with per-category action items.
- [ ] `audit_status` flipped only per the rule; any `fabricated` or
      `contradicts` → `audit_status: failed` and `stage` NOT advanced.
