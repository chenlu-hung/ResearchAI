"""Cover the canonical-wording pin: it must catch a reworded mirror, tolerate a
re-wrapped one, and refuse to pass vacuously.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL = """# Rules

| ID | Governs |
|---|---|
| `R-TEST-1` | a pinned sentence |

<!-- firm-rule: id=R-TEST-1 mirrors=mirrors/*.md -->
> The estimator is consistent under Assumption 2 and never derived from the
> working directory.
<!-- /firm-rule: R-TEST-1 -->
"""


def _module():
    path = ROOT / "scripts" / "check_firm_rules.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture(tmp_path: Path, mirror_text: str, canonical: str = CANONICAL) -> Path:
    (tmp_path / "mirrors").mkdir(exist_ok=True)
    (tmp_path / "rules.md").write_text(canonical, encoding="utf-8")
    (tmp_path / "mirrors" / "one.md").write_text(mirror_text, encoding="utf-8")
    return tmp_path


def test_repo_mirrors_carry_the_canonical_wording(run_script) -> None:
    result = run_script("scripts/check_firm_rules.py")
    assert result.returncode == 0, result.stdout
    assert "firm rules: PASS" in result.stdout


def test_rewrapping_a_paragraph_is_not_drift(tmp_path: Path) -> None:
    root = _fixture(tmp_path, (
        "Intro text.\n\nThe estimator is consistent\nunder Assumption 2 and never\n"
        "derived from the working directory.\n\nMore text.\n"
    ))
    assert _module().check(root, root / "rules.md") == []


def test_rewording_a_mirror_is_caught(tmp_path: Path) -> None:
    root = _fixture(tmp_path, (
        "The estimator is consistent under Assumption 3 and never derived from "
        "the working directory.\n"
    ))
    errors = _module().check(root, root / "rules.md")
    assert len(errors) == 1
    assert "has drifted" in errors[0]


def test_a_glob_matching_nothing_is_an_error(tmp_path: Path) -> None:
    canonical = CANONICAL.replace("mirrors=mirrors/*.md", "mirrors=typo/*.md")
    root = _fixture(tmp_path, "irrelevant\n", canonical)
    errors = _module().check(root, root / "rules.md")
    assert any("matches no file" in error for error in errors)


def test_a_block_missing_from_the_index_is_an_error(tmp_path: Path) -> None:
    canonical = CANONICAL.replace("| `R-TEST-1` | a pinned sentence |\n", "")
    root = _fixture(tmp_path, "irrelevant\n", canonical)
    errors = _module().check(root, root / "rules.md")
    assert any("no row in the rule index" in error for error in errors)


def test_a_block_with_no_fragments_cannot_pass_vacuously(tmp_path: Path) -> None:
    canonical = CANONICAL.replace(
        "> The estimator is consistent under Assumption 2 and never derived from the\n"
        "> working directory.\n", "")
    root = _fixture(tmp_path, "irrelevant\n", canonical)
    errors = _module().check(root, root / "rules.md")
    assert any("declares no `> ` fragments" in error for error in errors)


def test_ci_match_tolerates_a_sentence_initial_anchor(tmp_path: Path) -> None:
    canonical = CANONICAL.replace(
        "mirrors=mirrors/*.md -->", "mirrors=mirrors/*.md match=ci -->").replace(
        "> The estimator is consistent under Assumption 2 and never derived from the\n"
        "> working directory.\n", "> alarm evidence\n")
    root = _fixture(tmp_path, "**Alarm evidence only**: a corpus hit motivates a query.\n",
                    canonical)
    assert _module().check(root, root / "rules.md") == []
