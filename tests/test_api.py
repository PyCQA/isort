"""Tests the isort API module"""
import pytest

from isort import api, exceptions


def test_sort_file_invalid_syntax(tmpdir) -> None:
    """Test to ensure file encoding is respected"""
    tmp_file = tmpdir.join(f"test_bad_syntax.py")
    tmp_file.write_text("""print('mismathing quotes")""", "utf8")
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True)
