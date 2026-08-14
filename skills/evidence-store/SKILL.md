---
name: evidence-store
description: Manage reusable scholarly evidence in an Obsidian Markdown vault. Use when a Stats/ML research workflow must retrieve prior art before brainstorming, preserve paper and dataset provenance across topics, turn literature into atomic claim-to-source links, audit source versions or stale evidence, freeze a candidate-specific evidence packet, or rebuild and validate the shared research index. Also use before making novelty, method, experiment, or citation claims that should survive across sessions.
---

# Evidence Store

Use the repository-bundled `scripts/evidencectl.py` from either Claude Code or Codex. Treat vault Markdown as canonical; do not depend on host-specific APIs.

## Grounding loop

1. Run `validate` before reusing stored evidence. Resolve errors that affect the current topic or candidate.
2. Search the existing Works, Claims, Query Runs, and Evidence Packets before external retrieval.
3. Record each new literature query with `query add`; ingest each work once and associate it with all relevant topic IDs.
4. Capture reusable synthesis with `reading add`, located paraphrases with `passage add`, and transferable algorithm primitives with `method add`.
5. Rewrite a research assertion as an atomic claim. Persist the inspected span with `passage add`, then link the claim with `claim link --passage`. Verified full-text `supports`/`contradicts` links require a passage whose source, locator, and excerpt hash match exactly.
6. Keep model-memory statements explicitly speculative. Do not use them as evidence; use them to formulate retrieval queries.
7. Freeze a candidate-specific packet before giving novelty advice, freezing a method, designing confirmatory experiments, or drafting a contribution claim. Record the result with `audit add`.
8. Re-freeze after a candidate component, claim, evidence link, source version, selected work/dataset, or topic query changes. New links invalidate only packets selecting that claim; new queries invalidate packets for that topic. Use `packet invalidate --reason` for other material discoveries. A stale or invalidated packet does not pass the gate. Its audit remains an immutable historical verdict, but is not current or gate-eligible once the referenced packet is no longer frozen.

## Evidence rules

- Use `verified` only after inspecting the cited full-text, supplement, or dataset location. Supply both locator and excerpt hash; verified full-text support/contradiction also requires `passage_id`.
- Treat abstract-only evidence as discovery evidence. Never mark it `verified`, `supports`, or `contradicts`.
- Treat URL-derived metadata/abstract `content_hash` values as `hash_kind: discovery_fingerprint`, not source-content validation. Full text, supplement, and dataset sources require `hash_kind: content_sha256` over a real source file.
- Distinguish `cannot_determine` from absence of a method in the literature.
- Store a paper once under `20 Library/Works`; connect it to multiple topics by stable IDs.
- Store large datasets externally and add only their URI, version, and content hash to the vault.
- Copy a source into `90 Attachments` only when the user explicitly requests `--copy-source`. Otherwise preserve its path and hash.
- Do not put SQLite, WAL, embedding caches, or other live derived databases inside a synced vault.
- Never edit text between `EVIDENCECTL` markers by hand. Put durable synthesis outside the generated block.
- Treat packet `frozen` as state `current` only after validation. Packet dependencies cover candidate, claims, evidence links, source versions, passages, query runs, works, and selected datasets.
- Use bare lowercase 64-character SHA-256 only when a hash exists. Dataset hashes may be empty with `hash_status: unknown`; query raw-response hashes, non-verified excerpt hashes, and optional audit subject/protocol hashes may also be empty.
- `init` seeds versioned templates under `99 Templates/v1` and canonical schemas under `.evidence/schemas` without overwriting existing files.

## Commands

Set `CTL` to the absolute path of this skill's `scripts/evidencectl.py`, then call it with Python 3.11 or newer.

```bash
python3 "$CTL" init --vault "$VAULT"
python3 "$CTL" topic add --vault "$VAULT" --title "Neural operator cross-resolution"
python3 "$CTL" work ingest --vault "$VAULT" --title "..." --author "..." \
  --year 2024 --doi "10..." --url "https://..." --topic topic-neural-operator-cross-resolution
python3 "$CTL" work update --vault "$VAULT" --work work-... --title "Corrected title"
python3 "$CTL" claim add --vault "$VAULT" --topic topic-neural-operator-cross-resolution \
  --text "Atomic, falsifiable statement"
python3 "$CTL" passage add --vault "$VAULT" --source source-... \
  --locator "Section 3, Eq. 4" --paraphrase "Located non-verbatim summary" \
  --excerpt-hash SHA256 --claim claim-... --topic topic-...
python3 "$CTL" claim link --vault "$VAULT" --claim claim-... --source source-... \
  --passage passage-... --locator "Section 3, Eq. 4" --relation supports --verdict verified \
  --scope full_text --excerpt-hash SHA256 --verifier "human-or-agent-id"
python3 "$CTL" packet freeze --vault "$VAULT" --topic topic-... \
  --candidate candidate-... --claim claim-... --evidence-link evidence-... \
  --query-run query-... --dataset dataset-...
python3 "$CTL" packet invalidate --vault "$VAULT" --packet packet-... \
  --reason "new near-neighbor changes the comparison"
python3 "$CTL" export bibtex --vault "$VAULT" --topic topic-... --out references.bib
python3 "$CTL" index rebuild --vault "$VAULT"
python3 "$CTL" validate --vault "$VAULT"
```

Also use `reading add`, `passage add`, `method add`, `audit add`, `candidate add`, `dataset add`, and `query add`; run the command with `--help` for exact arguments.

## Read on demand

- Read [references/record-model.md](references/record-model.md) when mapping another workflow or vault into the store.
- Read [references/schemas/evidence-records.schema.json](references/schemas/evidence-records.schema.json) when generating or validating records outside the CLI.
- Read [references/schemas/config.schema.json](references/schemas/config.schema.json) when provisioning a vault from another tool.
