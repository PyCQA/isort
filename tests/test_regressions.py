"""A growing set of tests designed to ensure isort doesn't have regressions in new versions"""
import isort


def test_isort_duplicating_comments_issue_1264():
    """Ensure isort doesn't duplicate comments when force_sort_within_sections is set to `True`
    as was the case in issue #1264: https://github.com/timothycrosley/isort/issues/1264
    """
    assert (
        isort.code(
            """
from homeassistant.util.logging import catch_log_exception

# Loading the config flow...
from . import config_flow
""",
            force_sort_within_sections=True,
        ).count("# Loading the config flow...")
        == 1
    )


def test_moving_comments_issue_726():
    test_input = (
        "from Blue import models as BlueModels\n"
        "# comment for PlaidModel\n"
        "from Plaid.models import PlaidModel\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input

    test_input = (
        "# comment for BlueModels\n"
        "from Blue import models as BlueModels\n"
        "# comment for PlaidModel\n"
        "# another comment for PlaidModel\n"
        "from Plaid.models import PlaidModel\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input


def test_blank_lined_removed_issue_1275():
    """Ensure isort doesn't accidentally remove blank lines after doc strings and before imports.
    See: https://github.com/timothycrosley/isort/issues/1275
    """
    assert (
        isort.code(
            '''"""
My docstring
"""

from b import thing
from a import other_thing
'''
        )
        == '''"""
My docstring
"""

from a import other_thing
from b import thing
'''
    )


def test_blank_lined_removed_issue_1283():
    """Ensure isort doesn't accidentally remove blank lines after __version__ identifiers.
    See: https://github.com/timothycrosley/isort/issues/1283
    """
    test_input = """__version__ = "0.58.1"

from starlette import status
"""
    assert isort.code(test_input) == test_input


def test_extra_blank_line_added_nested_imports_issue_1290():
    """Ensure isort doesn't added unecessary blank lines above nested imports.
    See: https://github.com/timothycrosley/isort/issues/1290
    """
    test_input = '''from typing import TYPE_CHECKING

# Special imports
from special import thing

if TYPE_CHECKING:
    # Special imports
    from special import another_thing


def func():
    """Docstring"""

    # Special imports
    from special import something_else
    return
'''
    assert (
        isort.code(
            test_input,
            import_heading_special="Special imports",
            known_special=["special"],
            sections=["FUTURE", "STDLIB", "THIRDPARTY", "SPECIAL", "FIRSTPARTY", "LOCALFOLDER"],
        )
        == test_input
    )


def test_add_imports_shouldnt_make_isort_unusable_issue_1297():
    """Test to ensure add imports doesn't cause any unexpected behaviour when combined with check
    See: https://github.com/timothycrosley/isort/issues/1297
    """
    assert isort.check_code(
        """from __future__ import unicode_literals

from os import path
""",
        add_imports={"from __future__ import unicode_literals"},
    )


def test_no_extra_lines_for_imports_in_functions_issue_1277():
    """Test to ensure isort doesn't introduce extra blank lines for imports within function.
    See: https://github.com/timothycrosley/isort/issues/1277
    """
    test_input = """
def main():
    import time

    import sys
"""
    expected_output = """
def main():
    import sys
    import time
"""
    assert isort.code(isort.code(isort.code(test_input))) == expected_output


def test_no_extra_blank_lines_in_methods_issue_1293():
    """Test to ensure isort isn't introducing extra lines in methods that contain imports
    See: https://github.com/timothycrosley/isort/issues/1293
    """
    test_input = """

class Something(object):
    def on_email_deleted(self, email):
        from hyperkitty.tasks import rebuild_thread_cache_new_email

        # update or cleanup thread                  # noqa: E303 (isort issue)
        if self.emails.count() == 0:
            ...
"""
    assert isort.code(test_input) == test_input
    assert isort.code(test_input, lines_after_imports=2) == test_input


def test_force_single_line_shouldnt_remove_preceding_comment_lines_issue_1296():
    """Tests to ensure force_single_line setting doesn't result in lost comments.
    See: https://github.com/timothycrosley/isort/issues/1296
    """
    test_input = """
# A comment
# A comment

# Oh no, I'm gone
from moo import foo
"""
    # assert isort.code(test_input) == test_input
    assert isort.code(test_input, force_single_line=True) == test_input


def test_ensure_new_line_before_comments_mixed_with_ensure_newline_before_comments_1295():
    """Tests to ensure that the black profile can be used in conjunction with
    force_sort_within_sections.

    See: https://github.com/timothycrosley/isort/issues/1295
    """
    test_input = """
from openzwave.group import ZWaveGroup
from openzwave.network import ZWaveNetwork

# pylint: disable=import-error
from openzwave.option import ZWaveOption
"""
    assert isort.code(test_input, profile="black") == test_input
    assert isort.code(test_input, profile="black", force_sort_within_sections=True) == test_input


def test_trailing_comma_doesnt_introduce_broken_code_with_comment_and_wrap_issue_1302():
    """Tests to assert the combination of include_trailing_comma and a wrapped line doesnt break.
    See: https://github.com/timothycrosley/isort/issues/1302.
    """
    assert (
        isort.code(
            """
from somewhere import very_very_very_very_very_very_long_symbol # some comment
""",
            line_length=50,
            include_trailing_comma=True,
        )
        == """
from somewhere import \\
    very_very_very_very_very_very_long_symbol  # some comment
"""
    )
