from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_repository_host_wrappers_are_in_parity(tmp_path: Path, run_script) -> None:
    result = run_script("scripts/check_host_parity.py", cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "host parity: PASS" in result.stdout


def test_readme_splits_claude_commands_from_codex_skills() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for command in ("research", "explore", "algo", "write", "review"):
        assert f"/research-assistant:{command}" in readme
    for skill in (
        "research-conductor",
        "literature-explorer",
        "algo-brainstorm",
        "paper-writer",
        "peer-reviewer",
        "evidence-store",
    ):
        assert f"$research-ai:{skill}" in readme
    assert "Codex does not load `commands/`" in readme
    assert not re.search(
        r"(?<![A-Za-z0-9_-])/(research|explore|algo|write|review)(?=[\s`<]|$)",
        readme,
    )


def test_readme_codex_install_is_generic_and_non_destructive() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "create_basic_plugin.py" in readme
    assert "--with-marketplace" in readme
    assert "read_marketplace_name.py" in readme
    assert "codex plugin add research-ai@personal" in readme
    assert "rsync -az" in readme
    assert "--delete" not in readme
    assert "/Users/" not in readme
    assert "/home/" not in readme


def test_cachebuster_does_not_break_base_version_parity(tmp_path: Path, run_script) -> None:
    for relative in (
        Path(".codex-plugin/plugin.json"),
        Path(".claude-plugin/plugin.json"),
        Path(".claude-plugin/marketplace.json"),
        Path("pyproject.toml"),
        Path("README.md"),
    ):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copytree(ROOT / "commands", tmp_path / "commands")
    for skill_name in (
        "algo-brainstorm",
        "evidence-store",
        "literature-explorer",
        "paper-writer",
        "peer-reviewer",
        "research-conductor",
    ):
        skill = tmp_path / "skills" / skill_name / "SKILL.md"
        skill.parent.mkdir(parents=True)
        body = f"---\nname: {skill_name}\ndescription: dummy\n---\n"
        if skill_name != "evidence-store":
            body += "Resolve PLUGIN_ROOT from this file, never from the working directory.\n"
        skill.write_text(body, encoding="utf-8")

    manifest_path = tmp_path / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] += "+codex.local-test"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = run_script("scripts/check_host_parity.py", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_host_specific_skill_tree_is_rejected(tmp_path: Path, run_script) -> None:
    destination = tmp_path / ".claude" / "skills" / "forked" / "SKILL.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("---\nname: forked\ndescription: fork\n---\n", encoding="utf-8")

    result = run_script("scripts/check_host_parity.py", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr

    # The validator must reject an otherwise complete copy once a host-only
    # implementation tree appears. Reuse the real tree so this test remains
    # focused on the fork guard rather than fixture completeness.
    result = run_script("scripts/check_host_parity.py", str(tmp_path))
    assert result.returncode != 0
    assert "host-specific skill tree" in result.stdout
