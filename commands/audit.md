---
description: Audit citations in the current paper draft (paper-writer citation-audit mode).
argument-hint: [--bib refs/<slug>.bib]
---

Invoke `paper-writer` in `citation-audit` mode for the current research
topic: $ARGUMENTS

Two-stage protocol:

1. **Metadata verification**: run `skills/paper-writer/scripts/verify_citations.py`
   against the `.bib` file. Output: `.research-state/<slug>-audit.json`
   with per-entry `verified` / `mismatched` / `fabricated` / `unreachable`
   classification.

2. **Claim-support audit**: for each `verified` citation invoked in the
   draft, check whether the cited paper's abstract supports the claim
   in the citing sentence. Classify `supports` / `tangential` /
   `contradicts` / `cannot_determine`.

Produce a markdown report with action items. Update
`key_claims[*].audit_status` in research state.

Hard rule: paper cannot advance to `final` stage until audit is clean
(no `fabricated`, no `contradicts`).
