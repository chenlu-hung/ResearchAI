---
description: Run a vault-first Stats/ML survey with passage-grounded claims, an evidence packet, and generated BibTeX.
argument-hint: [corpus-prefetch] <topic>
---

Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
it is the absolute parent of the file's `commands/` directory. Never derive it
from the user's working directory. Resolve every `skills/...`, `shared/...`, or
other plugin resource below as `$PLUGIN_ROOT/<path>`. Dependency-bearing Python
scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.

Invoke the `literature-explorer` skill on the topic: $ARGUMENTS

If the arguments begin with `corpus-prefetch`, run that mode instead
(`skills/literature-explorer/corpus-prefetch.md`): one broad shallow sweep —
metadata + abstracts for ~100–300 works across four mandatory axes
(application-field, mathematical-skeleton across fields and decades including
pre-2015, adjacent-fields, historical) — emitting a hashed
`docs/corpus-manifest-<slug>.md` plus a `corpus_manifest:` state pointer. It
produces no survey, claim map, or packet, satisfies no lifecycle gate, and its
abstract-scope records are alarm evidence only. `algo-brainstorm`'s
`gap-analysis`, `formalize`, and `ideate` refuse to start without it.

Otherwise follow the full pipeline in `skills/literature-explorer/SKILL.md`:

1. Create/load research state and its canonical evidence-vault topic
2. Generate 3–5 perspectives (see `perspectives.md`)
3. Treat model recall as query seeds only; persist query-runs and query the vault first
4. Retrieve externally (arXiv + Semantic Scholar + OpenAlex, or optional
   `literature-review-ml`) only for recorded coverage gaps; before ranking,
   identity-resolve/ingest every raw result and persist each query×provider's
   ordered work IDs, raw-response hash, observations/ranks, filters, and exclusions
5. Deduplicate/rank only as a downstream view; persist immutable primary source
   versions, atomic claims, and passage links
6. Build the outline/dialogue; loop retrieval on each new gap or near-neighbor
7. Freeze/validate the packet, emit `docs/survey-<slug>.md`, and deterministically
   export `refs/<slug>.bib` from canonical works via the absolute evidence CLI
8. Update research-state packet IDs/hashes/status plus legacy artifact paths

Follow `shared/prompts/evidence_grounding.md`. A BibTeX key, abstract, model
memory, or panel output cannot support a substantive claim.
