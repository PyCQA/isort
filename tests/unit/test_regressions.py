"""A growing set of tests designed to ensure isort doesn't have regressions in new versions"""

from io import StringIO

import pytest

import isort


def test_isort_duplicating_comments_issue_1264():
    """Ensure isort doesn't duplicate comments when force_sort_within_sections is set to `True`
    as was the case in issue #1264: https://github.com/pycqa/isort/issues/1264
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
    See: https://github.com/pycqa/isort/issues/1275
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

    assert (
        isort.code(
            '''"""
My docstring
"""

from b import thing
from a import other_thing
''',
            add_imports=["from b import thing"],
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
    See: https://github.com/pycqa/isort/issues/1283
    """
    test_input = """__version__ = "0.58.1"

from starlette import status
"""
    assert isort.code(test_input) == test_input


def test_extra_blank_line_added_nested_imports_issue_1290():
    """Ensure isort doesn't add unnecessary blank lines above nested imports.
    See: https://github.com/pycqa/isort/issues/1290
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
    See: https://github.com/pycqa/isort/issues/1297
    """
    assert isort.check_code(
        """from __future__ import unicode_literals

from os import path
""",
        add_imports={"from __future__ import unicode_literals"},
    )


def test_no_extra_lines_for_imports_in_functions_issue_1277():
    """Test to ensure isort doesn't introduce extra blank lines for imports within function.
    See: https://github.com/pycqa/isort/issues/1277
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
    See: https://github.com/pycqa/isort/issues/1293
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
    See: https://github.com/pycqa/isort/issues/1296
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

    See: https://github.com/pycqa/isort/issues/1295
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
    See: https://github.com/pycqa/isort/issues/1302.
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


def test_ensure_sre_parse_is_identified_as_stdlib_issue_1304():
    """Ensure sre_parse is idenified as STDLIB.
    See: https://github.com/pycqa/isort/issues/1304.
    """
    assert (
        isort.place_module("sre_parse") == isort.place_module("sre") == isort.settings.STDLIB  # type: ignore # noqa
    )


def test_add_imports_shouldnt_move_lower_comments_issue_1300():
    """Ensure add_imports doesn't move comments immediately below imports.
    See:: https://github.com/pycqa/isort/issues/1300.
    """
    test_input = """from __future__ import unicode_literals

from os import path

# A comment for a constant
ANSWER = 42
"""
    assert isort.code(test_input, add_imports=["from os import path"]) == test_input


def test_windows_newline_issue_1277():
    """Test to ensure windows new lines are correctly handled within indented scopes.
    See: https://github.com/pycqa/isort/issues/1277
    """
    assert (
        isort.code("\ndef main():\r\n    import time\r\n\n    import sys\r\n")
        == "\ndef main():\r\n    import sys\r\n    import time\r\n"
    )


def test_windows_newline_issue_1278():
    """Test to ensure windows new lines are correctly handled within indented scopes.
    See: https://github.com/pycqa/isort/issues/1278
    """
    assert isort.check_code(
        "\ntry:\r\n    import datadog_agent\r\n\r\n    "
        "from ..log import CheckLoggingAdapter, init_logging\r\n\r\n    init_logging()\r\n"
        "except ImportError:\r\n    pass\r\n"
    )


def test_check_never_passes_with_indented_headings_issue_1301():
    """Test to ensure that test can pass even when there are indented headings.
    See: https://github.com/pycqa/isort/issues/1301
    """
    assert isort.check_code(
        """
try:
    # stdlib
    import logging
    from os import abc, path
except ImportError:
    pass
""",
        import_heading_stdlib="stdlib",
    )


def test_isort_shouldnt_fail_on_long_from_with_dot_issue_1190():
    """Test to ensure that isort will correctly handle formatting a long from import that contains
    a dot.
    See: https://github.com/pycqa/isort/issues/1190
    """
    assert (
        isort.code(
            """
from this_is_a_very_long_import_statement.that_will_occur_across_two_lines\\
        .when_the_line_length.is_only_seventynine_chars import (
    function1,
    function2,
)
        """,
            line_length=79,
            multi_line_output=3,
        )
        == """
from this_is_a_very_long_import_statement.that_will_occur_across_two_lines"""
        """.when_the_line_length.is_only_seventynine_chars import (
    function1,
    function2
)
"""
    )


def test_isort_shouldnt_add_extra_new_line_when_fass_and_n_issue_1315():
    """Test to ensure isort doesnt add a second extra new line when combining --fss and -n options.
    See: https://github.com/pycqa/isort/issues/1315
    """
    assert isort.check_code(
        """import sys

# Comment canary
from . import foo
""",
        ensure_newline_before_comments=True,  # -n
        force_sort_within_sections=True,  # -fss
        show_diff=True,  # for better debugging in the case the test case fails.
    )

    assert (
        isort.code(
            """
from . import foo
# Comment canary
from .. import foo
""",
            ensure_newline_before_comments=True,
            force_sort_within_sections=True,
        )
        == """
from . import foo

# Comment canary
from .. import foo
"""
    )


def test_isort_doesnt_rewrite_import_with_dot_to_from_import_issue_1280():
    """Test to ensure isort doesn't rewrite imports in the from of import y.x into from y import x.
    This is because they are not technically fully equivalent to eachother and can introduce broken
    behaviour.
    See: https://github.com/pycqa/isort/issues/1280
    """
    assert isort.check_code(
        """
        import test.module
        import test.module as m
        from test import module
        from test import module as m
    """,
        show_diff=True,
    )


def test_isort_shouldnt_introduce_extra_lines_with_fass_issue_1322():
    """Tests to ensure isort doesn't introduce extra lines when used with fass option.
    See: https://github.com/pycqa/isort/issues/1322
    """
    assert (
        isort.code(
            """
        import logging

# Comment canary
from foo import bar
import quux
""",
            force_sort_within_sections=True,
            ensure_newline_before_comments=True,
        )
        == """
        import logging

# Comment canary
from foo import bar
import quux
"""
    )


def test_comments_should_cause_wrapping_on_long_lines_black_mode_issue_1219():
    """Tests to ensure if isort encounters a single import line which is made too long with a comment
    it is wrapped when using black profile.
    See: https://github.com/pycqa/isort/issues/1219
    """
    assert isort.check_code(
        """
from many_stop_words import (
    get_stop_words as get_base_stopwords,  # extended list of stop words, also for en
)
""",
        show_diff=True,
        profile="black",
    )


def test_comment_blocks_should_stay_associated_without_extra_lines_issue_1156():
    """Tests to ensure isort doesn't add an extra line when there are large import blocks
    or otherwise warp the intent.
    See: https://github.com/pycqa/isort/issues/1156
    """
    assert (
        isort.code(
            """from top_level_ignored import config  # isort:skip
####################################
# COMMENT BLOCK SEPARATING THESE   #
####################################
from ast import excepthandler
import logging
"""
        )
        == """from top_level_ignored import config  # isort:skip
import logging
####################################
# COMMENT BLOCK SEPARATING THESE   #
####################################
from ast import excepthandler
"""
    )


def test_comment_shouldnt_be_duplicated_with_fass_enabled_issue_1329():
    """Tests to ensure isort doesn't duplicate comments when imports occur with comment on top,
    immediately after large comment blocks.
    See: https://github.com/pycqa/isort/pull/1329/files.
    """
    assert isort.check_code(
        """'''
Multi-line docstring
'''
# Comment for A.
import a
# Comment for B - not A!
import b
""",
        force_sort_within_sections=True,
        show_diff=True,
    )


def test_wrap_mode_equal_to_line_length_with_indendet_imports_issue_1333():
    assert isort.check_code(
        """
import a
import b


def function():
    import a as b
    import c as d
""",
        line_length=17,
        wrap_length=17,
        show_diff=True,
    )


def test_isort_skipped_nested_imports_issue_1339():
    """Ensure `isort:skip are honored in nested imports.
    See: https://github.com/pycqa/isort/issues/1339.
    """
    assert isort.check_code(
        """
    def import_test():
        from os ( # isort:skip
            import path
        )
    """,
        show_diff=True,
    )


def test_windows_diff_too_large_misrepresentative_issue_1348(test_path):
    """Ensure isort handles windows files correctly when it come to producing a diff with --diff.
    See: https://github.com/pycqa/isort/issues/1348
    """
    diff_output = StringIO()
    isort.file(test_path / "example_crlf_file.py", show_diff=diff_output)
    diff_output.seek(0)
    assert diff_output.read().endswith(
        "-1,5 +1,5 @@\n+import a\r\n import b\r\n" "-import a\r\n \r\n \r\n def func():\r\n"
    )


def test_combine_as_does_not_lose_comments_issue_1321():
    """Test to ensure isort doesn't lose comments when --combine-as is used.
    See: https://github.com/pycqa/isort/issues/1321
    """
    test_input = """
from foo import *  # noqa
from foo import bar as quux  # other
from foo import x as a  # noqa

import operator as op  # op comment
import datetime as dtime  # dtime comment

from datetime import date as d  # dcomm
from datetime import datetime as dt  # dtcomm
"""

    expected_output = """
import datetime as dtime  # dtime comment
import operator as op  # op comment
from datetime import date as d, datetime as dt  # dcomm; dtcomm

from foo import *  # noqa
from foo import bar as quux, x as a  # other; noqa
"""

    assert isort.code(test_input, combine_as_imports=True) == expected_output


def test_combine_as_does_not_lose_comments_issue_1381():
    """Test to ensure isort doesn't lose comments when --combine-as is used.
    See: https://github.com/pycqa/isort/issues/1381
    """
    test_input = """
from smtplib import SMTPConnectError, SMTPNotSupportedError  # important comment
"""
    assert "# important comment" in isort.code(test_input, combine_as_imports=True)

    test_input = """
from appsettings import AppSettings, ObjectSetting, StringSetting  # type: ignore
"""
    assert "# type: ignore" in isort.code(test_input, combine_as_imports=True)


def test_incorrect_grouping_when_comments_issue_1396():
    """Test to ensure isort groups import correct independent of the comments present.
    See: https://github.com/pycqa/isort/issues/1396
    """
    assert (
        isort.code(
            """from django.shortcuts import render
from apps.profiler.models import Project
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    # ListView,
    # DetailView,
    TemplateView,
    # CreateView,
    # View
)
""",
            line_length=88,
            known_first_party=["apps"],
            known_django=["django"],
            sections=["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
        )
        == """from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import \\
    TemplateView  # ListView,; DetailView,; CreateView,; View

from apps.profiler.models import Project
"""
    )
    assert (
        isort.code(
            """from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.profiler.models import Project

from django.views.generic import ( # ListView,; DetailView,; CreateView,; View
    TemplateView,
)
""",
            line_length=88,
            known_first_party=["apps"],
            known_django=["django"],
            sections=["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"],
            include_trailing_comma=True,
            multi_line_output=3,
            force_grid_wrap=0,
            use_parentheses=True,
            ensure_newline_before_comments=True,
        )
        == """from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import (  # ListView,; DetailView,; CreateView,; View
    TemplateView,
)

from apps.profiler.models import Project
"""
    )


def test_reverse_relative_combined_with_force_sort_within_sections_issue_1395():
    """Test to ensure reverse relative combines well with other common isort settings.
    See: https://github.com/pycqa/isort/issues/1395.
    """
    assert isort.check_code(
        """from .fileA import a_var
from ..fileB import b_var
""",
        show_diff=True,
        reverse_relative=True,
        force_sort_within_sections=True,
        order_by_type=False,
        case_sensitive=False,
        multi_line_output=5,
        sections=["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "APPLICATION", "LOCALFOLDER"],
        lines_after_imports=2,
        no_lines_before="LOCALFOLDER",
    )


def test_isort_should_be_able_to_add_independent_of_doc_string_placement_issue_1420():
    """isort should be able to know when an import requested to be added is sucesfully added,
    independent of where the top doc string is located.
    See: https://github.com/PyCQA/isort/issues/1420
    """
    assert isort.check_code(
        '''"""module docstring"""

import os
''',
        show_diff=True,
        add_imports=["os"],
    )


def test_comments_should_never_be_moved_between_imports_issue_1427():
    """isort should never move comments to different import statement.
    See: https://github.com/PyCQA/isort/issues/1427
    """
    assert isort.check_code(
        """from package import CONSTANT
from package import *  # noqa
        """,
        force_single_line=True,
        show_diff=True,
    )


def test_isort_doesnt_misplace_comments_issue_1431():
    """Test to ensure isort wont misplace comments.
    See: https://github.com/PyCQA/isort/issues/1431
    """
    input_text = """from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent,  # NOT DRY
)
from com.my_lovely_company.my_lovely_team.my_lovely_project.my_lovely_component import (
    MyLovelyCompanyTeamProjectComponent as component,  # DRY
)
"""
    assert isort.code(input_text, profile="black") == input_text


def test_isort_doesnt_misplace_add_import_issue_1445():
    """Test to ensure isort won't misplace an added import depending on docstring position
    See: https://github.com/PyCQA/isort/issues/1445
    """
    assert (
        isort.code(
            '''#!/usr/bin/env python

"""module docstring"""
''',
            add_imports=["import os"],
        )
        == '''#!/usr/bin/env python

"""module docstring"""

import os
'''
    )

    assert isort.check_code(
        '''#!/usr/bin/env python

"""module docstring"""

import os
    ''',
        add_imports=["import os"],
        show_diff=True,
    )


def test_isort_doesnt_mangle_code_when_adding_imports_issue_1444():
    """isort should NEVER mangle code. This particularly nasty and easy to reproduce bug,
    caused isort to produce invalid code just by adding a single import statement depending
    on comment placement.
    See: https://github.com/PyCQA/isort/issues/1444
    """
    assert (
        isort.code(
            '''

"""module docstring"""
''',
            add_imports=["import os"],
        )
        == '''

"""module docstring"""

import os
'''
    )


def test_isort_float_to_top_with_sort_on_off_tests():
    """Characterization test for current behaviour of float-to-top on isort: on/off sections.
    - imports in isort:off sections stay where they are
    - imports in isort:on sections float up, but to the top of the isort:on section (not the
      top of the file)"""
    assert (
        isort.code(
            """
def foo():
    pass

import a

# isort: off
import stays_in_section

x = 1

import stays_in_place

# isort: on

def bar():
    pass

import floats_to_top_of_section

def baz():
    pass
""",
            float_to_top=True,
        )
        == """import a


def foo():
    pass

# isort: off
import stays_in_section

x = 1

import stays_in_place

# isort: on
import floats_to_top_of_section


def bar():
    pass


def baz():
    pass
"""
    )

    to_sort = """# isort: off

def foo():
    pass

import stays_in_place
import no_float_to_to_top
import no_ordering

def bar():
    pass
"""

    # No changes if isort is off
    assert isort.code(to_sort, float_to_top=True) == to_sort


def test_isort_doesnt_float_to_top_correctly_when_imports_not_at_top_issue_1382():
    """isort should float existing imports to the top, if they are currently below the top.
    See: https://github.com/PyCQA/isort/issues/1382
    """
    assert (
        isort.code(
            """
def foo():
    pass

import a

def bar():
    pass
""",
            float_to_top=True,
        )
        == """import a


def foo():
    pass


def bar():
    pass
"""
    )

    assert (
        isort.code(
            """






def foo():
    pass

import a

def bar():
    pass
""",
            float_to_top=True,
        )
        == """import a


def foo():
    pass


def bar():
    pass
"""
    )

    assert (
        isort.code(
            '''"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''
"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''
"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''#!/bin/bash
"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''#!/bin/bash
"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )

    assert (
        isort.code(
            '''#!/bin/bash

"""My comment


"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == '''#!/bin/bash

"""My comment


"""
import a


def foo():
    pass


def bar():
    pass
'''
    )


def test_empty_float_to_top_shouldnt_error_issue_1453():
    """isort shouldn't error when float to top is set with a mostly empty file"""
    assert isort.check_code(
        """
""",
        show_diff=True,
        float_to_top=True,
    )
    assert isort.check_code(
        """
""",
        show_diff=True,
    )


def test_import_sorting_shouldnt_be_endless_with_headers_issue_1454():
    """isort should never enter an endless sorting loop.
    See: https://github.com/PyCQA/isort/issues/1454
    """
    assert isort.check_code(
        """

# standard library imports
import sys

try:
    # Comment about local lib
    # related third party imports
    from local_lib import stuff
except ImportError as e:
    pass
""",
        known_third_party=["local_lib"],
        import_heading_thirdparty="related third party imports",
        show_diff=True,
    )


def test_isort_should_leave_non_import_from_lines_alone_issue_1488():
    """isort should never mangle non-import from statements.
    See: https://github.com/PyCQA/isort/issues/1488
    """
    raise_from_should_be_ignored = """
raise SomeException("Blah") \\
    from exceptionsInfo.popitem()[1]
"""
    assert isort.check_code(raise_from_should_be_ignored, show_diff=True)

    yield_from_should_be_ignored = """
def generator_function():
    yield \\
        from other_function()[1]
"""
    assert isort.check_code(yield_from_should_be_ignored, show_diff=True)

    wont_ignore_comment_contiuation = """
# one

# two


def function():
    # three \\
    import b
    import a
"""
    assert (
        isort.code(wont_ignore_comment_contiuation)
        == """
# one

# two


def function():
    # three \\
    import a
    import b
"""
    )

    will_ignore_if_non_comment_continuation = """
# one

# two


def function():
    raise \\
    import b
    import a
"""
    assert isort.check_code(will_ignore_if_non_comment_continuation, show_diff=True)

    yield_from_parens_should_be_ignored = """
def generator_function():
    (
     yield
     from other_function()[1]
    )
"""
    assert isort.check_code(yield_from_parens_should_be_ignored, show_diff=True)

    yield_from_lots_of_parens_and_space_should_be_ignored = """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     yield



     from other_function()[1]
    )))))))))))))
    )))
"""
    assert isort.check_code(yield_from_lots_of_parens_and_space_should_be_ignored, show_diff=True)

    yield_from_should_be_ignored_when_following_import_statement = """
def generator_function():
    import os

    yield \\
    from other_function()[1]
"""
    assert isort.check_code(
        yield_from_should_be_ignored_when_following_import_statement, show_diff=True
    )

    yield_at_file_end_ignored = """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     yield
"""
    assert isort.check_code(yield_at_file_end_ignored, show_diff=True)

    raise_at_file_end_ignored = """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     raise (
"""
    assert isort.check_code(raise_at_file_end_ignored, show_diff=True)

    raise_from_at_file_end_ignored = """
def generator_function():
    (
    (
    ((((
    (((((
    ((
    (((
     raise \\
     from \\
"""
    assert isort.check_code(raise_from_at_file_end_ignored, show_diff=True)


def test_isort_float_to_top_correctly_identifies_single_line_comments_1499():
    """Test to ensure isort correctly handles the case where float to top is used
    to push imports to the top and the top comment is a multiline type but only
    one line.
    See: https://github.com/PyCQA/isort/issues/1499
    """
    assert (
        isort.code(
            '''#!/bin/bash
"""My comment"""
def foo():
    pass

import a

def bar():
    pass
''',
            float_to_top=True,
        )
        == (
            '''#!/bin/bash
"""My comment"""
import a


def foo():
    pass


def bar():
    pass
'''
        )
    )
    assert (
        isort.code(
            """#!/bin/bash
'''My comment'''
def foo():
    pass

import a

def bar():
    pass
""",
            float_to_top=True,
        )
        == (
            """#!/bin/bash
'''My comment'''
import a


def foo():
    pass


def bar():
    pass
"""
        )
    )

    assert isort.check_code(
        """#!/bin/bash
'''My comment'''
import a

x = 1
""",
        float_to_top=True,
        show_diff=True,
    )


def test_isort_shouldnt_mangle_from_multi_line_string_issue_1507():
    """isort was seen mangling lines that happened to contain the word from after
    a yield happened to be in a file. Clearly this shouldn't happen.
    See: https://github.com/PyCQA/isort/issues/1507.
    """
    assert isort.check_code(
        '''
def a():
    yield f(
        """
        select %s from (values %%s) as t(%s)
        """
    )

def b():
    return (
        """
        select name
        from foo
        """
        % main_table
    )

def c():
    query = (
        """
        select {keys}
        from (values %s) as t(id)
        """
    )

def d():
    query = f"""select t.id
                from {table} t
                {extra}"""
''',
        show_diff=True,
    )


def test_isort_should_keep_all_as_and_non_as_imports_issue_1523():
    """isort should keep as and non-as imports of the same path that happen to exist within the
    same statement.
    See: https://github.com/PyCQA/isort/issues/1523.
    """
    assert isort.check_code(
        """
from selenium.webdriver import Remote, Remote as Driver
""",
        show_diff=True,
        combine_as_imports=True,
    )


def test_isort_shouldnt_introduce_syntax_error_issue_1539():
    """isort should NEVER introduce syntax errors.
    In 5.5.4 some strings that contained a line starting with from could lead to no empty paren.
    See: https://github.com/PyCQA/isort/issues/1539.
    """
    assert isort.check_code(
        '''"""Foobar
    from {}""".format(
    "bar",
)
''',
        show_diff=True,
    )
    assert isort.check_code(
        '''"""Foobar
    import {}""".format(
    "bar",
)
''',
        show_diff=True,
    )
    assert (
        isort.code(
            '''"""Foobar
    from {}"""
    from a import b, a
''',
        )
        == '''"""Foobar
    from {}"""
    from a import a, b
'''
    )
    assert (
        isort.code(
            '''"""Foobar
    from {}"""
    import b
    import a
''',
        )
        == '''"""Foobar
    from {}"""
    import a
    import b
'''
    )


def test_isort_shouldnt_split_skip_issue_1548():
    """Ensure isort doesn't add a spurious new line if isort: skip is combined with float to top.
    See: https://github.com/PyCQA/isort/issues/1548.
    """
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
    prune_dependencies,
)
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
    prune_dependencies,
)
import a
import b
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import  # isort:skip
import a
import b
""",
        show_diff=True,
        float_to_top=True,
    )
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
    a
)
import b
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
        )
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert isort.check_code(
        """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
)""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert (
        isort.code(
            """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
)
""",
            profile="black",
            float_to_top=True,
            add_imports=["import os"],
        )
        == """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
)
import os
"""
    )
    assert (
        isort.code(
            """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
)""",
            profile="black",
            float_to_top=True,
            add_imports=["import os"],
        )
        == """from tools.dependency_pruning.prune_dependencies import (  # isort:skip
)
import os
"""
    )


def test_isort_shouldnt_split_skip_issue_1556():
    assert isort.check_code(
        """
from tools.dependency_pruning.prune_dependencies import (  # isort:skip
    prune_dependencies,
)
from tools.developer_pruning.prune_developers import (  # isort:skip
    prune_developers,
)
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )
    assert isort.check_code(
        """
from tools.dependency_pruning.prune_dependencies import (  # isort:skip
    prune_dependencies,
)
from tools.developer_pruning.prune_developers import x  # isort:skip
""",
        show_diff=True,
        profile="black",
        float_to_top=True,
    )


def test_isort_losing_imports_vertical_prefix_from_module_import_wrap_mode_issue_1542():
    """Ensure isort doesnt lose imports when a comment is combined with an import and
    wrap mode VERTICAL_PREFIX_FROM_MODULE_IMPORT is used.
    See: https://github.com/PyCQA/isort/issues/1542.
    """
    assert (
        isort.code(
            """
from xxxxxxxxxxxxxxxx import AAAAAAAAAA, BBBBBBBBBB
from xxxxxxxxxxxxxxxx import CCCCCCCCC, DDDDDDDDD  # xxxxxxxxxxxxxxxxxx

print(CCCCCCCCC)
""",
            multi_line_output=9,
        )
        == """
from xxxxxxxxxxxxxxxx import AAAAAAAAAA, BBBBBBBBBB  # xxxxxxxxxxxxxxxxxx
from xxxxxxxxxxxxxxxx import CCCCCCCCC, DDDDDDDDD

print(CCCCCCCCC)
"""
    )

    assert isort.check_code(
        """
from xxxxxxxxxxxxxxxx import AAAAAAAAAA, BBBBBBBBBB

from xxxxxxxxxxxxxxxx import CCCCCCCCC, DDDDDDDDD  # xxxxxxxxxxxxxxxxxx isort: skip

print(CCCCCCCCC)
""",
        show_diff=True,
        multi_line_output=9,
    )


def test_isort_adding_second_comma_issue_1621():
    """Ensure isort doesnt add a second comma when very long comment is present
    See: https://github.com/PyCQA/isort/issues/1621.
    """
    assert isort.check_code(
        """from .test import (
    TestTestTestTestTestTest2 as TestTestTestTestTestTest1,  """
        """# Some really long comment bla bla bla bla bla
)
""",
        profile="black",
        show_diff=True,
    )
    assert (
        isort.code(
            """from .test import (
    TestTestTestTestTestTest2 as TestTestTestTestTestTest1  """
            """# Some really long comment bla bla bla bla bla
)
""",
            profile="black",
        )
        == """from .test import (
    TestTestTestTestTestTest2 as TestTestTestTestTestTest1,  """
        """# Some really long comment bla bla bla bla bla
)
"""
    )


def test_isort_shouldnt_duplicate_comments_issue_1631():
    assert isort.check_code(
        """
import a  # a comment
import a as b  # b comment
""",
        show_diff=True,
    )
    assert (
        isort.code(
            """
import a  # a comment
import a as a  # b comment
""",
            remove_redundant_aliases=True,
        )
        == """
import a  # a comment; b comment
"""
    )


def test_isort_shouldnt_add_extra_new_lines_with_import_heading_issue_1670():
    snippet = """#!/usr/bin/python3 -ttu
# Standard Library
import argparse
import datetime

import attr
import requests


def foo() -> int:
    print("Hello world")
    return 0


def spam():


    # Standard Library
    import collections
    import logging
"""
    assert (
        isort.code(
            snippet,
            import_heading_stdlib="Standard Library",
        )
        == snippet
    )


def test_isort_shouldnt_add_extra_line_float_to_top_issue_1667():
    assert isort.check_code(
        """
import sys

sys.path.insert(1, 'path/containing/something_else/..')

import something_else  # isort:skip

# Some constant
SOME_CONSTANT = 4
""",
        show_diff=True,
        float_to_top=True,
    )


def test_isort_shouldnt_move_noqa_comment_issue_1594():
    assert (
        isort.code(
            """
from .test import TestTestTestTestTestTest1  # noqa: F401
from .test import TestTestTestTestTestTest2, TestTestTestTestTestTest3, """
            """TestTestTestTestTestTest4, TestTestTestTestTestTest5  # noqa: F401
""",
            profile="black",
        )
        == """
from .test import TestTestTestTestTestTest1  # noqa: F401
from .test import (  # noqa: F401
    TestTestTestTestTestTest2,
    TestTestTestTestTestTest3,
    TestTestTestTestTestTest4,
    TestTestTestTestTestTest5,
)
"""
    )


def test_isort_correctly_handles_unix_vs_linux_newlines_issue_1566():
    import_statement = (
        "from impacket.smb3structs import (\n"
        "SMB2_CREATE, SMB2_FLAGS_DFS_OPERATIONS, SMB2_IL_IMPERSONATION, "
        "SMB2_OPLOCK_LEVEL_NONE, SMB2Create,"
        "\nSMB2Create_Response, SMB2Packet)\n"
    )
    assert isort.code(import_statement, line_length=120) == isort.code(
        import_statement.replace("\n", "\r\n"), line_length=120
    ).replace("\r\n", "\n")


def test_isort_treats_src_paths_same_as_from_config_as_cli_issue_1711(tmpdir):
    assert isort.check_code(
        """
import mymodule
import sqlalchemy
""",
        show_diff=True,
    )

    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
src_paths=
    api
"""
    )
    api_dir = tmpdir.mkdir("api")
    api_dir.join("mymodule.py").write("# comment")

    config = isort.settings.Config(str(config_file))
    assert isort.check_code(
        """
import sqlalchemy

import mymodule
""",
        show_diff=True,
        config=config,
    )


def test_isort_should_never_quietly_remove_imports_in_hanging_line_mode_issue_1741():
    assert (
        isort.code(
            """
from src import abcd, qwerty, efg, xyz  # some comment
""",
            line_length=50,
            multi_line_output=2,
        )
        == """
from src import abcd, efg, qwerty, xyz \\
    # some comment
"""
    )
    assert (
        isort.code(
            """
from src import abcd, qwerty, efg, xyz  # some comment
""",
            line_length=54,
            multi_line_output=2,
        )
        == """
from src import abcd, efg, qwerty, xyz  # some comment
"""
    )
    assert (
        isort.code(
            """
from src import abcd, qwerty, efg, xyz  # some comment
""",
            line_length=53,
            multi_line_output=2,
        )
        == """
from src import abcd, efg, qwerty, xyz \\
    # some comment
"""
    )
    assert (
        isort.code(
            """
from src import abcd, qwerty, efg, xyz  # some comment
""",
            line_length=30,
            multi_line_output=2,
        )
        == """
from src import abcd, efg, \\
    qwerty, xyz \\
    # some comment
"""
    )


@pytest.mark.parametrize("multi_line_output", range(12))
def test_isort_should_never_quietly_remove_imports_in_any_hangin_mode_issue_1741(
    multi_line_output: int,
):
    sorted_code = isort.code(
        """
from src import abcd, qwerty, efg, xyz  # some comment
""",
        line_length=30,
        multi_line_output=multi_line_output,
    )
    assert "abcd" in sorted_code
    assert "qwerty" in sorted_code
    assert "efg" in sorted_code
    assert "xyz" in sorted_code


def test_isort_should_keep_multi_noqa_with_star_issue_1744():
    assert isort.check_code(
        """
from typing import *  # noqa
from typing import IO, BinaryIO, Union  # noqa
""",
        show_diff=True,
    )
    assert isort.check_code(
        """
from typing import *  # noqa 1
from typing import IO, BinaryIO, Union  # noqa 2
""",
        show_diff=True,
    )
    assert isort.check_code(
        """
from typing import *  # noqa
from typing import IO, BinaryIO, Union
""",
        show_diff=True,
    )
    assert isort.check_code(
        """
from typing import *
from typing import IO, BinaryIO, Union  # noqa
""",
        show_diff=True,
    )
    assert (
        isort.code(
            """
from typing import *  # hi
from typing import IO, BinaryIO, Union  # noqa
""",
            combine_star=True,
        )
        == """
from typing import *  # noqa; hi
"""
    )
    assert (
        isort.code(
            """
from typing import *  # noqa
from typing import IO, BinaryIO, Union  # noqa
""",
            combine_star=True,
        )
        == """
from typing import *  # noqa
"""
    )


def test_isort_should_keep_multiple_noqa_comments_force_single_line_mode_issue_1721():
    assert isort.check_code(
        """
from some_very_long_filename_to_import_from_that_causes_a_too_long_import_row import (  # noqa: E501
    CONSTANT_1,
)
from some_very_long_filename_to_import_from_that_causes_a_too_long_import_row import (  # noqa: E501
    CONSTANT_2,
)
""",
        show_diff=True,
        profile="black",
        force_single_line=True,
    )


def test_isort_should_only_add_imports_to_valid_location_issue_1769():
    assert (
        isort.code(
            '''v = """
""".split(
    "\n"
)
''',
            add_imports=["from __future__ import annotations"],
        )
        == '''from __future__ import annotations

v = """
""".split(
    "\n"
)
'''
    )
    assert (
        isort.code(
            '''v=""""""''',
            add_imports=["from __future__ import annotations"],
        )
        == '''from __future__ import annotations

v=""""""
'''
    )


def test_literal_sort_at_top_of_file_issue_1792():
    assert (
        isort.code(
            '''"""I'm a docstring! Look at me!"""

# isort: unique-list
__all__ = ["Foo", "Foo", "Bar"]

from typing import final  # arbitrary


@final
class Foo:
    ...


@final
class Bar:
    ...
'''
        )
        == '''"""I'm a docstring! Look at me!"""

# isort: unique-list
__all__ = ['Bar', 'Foo']

from typing import final  # arbitrary


@final
class Foo:
    ...


@final
class Bar:
    ...
'''
    )


def test_isort_should_produce_the_same_code_on_subsequent_runs_issue_1799(tmpdir):
    code = """import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover
"""
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """[isort]
profile=black
src_paths=isort,test
line_length=100
skip=.tox,.venv,build,dist,docs,tests
extra_standard_library=pkg_resources,setuptools,typing
known_test=pytest
known_first_party=ibpt
sections=FUTURE,STDLIB,TEST,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
import_heading_firstparty=internal
import_heading_thirdparty=external
"""
    )
    settings = isort.settings.Config(str(config_file))
    assert isort.code(code, config=settings) == isort.code(
        isort.code(code, config=settings), config=settings
    )
