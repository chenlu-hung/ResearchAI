"""Cover the mode-registry consistency check across its four declarations:
disk, the owning SKILL.md, routing.md, and the registry itself.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REGISTRY = """# Mode Registry

| Skill | Mode | File | Purpose | Lifecycle phase(s) owned |
|---|---|---|---|---|
| demo | `alpha` | `skills/demo/modes/alpha.md` | Do the thing | `drafting` |

## Skills with no modes

| Skill | Why | Entry files |
|---|---|---|
| `orchestrator` | Selects other skills' modes. | `routing.md` |
"""

SKILL_MD = """---
name: demo
---

## Modes

| Mode | Purpose | Mode file |
|---|---|---|
| `alpha` | Do the thing | `modes/alpha.md` |
"""

ROUTING_MD = "| alpha | `skills/demo/modes/alpha.md` |\n"


def _module():
    path = ROOT / "scripts" / "check_mode_registry.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture(tmp_path: Path) -> Path:
    (tmp_path / "shared").mkdir()
    (tmp_path / "shared" / "mode_registry.md").write_text(REGISTRY, encoding="utf-8")
    modes = tmp_path / "skills" / "demo" / "modes"
    modes.mkdir(parents=True)
    (modes / "alpha.md").write_text("alpha mode\n", encoding="utf-8")
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    conductor = tmp_path / "skills" / "research-conductor"
    conductor.mkdir(parents=True)
    (conductor / "routing.md").write_text(ROUTING_MD, encoding="utf-8")
    return tmp_path


def _check(root: Path) -> list[str]:
    return _module().check(root, root / "shared" / "mode_registry.md")


def test_repo_registry_is_consistent(run_script) -> None:
    result = run_script("scripts/check_mode_registry.py")
    assert result.returncode == 0, result.stdout
    assert "mode registry: PASS" in result.stdout


def test_consistent_fixture_passes(tmp_path: Path) -> None:
    assert _check(_fixture(tmp_path)) == []


def test_registry_row_pointing_at_a_missing_file_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "demo" / "modes" / "alpha.md").unlink()
    errors = _check(root)
    assert any("points at missing file" in error for error in errors)


def test_an_unregistered_mode_file_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "demo" / "modes" / "beta.md").write_text("beta\n", encoding="utf-8")
    errors = _check(root)
    assert any("has no registry row" in error for error in errors)


def test_a_mode_missing_from_its_skill_table_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "demo" / "SKILL.md").write_text(
        SKILL_MD.replace("| `alpha` | Do the thing | `modes/alpha.md` |",
                         "| `gamma` | Something else | `modes/gamma.md` |"),
        encoding="utf-8")
    errors = _check(root)
    assert any("absent from the registry" in error for error in errors)
    assert any("absent from that skill's `## Modes` table" in error for error in errors)


def test_routing_to_an_unregistered_mode_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "research-conductor" / "routing.md").write_text(
        ROUTING_MD + "| delta | `skills/demo/modes/delta.md` |\n", encoding="utf-8")
    errors = _check(root)
    assert any("routing.md routes to" in error for error in errors)


def test_routing_brace_expansion_is_understood(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "research-conductor" / "routing.md").write_text(
        "`skills/demo/modes/{alpha,epsilon}.md`\n", encoding="utf-8")
    errors = _check(root)
    assert any("skills/demo/modes/epsilon.md" in error for error in errors)
    assert not any("skills/demo/modes/alpha.md" in error for error in errors)


def test_a_modeless_skill_shipping_modes_fails(tmp_path: Path) -> None:
    root = _fixture(tmp_path)
    (root / "skills" / "orchestrator" / "modes").mkdir(parents=True)
    errors = _check(root)
    assert any("registered as mode-less but ships a modes/ directory" in error
               for error in errors)
