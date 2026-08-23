# Evidence-Grounding Protocol

Use this protocol whenever a skill searches literature, evaluates a gap or
candidate, or writes a literature-backed claim. It is the detailed contract;
skill entrypoints should link here instead of duplicating it.

## Three artifacts, three jobs

- `.research-state/<slug>.md` is the **control plane**: stage, selected
  candidate, and IDs/hashes of the current evidence snapshot.
- The user-selected **external Obsidian vault root** is the canonical data plane:
  works, immutable source versions, query runs, atomic claims, passage links,
  candidates, datasets, and frozen evidence packets. Its internal `.evidence/`
  directory is machine metadata; it is not the vault root and must not be
  confused with a project-local store.
- `refs/<slug>.bib` is a **generated view** of canonical work records. It is
  useful to LaTeX but is neither a source of truth nor evidence that a claim is
  supported.

Use the host-neutral evidence-store workflow and CLI described by the bundled
`evidence-store` skill. When invoking the CLI directly, use the checked-in
entrypoint. Resolve the plugin root from the already loaded skill file and set
`EVIDENCECTL` to the **absolute** `<plugin-root>/shared/evidencectl.py`, or use
the evidence-store skill-local wrapper by absolute path. Never assume the
research project's working directory is the plugin root. `EVIDENCECTL` below is
a path placeholder, not a Codex/Claude environment API. Invoke it with Python
3.11 or newer (`python3`), not a possibly absent `python` alias. A host may use its
native question, shell, or subagent facility, but persisted records/gates are identical.
Every leaf command takes `--vault`, for example:

```bash
python3 "$EVIDENCECTL" validate --vault "<external-vault-root>"
python3 "$EVIDENCECTL" query add --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" work ingest --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" passage add --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" claim add --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" claim link --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" candidate add --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" packet freeze --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" audit add --vault "<external-vault-root>" --help
python3 "$EVIDENCECTL" export bibtex --vault "<external-vault-root>" --help
```

Use `--help` rather than guessing flags. Other canonical operations include
`topic add`, `reading add`, `method add`, `dataset add`, and `index rebuild`.
Every **present, verified** evidence-store or project artifact SHA-256 is stored
as bare lowercase 64-character hexadecimal text; never add a prefix. An
intentionally unavailable dataset hash, raw provider-response hash, or
unverified excerpt hash may be empty only where the evidence schema explicitly
allows it, and must retain its `unknown`/unverified status. A metadata/abstract
discovery fingerprint is not a hash of source bytes and cannot validate content.

## What counts as evidence

Parametric/model knowledge, user recollection, panel output, search-result
snippets, and generated prose may produce **queries or hypotheses only**. They
never establish novelty, support a paper claim, or resolve a gap.

A literature-backed assertion is grounded only when it has all of:

1. a canonical work record;
2. an immutable source-version record with a byte-content hash for inspected
   full text/supplement/dataset evidence (metadata/abstract discovery records
   carry only a discovery fingerprint and cannot ground substantive support);
3. an atomic claim record;
4. an evidence link to a stable locator or passage in that source version; and
5. an explicit relation/verdict and evidence scope.

Abstract-only evidence may establish metadata, topic relevance, or motivate a
follow-up query. It must never be marked `verified`, `supports`, or
`contradicts`, and cannot ground a substantive method, theorem, assumption,
experiment, or novelty claim. Prior verification
may be reused only when the source-version hash and locator are unchanged.

### The paraphrase is not the evidence (R-EV-1)

A passage record's paraphrase is not the evidence; the inspected span is.
`evidencectl passage add` stores a paraphrase and an excerpt hash — `--excerpt`
is hashed in memory and never written — so the store can prove that some span
hashing to a given value was inspected, but never that the paraphrase reports
that span correctly. The paraphrase is the artifact that can be wrong.

Capture the verbatim quote for every passage before calling `passage add`,
in the source's own vault note and under the same locator, so the paraphrase
stays checkable against it. A host-side reading skill may own that capture
step; the requirement holds whether or not one is installed. Never mark a
passage `verified`, `supports`, or `contradicts` for a substantive method,
theorem, assumption, experiment, or novelty claim when no verbatim quote for
it can be retrieved.

Canonical wording: `shared/firm_rules.md` § R-EV-1.

### Two-fidelity rule (corpus hits vs. grounded evidence)

The local corpus — `docs/corpus-manifest-<slug>.md` and its abstract-scope
records, built by `literature-explorer` in `corpus-prefetch` mode and queried
continuously by `algo-brainstorm`'s novelty reflex — is a **second, lower
fidelity**. It exists so that a near neighbor is noticed *during* discussion
rather than at a gate. It does not create a second standard of proof.

A corpus hit is **alarm evidence only**. It justifies a warning, a named nearest
neighbor with a one-line same/different statement, and a query. It can never
be, or substitute for:

- a novelty verdict of any value;
- a claim-to-passage evidence link;
- a Same/Different/Δ row in `novelty-check`;
- a sentence in the paper.

Promoting an idea to a registered candidate, or changing anything about a frozen
method, requires the full loop below — canonical work, immutable source version,
inspected passage, atomic claim, evidence link, frozen packet — exactly as if
the corpus did not exist. "The corpus says nothing is close" is a retrieval
observation, never a novelty finding.

## Mandatory retrieval loop

Run this loop before answering a literature-grounded question or crossing an
evidence gate:

1. **Canonicalize the question.** Identify the topic, candidate (if any), and
   atomic claims. For a candidate record the algorithmic primitives, objective
   or estimand, data regime, assumptions, and claimed delta.
2. **Query the vault first.** Search canonical works, source versions, claims,
   and packets already in the vault. Persist the query and result IDs as a
   query-run even when the result set is empty.
3. **Retrieve externally second.** Only unresolved coverage gaps become
   external queries. Persist each external query-run and provider. Ingest or
   update canonical works and immutable source versions; do not paste an
   untracked result straight into state or prose.
4. **Ground atomic claims.** Inspect the actual passage; persist a `passage`
   record with source-version ID, locator, and excerpt hash, then create the
   claim-to-source evidence link. Use only core relation/verdict enums:
   contradiction is relation `contradicts`; partial/contextual material uses
   `relevant_to` or `background` with verdict `provisional` or
   `cannot_determine`, rather than forcing `supports`/`verified`.
5. **Freeze a candidate-specific packet.** Include the candidate, atomic claim,
   evidence-link, referenced passage, exact source-version, query-run, canonical
   work, and applicable dataset IDs. Validate the packet with the evidence-store
   tooling. Canonical packets are `frozen` or
   `invalidated`; research state maps a validated `frozen` packet to `current`.
6. **Answer from that packet only.** Bibliographic display keys may come from
   the generated `.bib`, but every substantive sentence must trace to a packet
   claim and passage link.
7. **Loop on discoveries.** A new gap, competing formulation, or near-neighbor
   is not an aside. Convert it into one or more queries, return to step 2, add
   the resulting records/links, and freeze a replacement packet before revising
   the answer or verdict. Stop only when the coverage checklist is answered or
   the remaining uncertainty is explicitly reported. Persist the final decision
   as an `audit_verdict` (`pass`, `conditional`, `fail`, or
   `cannot_determine`) when the calling mode makes a gate decision.

Never turn `[VERIFY]` into prose by confidence. `[VERIFY]` is a durable query
queue item until this loop produces evidence or a documented no-result run.

## Packet scope and freshness

An evidence packet is candidate-specific. Its snapshot/fingerprint must cover:

- candidate ID and algorithmic primitives/components;
- objective, estimand, and claimed optimization target;
- data regime, assumptions, and evaluation setting;
- atomic claim IDs and their current text/content hashes;
- evidence-link IDs, referenced passage IDs, immutable source-version IDs,
  query-run/work IDs, and applicable dataset IDs/content hashes.

Changing any primitive/component, objective/estimand, data regime/assumption,
or material claim invalidates the canonical packet. Adding a new near-neighbor
or contradictory passage also invalidates it. Record dependency hashes and
`invalidated_by` in the vault, then set `evidence_packet_status: stale` in
research state. A stale packet
cannot satisfy a stage gate; repeat the retrieval loop and freeze a replacement.
Treat a candidate title/name change as material because the canonical candidate
ID and packet dependency may change; use the CLI and freeze a replacement
packet rather than assuming that a rename is cosmetic.

## Decision rules

- **Gap analysis:** an `unverified`, abstract-only, or memory-derived item may
  enter the query queue, but it cannot be ranked as a top gap. Top gaps require
  passage-grounded evidence both for the limitation and for the open/partial
  status claimed.
- **Ideation:** generated candidates are speculative. Register each surviving
  candidate, run targeted prior-art retrieval, and freeze a packet before
  ranking it or handing it to novelty review.
- **Novelty:** require a current packet for the exact candidate. Compare
  primitives, objective, regime, theory, and evidence—not just names. Moving an
  existing method to another application/domain/dataset is an application delta,
  never method novelty by itself.
- **Anti-sycophancy:** weaknesses are useful design feedback but cannot replace
  prior-art retrieval when judging novelty or endorsing a contribution. A
  positive novelty/contribution judgment always requires grounded near-neighbor
  evidence.
- **Writing:** a BibTeX key proves only that a canonical work can be rendered.
  It does not prove that the cited passage supports the sentence. Draft and
  audit at atomic-claim granularity from current packet links.

## Stage gates and backward compatibility

The following are hard gates:

| Transition/action | Required evidence state |
|---|---|
| start a discussion mode (`gap-analysis`, `formalize`, `ideate`) | `corpus_manifest:` present and refreshed if >6 months old — alarm fidelity, never a packet substitute |
| publish top gaps | passage-grounded gap claims; no unverified top item |
| rank/choose an idea | candidate registered; targeted retrieval completed; packet current |
| issue novelty verdict | current packet for the exact candidate and claim set |
| outline or draft cited claims | current packet(s); each substantive claim linked to a passage |
| mark citation/claim audit clean | metadata valid **and** every invoked substantive claim passage-grounded |

Legacy state remains readable. If it has only `literature:` and `citations:`
paths, import/deduplicate the works into the vault, create source versions and
atomic claim links, register the candidate, and freeze a packet. Preserve the
legacy fields as compatibility views. Do not treat an old survey or `.bib` as a
current packet, and do not silently advance the stage during migration.

## Failure behavior

If the vault, external retrieval, or a primary passage is unavailable:

- preserve the item as a query/hypothesis with `unverified` status;
- state which query-run, source, or passage is missing;
- do not issue a positive novelty verdict, rank it as a top gap, or write it as
  a supported fact; and
- offer the smallest retrieval step needed to unblock the gate.

Every evidence-dependent output ends with a compact evidence summary: packet
ID and status, source-version/link counts, unresolved queries, and whether any
answer changed because a newly retrieved near-neighbor was found.
