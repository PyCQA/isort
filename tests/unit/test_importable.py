"""Basic set of tests to ensure entire code base is importable"""

# ruff: noqa: PLC0415

import subprocess
import sys
from pathlib import Path

import pytest


def test_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simple smoketest to ensure all isort modules are importable"""

    import isort
    import isort._version
    import isort.api
    import isort.comments
    import isort.exceptions
    import isort.format
    import isort.hooks
    import isort.main
    import isort.output
    import isort.parse
    import isort.place
    import isort.profiles
    import isort.sections
    import isort.settings
    import isort.sorting
    import isort.stdlibs
    import isort.stdlibs.all
    import isort.stdlibs.py2
    import isort.stdlibs.py3
    import isort.stdlibs.py27
    import isort.stdlibs.py36
    import isort.stdlibs.py37
    import isort.stdlibs.py38
    import isort.stdlibs.py39
    import isort.stdlibs.py310
    import isort.stdlibs.py311
    import isort.stdlibs.py312
    import isort.stdlibs.py313
    import isort.stdlibs.py314
    import isort.stdlibs.py315
    import isort.utils
    import isort.wrap
    import isort.wrap_modes

    # `isort.__main__` runs isort with `sys.argv`. With pytest's argv it would sort any files and
    # directories passed to pytest in place, while without arguments it only prints a guide.
    monkeypatch.setattr(sys, "argv", ["isort"])
    import isort.__main__  # noqa: F401


def test_module_cli_invocation_works(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.py"
    file_path.write_text("import os\nimport sys\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "isort", str(file_path), "--check-only"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
