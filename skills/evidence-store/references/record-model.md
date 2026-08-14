# Evidence record model

The vault uses one Markdown file per canonical record. Frontmatter values are JSON-compatible YAML, so the format is readable without a YAML library. All records contain `record_type`, `id`, `schema_version`, `created_at`, and `updated_at`.

| Type | Stable identity | Important relations |
| --- | --- | --- |
| `topic` | normalized topic slug | root for candidates and packets |
| `work` | DOI, arXiv ID, or normalized bibliographic fingerprint | `topic_ids`, `current_source_version_id` |
| `source_version` | work ID plus SHA-256 digest | `work_id`, `source_path`, `source_url`, `source_scope`, `hash_kind` |
| `claim` | SHA-256 of normalized atomic claim | `topic_ids` |
| `evidence_link` | hash of claim, source span, passage, relation, verdict, and scope | `claim_id`, `source_version_id`, optional/required `passage_id` |
| `candidate` | topic plus normalized title | primitives, objective, data regime, assumptions, claims, and their hashes |
| `dataset` | normalized title plus external URI | `topic_ids`, real `content_hash`, and `hash_status` |
| `evidence_packet` | hash of frozen dependency hashes | candidate, claims, links, source versions, passages, query runs, works, and selected datasets |
| `query_run` | topic, query, provider, and execution time | provider-ranked `result_work_ids`, observations, and raw-response hash |
| `reading` | work ID | reusable summary plus inspected source versions |
| `passage` | source version, locator, and excerpt hash | work, topics, and atomic claims |
| `method` | normalized method name | works, topics, and typed method relations |
| `audit_verdict` | hash of audit inputs and time | frozen packet, optional candidate, and optional subject/artifact/protocol hashes |

Relations are `supports`, `contradicts`, `extends`, `subsumes`, `same_primitive_as`, `relevant_to`, `uses`, `evaluates_on`, `belongs_to`, `background`, `mentions`, or `compares`. Evidence verdicts are `verified`, `provisional`, `cannot_determine`, or `disputed`. Audit verdicts are `pass`, `conditional`, `fail`, or `cannot_determine`. Scopes are `metadata`, `abstract`, `full_text`, `supplement`, or `dataset`.

`source_version.content_hash` is retained for compatibility but its meaning is explicit. A local source file uses `hash_kind: content_sha256`; full text, supplement, and dataset scopes require it. A URL-derived metadata/abstract record uses `hash_kind: discovery_fingerprint`, which detects metadata identity changes but does **not** validate source content.

A missing dataset hash remains empty with `hash_status: unknown`; it is never replaced by a URI fingerprint. Validation warns until a real SHA-256 is supplied. Query `raw_response_hash`, non-verified excerpt hashes, and optional audit subject/protocol hashes may also be empty. Every hash that is present is bare lowercase 64-character SHA-256.

A frozen packet stores the semantic hash of its candidate, claims, evidence links, source versions, linked passages, query runs, works, and selected datasets, plus an immutable portable snapshot of those records. It does not copy full text or excerpts. Validation reports `stale_packet` when a frozen dependency is missing or changed. New evidence links invalidate packets selecting that claim; new query runs invalidate only packets for that topic. Candidate/dependency updates and explicit `packet invalidate --reason` also mark packets `invalidated` while preserving snapshots. Audit verdicts remain immutable records of what was concluded from their packet snapshot at audit time. They are current and gate-eligible only while the referenced packet remains `frozen`; an audit tied to an invalidated packet is historical provenance, not a current pass.

Generated Markdown is bounded by:

```text
<!-- EVIDENCECTL:BEGIN -->
...
<!-- EVIDENCECTL:END -->
```

Index rebuild replaces only that block and preserves all manual text around it.
