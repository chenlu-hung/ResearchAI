"""Cover the governance-doc reference check: dead paths fail, templates and
deliberately absent paths do not.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _module():
    path = ROOT / "scripts" / "check_doc_refs.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repo_governance_docs_resolve(run_script) -> None:
    result = run_script("scripts/check_doc_refs.py")
    assert result.returncode == 0, result.stdout
    assert "doc refs: PASS" in result.stdout


def test_real_paths_are_collected() -> None:
    found = _module().candidates("see `shared/firm_rules.md` and `scripts/eval_pack.py`")
    assert found == {"shared/firm_rules.md", "scripts/eval_pack.py"}


def test_templates_globs_and_directories_are_skipped() -> None:
    text = (
        "`docs/corpus-manifest-<slug>.md` `commands/*.md` `shared/...` "
        "`.claude/skills/` `evals/cases/` `refs/topic.bib` `SKILL.md` "
        '`python3 "$PLUGIN_ROOT/<path>"`'
    )
    assert _module().candidates(text) == set()


def test_a_dead_reference_fails(tmp_path: Path) -> None:
    doc = tmp_path / "GOVERNANCE.md"
    doc.write_text("enforced in `scripts/does_not_exist.py`\n", encoding="utf-8")
    errors = _module().check(tmp_path, ["GOVERNANCE.md"])
    assert len(errors) == 1
    assert "does not exist" in errors[0]


def test_a_missing_governance_doc_fails(tmp_path: Path) -> None:
    errors = _module().check(tmp_path, ["ABSENT.md"])
    assert any("does not exist" in error for error in errors)
