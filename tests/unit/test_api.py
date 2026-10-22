"""Tests the isort API module"""

import os
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from isort import ImportKey, api
from isort.settings import Config

imperfect_content = "import b\nimport a\n"
fixed_content = "import a\nimport b\n"
fixed_diff = "+import a\n import b\n-import a\n"


@pytest.fixture
def imperfect(tmp_path: Path) -> Path:
    imperfect_file = tmp_path / "test_needs_changes.py"
    imperfect_file.write_text(imperfect_content, "utf8")
    return imperfect_file


def test_sort_file_with_bad_syntax(tmp_path: Path) -> None:
    tmp_file = tmp_path / "test_bad_syntax.py"
    tmp_file.write_text("""print('mismatching quotes")""", "utf8")
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True)
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True, write_to_stdout=True)


def test_sort_file(imperfect: Path) -> None:
    assert api.sort_file(imperfect)
    assert imperfect.read_text() == fixed_content


def test_sort_file_in_place(imperfect: Path) -> None:
    assert api.sort_file(imperfect, overwrite_in_place=True)
    assert imperfect.read_text() == fixed_content


@pytest.mark.parametrize("line_ending", ["\n", "\r\n"])
def test_sort_file_in_place_keeps_line_endings(tmp_path: Path, line_ending: str) -> None:
    tmp_file = tmp_path / "test_needs_changes.py"
    tmp_file.write_bytes(imperfect_content.replace("\n", line_ending).encode())
    assert api.sort_file(tmp_file, overwrite_in_place=True)
    assert tmp_file.read_bytes() == fixed_content.replace("\n", line_ending).encode()


@pytest.mark.parametrize(
    ("header", "encoding"), [("# coding: latin-1\n", "latin-1"), ("\ufeff", "utf-8")]
)
def test_sort_file_in_place_keeps_encoding(tmp_path: Path, header: str, encoding: str) -> None:
    tmp_file = tmp_path / "test_needs_changes.py"
    tmp_file.write_bytes(f'{header}{imperfect_content}\ns = "ã"\n'.encode(encoding))
    assert api.sort_file(tmp_file, overwrite_in_place=True)
    assert tmp_file.read_bytes() == f'{header}{fixed_content}\ns = "ã"\n'.encode(encoding)


def test_sort_file_in_place_keeps_file_on_encoding_error(tmp_path: Path) -> None:
    tmp_file = tmp_path / "test_needs_changes.py"
    content = b"# coding: ascii\n" + imperfect_content.encode()
    tmp_file.write_bytes(content)
    with pytest.raises(UnicodeEncodeError):
        api.sort_file(
            tmp_file, overwrite_in_place=True, import_heading_thirdparty="Bibliothèques tierces"
        )
    assert tmp_file.read_bytes() == content


def test_sort_file_to_stdout(capsys: pytest.CaptureFixture[str], imperfect: Path) -> None:
    assert api.sort_file(imperfect, write_to_stdout=True)
    out, _ = capsys.readouterr()
    assert out == fixed_content.replace("\n", os.linesep)


def test_other_ask_to_apply(imperfect: Path) -> None:
    # First show diff, but ensure change won't get written by asking to apply
    # and ensuring answer is no.
    with patch("builtins.input", MagicMock(return_value="n")):
        assert not api.sort_file(imperfect, ask_to_apply=True)
        assert imperfect.read_text() == imperfect_content

    # Then run again, but apply the change (answer is yes)
    with patch("builtins.input", MagicMock(return_value="y")):
        assert api.sort_file(imperfect, ask_to_apply=True)
        assert imperfect.read_text() == fixed_content


def test_check_file_no_changes(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    perfect = tmp_path / "test_no_changes.py"
    perfect.write_text("import a\nimport b\n", "utf8")
    assert api.check_file(perfect, show_diff=True)
    out, _ = capsys.readouterr()
    assert not out


def test_check_file_with_changes(capsys: pytest.CaptureFixture[str], imperfect: Path) -> None:
    assert not api.check_file(imperfect, show_diff=True)
    out, _ = capsys.readouterr()
    assert fixed_diff.replace("\n", os.linesep) in out


def test_sorted_imports_multiple_configs() -> None:
    with pytest.raises(ValueError, match="You can either specify custom configuration options"):
        api.sort_code_string("import os", config=Config(line_length=80), line_length=80)


def test_diff_stream() -> None:
    output = StringIO()
    assert api.sort_stream(StringIO("import b\nimport a\n"), output, show_diff=True)
    output.seek(0)
    assert fixed_diff in output.read()


def test_sort_code_string_mixed_newlines() -> None:
    assert api.sort_code_string("import A\n\r\nimportA\n\n") == "import A\r\n\r\nimportA\r\n\n"


def test_find_imports_in_file(imperfect: Path) -> None:
    found_imports = list(api.find_imports_in_file(imperfect))
    assert "b" in [found_import.module for found_import in found_imports]


def test_find_imports_in_file_error(tmp_path: Path) -> None:
    test_path = tmp_path / "test_path.py"
    test_path.mkdir()
    with pytest.warns(UserWarning):
        assert not list(api.find_imports_in_file(test_path))


def test_find_imports_in_code() -> None:
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


@pytest.mark.parametrize("extension", ["pyx", "pxd"])
@pytest.mark.parametrize("atomic", [False, True])
def test_atomic_cython_write_only_output(tmp_path: Path, extension: str, atomic: bool) -> None:
    source = "cimport zlib\ncimport cython\n\ncdef int value\n"
    target = tmp_path / f"sorted.{extension}"

    with target.open("w", encoding="utf-8") as output:
        assert api.sort_stream(StringIO(source), output, extension=extension, atomic=atomic)

    assert (
        target.read_text(encoding="utf-8") == "cimport zlib\n\ncimport cython\n\n\ncdef int value\n"
    )
