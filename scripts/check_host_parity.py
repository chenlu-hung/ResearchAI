#!/usr/bin/env python3
"""Validate that the Codex and Claude Code plugin wrappers expose one core."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path


REQUIRED_SHARED_SKILLS = {
    "algo-brainstorm",
    "evidence-store",
    "literature-explorer",
    "paper-writer",
    "peer-reviewer",
    "research-conductor",
}

WORKFLOW_SKILLS = REQUIRED_SHARED_SKILLS - {"evidence-store"}
CLAUDE_COMMANDS = {"algo", "explore", "research", "review", "write"}
CODEX_SKILL_INVOCATIONS = {
    "algo-brainstorm",
    "evidence-store",
    "literature-explorer",
    "paper-writer",
    "peer-reviewer",
    "research-conductor",
}
ROOT_CONTRACT_MARKERS = (
    "PLUGIN_ROOT",
    "working directory",
)
BARE_CLAUDE_COMMAND = re.compile(
    r"(?<![A-Za-z0-9_-])/(research|explore|algo|write|review)(?=[\s`<]|$)"
)
UNSAFE_BARE_PYTHON = re.compile(
    r"\bpython3?\s+[\"']?(?:shared|skills|scripts)/",
    re.MULTILINE,
)
UNSAFE_BARE_UV = re.compile(
    r"\buv\s+run(?:\s+--extra\s+\S+)?\s+python\s+"
    r"[\"']?(?:shared|skills|scripts)/",
    re.MULTILINE,
)


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc


def _base_version(version: object) -> str:
    if not isinstance(version, str) or not version:
        return ""
    return version.split("+", 1)[0]


def _runtime_markdown(root: Path) -> list[Path]:
    docs = [root / "README.md"]
    docs.extend(sorted((root / "commands").glob("*.md")))
    for skill_name in sorted(WORKFLOW_SKILLS):
        docs.extend(sorted((root / "skills" / skill_name).rglob("*.md")))
    prompts = root / "shared" / "prompts"
    if prompts.is_dir():
        docs.extend(sorted(prompts.glob("*.md")))
    return docs


def _validate_documented_usage(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / "README.md"
    if not readme_path.is_file():
        return ["missing README.md"]
    readme = readme_path.read_text(encoding="utf-8")

    bare = sorted({match.group(0) for match in BARE_CLAUDE_COMMAND.finditer(readme)})
    if bare:
        errors.append(
            "README advertises unnamespaced Claude commands: " + ", ".join(bare)
        )
    for command in sorted(CLAUDE_COMMANDS):
        invocation = f"/research-assistant:{command}"
        if invocation not in readme:
            errors.append(f"README is missing Claude invocation {invocation}")
    for skill_name in sorted(CODEX_SKILL_INVOCATIONS):
        invocation = f"$research-ai:{skill_name}"
        if invocation not in readme:
            errors.append(f"README is missing Codex invocation {invocation}")
    if "Codex does not load `commands/`" not in readme:
        errors.append("README must state that Codex does not load commands/")
    if "/Users/" in readme or "/home/" in readme:
        errors.append("README must not hard-code a developer machine path")
    if "create_basic_plugin.py" not in readme or "--with-marketplace" not in readme:
        errors.append("README must document the plugin-creator personal-marketplace flow")
    if "rsync -az" not in readme:
        errors.append("README must document the non-destructive canonical checkout sync")
    if re.search(r"\brsync\b[^\n]*--delete", readme):
        errors.append("README install sync must not delete deployment files by default")

    commands_dir = root / "commands"
    command_names = (
        {path.stem for path in commands_dir.glob("*.md")}
        if commands_dir.is_dir()
        else set()
    )
    if command_names != CLAUDE_COMMANDS:
        errors.append(
            "Claude command wrappers differ: expected "
            f"{sorted(CLAUDE_COMMANDS)}, found {sorted(command_names)}"
        )
    for command in sorted(CLAUDE_COMMANDS & command_names):
        text = (commands_dir / f"{command}.md").read_text(encoding="utf-8")
        if any(marker not in text for marker in ROOT_CONTRACT_MARKERS):
            errors.append(f"commands/{command}.md is missing the plugin-root contract")

    for skill_name in sorted(WORKFLOW_SKILLS):
        path = root / "skills" / skill_name / "SKILL.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if any(marker not in text for marker in ROOT_CONTRACT_MARKERS):
            errors.append(f"skills/{skill_name}/SKILL.md is missing the plugin-root contract")

    for path in _runtime_markdown(root):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        if UNSAFE_BARE_PYTHON.search(text):
            errors.append(f"{relative} contains a cwd-relative Python script invocation")
        if UNSAFE_BARE_UV.search(text):
            errors.append(f"{relative} contains a cwd-relative uv script invocation")
        if 'cd "$PLUGIN_ROOT"' in text or "uv --directory" in text:
            errors.append(f"{relative} changes cwd instead of selecting the plugin project")
        for match in re.finditer(r"\buv\s+run\b", text):
            command_window = text[match.start() : match.start() + 180]
            if '--project "$PLUGIN_ROOT"' not in command_window:
                errors.append(
                    f"{relative} contains uv run without --project \"$PLUGIN_ROOT\""
                )
                break
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for host_specific in (root / ".claude" / "skills", root / ".codex" / "skills"):
        if host_specific.exists():
            errors.append(
                f"host-specific skill tree {host_specific.relative_to(root)} would fork the core"
            )
    codex_path = root / ".codex-plugin" / "plugin.json"
    claude_path = root / ".claude-plugin" / "plugin.json"
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    project_path = root / "pyproject.toml"

    for path in (codex_path, claude_path, marketplace_path, project_path):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(root)}")
    if errors:
        return errors

    try:
        codex = _read_json(codex_path)
        claude = _read_json(claude_path)
        marketplace = _read_json(marketplace_path)
        project = tomllib.loads(project_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"cannot read valid TOML from {project_path}: {exc}"]

    if codex.get("name") != "research-ai":
        errors.append("Codex manifest name must be research-ai")
    if claude.get("name") != "research-assistant":
        errors.append("Claude manifest name must be research-assistant")

    codex_version = _base_version(codex.get("version"))
    claude_version = _base_version(claude.get("version"))
    if not codex_version or codex_version != claude_version:
        errors.append(
            f"host base versions differ: Codex={codex.get('version')!r}, "
            f"Claude={claude.get('version')!r}"
        )
    project_version = _base_version(project.get("project", {}).get("version"))
    if project_version != claude_version:
        errors.append(
            f"package and host base versions differ: package={project_version!r}, "
            f"hosts={claude_version!r}"
        )

    entries = marketplace.get("plugins")
    entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
    if not isinstance(entry, dict):
        errors.append("Claude marketplace must contain exactly one plugin entry")
    else:
        if entry.get("name") != claude.get("name"):
            errors.append("Claude marketplace and manifest names differ")
        if _base_version(entry.get("version")) != claude_version:
            errors.append("Claude marketplace and manifest versions differ")
        if entry.get("source") != "./":
            errors.append("Claude marketplace source must remain ./")

    skills_dir = root / "skills"
    skills = sorted(path.name for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())
    missing_skills = sorted(REQUIRED_SHARED_SKILLS - set(skills))
    if missing_skills:
        errors.append(f"shared skills/ is missing: {', '.join(missing_skills)}")
    errors.extend(_validate_documented_usage(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    count = sum(1 for path in (root / "skills").iterdir() if (path / "SKILL.md").is_file())
    print(f"host parity: PASS (Codex + Claude Code, {count} shared skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
