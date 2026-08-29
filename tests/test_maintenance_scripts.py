"""Cover the repo-maintenance checks: the ratchet, the cadence, the freshness
wrapper, and the inventory generator they all read.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INVENTORY_HEADER = (
    "| Surface | Name | Path | Lines | Last touched | Age (d) | Verdict | Rationale |"
)


def _load(relative: str):
    """Import a repo script as a module (they are stdlib-only and side-effect free)."""
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _audits_with(tmp_path: Path, name: str, body: str = "body\n") -> Path:
    audits = tmp_path / "audits"
    audits.mkdir(exist_ok=True)
    (audits / name).write_text(body, encoding="utf-8")
    return audits


# --- test-count ratchet ---------------------------------------------------


def test_ratchet_flags_a_dropped_test(tmp_path: Path, run_script) -> None:
    baseline = tmp_path / "baseline_count.txt"
    baseline.write_text("100000\n", encoding="utf-8")
    result = run_script("scripts/check_test_count.py", "--baseline", str(baseline))
    assert result.returncode == 1, result.stdout
    assert "disappeared" in result.stdout


def test_ratchet_demands_the_baseline_advance(tmp_path: Path, run_script) -> None:
    baseline = tmp_path / "baseline_count.txt"
    baseline.write_text("1\n", encoding="utf-8")
    result = run_script("scripts/check_test_count.py", "--baseline", str(baseline))
    assert result.returncode == 1, result.stdout
    assert "advance the ratchet" in result.stdout


def test_ratchet_rejects_a_missing_baseline(tmp_path: Path, run_script) -> None:
    result = run_script(
        "scripts/check_test_count.py", "--baseline", str(tmp_path / "absent.txt")
    )
    assert result.returncode == 1, result.stdout
    assert "no usable baseline" in result.stdout


def test_ratchet_update_then_check_agrees(tmp_path: Path, run_script) -> None:
    baseline = tmp_path / "baseline_count.txt"
    written = run_script(
        "scripts/check_test_count.py", "--baseline", str(baseline), "--update"
    )
    assert written.returncode == 0, written.stdout
    result = run_script("scripts/check_test_count.py", "--baseline", str(baseline))
    assert result.returncode == 0, result.stdout
    assert "test count: PASS" in result.stdout


def test_committed_baseline_matches_the_suite(run_script) -> None:
    result = run_script("scripts/check_test_count.py")
    assert result.returncode == 0, result.stdout


# --- audit cadence --------------------------------------------------------


def test_audit_due_requires_a_dated_audit(tmp_path: Path, run_script) -> None:
    audits = tmp_path / "audits"
    audits.mkdir()
    (audits / "README.md").write_text("not an audit\n", encoding="utf-8")
    (audits / "TEMPLATE-retirement-audit.md").write_text("nor this\n", encoding="utf-8")
    result = run_script("scripts/check_audit_due.py", "--audits-dir", str(audits))
    assert result.returncode == 1, result.stdout
    assert "no dated audit" in result.stdout


def test_audit_due_flags_an_overdue_review(tmp_path: Path, run_script) -> None:
    audits = _audits_with(tmp_path, "2026-01-01-retirement.md")
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 1, result.stdout
    assert "overdue" in result.stdout


def test_audit_due_passes_within_cadence(tmp_path: Path, run_script) -> None:
    audits = _audits_with(tmp_path, "2026-07-01-retirement.md")
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 0, result.stdout
    assert "audit cadence: PASS" in result.stdout


def test_audit_due_reads_the_newest_audit_not_the_first(tmp_path: Path, run_script) -> None:
    audits = _audits_with(tmp_path, "2026-01-01-retirement.md")
    (audits / "2026-07-01-retirement.md").write_text("body\n", encoding="utf-8")
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 0, result.stdout


def test_unreviewed_inventory_rows_keep_the_check_red(tmp_path: Path, run_script) -> None:
    table = "\n".join([
        INVENTORY_HEADER,
        "|---|---|---|---|---|---|---|---|",
        "| mode | a/b | `x.md` | 1 | 2026-08-01 | 22 | keep | still load-bearing |",
        "| mode | a/c | `y.md` | 1 | 2026-08-01 | 22 |  |  |",
        "",
    ])
    audits = _audits_with(tmp_path, "2026-08-01-gate-inventory.md", table)
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 1, result.stdout
    assert "1 inventory row(s) with no verdict" in result.stdout


def test_fully_ruled_inventory_passes(tmp_path: Path, run_script) -> None:
    table = "\n".join([
        INVENTORY_HEADER,
        "|---|---|---|---|---|---|---|---|",
        "| mode | a/b | `x.md` | 1 | 2026-08-01 | 22 | keep | still load-bearing |",
        "| mode | a/c | `y.md` | 1 | 2026-08-01 | 22 | retire | never fired |",
        "",
    ])
    audits = _audits_with(tmp_path, "2026-08-01-gate-inventory.md", table)
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 0, result.stdout


def test_prose_audit_has_no_rows_to_review(tmp_path: Path, run_script) -> None:
    audits = _audits_with(
        tmp_path, "2026-08-01-retirement.md",
        "# Audit\n\nProse only, no inventory table.\n",
    )
    result = run_script(
        "scripts/check_audit_due.py", "--audits-dir", str(audits),
        "--today", "2026-08-23", "--max-age-days", "120",
    )
    assert result.returncode == 0, result.stdout


# --- venue freshness ------------------------------------------------------


def test_stale_warning_shape_is_still_matched(run_script) -> None:
    """check_freshness.py keys off check_venues.py's warning wording rather than
    re-implementing the age check. If that wording drifts, freshness would go
    quietly green forever — this is the pin that stops it."""
    result = run_script(
        "skills/paper-writer/scripts/check_venues.py", "--json", "--max-age-days", "0"
    )
    report = json.loads(result.stdout)
    assert report["warnings"], "every venue should read as stale at max-age 0"
    stale_re = _load("scripts/check_freshness.py").STALE_RE
    assert any(stale_re.search(warning) for warning in report["warnings"])


def test_freshness_fails_when_provenance_ages_out(run_script) -> None:
    result = run_script("scripts/check_freshness.py", "--max-age-days", "0")
    assert result.returncode == 1, result.stdout
    assert "STALE:" in result.stdout
    assert "venue-calibration" in result.stdout


def test_freshness_passes_inside_the_window(run_script) -> None:
    result = run_script("scripts/check_freshness.py", "--max-age-days", "100000")
    assert result.returncode == 0, result.stdout
    assert "freshness: PASS" in result.stdout


# --- gate inventory -------------------------------------------------------


def test_gate_inventory_covers_every_surface(run_script) -> None:
    result = run_script("scripts/gate_inventory.py", "--today", "2026-08-23")
    assert result.returncode == 0, result.stdout
    assert INVENTORY_HEADER in result.stdout
    for surface in (
        "lifecycle-gate", "mode", "checklist",
        "prompt-contract", "executable-check", "venue-style",
    ):
        assert f"| {surface} |" in result.stdout, surface


def test_generated_inventory_is_unruled_and_parseable(tmp_path: Path, run_script) -> None:
    """Two couplings in one: the generator must never pre-fill a verdict, and the
    table it emits must be the table the cadence check knows how to read."""
    output = tmp_path / "inventory.md"
    result = run_script(
        "scripts/gate_inventory.py", "--output", str(output), "--today", "2026-08-23"
    )
    assert result.returncode == 0, result.stdout
    blank = _load("scripts/check_audit_due.py").unreviewed_rows(output)
    assert blank > 0
