"""Tests the isort API module"""
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from isort import api
from isort.settings import Config


def test_sort_file(tmpdir) -> None:
    tmp_file = tmpdir.join("test_bad_syntax.py")
    tmp_file.write_text("""print('mismathing quotes")""", "utf8")
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True)
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True, write_to_stdout=True)

    imperfect = tmpdir.join("test_needs_changes.py")
    imperfect.write_text("import b\nimport a\n", "utf8")
    api.sort_file(imperfect, write_to_stdout=True, show_diff=True)

    # First show diff, but ensure change wont get written by asking to apply
    # and ensuring answer is no.
    with patch("isort.format.input", MagicMock(return_value="n")):
        api.sort_file(imperfect, show_diff=True, ask_to_apply=True)

    # Then run again, but apply the change without asking
    api.sort_file(imperfect, show_diff=True)


def test_check_file(tmpdir) -> None:
    perfect = tmpdir.join("test_no_changes.py")
    perfect.write_text("import a\nimport b\n", "utf8")
    assert api.check_file(perfect, show_diff=True)

    imperfect = tmpdir.join("test_needs_changes.py")
    imperfect.write_text("import b\nimport a\n", "utf8")
    assert not api.check_file(imperfect, show_diff=True)


def test_sorted_imports_multiple_configs() -> None:
    with pytest.raises(ValueError):
        api.sort_code_string("import os", config=Config(line_length=80), line_length=80)


def test_diff_stream() -> None:
    output = StringIO()
    assert api.sort_stream(StringIO("import b\nimport a\n"), output, show_diff=True)
    output.seek(0)
    assert "import a\n import b\n" in output.read()


def test_sort_code_string_mixed_newlines():
    assert api.sort_code_string("import A\n\r\nimportA\n\n") == "import A\r\n\r\nimportA\r\n\n"
