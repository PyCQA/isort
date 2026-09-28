from pathlib import Path

from isort import files
from isort.settings import DEFAULT_CONFIG


def test_find(tmp_path: Path) -> None:
    tmp_file = tmp_path / "file.py"
    tmp_file.write_text("import os, sys\n")
    assert tuple(files.find((tmp_file,), DEFAULT_CONFIG, [], [])) == (tmp_file,)
