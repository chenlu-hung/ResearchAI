import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "shared"))

from evidence_core.model import RECORD_TYPES, parse_markdown  # noqa: E402
from evidence_core.store import EvidenceStore, EvidenceStoreError  # noqa: E402


def _grounded_store(tmp_path):
    vault = tmp_path / "vault"
    store = EvidenceStore(vault)
    store.init("Test Research")
    topic = store.add_topic("Cross-resolution operators")
    fulltext = tmp_path / "paper.txt"
    fulltext.write_text("Section 3. The operator transfers coordinates.\n", encoding="utf-8")
    work, source = store.ingest_work(
        "Coordinate transfer for operators",
        authors=["Ada Researcher"],
        year=2025,
        doi="10.1000/example",
        topic_ids=[topic["id"]],
        source_file=fulltext,
        source_scope="full_text",
    )
    claim = store.add_claim(
        "The method transfers coordinates between resolutions.",
        topic_ids=[topic["id"]],
    )
    passage = store.add_passage(
        source["id"],
        locator="Section 3, paragraph 1",
        paraphrase="The operator maps coordinates across resolutions.",
        excerpt="The operator transfers coordinates.",
        topic_ids=[topic["id"]],
        claim_ids=[claim["id"]],
    )
    link = store.link_claim(
        claim["id"],
        source["id"],
        passage_id=passage["id"],
        locator="Section 3, paragraph 1",
        relation="supports",
        verdict="verified",
        evidence_scope="full_text",
        excerpt="The operator transfers coordinates.",
        verifier="test",
    )
    query = store.add_query_run(
        topic["id"],
        '"coordinate transfer" resolution operator',
        provider="OpenAlex",
        result_work_ids=[work["id"]],
        raw_response_hash="a" * 64,
        observations=[{"rank": 1, "work_id": work["id"]}],
        executed_at="2026-07-24T01:00:00Z",
    )
    candidate = store.add_candidate(
        topic["id"],
        "PCANN transfer",
        description="PCA coordinates plus a learned residual.",
        claim_ids=[claim["id"]],
        primitives=["PCA coordinate map", "residual MLP"],
        objective="Minimize normalized field reconstruction error",
        data_regime="paired multi-resolution operator data",
        assumptions=["shared latent rank"],
    )
    return store, topic, work, source, claim, link, query, candidate, fulltext


def test_cli_init_and_validate(tmp_path, run_script):
    vault = tmp_path / "cli vault"
    result = run_script("shared/evidencectl.py", "init", "--vault", str(vault))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["canonical_format"] == "markdown-json-frontmatter"
    result = run_script("shared/evidencectl.py", "validate", "--vault", str(vault))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["valid"] is True
    assert not list((vault / ".evidence").glob("*.sqlite*"))


def test_cli_can_freeze_a_grounded_packet_end_to_end(tmp_path, run_script):
    vault = tmp_path / "pipeline vault"
    source_file = tmp_path / "source.txt"
    source_file.write_text("A located full-text claim.", encoding="utf-8")

    def run(*args):
        result = run_script("shared/evidencectl.py", *args)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    run("init", "--vault", str(vault))
    topic = run(
        "topic", "add", "--vault", str(vault), "--title", "CLI evidence loop"
    )
    ingested = run(
        "work",
        "ingest",
        "--vault",
        str(vault),
        "--title",
        "CLI paper",
        "--topic",
        topic["id"],
        "--source-file",
        str(source_file),
        "--source-scope",
        "full_text",
    )
    claim = run(
        "claim",
        "add",
        "--vault",
        str(vault),
        "--topic",
        topic["id"],
        "--text",
        "The CLI paper contains a located claim.",
    )
    passage = run(
        "passage",
        "add",
        "--vault",
        str(vault),
        "--source",
        ingested["source_version"]["id"],
        "--locator",
        "line 1",
        "--paraphrase",
        "The paper contains the located claim.",
        "--topic",
        topic["id"],
        "--claim",
        claim["id"],
        "--excerpt",
        "located full-text claim",
    )
    link = run(
        "claim",
        "link",
        "--vault",
        str(vault),
        "--claim",
        claim["id"],
        "--source",
        ingested["source_version"]["id"],
        "--passage",
        passage["id"],
        "--locator",
        "line 1",
        "--relation",
        "supports",
        "--verdict",
        "verified",
        "--scope",
        "full_text",
        "--excerpt",
        "located full-text claim",
        "--verifier",
        "test",
    )
    query = run(
        "query",
        "add",
        "--vault",
        str(vault),
        "--topic",
        topic["id"],
        "--query",
        "located claim",
        "--provider",
        "test-provider",
        "--result-work",
        ingested["work"]["id"],
        "--executed-at",
        "2026-07-24T03:00:00Z",
    )
    candidate = run(
        "candidate",
        "add",
        "--vault",
        str(vault),
        "--topic",
        topic["id"],
        "--title",
        "CLI candidate",
        "--claim",
        claim["id"],
        "--primitive",
        "located mapping",
        "--objective",
        "minimize error",
        "--data-regime",
        "paired observations",
    )
    packet = run(
        "packet",
        "freeze",
        "--vault",
        str(vault),
        "--topic",
        topic["id"],
        "--candidate",
        candidate["id"],
        "--evidence-link",
        link["id"],
        "--query-run",
        query["id"],
    )
    assert packet["status"] == "frozen"
    assert packet["passage_ids"] == [passage["id"]]
    validated = run("validate", "--vault", str(vault))
    assert validated["valid"] is True
    audit = run(
        "audit",
        "add",
        "--vault",
        str(vault),
        "--topic",
        topic["id"],
        "--candidate",
        candidate["id"],
        "--packet",
        packet["id"],
        "--verdict",
        "pass",
        "--rationale",
        "CLI bindings validate.",
        "--auditor",
        "test",
        "--subject-type",
        "result_manifest",
        "--subject-id",
        "manifest.json",
        "--subject-hash",
        "d" * 64,
        "--artifact-hash",
        f"metrics.json={'e' * 64}",
        "--protocol-hash",
        "f" * 64,
    )
    assert audit["subject_id"] == "manifest.json"
    invalidated = run(
        "packet",
        "invalidate",
        "--vault",
        str(vault),
        "--packet",
        packet["id"],
        "--reason",
        "manual CLI review",
    )
    assert invalidated["status"] == "invalidated"
    historical_audit = EvidenceStore(vault).get(audit["id"], "audit_verdict")
    assert historical_audit == audit
    assert run("validate", "--vault", str(vault))["valid"] is True
    updated = run(
        "work",
        "update",
        "--vault",
        str(vault),
        "--work",
        ingested["work"]["id"],
        "--title",
        "Corrected CLI paper",
    )
    assert updated["id"] == ingested["work"]["id"]


def test_work_ingest_deduplicates_and_uses_stable_ids(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("A Topic")
    first_work, first_source = store.ingest_work(
        "A Stable Paper",
        authors=["A. Author"],
        year=2024,
        doi="https://doi.org/10.5555/STABLE",
        url="https://example.test/paper",
        topic_ids=[topic["id"]],
    )
    second_work, second_source = store.ingest_work(
        "a stable paper",
        authors=["A. Author"],
        year=2024,
        doi="doi:10.5555/stable",
        url="https://example.test/paper",
        topic_ids=[topic["id"]],
    )
    assert first_work["id"] == second_work["id"]
    assert first_source["id"] == second_source["id"]
    assert sum(r["record_type"] == "work" for r in store.records().values()) == 1


def test_url_cannot_masquerade_as_versioned_fulltext(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    with pytest.raises(EvidenceStoreError, match="not a content hash"):
        store.ingest_work(
            "Unversioned PDF",
            url="https://example.test/paper.pdf",
            source_scope="full_text",
        )


def test_abstract_cannot_verify_or_support(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("Abstract gate")
    _, source = store.ingest_work(
        "Abstract only", topic_ids=[topic["id"]], source_scope="abstract"
    )
    claim = store.add_claim("A strong result holds.", topic_ids=[topic["id"]])
    with pytest.raises(EvidenceStoreError, match="abstract-only"):
        store.link_claim(
            claim["id"],
            source["id"],
            locator="Abstract",
            relation="supports",
            verdict="verified",
            evidence_scope="abstract",
            excerpt="strong result",
            verifier="test",
        )


def test_query_preserves_provider_rank_and_raw_response_hash(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("Rank preservation")
    work_a, _ = store.ingest_work("Alpha", topic_ids=[topic["id"]])
    work_b, _ = store.ingest_work("Beta", topic_ids=[topic["id"]])
    query = store.add_query_run(
        topic["id"],
        "ranked query",
        provider="provider",
        result_work_ids=[work_b["id"], work_a["id"], work_b["id"]],
        raw_response_hash="b" * 64,
        observations=[{"rank": 1, "provider_id": "B"}, {"rank": 2, "provider_id": "A"}],
        executed_at="2026-07-24T02:00:00Z",
    )
    assert query["result_work_ids"] == [work_b["id"], work_a["id"]]
    assert query["raw_response_hash"] == "b" * 64
    assert [item["rank"] for item in query["observations"]] == [1, 2]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("primitives", ["PCA coordinate map", "attention transfer"]),
        ("objective", "Minimize a calibrated spectral loss"),
        ("data_regime", "unpaired cross-resolution operator data"),
    ],
)
def test_material_candidate_change_invalidates_packet_and_preserves_snapshot(
    tmp_path, field, value
):
    store, topic, _, _, claim, link, query, candidate, _ = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        claim_ids=[claim["id"]],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    snapshot_path = store.meta / "snapshots" / f"{packet['id']}.json"
    before = snapshot_path.read_bytes()
    snapshot = json.loads(before)
    assert snapshot["packet"]["id"] == packet["id"]
    assert candidate["id"] in snapshot["records"]
    assert query["id"] in snapshot["records"]

    args = {
        "description": candidate["description"],
        "claim_ids": candidate["claim_ids"],
        "primitives": candidate["primitives"],
        "objective": candidate["objective"],
        "data_regime": candidate["data_regime"],
        "assumptions": candidate["assumptions"],
    }
    args[field] = value
    store.add_candidate(topic["id"], candidate["title"], **args)

    changed_packet = store.get(packet["id"], "evidence_packet")
    assert changed_packet["status"] == "invalidated"
    assert candidate["id"] in changed_packet["invalidated_by"]
    assert changed_packet["snapshot_hash"] == packet["snapshot_hash"]
    assert changed_packet["dependency_hashes"] == packet["dependency_hashes"]
    assert snapshot_path.read_bytes() == before
    assert "stale_packet" not in {issue.code for issue in store.validate()}


def test_stale_source_hash_is_detected(tmp_path):
    store, topic, _, source, claim, link, query, candidate, source_file = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        claim_ids=[claim["id"]],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    assert packet["status"] == "frozen"
    source_file.write_text("changed full text", encoding="utf-8")
    issues = store.validate()
    stale = [issue for issue in issues if issue.code == "stale_source_hash"]
    assert stale and stale[0].record_id == source["id"]
    assert any(issue.code == "stale_packet" and issue.record_id == packet["id"] for issue in issues)


def test_dataset_without_real_hash_warns_and_later_hash_invalidates_packet(tmp_path):
    store, topic, _, _, claim, link, query, candidate, _ = _grounded_store(tmp_path)
    dataset = store.add_dataset(
        "External benchmark",
        "/external/data/benchmark.zarr",
        topic_ids=[topic["id"]],
        version="v1",
    )
    assert dataset["content_hash"] == ""
    assert dataset["hash_status"] == "unknown"
    assert "unverified_dataset_hash" in {issue.code for issue in store.validate()}
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        claim_ids=[claim["id"]],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
        dataset_ids=[dataset["id"]],
    )
    updated = store.add_dataset(
        "External benchmark",
        "/external/data/benchmark.zarr",
        topic_ids=[topic["id"]],
        content_hash="c" * 64,
        version="v1",
    )
    assert updated["hash_status"] == "verified"
    assert store.get(packet["id"], "evidence_packet")["status"] == "invalidated"


def test_human_notes_and_multiline_yaml_lists_coexist(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("Human notes")
    topic_path = store._record_path(topic)
    text = topic_path.read_text(encoding="utf-8")
    text = text.replace('tags: []', 'tags:\n  - manual\n  - reusable')
    topic_path.write_text(text, encoding="utf-8")
    parsed, _ = parse_markdown(text)
    assert parsed["tags"] == ["manual", "reusable"]

    note = topic_path.parent / "Candidates" / "Candidates Index.md"
    note.write_text(
        "---\nmanaged_by: human\ntags:\n  - planning\n---\n# Candidate notes\n",
        encoding="utf-8",
    )
    store.rebuild_indexes()
    assert note.exists()
    assert not [issue for issue in store.validate() if issue.path == str(note)]


def test_index_rebuild_preserves_manual_text(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    store.add_topic("Index topic")
    index = store.vault / "00 Research Index.md"
    index.write_text(index.read_text(encoding="utf-8") + "\nManual synthesis survives.\n", encoding="utf-8")
    store.rebuild_indexes()
    rebuilt = index.read_text(encoding="utf-8")
    assert "Manual synthesis survives." in rebuilt
    assert rebuilt.count("<!-- EVIDENCECTL:BEGIN -->") == 1
    assert rebuilt.count("<!-- EVIDENCECTL:END -->") == 1


def test_reusable_reading_passage_method_and_audit_are_first_class(tmp_path):
    store, topic, work, source, claim, link, query, candidate, _ = _grounded_store(tmp_path)
    reading = store.add_reading(
        work["id"],
        topic_ids=[topic["id"]],
        source_version_ids=[source["id"]],
        summary="Transfers coordinates through a low-rank representation.",
        status="complete",
    )
    passage = store.add_passage(
        source["id"],
        locator="Section 3, paragraph 1",
        paraphrase="The method maps coordinates between grids.",
        excerpt="operator transfers coordinates",
        topic_ids=[topic["id"]],
        claim_ids=[claim["id"]],
    )
    method = store.add_method(
        "Coordinate transfer",
        description="A reusable cross-representation alignment primitive.",
        topic_ids=[topic["id"]],
        work_ids=[work["id"]],
        relations=[{"relation": "relevant_to", "target_id": claim["id"]}],
    )
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    audit = store.add_audit_verdict(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_packet_id=packet["id"],
        verdict="conditional",
        rationale="Closest-prior coverage is adequate; component novelty remains conditional.",
        auditor="test",
    )
    assert {reading["record_type"], passage["record_type"], method["record_type"], audit["record_type"]} == {
        "reading",
        "passage",
        "method",
        "audit_verdict",
    }
    assert store.validate() == []
    for name in ("Readings Index.md", "Passages Index.md", "Methods Index.md", "Audit Verdicts Index.md"):
        assert (store.vault / "30 Indexes" / name).exists()


def test_bibtex_export_is_deterministic_with_stable_collision_keys(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("BibTeX")
    first, _ = store.ingest_work(
        "Learning One", authors=["Jane Smith"], year=2024, topic_ids=[topic["id"]]
    )
    second, _ = store.ingest_work(
        "Learning Two", authors=["Jane Smith"], year=2024, topic_ids=[topic["id"]]
    )
    first_out = tmp_path / "first.bib"
    second_out = tmp_path / "second.bib"
    result_a = store.export_bibtex(first_out, topic_id=topic["id"])
    result_b = store.export_bibtex(second_out, topic_id=topic["id"])
    assert first_out.read_bytes() == second_out.read_bytes()
    assert result_a["content_hash"] == result_b["content_hash"]
    assert result_a["bibkeys"] == result_b["bibkeys"]
    assert set(result_a["bibkeys"]) == {first["id"], second["id"]}
    assert sorted(result_a["bibkeys"].values()) == [
        "smith2024learninga",
        "smith2024learningb",
    ]


def test_init_seeds_single_source_schemas_and_all_templates_idempotently(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    schema_source = REPO / "shared" / "evidence_core" / "resources" / "schemas"
    schema_reference = REPO / "skills" / "evidence-store" / "references" / "schemas"
    for name in ("config.schema.json", "evidence-records.schema.json"):
        canonical = (schema_source / name).read_bytes()
        assert (schema_reference / name).read_bytes() == canonical
        assert (store.meta / "schemas" / name).read_bytes() == canonical

    templates = sorted((store.vault / "99 Templates" / "v1").glob("*.md"))
    template_types = {parse_markdown(path.read_text(encoding="utf-8"))[0]["record_type"] for path in templates}
    assert template_types == RECORD_TYPES

    edited = templates[0]
    manual = edited.read_text(encoding="utf-8") + "\nManual template guidance.\n"
    edited.write_text(manual, encoding="utf-8")
    store.init()
    assert edited.read_text(encoding="utf-8") == manual


def test_source_hash_kind_distinguishes_discovery_from_content(tmp_path):
    store = EvidenceStore(tmp_path / "vault")
    store.init()
    topic = store.add_topic("Source hashes")
    _, metadata = store.ingest_work(
        "Metadata source",
        url="https://example.test/metadata",
        topic_ids=[topic["id"]],
    )
    assert metadata["hash_kind"] == "discovery_fingerprint"
    metadata_claim = store.add_claim(
        "This work is relevant to source hash provenance.", topic_ids=[topic["id"]]
    )
    metadata_link = store.link_claim(
        metadata_claim["id"],
        metadata["id"],
        locator="metadata record",
        relation="background",
        verdict="cannot_determine",
        evidence_scope="metadata",
        verifier="test",
    )
    assert metadata_link["passage_id"] == ""

    source_file = tmp_path / "paper.txt"
    source_file.write_text("versioned content", encoding="utf-8")
    _, fulltext = store.ingest_work(
        "Full-text source",
        topic_ids=[topic["id"]],
        source_file=source_file,
        source_scope="full_text",
    )
    assert fulltext["hash_kind"] == "content_sha256"
    invalid = dict(fulltext, hash_kind="discovery_fingerprint")
    with store.lock():
        store._write_record_locked(invalid)
    assert "noncontent_source_hash" in {issue.code for issue in store.validate()}


def test_verified_fulltext_link_requires_matching_passage(tmp_path):
    store, topic, _, source, claim, _, _, _, _ = _grounded_store(tmp_path)
    with pytest.raises(EvidenceStoreError, match="requires --passage"):
        store.link_claim(
            claim["id"],
            source["id"],
            locator="Section 4",
            relation="supports",
            verdict="verified",
            evidence_scope="full_text",
            excerpt="another located result",
            verifier="test",
        )
    passage = store.add_passage(
        source["id"],
        locator="Section 5",
        paraphrase="A different result.",
        excerpt="different result",
        topic_ids=[topic["id"]],
        claim_ids=[claim["id"]],
    )
    with pytest.raises(EvidenceStoreError, match="passage must match"):
        store.link_claim(
            claim["id"],
            source["id"],
            passage_id=passage["id"],
            locator="Section 6",
            relation="contradicts",
            verdict="verified",
            evidence_scope="full_text",
            excerpt="different result",
            verifier="test",
        )


def test_packet_freezes_passage_and_auto_invalidation_is_scoped(tmp_path):
    store, topic, work, source, claim, link, query, candidate, _ = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    passage_id = link["passage_id"]
    assert packet["passage_ids"] == [passage_id]
    snapshot_path = store.meta / "snapshots" / f"{packet['id']}.json"
    before = snapshot_path.read_bytes()
    assert passage_id in json.loads(before)["records"]

    unrelated_claim = store.add_claim(
        "An unrelated claim for the same topic.", topic_ids=[topic["id"]]
    )
    unrelated_passage = store.add_passage(
        source["id"],
        locator="Section 8",
        paraphrase="This span addresses another claim.",
        excerpt="another claim span",
        topic_ids=[topic["id"]],
        claim_ids=[unrelated_claim["id"]],
    )
    store.link_claim(
        unrelated_claim["id"],
        source["id"],
        passage_id=unrelated_passage["id"],
        locator="Section 8",
        relation="supports",
        verdict="verified",
        evidence_scope="full_text",
        excerpt="another claim span",
        verifier="test",
    )
    assert store.get(packet["id"], "evidence_packet")["status"] == "frozen"

    other_topic = store.add_topic("Unrelated topic")
    store.add_query_run(
        other_topic["id"],
        "unrelated query",
        provider="test",
        executed_at="2026-07-26T01:00:00Z",
    )
    assert store.get(packet["id"], "evidence_packet")["status"] == "frozen"

    new_passage = store.add_passage(
        source["id"],
        locator="Section 9",
        paraphrase="A new near-neighbor changes the comparison.",
        excerpt="new near-neighbor",
        topic_ids=[topic["id"]],
        claim_ids=[claim["id"]],
    )
    new_link = store.link_claim(
        claim["id"],
        source["id"],
        passage_id=new_passage["id"],
        locator="Section 9",
        relation="contradicts",
        verdict="verified",
        evidence_scope="full_text",
        excerpt="new near-neighbor",
        verifier="test",
    )
    invalidated = store.get(packet["id"], "evidence_packet")
    assert invalidated["status"] == "invalidated"
    assert new_link["id"] in invalidated["invalidated_by"]
    assert snapshot_path.read_bytes() == before

    replacement = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        query_run_ids=[query["id"]],
    )
    historical_audit = store.add_audit_verdict(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_packet_id=replacement["id"],
        verdict="pass",
        rationale="The frozen evidence available at audit time supports the candidate.",
        auditor="test",
    )
    new_query = store.add_query_run(
        topic["id"],
        "new same-topic query",
        provider="test",
        result_work_ids=[work["id"]],
        executed_at="2026-07-26T02:00:00Z",
    )
    query_invalidated = store.get(replacement["id"], "evidence_packet")
    assert query_invalidated["status"] == "invalidated"
    assert new_query["id"] in query_invalidated["invalidated_by"]
    assert store.get(historical_audit["id"], "audit_verdict") == historical_audit
    assert store.validate() == []


def test_manual_packet_invalidation_preserves_snapshot(tmp_path):
    store, topic, _, _, _, link, query, candidate, _ = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    snapshot_path = store.meta / "snapshots" / f"{packet['id']}.json"
    before = snapshot_path.read_bytes()
    invalidated = store.invalidate_packet(packet["id"], reason="manual novelty review")
    assert invalidated["status"] == "invalidated"
    assert invalidated["invalidation_reasons"] == ["manual novelty review"]
    assert snapshot_path.read_bytes() == before
    assert store.validate() == []


def test_audit_subject_and_artifact_hash_bindings_validate(tmp_path):
    store, topic, _, _, _, link, query, candidate, _ = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    audit = store.add_audit_verdict(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_packet_id=packet["id"],
        verdict="pass",
        rationale="Result manifest and protocol agree.",
        auditor="test",
        subject_type="result_manifest",
        subject_id="results/topic/manifest.json",
        subject_hash="d" * 64,
        artifact_hashes={"metrics.json": "e" * 64},
        protocol_hash="f" * 64,
    )
    assert audit["subject_type"] == "result_manifest"
    assert audit["artifact_hashes"] == {"metrics.json": "e" * 64}
    assert store.validate() == []
    with pytest.raises(EvidenceStoreError, match="bare lowercase SHA-256"):
        store.add_audit_verdict(
            topic["id"],
            evidence_packet_id=packet["id"],
            verdict="pass",
            rationale="Invalid binding.",
            auditor="test",
            subject_type="result_manifest",
            subject_id="manifest.json",
            subject_hash="not-a-hash",
        )


def test_work_update_keeps_id_and_invalidates_containing_packets(tmp_path):
    store, topic, work, _, _, link, query, candidate, _ = _grounded_store(tmp_path)
    packet = store.freeze_packet(
        topic["id"],
        candidate_id=candidate["id"],
        evidence_link_ids=[link["id"]],
        query_run_ids=[query["id"]],
    )
    snapshot_path = store.meta / "snapshots" / f"{packet['id']}.json"
    before = snapshot_path.read_bytes()
    updated = store.update_work(
        work["id"],
        title="Corrected coordinate transfer title",
        authors=["Ada Researcher", "Grace Reviewer"],
        year=2026,
    )
    assert updated["id"] == work["id"]
    assert updated["title"] == "Corrected coordinate transfer title"
    invalidated = store.get(packet["id"], "evidence_packet")
    assert invalidated["status"] == "invalidated"
    assert work["id"] in invalidated["invalidated_by"]
    assert snapshot_path.read_bytes() == before
    assert store.validate() == []
