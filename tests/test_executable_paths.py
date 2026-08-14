from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SKILLS = (
    "algo-brainstorm",
    "literature-explorer",
    "paper-writer",
    "peer-reviewer",
    "research-conductor",
)


def _runtime_docs() -> list[Path]:
    docs = [ROOT / "README.md", *sorted((ROOT / "commands").glob("*.md"))]
    for skill in WORKFLOW_SKILLS:
        docs.extend(sorted((ROOT / "skills" / skill).rglob("*.md")))
    docs.extend(
        path
        for path in sorted((ROOT / "shared" / "prompts").glob("*.md"))
        if path.name not in {"evidence_grounding.md", "research_lifecycle.md"}
    )
    return docs


def test_direct_entrypoints_define_plugin_root_contract() -> None:
    entrypoints = [
        *sorted((ROOT / "commands").glob("*.md")),
        *(ROOT / "skills" / skill / "SKILL.md" for skill in WORKFLOW_SKILLS),
    ]
    assert len(entrypoints) == 10
    for path in entrypoints:
        text = path.read_text(encoding="utf-8")
        assert "PLUGIN_ROOT" in text, path
        assert "working directory" in text, path


def test_documented_runners_are_cwd_independent() -> None:
    bare_python = re.compile(r"\bpython3?\s+[\"']?(?:shared|skills|scripts)/")
    bare_uv = re.compile(
        r"\buv\s+run(?:\s+--extra\s+\S+)?\s+python\s+"
        r"[\"']?(?:shared|skills|scripts)/"
    )
    for path in _runtime_docs():
        text = path.read_text(encoding="utf-8")
        assert not bare_python.search(text), path
        assert not bare_uv.search(text), path
        assert 'cd "$PLUGIN_ROOT"' not in text, path
        assert not re.search(r"\buv(?:\s+run)?\s+--directory\b", text), path
        for match in re.finditer(r"\buv\s+run\b", text):
            assert '--project "$PLUGIN_ROOT"' in text[match.start() : match.start() + 180], path


@pytest.mark.parametrize(
    "relative",
    (
        "shared/council.py",
        "scripts/check_host_parity.py",
        "skills/literature-explorer/scripts/dedupe_rank.py",
        "skills/paper-writer/scripts/check_tex.py",
        "skills/paper-writer/scripts/check_prose.py",
        "skills/paper-writer/scripts/check_venues.py",
        "skills/peer-reviewer/scripts/scan_injection.py",
    ),
)
def test_stdlib_entrypoints_load_from_unrelated_cwd(
    relative: str, tmp_path: Path
) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / relative), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_CACHE_DIR": str(tmp_path / "uv-cache")},
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "relative",
    (
        "skills/literature-explorer/scripts/search_arxiv.py",
        "skills/literature-explorer/scripts/search_semantic_scholar.py",
        "skills/literature-explorer/scripts/search_openalex.py",
        "skills/literature-explorer/scripts/search_openreview.py",
        "skills/paper-writer/scripts/verify_citations.py",
    ),
)
def test_dependency_entrypoints_load_with_plugin_project_from_unrelated_cwd(
    relative: str, tmp_path: Path
) -> None:
    uv = shutil.which("uv")
    assert uv is not None
    result = subprocess.run(
        [
            uv,
            "run",
            "--project",
            str(ROOT),
            "--no-sync",
            "python",
            str(ROOT / relative),
            "--help",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_CACHE_DIR": str(tmp_path / "uv-cache")},
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_uv_project_selection_preserves_user_project_cwd(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    assert uv is not None
    result = subprocess.run(
        [
            uv,
            "run",
            "--project",
            str(ROOT),
            "--no-sync",
            "python",
            "-c",
            "import os; print(os.getcwd())",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "UV_CACHE_DIR": str(tmp_path / "uv-cache")},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert Path(result.stdout.strip()) == tmp_path


def test_shell_and_optional_executable_paths_exist_from_plugin_root(
    tmp_path: Path,
) -> None:
    build = ROOT / "skills/paper-writer/scripts/build_paper.sh"
    figures = ROOT / "skills/paper-writer/scripts/figs.py"
    assert build.is_file() and build.stat().st_mode & 0o111
    assert figures.is_file()
    result = subprocess.run(
        [str(build), "not-a-mode"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "usage:" in result.stderr
