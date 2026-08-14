"""Data-model and Markdown serialization helpers.

The on-disk frontmatter deliberately uses JSON values.  JSON scalars, arrays, and
objects are valid YAML, while remaining parseable with the Python standard
library.  This keeps the evidence store usable from both Claude Code and Codex
without adding a host or package-manager dependency.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
RECORD_TYPES = {
    "topic",
    "work",
    "source_version",
    "claim",
    "evidence_link",
    "candidate",
    "dataset",
    "evidence_packet",
    "query_run",
    "reading",
    "passage",
    "method",
    "audit_verdict",
}

RELATIONS = {
    "supports",
    "contradicts",
    "background",
    "mentions",
    "compares",
    "extends",
    "subsumes",
    "same_primitive_as",
    "relevant_to",
    "uses",
    "evaluates_on",
    "belongs_to",
}
VERDICTS = {"verified", "provisional", "cannot_determine", "disputed"}
EVIDENCE_SCOPES = {"metadata", "abstract", "full_text", "supplement", "dataset"}
AUDIT_VERDICTS = {"pass", "conditional", "fail", "cannot_determine"}
SOURCE_HASH_KINDS = {"discovery_fingerprint", "content_sha256"}

REQUIRED_FIELDS: dict[str, dict[str, type | tuple[type, ...]]] = {
    "topic": {"title": str, "slug": str, "status": str},
    "work": {"title": str, "authors": list, "topic_ids": list},
    "source_version": {
        "work_id": str,
        "source_kind": str,
        "source_scope": str,
        "content_hash": str,
        "hash_kind": str,
        "managed_copy": bool,
    },
    "claim": {"text": str, "topic_ids": list, "status": str},
    "evidence_link": {
        "claim_id": str,
        "source_version_id": str,
        "passage_id": str,
        "locator": str,
        "excerpt_hash": str,
        "relation": str,
        "verdict": str,
        "evidence_scope": str,
        "verified_at": str,
        "verifier": str,
    },
    "candidate": {
        "topic_id": str,
        "title": str,
        "claim_ids": list,
        "primitives": list,
        "objective": str,
        "data_regime": str,
        "assumptions": list,
        "component_hash": str,
        "objective_hash": str,
        "data_regime_hash": str,
        "status": str,
    },
    "dataset": {
        "title": str,
        "topic_ids": list,
        "uri": str,
        "content_hash": str,
        "hash_status": str,
    },
    "evidence_packet": {
        "topic_id": str,
        "claim_ids": list,
        "evidence_link_ids": list,
        "source_version_ids": list,
        "passage_ids": list,
        "dependency_hashes": dict,
        "snapshot_hash": str,
        "frozen_at": str,
        "status": str,
        "invalidated_by": list,
        "invalidation_reasons": list,
        "query_run_ids": list,
        "work_ids": list,
        "dataset_ids": list,
    },
    "query_run": {
        "topic_id": str,
        "query": str,
        "provider": str,
        "executed_at": str,
        "result_work_ids": list,
        "raw_response_hash": str,
        "observations": list,
    },
    "reading": {
        "work_id": str,
        "topic_ids": list,
        "source_version_ids": list,
        "summary": str,
        "status": str,
    },
    "passage": {
        "work_id": str,
        "source_version_id": str,
        "topic_ids": list,
        "claim_ids": list,
        "locator": str,
        "excerpt_hash": str,
        "paraphrase": str,
    },
    "method": {
        "name": str,
        "description": str,
        "topic_ids": list,
        "work_ids": list,
        "relations": list,
    },
    "audit_verdict": {
        "topic_id": str,
        "candidate_id": str,
        "evidence_packet_id": str,
        "verdict": str,
        "rationale": str,
        "audited_at": str,
        "auditor": str,
    },
}

COMMON_REQUIRED: dict[str, type | tuple[type, ...]] = {
    "record_type": str,
    "id": str,
    "schema_version": int,
    "created_at": str,
    "updated_at": str,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def slugify(value: str, fallback: str = "item") -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    if slug:
        return slug[:72].rstrip("-")
    return f"{fallback}-{digest(value)[:10]}"


def digest(value: Any) -> str:
    if isinstance(value, bytes):
        raw = value
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def semantic_hash(record: dict[str, Any]) -> str:
    ignored = {"created_at", "updated_at", "invalidated_by"}
    semantic = {key: value for key, value in record.items() if key not in ignored}
    return digest(semantic)


def make_record(record_type: str, record_id: str, **fields: Any) -> dict[str, Any]:
    if record_type not in RECORD_TYPES:
        raise ValueError(f"unknown record type: {record_type}")
    timestamp = now_utc()
    return {
        "record_type": record_type,
        "id": record_id,
        "schema_version": SCHEMA_VERSION,
        "created_at": timestamp,
        "updated_at": timestamp,
        **fields,
    }


def _frontmatter_value(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # Tolerate a manually entered bare YAML scalar.  Generated files always
        # use JSON values, so nested hand-written YAML intentionally remains out
        # of scope for the dependency-free parser.
        scalar = value.strip()
        lowered = scalar.casefold()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if lowered in {"null", "~"}:
            return None
        if re.fullmatch(r"-?\d+", scalar):
            return int(scalar)
        if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", scalar):
            return float(scalar)
        return scalar


def parse_markdown(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    frontmatter: dict[str, Any] = {}
    pending_list_key: str | None = None
    for number, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace():
            stripped = line.strip()
            if pending_list_key and stripped.startswith("- "):
                frontmatter[pending_list_key].append(
                    _frontmatter_value(stripped.removeprefix("- ").strip())
                )
                continue
            raise ValueError(
                f"unsupported multiline YAML on frontmatter line {number}; "
                "only indented '- item' lists are supported"
            )
        pending_list_key = None
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line {number}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"empty frontmatter key on line {number}")
        raw_value = value.strip()
        if raw_value == "":
            frontmatter[key] = []
            pending_list_key = key
        else:
            frontmatter[key] = _frontmatter_value(raw_value)
    return frontmatter, text[end + 5 :]


def default_body(record: dict[str, Any]) -> str:
    title = (
        record.get("title")
        or record.get("text")
        or record.get("query")
        or record["id"]
    )
    return (
        f"# {title}\n\n"
        "## Notes\n\n"
        "<!-- Add interpretation and topic-specific notes here. "
        "Keep provenance fields in frontmatter. -->\n"
    )


def render_markdown(record: dict[str, Any], body: str | None = None) -> str:
    preferred = [
        "record_type",
        "id",
        "schema_version",
        "created_at",
        "updated_at",
    ]
    keys = [key for key in preferred if key in record]
    keys.extend(sorted(key for key in record if key not in preferred))
    lines = ["---"]
    for key in keys:
        encoded = json.dumps(record[key], ensure_ascii=False, sort_keys=True)
        lines.append(f"{key}: {encoded}")
    lines.append("---")
    content = body if body is not None else default_body(record)
    return "\n".join(lines) + "\n" + content.lstrip("\n")


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip().lower()
    normalized = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", normalized)
    return normalized.removeprefix("doi:").strip()


def normalize_arxiv(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip().lower()
    normalized = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", normalized)
    normalized = normalized.removesuffix(".pdf")
    return re.sub(r"v\d+$", "", normalized)


def work_id(
    title: str,
    *,
    doi: str = "",
    arxiv_id: str = "",
    year: int | None = None,
    authors: list[str] | None = None,
) -> str:
    doi = normalize_doi(doi)
    arxiv_id = normalize_arxiv(arxiv_id)
    if doi:
        return f"work-doi-{digest(doi)[:14]}"
    if arxiv_id:
        return f"work-arxiv-{slugify(arxiv_id)}"
    identity = {
        "title": normalize_text(title),
        "year": year,
        "first_author": normalize_text((authors or [""])[0]),
    }
    return f"work-{digest(identity)[:14]}"


def base_record_errors(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    record_type = record.get("record_type")
    if record_type not in RECORD_TYPES:
        return [f"unknown record_type {record_type!r}"]
    for field, expected in {**COMMON_REQUIRED, **REQUIRED_FIELDS[record_type]}.items():
        if field not in record:
            errors.append(f"missing required field {field}")
        elif not isinstance(record[field], expected):
            errors.append(
                f"field {field} must be {getattr(expected, '__name__', expected)}, "
                f"got {type(record[field]).__name__}"
            )
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"unsupported schema_version {record.get('schema_version')!r}; "
            f"expected {SCHEMA_VERSION}"
        )
    return errors
