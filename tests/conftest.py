import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def run_script():
    """Run a repo script by relative path; returns CompletedProcess."""

    def _run(rel_path: str, *args: str, cwd: Path | None = None):
        return subprocess.run(
            [sys.executable, str(REPO / rel_path), *args],
            capture_output=True,
            text=True,
            cwd=cwd or REPO,
        )

    return _run
