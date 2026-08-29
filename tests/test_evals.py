"""Cover the eval case files and the isolation property the pack/score split
exists to provide.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "evals" / "cases"


def _surfaces() -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(CASES_DIR.glob("*.json"))
    ]


def test_case_files_are_well_formed() -> None:
    seen_surfaces: set[str] = set()
    for surface in _surfaces():
        name = surface["surface"]
        assert name not in seen_surfaces, f"duplicate surface {name}"
        seen_surfaces.add(name)
        assert surface["question"].strip()
        assert len(surface["answers"]) >= 2
        for rule in surface["rules"]:
            assert (ROOT / rule).is_file(), f"{name} names missing rule file {rule}"
        ids: set[str] = set()
        for case in surface["cases"]:
            assert case["id"] not in ids, f"duplicate case id {case['id']}"
            ids.add(case["id"])
            assert case["prompt"].strip()
            assert case["answer"] in surface["answers"]
            assert len(case["because"]) >= 20, (
                f"{case['id']} has a rationale too short to explain a wrong answer")
    assert seen_surfaces, "no eval surfaces found"


def test_no_surface_is_won_by_a_constant_answer() -> None:
    """A set where one answer is always right measures nothing: a model that
    always refuses would ace it. Every surface must exercise both directions."""
    for surface in _surfaces():
        answers = {case["answer"] for case in surface["cases"]}
        assert len(answers) >= 2, (
            f"{surface['surface']} only ever expects {answers} — add cases where "
            "the other answer is correct")


def test_pack_withholds_the_key(tmp_path: Path, run_script) -> None:
    out = tmp_path / "pack"
    result = run_script("scripts/eval_pack.py", "--out", str(out), "--today", "2026-08-23")
    assert result.returncode == 0, result.stdout

    written = "\n".join(path.read_text(encoding="utf-8") for path in sorted(out.iterdir()))
    for surface in _surfaces():
        for case in surface["cases"]:
            assert case["because"] not in written, f"rationale for {case['id']} leaked"
    assert '"answer"' not in written
    assert '"because"' not in written


def test_scoring_a_correct_submission(tmp_path: Path, run_script) -> None:
    out = tmp_path / "pack"
    assert run_script("scripts/eval_pack.py", "--out", str(out)).returncode == 0
    answers = {
        f"{surface['surface']}/{case['id']}": case["answer"]
        for surface in _surfaces()
        for case in surface["cases"]
    }
    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps(answers), encoding="utf-8")

    result = run_script(
        "scripts/eval_score.py", "--answers", str(answers_path),
        "--pack", str(out), "--min-accuracy", "1.0",
    )
    assert result.returncode == 0, result.stdout
    assert f"({len(answers)}/{len(answers)}".replace("(", "") in result.stdout or \
        f"overall: {len(answers)}/{len(answers)}" in result.stdout


def test_scoring_reports_the_rationale_only_for_wrong_answers(tmp_path: Path, run_script) -> None:
    surfaces = _surfaces()
    target = surfaces[0]["cases"][0]
    key = f"{surfaces[0]['surface']}/{target['id']}"
    other = next(a for a in surfaces[0]["answers"] if a != target["answer"])

    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({key: other}), encoding="utf-8")
    result = run_script("scripts/eval_score.py", "--answers", str(answers_path))
    assert result.returncode == 0, result.stdout
    assert f"WRONG {key}" in result.stdout
    assert target["because"] in result.stdout
    # Every other case was left blank, so no other rationale may appear.
    for case in surfaces[0]["cases"][1:]:
        assert case["because"] not in result.stdout


def test_scoring_refuses_a_stale_pack(tmp_path: Path, run_script) -> None:
    out = tmp_path / "pack"
    cases = tmp_path / "cases"
    cases.mkdir()
    payload = {
        "surface": "demo", "question": "q?", "answers": ["A", "B"], "rules": [],
        "cases": [{"id": "one", "prompt": "p",
                   "answer": "A", "because": "the rule says A in this situation"}],
    }
    (cases / "demo.json").write_text(json.dumps(payload), encoding="utf-8")
    assert run_script(
        "scripts/eval_pack.py", "--out", str(out), "--cases-dir", str(cases)
    ).returncode == 0

    payload["cases"][0]["answer"] = "B"
    (cases / "demo.json").write_text(json.dumps(payload), encoding="utf-8")

    answers_path = tmp_path / "answers.json"
    answers_path.write_text(json.dumps({"demo/one": "B"}), encoding="utf-8")
    result = run_script(
        "scripts/eval_score.py", "--answers", str(answers_path),
        "--cases-dir", str(cases), "--pack", str(out),
    )
    assert result.returncode == 1
    assert "cases changed after this pack was built" in result.stdout
