"""A growing set of tests designed to ensure when isort implements a feature described in a ticket
it fully works as defined in the associated ticket.
"""
import isort


def test_semicolon_ignored_for_dynamic_lines_after_import_issue_1178():
    """Test to ensure even if a semicolon is in the decorator in the line following an import
    the correct line spacing detrmination will be made.
    See: https://github.com/timothycrosley/isort/issues/1178.
    """
    assert isort.check_code(
        """
import pytest


@pytest.mark.skip(';')
def test_thing(): pass
""",
        show_diff=True,
    )


def test_isort_automatically_removes_duplicate_aliases_issue_1193():
    """Test to ensure isort can automatically remove duplicate aliases.
    See: https://github.com/timothycrosley/isort/issues/1281
    """
    assert isort.check_code("from urllib import parse as parse\n", show_diff=True)
    assert (
        isort.code("from urllib import parse as parse", remove_redundant_aliases=True)
        == "from urllib import parse\n"
    )
    assert isort.check_code("import os as os\n", show_diff=True)
    assert isort.code("import os as os", remove_redundant_aliases=True) == "import os\n"
