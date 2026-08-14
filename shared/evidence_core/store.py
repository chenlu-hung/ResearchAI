"""Filesystem implementation of the portable evidence store."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence

from .model import (
    AUDIT_VERDICTS,
    EVIDENCE_SCOPES,
    RELATIONS,
    SOURCE_HASH_KINDS,
    VERDICTS,
    base_record_errors,
    digest,
    hash_file,
    make_record,
    normalize_arxiv,
    normalize_doi,
    normalize_text,
    now_utc,
    parse_markdown,
    render_markdown,
    semantic_hash,
    slugify,
    work_id,
)


BEGIN_MARKER = "<!-- EVIDENCECTL:BEGIN -->"
END_MARKER = "<!-- EVIDENCECTL:END -->"
RESOURCE_ROOT = Path(__file__).resolve().parent / "resources"


class EvidenceStoreError(RuntimeError):
    """Raised when a store operation cannot preserve evidence integrity."""


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    record_id: str = ""
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _atomic_write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    binary = isinstance(content, bytes)
    mode = "wb" if binary else "w"
    kwargs: dict[str, Any] = {} if binary else {"encoding": "utf-8", "newline": "\n"}
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, mode, **kwargs) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _replace_generated(existing: str, generated: str) -> str:
    block = f"{BEGIN_MARKER}\n{generated.rstrip()}\n{END_MARKER}"
    begin_count = existing.count(BEGIN_MARKER)
    end_count = existing.count(END_MARKER)
    if begin_count == end_count == 0:
        return existing.rstrip() + "\n\n" + block + "\n"
    if begin_count != 1 or end_count != 1:
        raise EvidenceStoreError("index has malformed or duplicate EVIDENCECTL markers")
    start = existing.index(BEGIN_MARKER)
    end = existing.index(END_MARKER, start) + len(END_MARKER)
    return existing[:start] + block + existing[end:]


def _ordered_unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


class EvidenceStore:
    """Manage one evidence vault using Markdown as the source of truth."""

    CONFIG_VERSION = 1

    def __init__(self, vault: str | Path):
        self.vault = Path(vault).expanduser().resolve()
        self.meta = self.vault / ".evidence"
        self.config_path = self.meta / "config.json"
        self.lock_path = self.meta / "locks" / "write.lock"

    @contextmanager
    def lock(self, stale_after_seconds: int = 3600) -> Iterator[None]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"pid": os.getpid(), "created_at": now_utc()}) + "\n"
        try:
            fd = os.open(self.lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            try:
                age = time.time() - self.lock_path.stat().st_mtime
            except FileNotFoundError:
                age = 0
            if age > stale_after_seconds:
                raise EvidenceStoreError(
                    f"stale write lock at {self.lock_path}; inspect and remove it explicitly"
                ) from exc
            raise EvidenceStoreError(f"evidence store is locked: {self.lock_path}") from exc
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            yield
        finally:
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass

    def require_initialized(self) -> None:
        if not self.config_path.is_file():
            raise EvidenceStoreError(
                f"{self.vault} is not an evidence vault; run evidencectl init first"
            )

    def init(self, name: str | None = None) -> dict[str, Any]:
        self.vault.mkdir(parents=True, exist_ok=True)
        directories = [
            "10 Topics",
            "20 Library/Works",
            "20 Library/Claims",
            "20 Library/Evidence Links",
            "20 Library/Datasets",
            "20 Library/Query Runs",
            "20 Library/Methods",
            "30 Indexes",
            "90 Attachments/Papers",
            "90 Attachments/Supplements",
            "99 Templates",
            ".evidence/locks",
            ".evidence/schemas",
            ".evidence/snapshots",
            ".evidence/exports",
        ]
        for relative in directories:
            (self.vault / relative).mkdir(parents=True, exist_ok=True)
        with self.lock():
            if self.config_path.exists():
                config = json.loads(self.config_path.read_text(encoding="utf-8"))
            else:
                vault_name = name or self.vault.name
                config = {
                    "schema_version": self.CONFIG_VERSION,
                    "vault_id": f"vault-{digest(str(self.vault))[:12]}",
                    "name": vault_name,
                    "created_at": now_utc(),
                    "canonical_format": "markdown-json-frontmatter",
                    "derived_index": {
                        "policy": "outside-vault",
                        "note": "Do not place live SQLite, WAL, or embedding caches in this vault.",
                    },
                }
                _atomic_write(
                    self.config_path,
                    json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                )
            root = self.vault / "00 Research Index.md"
            if not root.exists():
                _atomic_write(
                    root,
                    "# Research Evidence Index\n\n"
                    "Use this area for durable, hand-written navigation and synthesis.\n\n",
                )
            self._seed_bundled_resources_locked()
            self._rebuild_indexes_locked()
        return config

    def _seed_bundled_resources_locked(self) -> None:
        """Install versioned schemas/templates without overwriting vault edits."""
        schema_dir = RESOURCE_ROOT / "schemas"
        schemas = sorted(schema_dir.glob("*.json"))
        if not schemas:
            raise EvidenceStoreError(f"bundled evidence resource is missing: {schema_dir}")
        for source in schemas:
            destination = self.meta / "schemas" / source.name
            if not destination.exists():
                _atomic_write(destination, source.read_bytes())

        manifest_path = RESOURCE_ROOT / "templates-v1.json"
        try:
            templates = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceStoreError(
                f"bundled evidence template manifest is invalid: {exc}"
            ) from exc
        if not isinstance(templates, dict) or not templates:
            raise EvidenceStoreError("bundled evidence template manifest must be an object")
        template_dir = self.vault / "99 Templates" / "v1"
        for filename, content in sorted(templates.items()):
            if (
                not isinstance(filename, str)
                or Path(filename).name != filename
                or not filename.endswith(".md")
                or not isinstance(content, str)
            ):
                raise EvidenceStoreError(f"invalid bundled template entry: {filename!r}")
            destination = template_dir / filename
            if not destination.exists():
                _atomic_write(destination, content)

    def _record_path(self, record: dict[str, Any]) -> Path:
        record_type = record["record_type"]
        record_id = record["id"]
        if record_type == "topic":
            return self.vault / "10 Topics" / record_id / "Topic.md"
        if record_type == "work":
            return self.vault / "20 Library" / "Works" / record_id / "Work.md"
        if record_type == "source_version":
            return (
                self.vault
                / "20 Library"
                / "Works"
                / record["work_id"]
                / "Sources"
                / f"{record_id}.md"
            )
        if record_type == "claim":
            return self.vault / "20 Library" / "Claims" / f"{record_id}.md"
        if record_type == "evidence_link":
            return self.vault / "20 Library" / "Evidence Links" / f"{record_id}.md"
        if record_type == "candidate":
            return (
                self.vault
                / "10 Topics"
                / record["topic_id"]
                / "Candidates"
                / f"{record_id}.md"
            )
        if record_type == "dataset":
            return self.vault / "20 Library" / "Datasets" / f"{record_id}.md"
        if record_type == "evidence_packet":
            return (
                self.vault
                / "10 Topics"
                / record["topic_id"]
                / "Evidence Packets"
                / f"{record_id}.md"
            )
        if record_type == "query_run":
            return self.vault / "20 Library" / "Query Runs" / f"{record_id}.md"
        if record_type == "reading":
            return (
                self.vault
                / "20 Library"
                / "Works"
                / record["work_id"]
                / "Readings"
                / f"{record_id}.md"
            )
        if record_type == "passage":
            return (
                self.vault
                / "20 Library"
                / "Works"
                / record["work_id"]
                / "Passages"
                / f"{record_id}.md"
            )
        if record_type == "method":
            return self.vault / "20 Library" / "Methods" / f"{record_id}.md"
        if record_type == "audit_verdict":
            return (
                self.vault
                / "10 Topics"
                / record["topic_id"]
                / "Audits"
                / f"{record_id}.md"
            )
        raise EvidenceStoreError(f"unsupported record type: {record_type}")

    def _is_record_container(self, path: Path) -> bool:
        try:
            relative = path.relative_to(self.vault)
        except ValueError:
            return False
        parts = relative.parts
        if len(parts) >= 3 and parts[0] == "10 Topics":
            return (
                path.name == "Topic.md"
                or "Candidates" in parts
                or "Evidence Packets" in parts
                or "Audits" in parts
            )
        if len(parts) >= 3 and parts[:2] == ("20 Library", "Works"):
            return (
                path.name == "Work.md"
                or "Sources" in parts
                or "Readings" in parts
                or "Passages" in parts
            )
        return len(parts) >= 3 and parts[:2] in {
            ("20 Library", "Claims"),
            ("20 Library", "Evidence Links"),
            ("20 Library", "Datasets"),
            ("20 Library", "Query Runs"),
            ("20 Library", "Methods"),
        }

    def _is_generated_record_name(self, path: Path) -> bool:
        """Recognize files emitted by this CLI without claiming human topic notes."""
        if path.name in {"Topic.md", "Work.md"}:
            return True
        prefixes = (
            "source-",
            "reading-",
            "passage-",
            "claim-",
            "evidence-",
            "candidate-",
            "dataset-",
            "query-",
            "method-",
            "packet-",
            "audit-",
        )
        return path.stem.casefold().startswith(prefixes)

    def _write_record_locked(
        self, record: dict[str, Any], *, body: str | None = None
    ) -> Path:
        path = self._record_path(record)
        if path.exists() and body is None:
            try:
                old_record, old_body = parse_markdown(path.read_text(encoding="utf-8"))
                record.setdefault("created_at", old_record.get("created_at", now_utc()))
                body = old_body
            except ValueError:
                body = None
        record["updated_at"] = now_utc()
        _atomic_write(path, render_markdown(record, body))
        return path

    def _scan(
        self,
    ) -> tuple[list[tuple[dict[str, Any], Path]], list[ValidationIssue]]:
        records: list[tuple[dict[str, Any], Path]] = []
        issues: list[ValidationIssue] = []
        if not self.vault.exists():
            return records, issues
        for path in sorted(self.vault.rglob("*.md")):
            if not self._is_record_container(path):
                continue
            try:
                raw = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                issues.append(
                    ValidationIssue(
                        "error", "invalid_frontmatter", str(exc), path=str(path)
                    )
                )
                continue
            # Human-maintained notes may coexist in Candidates, Evidence Packets,
            # and other record containers.  Only parse files explicitly marked as
            # records, except for CLI-generated filenames whose corruption should
            # remain visible to validation.
            frontmatter_end = raw.find("\n---\n", 4) if raw.startswith("---\n") else -1
            frontmatter = raw[4:frontmatter_end] if frontmatter_end >= 0 else ""
            has_record_marker = any(
                line.startswith("record_type:") for line in frontmatter.splitlines()
            )
            if not has_record_marker and not self._is_generated_record_name(path):
                continue
            try:
                record, _ = parse_markdown(raw)
            except ValueError as exc:
                issues.append(
                    ValidationIssue(
                        "error", "invalid_frontmatter", str(exc), path=str(path)
                    )
                )
                continue
            records.append((record, path))
        return records, issues

    def records(self) -> dict[str, dict[str, Any]]:
        self.require_initialized()
        scanned, _ = self._scan()
        result: dict[str, dict[str, Any]] = {}
        for record, _ in scanned:
            record_id = record.get("id")
            if isinstance(record_id, str):
                result[record_id] = record
        return result

    def get(self, record_id: str, expected_type: str | None = None) -> dict[str, Any]:
        record = self.records().get(record_id)
        if record is None:
            raise EvidenceStoreError(f"record not found: {record_id}")
        if expected_type and record.get("record_type") != expected_type:
            raise EvidenceStoreError(
                f"{record_id} is {record.get('record_type')}, expected {expected_type}"
            )
        return record

    def add_topic(
        self, title: str, *, slug: str = "", status: str = "active", tags: Sequence[str] = ()
    ) -> dict[str, Any]:
        self.require_initialized()
        topic_slug = slugify(slug or title, "topic")
        record_id = f"topic-{topic_slug}"
        existing = self.records().get(record_id)
        if existing:
            return existing
        record = make_record(
            "topic",
            record_id,
            title=title.strip(),
            slug=topic_slug,
            status=status,
            tags=sorted(set(tags)),
        )
        with self.lock():
            self._write_record_locked(record)
            topic_dir = self.vault / "10 Topics" / record_id
            for child in (
                "Papers",
                "Questions",
                "Candidates",
                "Evidence Packets",
                "Audits",
                "Decisions",
                "Data",
            ):
                (topic_dir / child).mkdir(parents=True, exist_ok=True)
            for note, heading in (
                ("Literature Map.md", "Literature Map"),
                ("Questions/Research Questions.md", "Research Questions"),
            ):
                path = topic_dir / note
                if not path.exists():
                    _atomic_write(path, f"# {heading}\n\n")
            self._rebuild_indexes_locked()
        return record

    def _find_existing_work(
        self,
        title: str,
        *,
        doi: str,
        arxiv_id: str,
        year: int | None,
    ) -> dict[str, Any] | None:
        normalized_title = normalize_text(title)
        for record in self.records().values():
            if record.get("record_type") != "work":
                continue
            if doi and normalize_doi(record.get("doi")) == doi:
                return record
            if arxiv_id and normalize_arxiv(record.get("arxiv_id")) == arxiv_id:
                return record
            if normalize_text(record.get("title", "")) == normalized_title:
                existing_year = record.get("year")
                if not year or not existing_year or abs(int(existing_year) - int(year)) <= 1:
                    return record
        return None

    def ingest_work(
        self,
        title: str,
        *,
        authors: Sequence[str] = (),
        year: int | None = None,
        doi: str = "",
        arxiv_id: str = "",
        url: str = "",
        topic_ids: Sequence[str] = (),
        source_file: str | Path | None = None,
        copy_source: bool = False,
        source_kind: str = "web",
        source_scope: str = "metadata",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        self.require_initialized()
        doi = normalize_doi(doi)
        arxiv_id = normalize_arxiv(arxiv_id)
        known = self.records()
        for topic_id in topic_ids:
            if known.get(topic_id, {}).get("record_type") != "topic":
                raise EvidenceStoreError(f"unknown topic: {topic_id}")
        existing = self._find_existing_work(
            title, doi=doi, arxiv_id=arxiv_id, year=year
        )
        previous_work_hash = semantic_hash(existing) if existing else ""
        if existing:
            work = dict(existing)
            work["topic_ids"] = sorted(set(work.get("topic_ids", [])) | set(topic_ids))
            for key, value in {
                "doi": doi,
                "arxiv_id": arxiv_id,
                "url": url,
                "year": year,
            }.items():
                if value and not work.get(key):
                    work[key] = value
            if authors and not work.get("authors"):
                work["authors"] = list(authors)
        else:
            record_id = work_id(
                title, doi=doi, arxiv_id=arxiv_id, year=year, authors=list(authors)
            )
            work = make_record(
                "work",
                record_id,
                title=title.strip(),
                authors=list(authors),
                year=year,
                doi=doi,
                arxiv_id=arxiv_id,
                url=url,
                topic_ids=sorted(set(topic_ids)),
                current_source_version_id="",
            )

        source_path = ""
        path_kind = ""
        managed_copy = False
        if source_file:
            input_path = Path(source_file).expanduser().resolve()
            if not input_path.is_file():
                raise EvidenceStoreError(f"source file not found: {input_path}")
            content_hash = hash_file(input_path)
            hash_kind = "content_sha256"
            source_kind = source_kind if source_kind != "web" else input_path.suffix.lstrip(".") or "file"
            if copy_source:
                suffix = input_path.suffix.lower()
                destination = (
                    self.vault
                    / "90 Attachments"
                    / "Papers"
                    / work["id"]
                    / f"{content_hash}{suffix}"
                )
                source_path = destination.relative_to(self.vault).as_posix()
                path_kind = "vault_relative"
                managed_copy = True
            else:
                try:
                    source_path = input_path.relative_to(self.vault).as_posix()
                    path_kind = "vault_relative"
                except ValueError:
                    source_path = str(input_path)
                    path_kind = "absolute"
                destination = None
        else:
            if source_scope not in {"metadata", "abstract"}:
                raise EvidenceStoreError(
                    "full_text, supplement, and dataset sources require --source-file; "
                    "a URL/metadata fingerprint is not a content hash"
                )
            effective_url = url or work.get("url", "")
            content_hash = digest(
                {
                    "work_id": work["id"],
                    "source_kind": source_kind,
                    "source_scope": source_scope,
                    "url": effective_url,
                }
            )
            hash_kind = "discovery_fingerprint"
            destination = None

        source_id = f"source-{work['id'].removeprefix('work-')}-{content_hash[:14]}"
        source = make_record(
            "source_version",
            source_id,
            work_id=work["id"],
            source_kind=source_kind,
            source_scope=source_scope,
            source_path=source_path,
            path_kind=path_kind,
            source_url=url or work.get("url", ""),
            content_hash=content_hash,
            hash_kind=hash_kind,
            managed_copy=managed_copy,
            ingested_at=now_utc(),
        )
        existing_source = known.get(source_id)
        if existing_source:
            source = existing_source
        work["current_source_version_id"] = source_id
        with self.lock():
            if destination is not None and not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                fd, temp_name = tempfile.mkstemp(prefix=".source.", dir=destination.parent)
                os.close(fd)
                try:
                    shutil.copyfile(input_path, temp_name)
                    if hash_file(Path(temp_name)) != content_hash:
                        raise EvidenceStoreError("source changed while it was being copied")
                    os.replace(temp_name, destination)
                finally:
                    try:
                        os.unlink(temp_name)
                    except FileNotFoundError:
                        pass
            self._write_record_locked(work)
            if not existing_source:
                self._write_record_locked(source)
            if previous_work_hash and previous_work_hash != semantic_hash(work):
                self._invalidate_packets_locked([work["id"]])
            self._rebuild_indexes_locked()
        return work, source

    def update_work(
        self,
        work_id_value: str,
        *,
        title: str | None = None,
        authors: Sequence[str] | None = None,
        year: int | None = None,
        doi: str | None = None,
        arxiv_id: str | None = None,
        url: str | None = None,
        topic_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Correct canonical work metadata without changing its stable ID."""
        self.require_initialized()
        records = self.records()
        existing = records.get(work_id_value)
        if not existing or existing.get("record_type") != "work":
            raise EvidenceStoreError(f"record not found: {work_id_value}")
        if all(
            value is None
            for value in (title, authors, year, doi, arxiv_id, url, topic_ids)
        ):
            raise EvidenceStoreError("work update requires at least one metadata field")
        if title is not None and not title.strip():
            raise EvidenceStoreError("work title cannot be empty")
        if topic_ids is not None:
            for topic_id in topic_ids:
                if records.get(topic_id, {}).get("record_type") != "topic":
                    raise EvidenceStoreError(f"unknown topic: {topic_id}")

        normalized_doi = normalize_doi(doi) if doi is not None else None
        normalized_arxiv = normalize_arxiv(arxiv_id) if arxiv_id is not None else None
        for other_id, other in records.items():
            if other_id == work_id_value or other.get("record_type") != "work":
                continue
            if normalized_doi and normalize_doi(other.get("doi")) == normalized_doi:
                raise EvidenceStoreError(f"DOI already belongs to {other_id}")
            if normalized_arxiv and normalize_arxiv(other.get("arxiv_id")) == normalized_arxiv:
                raise EvidenceStoreError(f"arXiv ID already belongs to {other_id}")

        work = dict(existing)
        updates: dict[str, Any] = {}
        if title is not None:
            updates["title"] = title.strip()
        if authors is not None:
            updates["authors"] = [author.strip() for author in authors if author.strip()]
        if year is not None:
            updates["year"] = year
        if doi is not None:
            updates["doi"] = normalized_doi
        if arxiv_id is not None:
            updates["arxiv_id"] = normalized_arxiv
        if url is not None:
            updates["url"] = url.strip()
        if topic_ids is not None:
            updates["topic_ids"] = sorted(set(topic_ids))
        work.update(updates)
        if semantic_hash(work) == semantic_hash(existing):
            return existing
        with self.lock():
            self._write_record_locked(work)
            self._invalidate_packets_locked(
                [work_id_value], reason="canonical work metadata changed"
            )
            self._rebuild_indexes_locked()
        return work

    def add_claim(
        self, text: str, *, topic_ids: Sequence[str], status: str = "open"
    ) -> dict[str, Any]:
        self.require_initialized()
        records = self.records()
        for topic_id in topic_ids:
            if records.get(topic_id, {}).get("record_type") != "topic":
                raise EvidenceStoreError(f"unknown topic: {topic_id}")
        record_id = f"claim-{digest(normalize_text(text))[:14]}"
        existing = records.get(record_id)
        if existing:
            merged = dict(existing)
            merged["topic_ids"] = sorted(set(existing.get("topic_ids", [])) | set(topic_ids))
            merged["status"] = status
            if merged == existing:
                return existing
            with self.lock():
                self._write_record_locked(merged)
                self._invalidate_packets_locked([record_id])
            return merged
        claim = make_record(
            "claim",
            record_id,
            text=text.strip(),
            topic_ids=sorted(set(topic_ids)),
            status=status,
        )
        with self.lock():
            self._write_record_locked(claim)
            self._rebuild_indexes_locked()
        return claim

    def link_claim(
        self,
        claim_id: str,
        source_version_id: str,
        *,
        locator: str,
        relation: str,
        verdict: str,
        evidence_scope: str,
        passage_id: str = "",
        excerpt_hash: str = "",
        excerpt: str = "",
        verifier: str,
        verified_at: str = "",
    ) -> dict[str, Any]:
        self.require_initialized()
        self.get(claim_id, "claim")
        source = self.get(source_version_id, "source_version")
        if relation not in RELATIONS:
            raise EvidenceStoreError(f"invalid relation: {relation}")
        if verdict not in VERDICTS:
            raise EvidenceStoreError(f"invalid verdict: {verdict}")
        if evidence_scope not in EVIDENCE_SCOPES:
            raise EvidenceStoreError(f"invalid evidence scope: {evidence_scope}")
        if evidence_scope == "abstract" and (
            verdict == "verified" or relation in {"supports", "contradicts"}
        ):
            raise EvidenceStoreError(
                "abstract-only evidence cannot verify, support, or contradict a claim"
            )
        if source.get("source_scope") == "abstract" and (
            verdict == "verified" or relation in {"supports", "contradicts"}
        ):
            raise EvidenceStoreError(
                "an abstract-only source cannot verify, support, or contradict a claim"
            )
        normalized_locator = locator.strip()
        excerpt_hash = excerpt_hash.strip().lower() or (digest(excerpt) if excerpt else "")
        passage: dict[str, Any] | None = None
        if passage_id:
            passage = self.get(passage_id, "passage")
            if not excerpt_hash:
                excerpt_hash = passage.get("excerpt_hash", "")
        requires_passage = (
            evidence_scope == "full_text"
            and verdict == "verified"
            and relation in {"supports", "contradicts"}
        )
        if requires_passage and passage is None:
            raise EvidenceStoreError(
                "verified full-text support/contradiction requires --passage"
            )
        if passage is not None and (
            passage.get("source_version_id") != source_version_id
            or passage.get("locator") != normalized_locator
            or passage.get("excerpt_hash", "") != excerpt_hash
        ):
            raise EvidenceStoreError(
                "passage must match the evidence source, locator, and excerpt hash"
            )
        if verdict == "verified" and (not normalized_locator or not excerpt_hash):
            raise EvidenceStoreError(
                "verified evidence requires a stable locator and excerpt hash"
            )
        identity = {
            "claim_id": claim_id,
            "source_version_id": source_version_id,
            "passage_id": passage_id,
            "locator": normalized_locator,
            "excerpt_hash": excerpt_hash,
            "relation": relation,
            "verdict": verdict,
            "evidence_scope": evidence_scope,
        }
        record_id = f"evidence-{digest(identity)[:16]}"
        existing = self.records().get(record_id)
        if existing:
            return existing
        link = make_record(
            "evidence_link",
            record_id,
            **identity,
            verified_at=verified_at or now_utc(),
            verifier=verifier.strip(),
        )
        with self.lock():
            self._write_record_locked(link)
            self._invalidate_claim_packets_locked(
                claim_id,
                changed_id=record_id,
                reason="new evidence link added for a selected claim",
            )
            self._rebuild_indexes_locked()
        return link

    def add_candidate(
        self,
        topic_id: str,
        title: str,
        *,
        description: str = "",
        claim_ids: Sequence[str] = (),
        primitives: Sequence[str] = (),
        objective: str,
        data_regime: str,
        assumptions: Sequence[str] = (),
        status: str = "proposed",
    ) -> dict[str, Any]:
        self.require_initialized()
        self.get(topic_id, "topic")
        if not [item for item in primitives if item.strip()]:
            raise EvidenceStoreError("candidate requires at least one primitive")
        if not objective.strip():
            raise EvidenceStoreError("candidate requires an objective")
        if not data_regime.strip():
            raise EvidenceStoreError("candidate requires a data regime")
        for claim_id in claim_ids:
            self.get(claim_id, "claim")
        record_id = f"candidate-{slugify(title, 'candidate')}-{digest(topic_id)[:6]}"
        component_hash = digest(
            {
                "description": normalize_text(description),
                "claim_ids": sorted(set(claim_ids)),
                "primitives": sorted(normalize_text(item) for item in primitives),
                "assumptions": sorted(normalize_text(item) for item in assumptions),
            }
        )
        objective_hash = digest(normalize_text(objective))
        data_regime_hash = digest(normalize_text(data_regime))
        records = self.records()
        existing = records.get(record_id)
        candidate = dict(existing) if existing else make_record("candidate", record_id)
        previous_hashes = (
            candidate.get("component_hash"),
            candidate.get("objective_hash"),
            candidate.get("data_regime_hash"),
        )
        candidate.update(
            topic_id=topic_id,
            title=title.strip(),
            description=description.strip(),
            claim_ids=sorted(set(claim_ids)),
            primitives=_ordered_unique([item.strip() for item in primitives if item.strip()]),
            objective=objective.strip(),
            data_regime=data_regime.strip(),
            assumptions=_ordered_unique([item.strip() for item in assumptions if item.strip()]),
            component_hash=component_hash,
            objective_hash=objective_hash,
            data_regime_hash=data_regime_hash,
            status=status,
        )
        if existing and semantic_hash(candidate) == semantic_hash(existing):
            return existing
        with self.lock():
            self._write_record_locked(candidate)
            current_hashes = (component_hash, objective_hash, data_regime_hash)
            if any(previous_hashes) and previous_hashes != current_hashes:
                self._invalidate_packets_locked([record_id])
            self._rebuild_indexes_locked()
        return candidate

    def add_dataset(
        self,
        title: str,
        uri: str,
        *,
        topic_ids: Sequence[str] = (),
        content_hash: str = "",
        version: str = "",
    ) -> dict[str, Any]:
        self.require_initialized()
        for topic_id in topic_ids:
            self.get(topic_id, "topic")
        supplied_hash = content_hash.strip().lower()
        record_id = f"dataset-{digest({'title': normalize_text(title), 'uri': uri})[:14]}"
        existing = self.records().get(record_id)
        dataset = dict(existing) if existing else make_record("dataset", record_id)
        dataset.update(
            title=title.strip(),
            topic_ids=sorted(set(dataset.get("topic_ids", [])) | set(topic_ids)),
            uri=uri,
            content_hash=supplied_hash or dataset.get("content_hash", ""),
            hash_status=(
                "verified"
                if supplied_hash or dataset.get("content_hash")
                else "unknown"
            ),
            version=version or dataset.get("version", ""),
        )
        if existing and semantic_hash(dataset) == semantic_hash(existing):
            return existing
        with self.lock():
            self._write_record_locked(dataset)
            if existing:
                self._invalidate_packets_locked([record_id])
            self._rebuild_indexes_locked()
        return dataset

    def add_query_run(
        self,
        topic_id: str,
        query: str,
        *,
        provider: str,
        result_work_ids: Sequence[str] = (),
        filters: dict[str, Any] | None = None,
        executed_at: str = "",
        raw_response_hash: str = "",
        observations: Sequence[dict[str, Any]] = (),
    ) -> dict[str, Any]:
        self.require_initialized()
        self.get(topic_id, "topic")
        for result in result_work_ids:
            self.get(result, "work")
        timestamp = executed_at or now_utc()
        ordered_results = _ordered_unique(result_work_ids)
        normalized_observations = list(observations)
        normalized_filters = filters or {}
        identity = {
            "topic_id": topic_id,
            "query": query,
            "provider": provider,
            "executed_at": timestamp,
            "result_work_ids": ordered_results,
            "raw_response_hash": raw_response_hash.strip().lower(),
            "observations": normalized_observations,
            "filters": normalized_filters,
        }
        record_id = f"query-{digest(identity)[:16]}"
        query_run = make_record(
            "query_run",
            record_id,
            **identity,
        )
        existing = self.records().get(record_id)
        if existing:
            return existing
        with self.lock():
            self._write_record_locked(query_run)
            self._invalidate_topic_packets_locked(
                topic_id,
                changed_id=record_id,
                reason="new literature query run added for this topic",
            )
            self._rebuild_indexes_locked()
        return query_run

    def add_reading(
        self,
        work_id_value: str,
        *,
        topic_ids: Sequence[str] = (),
        source_version_ids: Sequence[str] = (),
        summary: str = "",
        status: str = "in_progress",
    ) -> dict[str, Any]:
        """Create or update the reusable reading memory for one work."""
        self.require_initialized()
        work = self.get(work_id_value, "work")
        del work
        for topic_id in topic_ids:
            self.get(topic_id, "topic")
        if not source_version_ids:
            current = self.get(work_id_value, "work").get("current_source_version_id")
            source_version_ids = [current] if current else []
        for source_id in source_version_ids:
            source = self.get(source_id, "source_version")
            if source.get("work_id") != work_id_value:
                raise EvidenceStoreError(f"source {source_id} belongs to a different work")
        record_id = f"reading-{work_id_value.removeprefix('work-')}"
        existing = self.records().get(record_id)
        reading = dict(existing) if existing else make_record("reading", record_id)
        reading.update(
            work_id=work_id_value,
            topic_ids=sorted(set(reading.get("topic_ids", [])) | set(topic_ids)),
            source_version_ids=sorted(
                set(reading.get("source_version_ids", [])) | set(source_version_ids)
            ),
            summary=summary.strip() or reading.get("summary", ""),
            status=status,
        )
        with self.lock():
            self._write_record_locked(reading)
            self._rebuild_indexes_locked()
        return reading

    def add_passage(
        self,
        source_version_id: str,
        *,
        locator: str,
        paraphrase: str,
        topic_ids: Sequence[str] = (),
        excerpt_hash: str = "",
        excerpt: str = "",
        claim_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Persist a reusable source location without retaining copyrighted text."""
        self.require_initialized()
        source = self.get(source_version_id, "source_version")
        for topic_id in topic_ids:
            self.get(topic_id, "topic")
        for claim_id in claim_ids:
            self.get(claim_id, "claim")
        excerpt_hash = excerpt_hash.strip().lower() or (digest(excerpt) if excerpt else "")
        identity = {
            "source_version_id": source_version_id,
            "locator": locator.strip(),
            "excerpt_hash": excerpt_hash,
        }
        record_id = f"passage-{digest(identity)[:16]}"
        existing = self.records().get(record_id)
        if existing:
            return existing
        passage = make_record(
            "passage",
            record_id,
            work_id=source["work_id"],
            source_version_id=source_version_id,
            topic_ids=sorted(set(topic_ids)),
            locator=locator.strip(),
            excerpt_hash=excerpt_hash,
            paraphrase=paraphrase.strip(),
            claim_ids=sorted(set(claim_ids)),
        )
        with self.lock():
            self._write_record_locked(passage)
            self._rebuild_indexes_locked()
        return passage

    def add_method(
        self,
        name: str,
        *,
        description: str,
        topic_ids: Sequence[str] = (),
        work_ids: Sequence[str] = (),
        relations: Sequence[dict[str, str]] = (),
    ) -> dict[str, Any]:
        self.require_initialized()
        for topic_id in topic_ids:
            self.get(topic_id, "topic")
        for linked_work in work_ids:
            self.get(linked_work, "work")
        normalized_relations: list[dict[str, str]] = []
        for relation in relations:
            relation_name = relation.get("relation", "")
            target_id = relation.get("target_id", "")
            if relation_name not in RELATIONS:
                raise EvidenceStoreError(f"invalid method relation: {relation_name}")
            if not target_id or target_id not in self.records():
                raise EvidenceStoreError(f"unknown method relation target: {target_id}")
            normalized_relations.append(
                {"relation": relation_name, "target_id": target_id}
            )
        record_id = f"method-{slugify(name, 'method')}"
        existing = self.records().get(record_id)
        method = dict(existing) if existing else make_record("method", record_id)
        method.update(
            name=name.strip(),
            title=name.strip(),
            description=description.strip(),
            topic_ids=sorted(set(topic_ids)),
            work_ids=sorted(set(work_ids)),
            relations=sorted(
                normalized_relations,
                key=lambda item: (item["relation"], item["target_id"]),
            ),
        )
        with self.lock():
            self._write_record_locked(method)
            self._rebuild_indexes_locked()
        return method

    def add_audit_verdict(
        self,
        topic_id: str,
        *,
        candidate_id: str = "",
        evidence_packet_id: str,
        verdict: str,
        rationale: str,
        auditor: str,
        audited_at: str = "",
        subject_type: str = "",
        subject_id: str = "",
        subject_hash: str = "",
        artifact_hashes: dict[str, str] | None = None,
        protocol_hash: str = "",
    ) -> dict[str, Any]:
        self.require_initialized()
        self.get(topic_id, "topic")
        if candidate_id:
            candidate = self.get(candidate_id, "candidate")
            if candidate.get("topic_id") != topic_id:
                raise EvidenceStoreError("candidate belongs to a different topic")
        packet = self.get(evidence_packet_id, "evidence_packet")
        if packet.get("topic_id") != topic_id:
            raise EvidenceStoreError("evidence packet belongs to a different topic")
        if packet.get("status") != "frozen":
            raise EvidenceStoreError("audit verdict requires a currently frozen evidence packet")
        if verdict not in AUDIT_VERDICTS:
            raise EvidenceStoreError(f"invalid audit verdict: {verdict}")
        subject_type = subject_type.strip()
        subject_id = subject_id.strip()
        if bool(subject_type) != bool(subject_id):
            raise EvidenceStoreError("subject_type and subject_id must be supplied together")
        subject_hash = subject_hash.strip().lower()
        protocol_hash = protocol_hash.strip().lower()
        normalized_artifacts = {
            str(key).strip(): str(value).strip().lower()
            for key, value in (artifact_hashes or {}).items()
        }
        for label, value in {
            "subject_hash": subject_hash,
            "protocol_hash": protocol_hash,
            **{f"artifact_hashes[{key!r}]": value for key, value in normalized_artifacts.items()},
        }.items():
            if value and not _is_sha256(value):
                raise EvidenceStoreError(f"{label} must be a bare lowercase SHA-256 hash")
        if any(not key for key in normalized_artifacts):
            raise EvidenceStoreError("artifact hash labels cannot be empty")
        timestamp = audited_at or now_utc()
        identity = {
            "topic_id": topic_id,
            "candidate_id": candidate_id,
            "evidence_packet_id": evidence_packet_id,
            "verdict": verdict,
            "rationale": rationale.strip(),
            "audited_at": timestamp,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "subject_hash": subject_hash,
            "artifact_hashes": dict(sorted(normalized_artifacts.items())),
            "protocol_hash": protocol_hash,
        }
        record_id = f"audit-{digest(identity)[:16]}"
        audit = make_record(
            "audit_verdict",
            record_id,
            **identity,
            auditor=auditor.strip(),
        )
        with self.lock():
            self._write_record_locked(audit)
            self._rebuild_indexes_locked()
        return audit

    def _selected_packet_records(
        self,
        topic_id: str,
        candidate_id: str,
        claim_ids: Sequence[str],
        evidence_link_ids: Sequence[str],
        query_run_ids: Sequence[str],
        dataset_ids: Sequence[str],
    ) -> tuple[
        list[str],
        list[str],
        list[str],
        list[str],
        list[str],
        list[str],
        list[str],
        dict[str, dict[str, Any]],
    ]:
        records = self.records()
        if records.get(topic_id, {}).get("record_type") != "topic":
            raise EvidenceStoreError(f"unknown topic: {topic_id}")
        candidate: dict[str, Any] | None = None
        if candidate_id:
            candidate = records.get(candidate_id)
            if not candidate or candidate.get("record_type") != "candidate":
                raise EvidenceStoreError(f"unknown candidate: {candidate_id}")
            if candidate.get("topic_id") != topic_id:
                raise EvidenceStoreError("candidate belongs to a different topic")
        selected_claims = set(claim_ids)
        if candidate:
            selected_claims.update(candidate.get("claim_ids", []))
        if not selected_claims:
            raise EvidenceStoreError("an evidence packet requires at least one claim")
        for claim_id in selected_claims:
            if records.get(claim_id, {}).get("record_type") != "claim":
                raise EvidenceStoreError(f"unknown claim: {claim_id}")

        selected_links = set(evidence_link_ids)
        if not selected_links:
            selected_links.update(
                record_id
                for record_id, record in records.items()
                if record.get("record_type") == "evidence_link"
                and record.get("claim_id") in selected_claims
            )
        if not selected_links:
            raise EvidenceStoreError("an evidence packet requires at least one evidence link")
        source_ids: set[str] = set()
        passage_ids: set[str] = set()
        for link_id in selected_links:
            link = records.get(link_id)
            if not link or link.get("record_type") != "evidence_link":
                raise EvidenceStoreError(f"unknown evidence link: {link_id}")
            if link.get("claim_id") not in selected_claims:
                raise EvidenceStoreError(
                    f"evidence link {link_id} does not belong to a selected claim"
                )
            source_ids.add(link["source_version_id"])
            passage_id = link.get("passage_id", "")
            if passage_id:
                passage = records.get(passage_id)
                if not passage or passage.get("record_type") != "passage":
                    raise EvidenceStoreError(f"unknown passage: {passage_id}")
                passage_ids.add(passage_id)
        selected_queries = _ordered_unique(query_run_ids)
        if not selected_queries:
            selected_queries = sorted(
                record_id
                for record_id, record in records.items()
                if record.get("record_type") == "query_run"
                and record.get("topic_id") == topic_id
            )
        if not selected_queries:
            raise EvidenceStoreError(
                "an evidence packet requires at least one query run, including no-result searches"
            )
        work_ids: set[str] = set()
        for source_id in source_ids:
            source = records.get(source_id)
            if source:
                work_ids.add(source["work_id"])
        for query_id in selected_queries:
            query = records.get(query_id)
            if not query or query.get("record_type") != "query_run":
                raise EvidenceStoreError(f"unknown query run: {query_id}")
            if query.get("topic_id") != topic_id:
                raise EvidenceStoreError(f"query run {query_id} belongs to a different topic")
            work_ids.update(query.get("result_work_ids", []))
        selected_datasets = _ordered_unique(dataset_ids)
        for dataset_id in selected_datasets:
            dataset = records.get(dataset_id)
            if not dataset or dataset.get("record_type") != "dataset":
                raise EvidenceStoreError(f"unknown dataset: {dataset_id}")
            if topic_id not in dataset.get("topic_ids", []):
                raise EvidenceStoreError(f"dataset {dataset_id} belongs to a different topic")
        return (
            sorted(selected_claims),
            sorted(selected_links),
            sorted(source_ids),
            sorted(passage_ids),
            selected_queries,
            sorted(work_ids),
            selected_datasets,
            records,
        )

    def freeze_packet(
        self,
        topic_id: str,
        *,
        candidate_id: str = "",
        claim_ids: Sequence[str] = (),
        evidence_link_ids: Sequence[str] = (),
        query_run_ids: Sequence[str] = (),
        dataset_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        self.require_initialized()
        (
            claims,
            links,
            sources,
            passages,
            queries,
            works,
            datasets,
            records,
        ) = self._selected_packet_records(
            topic_id,
            candidate_id,
            claim_ids,
            evidence_link_ids,
            query_run_ids,
            dataset_ids,
        )
        selected_ids = (
            claims
            + links
            + sources
            + passages
            + queries
            + works
            + datasets
            + ([candidate_id] if candidate_id else [])
        )
        dependency_hashes = {
            record_id: semantic_hash(records[record_id]) for record_id in sorted(selected_ids)
        }
        snapshot_hash = digest(dependency_hashes)
        topic_slug = topic_id.removeprefix("topic-")
        packet_id = f"packet-{topic_slug}-{snapshot_hash[:14]}"
        existing = records.get(packet_id)
        if existing:
            return existing
        packet = make_record(
            "evidence_packet",
            packet_id,
            topic_id=topic_id,
            candidate_id=candidate_id,
            claim_ids=claims,
            evidence_link_ids=links,
            source_version_ids=sources,
            passage_ids=passages,
            query_run_ids=queries,
            work_ids=works,
            dataset_ids=datasets,
            dependency_hashes=dependency_hashes,
            snapshot_hash=snapshot_hash,
            frozen_at=now_utc(),
            status="frozen",
            invalidated_by=[],
            invalidation_reasons=[],
        )
        # Refuse to freeze a packet containing a known-invalid evidence link.
        selected_issues = self.validate(records_override=records)
        blocking_ids = (
            set(links)
            | set(sources)
            | set(passages)
            | set(claims)
            | set(queries)
            | set(works)
            | set(datasets)
            | ({candidate_id} if candidate_id else set())
        )
        blockers = [
            issue
            for issue in selected_issues
            if issue.severity == "error" and issue.record_id in blocking_ids
        ]
        if blockers:
            raise EvidenceStoreError(
                "cannot freeze invalid evidence: "
                + "; ".join(f"{issue.code}: {issue.message}" for issue in blockers)
            )
        with self.lock():
            snapshot_path = self.meta / "snapshots" / f"{packet_id}.json"
            if snapshot_path.exists():
                raise EvidenceStoreError(
                    f"immutable packet snapshot already exists: {snapshot_path}"
                )
            self._write_record_locked(packet)
            portable_records = {
                record_id: records[record_id] for record_id in sorted(selected_ids)
            }
            snapshot = {"packet": packet, "records": portable_records}
            _atomic_write(
                snapshot_path,
                json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            )
            self._rebuild_indexes_locked()
        return packet

    def _mark_packet_invalidated_locked(
        self,
        packet: dict[str, Any],
        *,
        changed_ids: Sequence[str] = (),
        reason: str,
    ) -> dict[str, Any]:
        packet = dict(packet)
        packet["status"] = "invalidated"
        packet["invalidated_by"] = sorted(
            set(packet.get("invalidated_by", [])) | set(changed_ids)
        )
        packet["invalidation_reasons"] = _ordered_unique(
            [*packet.get("invalidation_reasons", []), reason]
        )
        self._write_record_locked(packet)
        return packet

    def _invalidate_packets_locked(
        self, changed_ids: Sequence[str], *, reason: str = "packet dependency changed"
    ) -> None:
        changed = set(changed_ids)
        scanned, _ = self._scan()
        for packet, _ in scanned:
            if packet.get("record_type") != "evidence_packet":
                continue
            affected = changed & set(packet.get("dependency_hashes", {}))
            if not affected:
                continue
            self._mark_packet_invalidated_locked(
                packet,
                changed_ids=sorted(affected),
                reason=reason,
            )

    def _invalidate_claim_packets_locked(
        self, claim_id: str, *, changed_id: str, reason: str
    ) -> None:
        scanned, _ = self._scan()
        for packet, _ in scanned:
            if (
                packet.get("record_type") == "evidence_packet"
                and claim_id in packet.get("claim_ids", [])
            ):
                self._mark_packet_invalidated_locked(
                    packet, changed_ids=[changed_id], reason=reason
                )

    def _invalidate_topic_packets_locked(
        self, topic_id: str, *, changed_id: str, reason: str
    ) -> None:
        scanned, _ = self._scan()
        for packet, _ in scanned:
            if (
                packet.get("record_type") == "evidence_packet"
                and packet.get("topic_id") == topic_id
            ):
                self._mark_packet_invalidated_locked(
                    packet, changed_ids=[changed_id], reason=reason
                )

    def invalidate_packet(self, packet_id: str, *, reason: str) -> dict[str, Any]:
        """Explicitly invalidate a packet while preserving its immutable snapshot."""
        self.require_initialized()
        reason = reason.strip()
        if not reason:
            raise EvidenceStoreError("packet invalidation requires a reason")
        packet = self.get(packet_id, "evidence_packet")
        with self.lock():
            updated = self._mark_packet_invalidated_locked(packet, reason=reason)
            self._rebuild_indexes_locked()
        return updated

    def _relative_link(self, record: dict[str, Any]) -> str:
        path = self._record_path(record).relative_to(self.vault).with_suffix("")
        return f"[[{path.as_posix()}|{record.get('title') or record.get('text') or record['id']}]]"

    def _render_table(
        self, records: Sequence[dict[str, Any]], columns: Sequence[tuple[str, str]]
    ) -> str:
        header = "| " + " | ".join(label for label, _ in columns) + " |"
        divider = "| " + " | ".join("---" for _ in columns) + " |"
        rows = [header, divider]
        for record in records:
            cells: list[str] = []
            for _, field in columns:
                if field == "_link":
                    value: Any = self._relative_link(record)
                else:
                    value = record.get(field, "")
                if isinstance(value, list):
                    value = ", ".join(str(item) for item in value)
                cells.append(str(value).replace("|", "\\|").replace("\n", " "))
            rows.append("| " + " | ".join(cells) + " |")
        if not records:
            rows.append("| _None yet_ | " + " | ".join("" for _ in columns[1:]) + " |")
        return "\n".join(rows)

    def _write_generated_index_locked(
        self, path: Path, heading: str, generated: str
    ) -> None:
        if path.exists():
            existing = path.read_text(encoding="utf-8")
        else:
            existing = f"# {heading}\n\nAdd durable notes outside the generated block.\n\n"
        _atomic_write(path, _replace_generated(existing, generated))

    def _rebuild_indexes_locked(self) -> None:
        scanned, _ = self._scan()
        records = [record for record, _ in scanned if isinstance(record.get("id"), str)]
        by_type: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            by_type.setdefault(record.get("record_type", ""), []).append(record)
        for values in by_type.values():
            values.sort(key=lambda record: (str(record.get("title", "")).casefold(), record["id"]))

        specs = [
            ("Topics Index.md", "Topics Index", "topic", (("Topic", "_link"), ("Status", "status"))),
            ("Works Index.md", "Works Index", "work", (("Work", "_link"), ("Year", "year"), ("Topics", "topic_ids"))),
            ("Claims Index.md", "Claims Index", "claim", (("Claim", "_link"), ("Status", "status"), ("Topics", "topic_ids"))),
            ("Readings Index.md", "Readings Index", "reading", (("Reading", "_link"), ("Work", "work_id"), ("Status", "status"), ("Topics", "topic_ids"))),
            ("Passages Index.md", "Passages Index", "passage", (("Passage", "_link"), ("Work", "work_id"), ("Locator", "locator"), ("Topics", "topic_ids"))),
            ("Methods Index.md", "Methods Index", "method", (("Method", "_link"), ("Works", "work_ids"), ("Topics", "topic_ids"))),
            ("Datasets Index.md", "Datasets Index", "dataset", (("Dataset", "_link"), ("Version", "version"), ("Topics", "topic_ids"))),
            ("Evidence Packets Index.md", "Evidence Packets Index", "evidence_packet", (("Packet", "_link"), ("Status", "status"), ("Topic", "topic_id"))),
            ("Audit Verdicts Index.md", "Audit Verdicts Index", "audit_verdict", (("Audit", "_link"), ("Verdict", "verdict"), ("Topic", "topic_id"), ("Packet", "evidence_packet_id"))),
        ]
        for filename, heading, record_type, columns in specs:
            self._write_generated_index_locked(
                self.vault / "30 Indexes" / filename,
                heading,
                self._render_table(by_type.get(record_type, []), columns),
            )
        root_generated = (
            "## Topics\n\n"
            + self._render_table(by_type.get("topic", []), (("Topic", "_link"), ("Status", "status")))
            + "\n\n## Recent evidence packets\n\n"
            + self._render_table(
                by_type.get("evidence_packet", []),
                (("Packet", "_link"), ("Status", "status"), ("Topic", "topic_id")),
            )
            + "\n\n## Cross-topic indexes\n\n"
            + "- [[30 Indexes/Works Index]]\n"
            + "- [[30 Indexes/Claims Index]]\n"
            + "- [[30 Indexes/Readings Index]]\n"
            + "- [[30 Indexes/Passages Index]]\n"
            + "- [[30 Indexes/Methods Index]]\n"
            + "- [[30 Indexes/Datasets Index]]\n"
            + "- [[30 Indexes/Evidence Packets Index]]"
            + "\n- [[30 Indexes/Audit Verdicts Index]]"
        )
        self._write_generated_index_locked(
            self.vault / "00 Research Index.md", "Research Evidence Index", root_generated
        )

    def rebuild_indexes(self) -> None:
        self.require_initialized()
        with self.lock():
            self._rebuild_indexes_locked()

    def export_bibtex(self, out: str | Path, *, topic_id: str = "") -> dict[str, Any]:
        """Generate a deterministic BibTeX view from canonical work metadata."""
        self.require_initialized()
        if topic_id:
            self.get(topic_id, "topic")
        works = [
            record
            for record in self.records().values()
            if record.get("record_type") == "work"
            and (not topic_id or topic_id in record.get("topic_ids", []))
        ]
        works.sort(key=lambda record: record["id"])

        def base_key(work: dict[str, Any]) -> str:
            authors = work.get("authors", [])
            surname = (authors[0].split()[-1] if authors else "anon")
            author_part = slugify(surname, "anon").replace("-", "")
            year_part = str(work.get("year") or "nd")
            words = [
                word
                for word in slugify(work.get("title", "work"), "work").split("-")
                if word not in {"a", "an", "the", "of", "on", "for", "and", "in"}
            ]
            title_part = (words or ["work"])[0]
            return f"{author_part}{year_part}{title_part}"

        grouped: dict[str, list[dict[str, Any]]] = {}
        for work in works:
            grouped.setdefault(base_key(work), []).append(work)
        keys: dict[str, str] = {}
        for base, group in sorted(grouped.items()):
            for index, work in enumerate(sorted(group, key=lambda item: item["id"])):
                suffix = "" if len(group) == 1 else chr(ord("a") + index)
                keys[work["id"]] = base + suffix

        def bib_value(value: Any) -> str:
            text = str(value)
            return text.replace("\\", "\\textbackslash ").replace("{", "\\{").replace("}", "\\}")

        entries: list[str] = []
        for work in sorted(works, key=lambda item: keys[item["id"]]):
            fields: list[tuple[str, Any]] = [
                ("title", work.get("title", "")),
                ("author", " and ".join(work.get("authors", []))),
            ]
            if work.get("year"):
                fields.append(("year", work["year"]))
            if work.get("doi"):
                fields.append(("doi", work["doi"]))
            if work.get("arxiv_id"):
                fields.extend(
                    (("eprint", work["arxiv_id"]), ("archivePrefix", "arXiv"))
                )
            if work.get("url"):
                fields.append(("url", work["url"]))
            lines = [f"@article{{{keys[work['id']]},"]
            lines.extend(
                f"  {field} = {{{bib_value(value)}}}," for field, value in fields if value != ""
            )
            lines.append("}")
            entries.append("\n".join(lines))
        output = "\n\n".join(entries) + ("\n" if entries else "")
        out_path = Path(out).expanduser().resolve()
        _atomic_write(out_path, output)
        return {
            "status": "exported",
            "format": "bibtex",
            "topic_id": topic_id,
            "work_count": len(works),
            "out": str(out_path),
            "content_hash": digest(output),
            "bibkeys": {work_id: keys[work_id] for work_id in sorted(keys)},
        }

    def _resolve_source_path(self, source: dict[str, Any]) -> Path | None:
        value = source.get("source_path")
        if not value:
            return None
        if source.get("path_kind") == "vault_relative":
            return self.vault / value
        return Path(value).expanduser()

    def validate(
        self, *, records_override: dict[str, dict[str, Any]] | None = None
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if records_override is None:
            if not self.config_path.is_file():
                return [
                    ValidationIssue(
                        "error",
                        "not_initialized",
                        "missing .evidence/config.json",
                        path=str(self.config_path),
                    )
                ]
            try:
                config = json.loads(self.config_path.read_text(encoding="utf-8"))
                if config.get("schema_version") != self.CONFIG_VERSION:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_config",
                            f"unsupported config schema {config.get('schema_version')!r}",
                            path=str(self.config_path),
                        )
                    )
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(
                    ValidationIssue(
                        "error", "invalid_config", str(exc), path=str(self.config_path)
                    )
                )
            scanned, scan_issues = self._scan()
            issues.extend(scan_issues)
            records: dict[str, dict[str, Any]] = {}
            paths: dict[str, Path] = {}
            for record, path in scanned:
                record_id = record.get("id")
                if not isinstance(record_id, str):
                    issues.append(
                        ValidationIssue(
                            "error", "invalid_id", "record id must be a string", path=str(path)
                        )
                    )
                    continue
                if record_id in records:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "duplicate_id",
                            f"duplicate record id also found at {paths[record_id]}",
                            record_id,
                            str(path),
                        )
                    )
                records[record_id] = record
                paths[record_id] = path
        else:
            records = records_override
            paths = {}

        for record_id, record in records.items():
            path = paths.get(record_id)
            for message in base_record_errors(record):
                issues.append(
                    ValidationIssue(
                        "error", "schema_error", message, record_id, str(path or "")
                    )
                )
            if path:
                try:
                    expected = self._record_path(record)
                    if path != expected:
                        issues.append(
                            ValidationIssue(
                                "error",
                                "wrong_record_path",
                                f"expected canonical path {expected}",
                                record_id,
                                str(path),
                            )
                        )
                except (KeyError, EvidenceStoreError):
                    pass

        def require_ref(owner: dict[str, Any], field: str, expected_type: str) -> None:
            values = owner.get(field, [])
            if isinstance(values, str):
                values = [values] if values else []
            if not isinstance(values, list):
                return
            for target_id in values:
                target = records.get(target_id)
                if not target or target.get("record_type") != expected_type:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "dangling_id",
                            f"{field} references missing {expected_type} {target_id!r}",
                            owner.get("id", ""),
                            str(paths.get(owner.get("id", ""), "")),
                        )
                    )

        stale_physical_sources: set[str] = set()
        for record_id, record in records.items():
            record_type = record.get("record_type")
            if record_type in {"work", "claim", "dataset"}:
                require_ref(record, "topic_ids", "topic")
                if record_type == "work" and record.get("current_source_version_id"):
                    require_ref(record, "current_source_version_id", "source_version")
                if record_type == "dataset":
                    content_hash = record.get("content_hash", "")
                    hash_status = record.get("hash_status")
                    if hash_status not in {"unknown", "verified"}:
                        issues.append(
                            ValidationIssue(
                                "error",
                                "invalid_dataset_hash_status",
                                f"invalid hash_status {hash_status!r}",
                                record_id,
                            )
                        )
                    if hash_status == "unknown" or not content_hash:
                        issues.append(
                            ValidationIssue(
                                "warning",
                                "unverified_dataset_hash",
                                "external dataset has no verified content hash",
                                record_id,
                            )
                        )
                    elif len(content_hash) != 64 or any(
                        character not in "0123456789abcdefABCDEF"
                        for character in content_hash
                    ):
                        issues.append(
                            ValidationIssue(
                                "error",
                                "invalid_dataset_hash",
                                "verified dataset content_hash must be a SHA-256 hex digest",
                                record_id,
                            )
                        )
            elif record_type == "source_version":
                require_ref(record, "work_id", "work")
                scope = record.get("source_scope")
                hash_kind = record.get("hash_kind")
                if scope not in EVIDENCE_SCOPES:
                    issues.append(
                        ValidationIssue(
                            "error", "invalid_scope", f"invalid source_scope {scope!r}", record_id
                        )
                    )
                if hash_kind not in SOURCE_HASH_KINDS:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_source_hash_kind",
                            f"invalid source hash_kind {hash_kind!r}",
                            record_id,
                        )
                    )
                content_hash = record.get("content_hash", "")
                if not _is_sha256(content_hash):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_source_hash",
                            "source content_hash/fingerprint must be bare lowercase SHA-256",
                            record_id,
                        )
                    )
                if scope in {"full_text", "supplement", "dataset"} and hash_kind != "content_sha256":
                    issues.append(
                        ValidationIssue(
                            "error",
                            "noncontent_source_hash",
                            f"{scope} source requires hash_kind content_sha256",
                            record_id,
                        )
                    )
                source_path = self._resolve_source_path(record)
                if scope in {"full_text", "supplement", "dataset"} and source_path is None:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "unversioned_fulltext_source",
                            f"{scope} source has no content-addressed source file",
                            record_id,
                        )
                    )
                if source_path is not None:
                    if not source_path.is_file():
                        stale_physical_sources.add(record_id)
                        issues.append(
                            ValidationIssue(
                                "error",
                                "missing_source_file",
                                f"source file no longer exists: {source_path}",
                                record_id,
                            )
                        )
                    else:
                        actual = hash_file(source_path)
                        if actual != record.get("content_hash"):
                            stale_physical_sources.add(record_id)
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "stale_source_hash",
                                    f"source hash changed: expected {record.get('content_hash')}, got {actual}",
                                    record_id,
                                    str(source_path),
                                )
                            )
            elif record_type == "evidence_link":
                require_ref(record, "claim_id", "claim")
                require_ref(record, "source_version_id", "source_version")
                if record.get("passage_id"):
                    require_ref(record, "passage_id", "passage")
                relation = record.get("relation")
                verdict = record.get("verdict")
                scope = record.get("evidence_scope")
                if relation not in RELATIONS:
                    issues.append(
                        ValidationIssue(
                            "error", "invalid_relation", f"invalid relation {relation!r}", record_id
                        )
                    )
                if verdict not in VERDICTS:
                    issues.append(
                        ValidationIssue(
                            "error", "invalid_verdict", f"invalid verdict {verdict!r}", record_id
                        )
                    )
                if scope not in EVIDENCE_SCOPES:
                    issues.append(
                        ValidationIssue(
                            "error", "invalid_scope", f"invalid evidence_scope {scope!r}", record_id
                        )
                    )
                source = records.get(record.get("source_version_id"), {})
                abstract_only = scope == "abstract" or source.get("source_scope") == "abstract"
                if abstract_only and (
                    verdict == "verified" or relation in {"supports", "contradicts"}
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "abstract_overclaim",
                            "abstract-only evidence cannot verify, support, or contradict a claim",
                            record_id,
                        )
                    )
                scope_rank = {"metadata": 0, "abstract": 1, "full_text": 2, "supplement": 2, "dataset": 2}
                source_scope = source.get("source_scope")
                if scope in scope_rank and source_scope in scope_rank and scope_rank[scope] > scope_rank[source_scope]:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "scope_exceeds_source",
                            f"evidence scope {scope} exceeds source scope {source_scope}",
                            record_id,
                        )
                    )
                if verdict == "verified" and (
                    not record.get("locator") or not record.get("excerpt_hash")
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "untraceable_evidence",
                            "verified evidence requires locator and excerpt_hash",
                            record_id,
                        )
                    )
                excerpt_hash = record.get("excerpt_hash", "")
                if excerpt_hash and not _is_sha256(excerpt_hash):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_excerpt_hash",
                            "excerpt_hash must be bare lowercase SHA-256",
                            record_id,
                        )
                    )
                passage_id = record.get("passage_id", "")
                requires_passage = (
                    scope == "full_text"
                    and verdict == "verified"
                    and relation in {"supports", "contradicts"}
                )
                if requires_passage and not passage_id:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "missing_passage_link",
                            "verified full-text support/contradiction requires a passage",
                            record_id,
                        )
                    )
                passage = records.get(passage_id, {}) if passage_id else {}
                if passage and (
                    passage.get("source_version_id") != record.get("source_version_id")
                    or passage.get("locator") != record.get("locator")
                    or passage.get("excerpt_hash", "") != excerpt_hash
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "mismatched_passage_link",
                            "passage does not match evidence source, locator, and excerpt hash",
                            record_id,
                        )
                    )
            elif record_type == "candidate":
                require_ref(record, "topic_id", "topic")
                require_ref(record, "claim_ids", "claim")
                if not record.get("primitives") or not record.get("objective") or not record.get("data_regime"):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "incomplete_candidate_contract",
                            "candidate requires primitives, objective, and data_regime",
                            record_id,
                        )
                    )
                expected_component = digest(
                    {
                        "description": normalize_text(record.get("description", "")),
                        "claim_ids": sorted(set(record.get("claim_ids", []))),
                        "primitives": sorted(
                            normalize_text(item) for item in record.get("primitives", [])
                        ),
                        "assumptions": sorted(
                            normalize_text(item) for item in record.get("assumptions", [])
                        ),
                    }
                )
                if record.get("component_hash") != expected_component:
                    issues.append(
                        ValidationIssue(
                            "error", "stale_candidate_hash", "component_hash is stale", record_id
                        )
                    )
                if record.get("objective_hash") != digest(normalize_text(record.get("objective", ""))):
                    issues.append(
                        ValidationIssue(
                            "error", "stale_candidate_hash", "objective_hash is stale", record_id
                        )
                    )
                if record.get("data_regime_hash") != digest(normalize_text(record.get("data_regime", ""))):
                    issues.append(
                        ValidationIssue(
                            "error", "stale_candidate_hash", "data_regime_hash is stale", record_id
                        )
                    )
            elif record_type == "evidence_packet":
                require_ref(record, "topic_id", "topic")
                if record.get("candidate_id"):
                    require_ref(record, "candidate_id", "candidate")
                require_ref(record, "claim_ids", "claim")
                require_ref(record, "evidence_link_ids", "evidence_link")
                require_ref(record, "source_version_ids", "source_version")
                require_ref(record, "passage_ids", "passage")
                require_ref(record, "query_run_ids", "query_run")
                require_ref(record, "work_ids", "work")
                require_ref(record, "dataset_ids", "dataset")
                linked_passages = {
                    records.get(link_id, {}).get("passage_id", "")
                    for link_id in record.get("evidence_link_ids", [])
                }
                linked_passages.discard("")
                if set(record.get("passage_ids", [])) != linked_passages:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "packet_passage_mismatch",
                            "packet passage_ids must exactly match selected evidence links",
                            record_id,
                        )
                    )
                if record.get("status") not in {"frozen", "invalidated"}:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_packet_status",
                            f"invalid evidence packet status {record.get('status')!r}",
                            record_id,
                        )
                    )
                dependency_hashes_value = record.get("dependency_hashes", {})
                dependency_hashes = (
                    dependency_hashes_value
                    if isinstance(dependency_hashes_value, dict)
                    else {}
                )
                stale: list[str] = []
                if isinstance(dependency_hashes_value, dict):
                    if digest(dependency_hashes) != record.get("snapshot_hash"):
                        issues.append(
                            ValidationIssue(
                                "error",
                                "invalid_packet_hash",
                                "snapshot_hash does not match frozen dependency hashes",
                                record_id,
                            )
                        )
                    if record.get("status") == "frozen":
                        for dependency_id, frozen_hash in dependency_hashes.items():
                            dependency = records.get(dependency_id)
                            if dependency is None or semantic_hash(dependency) != frozen_hash:
                                stale.append(dependency_id)
                if stale:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "stale_packet",
                            "evidence packet dependencies changed: " + ", ".join(sorted(set(stale))),
                            record_id,
                        )
                    )
                if records_override is None:
                    snapshot_path = self.meta / "snapshots" / f"{record_id}.json"
                    try:
                        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as exc:
                        issues.append(
                            ValidationIssue(
                                "error",
                                "invalid_packet_snapshot",
                                f"missing or invalid portable snapshot: {exc}",
                                record_id,
                                str(snapshot_path),
                            )
                        )
                    else:
                        frozen_packet = snapshot.get("packet", {})
                        frozen_records = snapshot.get("records", {})
                        if (
                            frozen_packet.get("id") != record_id
                            or frozen_packet.get("snapshot_hash") != record.get("snapshot_hash")
                        ):
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "invalid_packet_snapshot",
                                    "snapshot packet identity/hash does not match manifest",
                                    record_id,
                                    str(snapshot_path),
                                )
                            )
                        if not isinstance(frozen_records, dict):
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "invalid_packet_snapshot",
                                    "snapshot records must be an object",
                                    record_id,
                                    str(snapshot_path),
                                )
                            )
                        else:
                            for dependency_id, frozen_hash in dependency_hashes.items():
                                frozen_record = frozen_records.get(dependency_id)
                                if (
                                    not isinstance(frozen_record, dict)
                                    or semantic_hash(frozen_record) != frozen_hash
                                ):
                                    issues.append(
                                        ValidationIssue(
                                            "error",
                                            "invalid_packet_snapshot",
                                            f"snapshot does not preserve dependency {dependency_id}",
                                            record_id,
                                            str(snapshot_path),
                                        )
                                    )
            elif record_type == "query_run":
                require_ref(record, "topic_id", "topic")
                require_ref(record, "result_work_ids", "work")
                raw_response_hash = record.get("raw_response_hash", "")
                if raw_response_hash and (
                    len(raw_response_hash) != 64
                    or any(character not in "0123456789abcdefABCDEF" for character in raw_response_hash)
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_raw_response_hash",
                            "raw_response_hash must be a SHA-256 hex digest",
                            record_id,
                        )
                    )
            elif record_type == "reading":
                require_ref(record, "work_id", "work")
                require_ref(record, "topic_ids", "topic")
                require_ref(record, "source_version_ids", "source_version")
                for source_id in record.get("source_version_ids", []):
                    source = records.get(source_id, {})
                    if source and source.get("work_id") != record.get("work_id"):
                        issues.append(
                            ValidationIssue(
                                "error",
                                "cross_work_reading",
                                f"reading source {source_id} belongs to another work",
                                record_id,
                            )
                        )
            elif record_type == "passage":
                require_ref(record, "work_id", "work")
                require_ref(record, "source_version_id", "source_version")
                require_ref(record, "topic_ids", "topic")
                require_ref(record, "claim_ids", "claim")
                source = records.get(record.get("source_version_id"), {})
                if source and source.get("work_id") != record.get("work_id"):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "cross_work_passage",
                            "passage work_id does not match its source version",
                            record_id,
                        )
                    )
                if not record.get("locator"):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "untraceable_passage",
                            "passage requires a stable locator",
                            record_id,
                        )
                    )
                excerpt_hash = record.get("excerpt_hash", "")
                if excerpt_hash and not _is_sha256(excerpt_hash):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_excerpt_hash",
                            "passage excerpt_hash must be bare lowercase SHA-256",
                            record_id,
                        )
                    )
            elif record_type == "method":
                require_ref(record, "topic_ids", "topic")
                require_ref(record, "work_ids", "work")
                relations = record.get("relations", [])
                if isinstance(relations, list):
                    for relation in relations:
                        if not isinstance(relation, dict):
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "invalid_method_relation",
                                    "method relation must be an object",
                                    record_id,
                                )
                            )
                            continue
                        relation_name = relation.get("relation")
                        target_id = relation.get("target_id")
                        if relation_name not in RELATIONS:
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "invalid_relation",
                                    f"invalid method relation {relation_name!r}",
                                    record_id,
                                )
                            )
                        if target_id not in records:
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "dangling_id",
                                    f"method relation target is missing: {target_id!r}",
                                    record_id,
                                )
                            )
            elif record_type == "audit_verdict":
                require_ref(record, "topic_id", "topic")
                if record.get("candidate_id"):
                    require_ref(record, "candidate_id", "candidate")
                require_ref(record, "evidence_packet_id", "evidence_packet")
                if record.get("verdict") not in AUDIT_VERDICTS:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_audit_verdict",
                            f"invalid audit verdict {record.get('verdict')!r}",
                            record_id,
                        )
                    )
                subject_type = record.get("subject_type", "")
                subject_id = record.get("subject_id", "")
                if bool(subject_type) != bool(subject_id):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "incomplete_audit_subject",
                            "subject_type and subject_id must be supplied together",
                            record_id,
                        )
                    )
                for field in ("subject_hash", "protocol_hash"):
                    value = record.get(field, "")
                    if value and (not isinstance(value, str) or not _is_sha256(value)):
                        issues.append(
                            ValidationIssue(
                                "error",
                                "invalid_audit_hash",
                                f"{field} must be bare lowercase SHA-256",
                                record_id,
                            )
                        )
                artifact_hashes = record.get("artifact_hashes", {})
                if artifact_hashes and not isinstance(artifact_hashes, dict):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_audit_hashes",
                            "artifact_hashes must be an object",
                            record_id,
                        )
                    )
                elif isinstance(artifact_hashes, dict):
                    for label, value in artifact_hashes.items():
                        if not isinstance(label, str) or not label or not isinstance(value, str) or not _is_sha256(value):
                            issues.append(
                                ValidationIssue(
                                    "error",
                                    "invalid_audit_hash",
                                    "artifact_hashes entries require non-empty labels and bare lowercase SHA-256 values",
                                    record_id,
                                )
                            )

        if stale_physical_sources:
            already_stale = {
                issue.record_id for issue in issues if issue.code == "stale_packet"
            }
            for record_id, record in records.items():
                if record.get("record_type") != "evidence_packet":
                    continue
                affected = stale_physical_sources & set(
                    record.get("source_version_ids", [])
                )
                if (
                    affected
                    and record.get("status") == "frozen"
                    and record_id not in already_stale
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "stale_packet",
                            "packet source content changed: "
                            + ", ".join(sorted(affected)),
                            record_id,
                        )
                    )

        if records_override is None:
            for path in self.meta.rglob("*") if self.meta.exists() else ():
                lower = path.name.lower()
                if path.is_file() and (
                    lower.endswith((".sqlite", ".sqlite3", ".db", "-wal", "-shm"))
                    or lower in {"wal", "sqlite"}
                ):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "live_database_in_vault",
                            "derived SQLite/WAL data must live outside the synced vault",
                            path=str(path),
                        )
                    )
            for index in [self.vault / "00 Research Index.md", *(self.vault / "30 Indexes").glob("*.md")]:
                if not index.exists():
                    continue
                text = index.read_text(encoding="utf-8")
                if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "invalid_index_markers",
                            "index must contain exactly one generated block",
                            path=str(index),
                        )
                    )
        return issues
