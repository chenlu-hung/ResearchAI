"""Command-line interface for the Markdown evidence store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from .model import AUDIT_VERDICTS, EVIDENCE_SCOPES, RELATIONS, VERDICTS
from .store import EvidenceStore, EvidenceStoreError


def _leaf(subparsers: Any, name: str, help_text: str) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(name, help=help_text, description=help_text)
    parser.add_argument("--vault", required=True, type=Path, help="Obsidian vault root")
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evidencectl",
        description="Host-neutral, Markdown-backed scholarly evidence store",
    )
    parser.add_argument("--version", action="version", version="evidencectl 1")
    commands = parser.add_subparsers(dest="command", required=True)

    init = _leaf(commands, "init", "Initialize or repair the evidence-vault structure")
    init.add_argument("--name", default="", help="Human-readable vault name")

    topic = commands.add_parser("topic", help="Manage research topics")
    topic_commands = topic.add_subparsers(dest="topic_command", required=True)
    topic_add = _leaf(topic_commands, "add", "Add a research topic")
    topic_add.add_argument("--title", required=True)
    topic_add.add_argument("--slug", default="")
    topic_add.add_argument("--status", default="active")
    topic_add.add_argument("--tag", action="append", default=[])

    work = commands.add_parser("work", help="Manage scholarly works and source versions")
    work_commands = work.add_subparsers(dest="work_command", required=True)
    work_ingest = _leaf(work_commands, "ingest", "Ingest work metadata and an optional source")
    work_ingest.add_argument("--title", required=True)
    work_ingest.add_argument("--author", action="append", default=[])
    work_ingest.add_argument("--year", type=int)
    work_ingest.add_argument("--doi", default="")
    work_ingest.add_argument("--arxiv-id", default="")
    work_ingest.add_argument("--url", default="")
    work_ingest.add_argument("--topic", action="append", default=[])
    work_ingest.add_argument("--source-file", type=Path)
    work_ingest.add_argument(
        "--copy-source",
        action="store_true",
        help="Copy the source into content-addressed vault attachments",
    )
    work_ingest.add_argument("--source-kind", default="web")
    work_ingest.add_argument(
        "--source-scope", choices=sorted(EVIDENCE_SCOPES), default="metadata"
    )
    work_update = _leaf(work_commands, "update", "Correct canonical work metadata")
    work_update.add_argument("--work", required=True)
    work_update.add_argument("--title")
    work_update.add_argument("--author", action="append", default=None)
    work_update.add_argument("--year", type=int)
    work_update.add_argument("--doi")
    work_update.add_argument("--arxiv-id")
    work_update.add_argument("--url")
    work_update.add_argument("--topic", action="append", default=None)

    claim = commands.add_parser("claim", help="Manage atomic claims and evidence links")
    claim_commands = claim.add_subparsers(dest="claim_command", required=True)
    claim_add = _leaf(claim_commands, "add", "Add an atomic, falsifiable claim")
    claim_add.add_argument("--text", required=True)
    claim_add.add_argument("--topic", action="append", required=True)
    claim_add.add_argument("--status", default="open")
    claim_link = _leaf(claim_commands, "link", "Link a claim to a versioned source span")
    claim_link.add_argument("--claim", required=True)
    claim_link.add_argument("--source", required=True)
    claim_link.add_argument("--passage", default="")
    claim_link.add_argument("--locator", required=True)
    claim_link.add_argument("--relation", choices=sorted(RELATIONS), required=True)
    claim_link.add_argument("--verdict", choices=sorted(VERDICTS), required=True)
    claim_link.add_argument("--scope", choices=sorted(EVIDENCE_SCOPES), required=True)
    excerpt = claim_link.add_mutually_exclusive_group()
    excerpt.add_argument("--excerpt", default="", help="Hashed in memory; not stored verbatim")
    excerpt.add_argument("--excerpt-hash", default="")
    claim_link.add_argument("--verifier", required=True)
    claim_link.add_argument("--verified-at", default="")

    candidate = commands.add_parser("candidate", help="Manage candidate research methods")
    candidate_commands = candidate.add_subparsers(dest="candidate_command", required=True)
    candidate_add = _leaf(candidate_commands, "add", "Add or update a candidate method")
    candidate_add.add_argument("--topic", required=True)
    candidate_add.add_argument("--title", required=True)
    candidate_add.add_argument("--description", default="")
    candidate_add.add_argument("--claim", action="append", default=[])
    candidate_add.add_argument("--primitive", action="append", required=True)
    candidate_add.add_argument("--objective", required=True)
    candidate_add.add_argument("--data-regime", required=True)
    candidate_add.add_argument("--assumption", action="append", default=[])
    candidate_add.add_argument("--status", default="proposed")

    dataset = commands.add_parser("dataset", help="Manage external dataset manifests")
    dataset_commands = dataset.add_subparsers(dest="dataset_command", required=True)
    dataset_add = _leaf(dataset_commands, "add", "Add a dataset manifest without copying data")
    dataset_add.add_argument("--title", required=True)
    dataset_add.add_argument("--uri", required=True)
    dataset_add.add_argument("--topic", action="append", default=[])
    dataset_add.add_argument("--content-hash", default="")
    dataset_add.add_argument("--dataset-version", default="")

    query = commands.add_parser("query", help="Record reproducible literature queries")
    query_commands = query.add_subparsers(dest="query_command", required=True)
    query_add = _leaf(query_commands, "add", "Record a query run and its returned works")
    query_add.add_argument("--topic", required=True)
    query_add.add_argument("--query", required=True)
    query_add.add_argument("--provider", required=True)
    query_add.add_argument("--result-work", action="append", default=[])
    query_add.add_argument("--filters-json", default="{}")
    query_add.add_argument("--raw-response-hash", default="")
    query_add.add_argument(
        "--observations-json",
        default="[]",
        help="Ordered provider observations/ranks as a JSON array",
    )
    query_add.add_argument("--executed-at", default="")

    reading = commands.add_parser("reading", help="Manage reusable paper-reading memory")
    reading_commands = reading.add_subparsers(dest="reading_command", required=True)
    reading_add = _leaf(reading_commands, "add", "Create or update a reusable work reading")
    reading_add.add_argument("--work", required=True)
    reading_add.add_argument("--topic", action="append", default=[])
    reading_add.add_argument("--source", action="append", default=[])
    reading_add.add_argument("--summary", default="")
    reading_add.add_argument("--status", default="in_progress")

    passage = commands.add_parser("passage", help="Manage reusable versioned source passages")
    passage_commands = passage.add_subparsers(dest="passage_command", required=True)
    passage_add = _leaf(passage_commands, "add", "Add a located passage and paraphrase")
    passage_add.add_argument("--source", required=True)
    passage_add.add_argument("--locator", required=True)
    passage_add.add_argument("--paraphrase", required=True)
    passage_add.add_argument("--topic", action="append", default=[])
    passage_add.add_argument("--claim", action="append", default=[])
    passage_excerpt = passage_add.add_mutually_exclusive_group()
    passage_excerpt.add_argument("--excerpt", default="", help="Hashed in memory; not stored verbatim")
    passage_excerpt.add_argument("--excerpt-hash", default="")

    method = commands.add_parser("method", help="Manage reusable method concepts")
    method_commands = method.add_subparsers(dest="method_command", required=True)
    method_add = _leaf(method_commands, "add", "Add or update a method concept")
    method_add.add_argument("--name", required=True)
    method_add.add_argument("--description", required=True)
    method_add.add_argument("--topic", action="append", default=[])
    method_add.add_argument("--work", action="append", default=[])
    method_add.add_argument(
        "--relation",
        action="append",
        default=[],
        metavar="RELATION:TARGET_ID",
        help="Repeatable typed relation to another canonical record",
    )

    audit = commands.add_parser("audit", help="Manage packet-grounded audit verdicts")
    audit_commands = audit.add_subparsers(dest="audit_command", required=True)
    audit_add = _leaf(audit_commands, "add", "Record an audit against a frozen packet")
    audit_add.add_argument("--topic", required=True)
    audit_add.add_argument("--candidate", default="")
    audit_add.add_argument("--packet", required=True)
    audit_add.add_argument("--verdict", choices=sorted(AUDIT_VERDICTS), required=True)
    audit_add.add_argument("--rationale", required=True)
    audit_add.add_argument("--auditor", required=True)
    audit_add.add_argument("--audited-at", default="")
    audit_add.add_argument("--subject-type", default="")
    audit_add.add_argument("--subject-id", default="")
    audit_add.add_argument("--subject-hash", default="")
    audit_add.add_argument("--protocol-hash", default="")
    audit_add.add_argument(
        "--artifact-hash",
        action="append",
        default=[],
        metavar="LABEL=SHA256",
        help="Repeatable artifact label and bare lowercase SHA-256 binding",
    )

    packet = commands.add_parser("packet", help="Manage immutable evidence snapshots")
    packet_commands = packet.add_subparsers(dest="packet_command", required=True)
    packet_freeze = _leaf(packet_commands, "freeze", "Freeze candidate-specific evidence")
    packet_freeze.add_argument("--topic", required=True)
    packet_freeze.add_argument("--candidate", default="")
    packet_freeze.add_argument("--claim", action="append", default=[])
    packet_freeze.add_argument("--evidence-link", action="append", default=[])
    packet_freeze.add_argument("--query-run", action="append", default=[])
    packet_freeze.add_argument("--dataset", action="append", default=[])
    packet_invalidate = _leaf(
        packet_commands, "invalidate", "Explicitly invalidate an evidence packet"
    )
    packet_invalidate.add_argument("--packet", required=True)
    packet_invalidate.add_argument("--reason", required=True)

    index = commands.add_parser("index", help="Manage generated Markdown indexes")
    index_commands = index.add_subparsers(dest="index_command", required=True)
    _leaf(index_commands, "rebuild", "Rebuild generated index blocks")

    export = commands.add_parser("export", help="Generate views from canonical records")
    export_commands = export.add_subparsers(dest="export_command", required=True)
    export_bibtex = _leaf(export_commands, "bibtex", "Export deterministic BibTeX")
    export_bibtex.add_argument("--topic", default="")
    export_bibtex.add_argument("--out", required=True, type=Path)

    validate = _leaf(commands, "validate", "Validate schemas, references, hashes, and packets")
    validate.add_argument("--format", choices=("json", "text"), default="json")
    return parser


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def dispatch(args: argparse.Namespace) -> tuple[Any, int]:
    store = EvidenceStore(args.vault)
    if args.command == "init":
        return store.init(args.name or None), 0
    if args.command == "topic" and args.topic_command == "add":
        return store.add_topic(
            args.title, slug=args.slug, status=args.status, tags=args.tag
        ), 0
    if args.command == "work" and args.work_command == "ingest":
        work, source = store.ingest_work(
            args.title,
            authors=args.author,
            year=args.year,
            doi=args.doi,
            arxiv_id=args.arxiv_id,
            url=args.url,
            topic_ids=args.topic,
            source_file=args.source_file,
            copy_source=args.copy_source,
            source_kind=args.source_kind,
            source_scope=args.source_scope,
        )
        return {"work": work, "source_version": source}, 0
    if args.command == "work" and args.work_command == "update":
        return store.update_work(
            args.work,
            title=args.title,
            authors=args.author,
            year=args.year,
            doi=args.doi,
            arxiv_id=args.arxiv_id,
            url=args.url,
            topic_ids=args.topic,
        ), 0
    if args.command == "claim" and args.claim_command == "add":
        return store.add_claim(args.text, topic_ids=args.topic, status=args.status), 0
    if args.command == "claim" and args.claim_command == "link":
        return store.link_claim(
            args.claim,
            args.source,
            passage_id=args.passage,
            locator=args.locator,
            relation=args.relation,
            verdict=args.verdict,
            evidence_scope=args.scope,
            excerpt_hash=args.excerpt_hash,
            excerpt=args.excerpt,
            verifier=args.verifier,
            verified_at=args.verified_at,
        ), 0
    if args.command == "candidate" and args.candidate_command == "add":
        return store.add_candidate(
            args.topic,
            args.title,
            description=args.description,
            claim_ids=args.claim,
            primitives=args.primitive,
            objective=args.objective,
            data_regime=args.data_regime,
            assumptions=args.assumption,
            status=args.status,
        ), 0
    if args.command == "dataset" and args.dataset_command == "add":
        return store.add_dataset(
            args.title,
            args.uri,
            topic_ids=args.topic,
            content_hash=args.content_hash,
            version=args.dataset_version,
        ), 0
    if args.command == "query" and args.query_command == "add":
        try:
            filters = json.loads(args.filters_json)
        except json.JSONDecodeError as exc:
            raise EvidenceStoreError(f"invalid --filters-json: {exc}") from exc
        if not isinstance(filters, dict):
            raise EvidenceStoreError("--filters-json must decode to an object")
        try:
            observations = json.loads(args.observations_json)
        except json.JSONDecodeError as exc:
            raise EvidenceStoreError(f"invalid --observations-json: {exc}") from exc
        if not isinstance(observations, list) or not all(
            isinstance(item, dict) for item in observations
        ):
            raise EvidenceStoreError("--observations-json must decode to an array of objects")
        return store.add_query_run(
            args.topic,
            args.query,
            provider=args.provider,
            result_work_ids=args.result_work,
            filters=filters,
            executed_at=args.executed_at,
            raw_response_hash=args.raw_response_hash,
            observations=observations,
        ), 0
    if args.command == "reading" and args.reading_command == "add":
        return store.add_reading(
            args.work,
            topic_ids=args.topic,
            source_version_ids=args.source,
            summary=args.summary,
            status=args.status,
        ), 0
    if args.command == "passage" and args.passage_command == "add":
        return store.add_passage(
            args.source,
            locator=args.locator,
            paraphrase=args.paraphrase,
            topic_ids=args.topic,
            claim_ids=args.claim,
            excerpt_hash=args.excerpt_hash,
            excerpt=args.excerpt,
        ), 0
    if args.command == "method" and args.method_command == "add":
        relations: list[dict[str, str]] = []
        for raw in args.relation:
            if ":" not in raw:
                raise EvidenceStoreError(
                    f"invalid --relation {raw!r}; expected RELATION:TARGET_ID"
                )
            relation, target_id = raw.split(":", 1)
            relations.append({"relation": relation, "target_id": target_id})
        return store.add_method(
            args.name,
            description=args.description,
            topic_ids=args.topic,
            work_ids=args.work,
            relations=relations,
        ), 0
    if args.command == "audit" and args.audit_command == "add":
        artifact_hashes: dict[str, str] = {}
        for raw in args.artifact_hash:
            if "=" not in raw:
                raise EvidenceStoreError(
                    f"invalid --artifact-hash {raw!r}; expected LABEL=SHA256"
                )
            label, value = raw.split("=", 1)
            if not label.strip() or label.strip() in artifact_hashes:
                raise EvidenceStoreError(
                    f"artifact hash label must be non-empty and unique: {label!r}"
                )
            artifact_hashes[label.strip()] = value
        return store.add_audit_verdict(
            args.topic,
            candidate_id=args.candidate,
            evidence_packet_id=args.packet,
            verdict=args.verdict,
            rationale=args.rationale,
            auditor=args.auditor,
            audited_at=args.audited_at,
            subject_type=args.subject_type,
            subject_id=args.subject_id,
            subject_hash=args.subject_hash,
            artifact_hashes=artifact_hashes,
            protocol_hash=args.protocol_hash,
        ), 0
    if args.command == "packet" and args.packet_command == "freeze":
        return store.freeze_packet(
            args.topic,
            candidate_id=args.candidate,
            claim_ids=args.claim,
            evidence_link_ids=args.evidence_link,
            query_run_ids=args.query_run,
            dataset_ids=args.dataset,
        ), 0
    if args.command == "packet" and args.packet_command == "invalidate":
        return store.invalidate_packet(args.packet, reason=args.reason), 0
    if args.command == "index" and args.index_command == "rebuild":
        store.rebuild_indexes()
        return {"status": "rebuilt", "vault": str(store.vault)}, 0
    if args.command == "export" and args.export_command == "bibtex":
        return store.export_bibtex(args.out, topic_id=args.topic), 0
    if args.command == "validate":
        issues = store.validate()
        errors = [issue for issue in issues if issue.severity == "error"]
        result = {
            "valid": not errors,
            "error_count": len(errors),
            "warning_count": sum(issue.severity == "warning" for issue in issues),
            "issues": [issue.to_dict() for issue in issues],
        }
        if args.format == "text":
            if issues:
                for issue in issues:
                    location = f" [{issue.record_id or issue.path}]" if issue.record_id or issue.path else ""
                    print(f"{issue.severity.upper()} {issue.code}{location}: {issue.message}")
            else:
                print("VALID: no evidence-store integrity issues found")
            return None, 1 if errors else 0
        return result, 1 if errors else 0
    raise EvidenceStoreError("unsupported command")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result, exit_code = dispatch(args)
    except (EvidenceStoreError, OSError, ValueError) as exc:
        print(
            json.dumps(
                {"error": type(exc).__name__, "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    if result is not None:
        _emit(result)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
