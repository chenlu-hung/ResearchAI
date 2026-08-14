from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PHASES = (
    "intake_import",
    "atomic_claim_map",
    "prior_art_audit",
    "method_frozen",
    "positioning_skeleton",
    "experiment_contract",
    "protocol_frozen",
    "results_ingested",
    "evidence_audited",
    "results_red_team",
    "drafting",
    "scientific_review",
    "submission",
    "final",
)

PHASE_TO_GATE = {
    "intake_import": "intake_import",
    "atomic_claim_map": "atomic_claim_map",
    "prior_art_audit": "prior_art_audit",
    "method_frozen": "method_freeze",
    "positioning_skeleton": "positioning_skeleton",
    "experiment_contract": "experiment_contract",
    "protocol_frozen": "protocol_freeze",
    "results_ingested": "results_ingested",
    "evidence_audited": "evidence_audited",
    "results_red_team": "results_red_team",
    "drafting": "draft",
    "scientific_review": "scientific_review",
    "submission": "submission",
    "final": "all prior gates",
}


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_lifecycle_phases_and_gate_mapping_are_documented_consistently() -> None:
    lifecycle = _read("shared/prompts/research_lifecycle.md")
    state_schema = _read("shared/research_state.schema.md")
    routing = _read("skills/research-conductor/routing.md")

    for phase in PHASES:
        assert f"`{phase}`" in lifecycle
        assert f"`{phase}`" in state_schema
        assert f"| `{phase}` |" in routing

    for phase, gate in PHASE_TO_GATE.items():
        rendered_gate = gate if phase == "final" else f"`{gate}`"
        assert f"| `{phase}` | {rendered_gate} |" in state_schema


def test_final_requires_lifecycle_and_legacy_completion() -> None:
    conductor = _read("skills/research-conductor/SKILL.md")
    command = _read("commands/research.md")

    for text in (conductor, command):
        assert "research_phase: final" in text
        assert "stage: final" in text
    assert "stage: final` by itself is never a completion signal" in conductor


def test_scientific_review_is_a_non_circular_composite_gate() -> None:
    full_draft = _read("skills/paper-writer/modes/full-draft.md")
    self_review = _read("skills/paper-writer/modes/self-review.md")
    citation_audit = _read("skills/paper-writer/modes/citation-audit.md")
    lifecycle = _read("shared/prompts/research_lifecycle.md")

    assert full_draft.index("Run `self-review`") < full_draft.index("Run `citation-audit`")
    assert "scientific-review lifecycle gate to `conditional`" in self_review
    assert "current **self-review artifact**" in citation_audit
    assert "may still be `conditional`" in citation_audit
    assert "composite artifact" in lifecycle


def test_evidence_packet_scope_carries_all_reproducibility_dependencies() -> None:
    grounding = _read("shared/prompts/evidence_grounding.md")
    state_schema = _read("shared/research_state.schema.md")

    for token in (
        "claim_ids",
        "query_run_ids",
        "work_ids",
        "source_version_ids",
        "passage_ids",
        "dataset_ids",
    ):
        assert token in state_schema
    assert "referenced passage IDs" in grounding


def test_shared_prompts_use_host_neutral_coordination_language() -> None:
    dispatch = _read("shared/prompts/model_dispatch.md")
    assert "via SendMessage" not in dispatch
    assert "same-worker" in dispatch
