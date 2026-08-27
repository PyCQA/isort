"""Basic set of tests to ensure entire code base is importable"""

# ruff: noqa: PLC0415

import subprocess
import sys
from contextlib import suppress
from pathlib import Path


def test_importable():
    """Simple smoketest to ensure all isort modules are importable"""

    import isort
    import isort._version
    import isort.api
    import isort.comments
    import isort.exceptions
    import isort.format
    import isort.hooks
    import isort.logo
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

    # Ensure predictable test failure regardless of the ambient pytest argv causing a `SystemExit`
    # in isort.__main__ when it tries to parse the pytest argv.
    with suppress(SystemExit):
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
