"""Tests the isort API module"""
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from isort import api
from isort.api import detect_newline
from isort.settings import Config

imperfect_content = "import b\nimport a\n"
fixed_content = "import a\nimport b\n"
fixed_diff = "+import a\n import b\n-import a\n"


@pytest.fixture
def imperfect(tmpdir) -> Path:
    imperfect_file = tmpdir.join("test_needs_changes.py")
    with open(imperfect_file, mode="w", encoding="utf-8", newline=os.linesep) as f:
        f.write(imperfect_content)
    return imperfect_file


def test_detect_newline():
    lf: str = "a\nb"
    crlf: str = "a\r\nb"
    cr: str = "a\rb"
    empty: str = ""

    assert "\n" == detect_newline(lf)
    assert "\r\n" == detect_newline(crlf)
    assert "\r" == detect_newline(cr)
    assert "\n" == detect_newline(empty)


def test_sort_file_with_bad_syntax(tmpdir) -> None:
    tmp_file = tmpdir.join("test_bad_syntax.py")
    tmp_file.write_text("""print('mismatching quotes")""", "utf8")
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True)
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True, write_to_stdout=True)


def test_sort_file(imperfect) -> None:
    assert api.sort_file(imperfect)
    assert imperfect.read() == fixed_content


def test_sort_file_to_stdout(capsys, imperfect) -> None:
    assert api.sort_file(imperfect, write_to_stdout=True)
    out, _ = capsys.readouterr()
    assert out == fixed_content.replace("\n", os.linesep)


def test_other_ask_to_apply(imperfect) -> None:
    # First show diff, but ensure change wont get written by asking to apply
    # and ensuring answer is no.
    with patch("isort.format.input", MagicMock(return_value="n")):
        assert not api.sort_file(imperfect, ask_to_apply=True)
        assert imperfect.read() == imperfect_content

    # Then run again, but apply the change (answer is yes)
    with patch("isort.format.input", MagicMock(return_value="y")):
        assert api.sort_file(imperfect, ask_to_apply=True)
        assert imperfect.read() == fixed_content


def test_check_file_no_changes(capsys, tmpdir) -> None:
    perfect = tmpdir.join("test_no_changes.py")
    perfect.write_text("import a\nimport b\n", "utf8")
    assert api.check_file(perfect, show_diff=True)
    out, _ = capsys.readouterr()
    assert not out


def test_check_file_with_changes(capsys, imperfect) -> None:
    assert not api.check_file(imperfect, show_diff=True)
    out, _ = capsys.readouterr()
    assert fixed_diff.replace("\n", os.linesep) in out


def test_sorted_imports_multiple_configs() -> None:
    with pytest.raises(ValueError):
        api.sort_code_string("import os", config=Config(line_length=80), line_length=80)


def test_diff_stream() -> None:
    output = StringIO()
    assert api.sort_stream(StringIO("import b\nimport a\n"), output, show_diff=True)
    output.seek(0)
    assert fixed_diff in output.read()


def test_sort_code_string_mixed_newlines():
    assert api.sort_code_string("import A\n\r\nimportA\n\n") == "import A\r\n\r\nimportA\r\n\n"


def test_get_import_file(imperfect, capsys):
    api.get_imports_file(imperfect, sys.stdout)
    out, _ = capsys.readouterr()
    assert out == imperfect_content.replace("\n", os.linesep)
