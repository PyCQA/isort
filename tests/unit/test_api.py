"""Tests the isort API module"""
import os
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from isort import ImportKey, api
from isort.settings import Config

imperfect_content = "import b\nimport a\n"
fixed_content = "import a\nimport b\n"
fixed_diff = "+import a\n import b\n-import a\n"


@pytest.fixture
def imperfect(tmpdir) -> None:
    imperfect_file = tmpdir.join("test_needs_changes.py")
    imperfect_file.write_text(imperfect_content, "utf8")
    return imperfect_file


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


def test_sort_file_in_place(imperfect) -> None:
    assert api.sort_file(imperfect, overwrite_in_place=True)
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


def test_find_imports_in_file(imperfect):
    found_imports = list(api.find_imports_in_file(imperfect))
    assert "b" in [found_import.module for found_import in found_imports]


def test_find_imports_in_code():
    code = """
from x.y import z as a
from x.y import z as a
from x.y import z
import x.y
import x
"""
    assert len(list(api.find_imports_in_code(code))) == 5
    assert len(list(api.find_imports_in_code(code, unique=True))) == 4
    assert len(list(api.find_imports_in_code(code, unique=ImportKey.ATTRIBUTE))) == 3
    assert len(list(api.find_imports_in_code(code, unique=ImportKey.MODULE))) == 2
    assert len(list(api.find_imports_in_code(code, unique=ImportKey.PACKAGE))) == 1
