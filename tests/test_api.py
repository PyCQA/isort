"""Tests the isort API module"""
import pytest

from isort import api, exceptions


def test_sort_file_invalid_syntax(tmpdir) -> None:
    """Test to ensure file encoding is respected"""
    tmp_file = tmpdir.join(f"test_bad_syntax.py")
    tmp_file.write_text("""print('mismathing quotes")""", "utf8")
    with pytest.warns(UserWarning):
        api.sort_file(tmp_file, atomic=True)


def test_check_file(tmpdir) -> None:
    perfect = tmpdir.join(f"test_no_changes.py")
    perfect.write_text("import a\nimport b\n", "utf8")
    assert api.check_file(perfect, show_diff=True)
    
    imperfect = tmpdir.join(f"test_needs_changes.py")
    imperfect.write_text("import b\nimport a\n", "utf8")
    assert not api.check_file(imperfect, show_diff=True)
