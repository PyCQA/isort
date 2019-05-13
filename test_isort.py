# coding: utf-8
"""test_isort.py.

Tests all major functionality of the isort library
Should be ran using py.test by simply running py.test in the isort project directory

Copyright (C) 2013  Timothy Edmund Crosley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os
import os.path
import posixpath
import sys
import sysconfig
from subprocess import check_output
from tempfile import NamedTemporaryFile

import pytest

from isort import finders, main, settings
from isort.isort import SortImports
from isort.main import is_python_file
from isort.settings import WrapModes
from isort.utils import exists_case_sensitive

try:
    import toml
except ImportError:
    toml = None

TEST_DEFAULT_CONFIG = """
[*.py]
max_line_length = 120
indent_style = space
indent_size = 4
known_first_party = isort
known_third_party = kate
ignore_frosted_errors = E103
skip = build,.tox,venv
balanced_wrapping = true
not_skip = __init__.py
"""
SHORT_IMPORT = "from third_party import lib1, lib2, lib3, lib4"
SINGLE_FROM_IMPORT = "from third_party import lib1"
SINGLE_LINE_LONG_IMPORT = "from third_party import lib1, lib2, lib3, lib4, lib5, lib5ab"
REALLY_LONG_IMPORT = ("from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11,"
                      "lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22")
REALLY_LONG_IMPORT_WITH_COMMENT = ("from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, "
                                   "lib10, lib11, lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22"
                                   " # comment")


@pytest.fixture(scope="session", autouse=True)
def default_settings_path(tmpdir_factory):
    config_dir = tmpdir_factory.mktemp('config')
    config_file = config_dir.join('.editorconfig').strpath
    with open(config_file, 'w') as editorconfig:
        editorconfig.write(TEST_DEFAULT_CONFIG)

    with config_dir.as_cwd():
        yield config_dir.strpath


def test_happy_path():
    """Test the most basic use case, straight imports no code, simply not organized by category."""
    test_input = ("import sys\n"
                  "import os\n"
                  "import myproject.test\n"
                  "import django.settings")
    test_output = SortImports(file_contents=test_input, known_third_party=['django']).output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "\n"
                           "import django.settings\n"
                           "\n"
                           "import myproject.test\n")


def test_code_intermixed():
    """Defines what should happen when isort encounters imports intermixed with
    code.

    (it should pull them all to the top)

    """
    test_input = ("import sys\n"
                  "print('yo')\n"
                  "print('I like to put code between imports cause I want stuff to break')\n"
                  "import myproject.test\n")
    test_output = SortImports(file_contents=test_input).output
    assert test_output == ("import sys\n"
                           "\n"
                           "import myproject.test\n"
                           "\n"
                           "print('yo')\n"
                           "print('I like to put code between imports cause I want stuff to break')\n")


def test_correct_space_between_imports():
    """Ensure after imports a correct amount of space (in newlines) is
    enforced.

    (2 for method, class, or decorator definitions 1 for anything else)

    """
    test_input_method = ("import sys\n"
                         "def my_method():\n"
                         "    print('hello world')\n")
    test_output_method = SortImports(file_contents=test_input_method).output
    assert test_output_method == ("import sys\n"
                                  "\n"
                                  "\n"
                                  "def my_method():\n"
                                  "    print('hello world')\n")

    test_input_decorator = ("import sys\n"
                            "@my_decorator\n"
                            "def my_method():\n"
                            "    print('hello world')\n")
    test_output_decorator = SortImports(file_contents=test_input_decorator).output
    assert test_output_decorator == ("import sys\n"
                                     "\n"
                                     "\n"
                                     "@my_decorator\n"
                                     "def my_method():\n"
                                     "    print('hello world')\n")

    test_input_class = ("import sys\n"
                        "class MyClass(object):\n"
                        "    pass\n")
    test_output_class = SortImports(file_contents=test_input_class).output
    assert test_output_class == ("import sys\n"
                                 "\n"
                                 "\n"
                                 "class MyClass(object):\n"
                                 "    pass\n")

    test_input_other = ("import sys\n"
                        "print('yo')\n")
    test_output_other = SortImports(file_contents=test_input_other).output
    assert test_output_other == ("import sys\n"
                                 "\n"
                                 "print('yo')\n")


def test_sort_on_number():
    """Ensure numbers get sorted logically (10 > 9 not the other way around)"""
    test_input = ("import lib10\n"
                  "import lib9\n")
    test_output = SortImports(file_contents=test_input).output
    assert test_output == ("import lib9\n"
                           "import lib10\n")


def test_line_length():
    """Ensure isort enforces the set line_length."""
    assert len(SortImports(file_contents=REALLY_LONG_IMPORT, line_length=80).output.split("\n")[0]) <= 80
    assert len(SortImports(file_contents=REALLY_LONG_IMPORT, line_length=120).output.split("\n")[0]) <= 120

    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, line_length=42).output
    assert test_output == ("from third_party import (lib1, lib2, lib3,\n"
                           "                         lib4, lib5, lib6,\n"
                           "                         lib7, lib8, lib9,\n"
                           "                         lib10, lib11,\n"
                           "                         lib12, lib13,\n"
                           "                         lib14, lib15,\n"
                           "                         lib16, lib17,\n"
                           "                         lib18, lib20,\n"
                           "                         lib21, lib22)\n")

    TEST_INPUT = ('from django.contrib.gis.gdal.field import (\n'
                  '    OFTDate, OFTDateTime, OFTInteger, OFTInteger64, OFTReal, OFTString,\n'
                  '    OFTTime,\n'
                  ')\n')  # Test case described in issue #654
    assert SortImports(file_contents=TEST_INPUT, include_trailing_comma=True, line_length=79,
                       multi_line_output=WrapModes.VERTICAL_GRID_GROUPED, balanced_wrapping=False).output == TEST_INPUT

    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, line_length=42, wrap_length=32).output
    assert test_output == ("from third_party import (lib1,\n"
                           "                         lib2,\n"
                           "                         lib3,\n"
                           "                         lib4,\n"
                           "                         lib5,\n"
                           "                         lib6,\n"
                           "                         lib7,\n"
                           "                         lib8,\n"
                           "                         lib9,\n"
                           "                         lib10,\n"
                           "                         lib11,\n"
                           "                         lib12,\n"
                           "                         lib13,\n"
                           "                         lib14,\n"
                           "                         lib15,\n"
                           "                         lib16,\n"
                           "                         lib17,\n"
                           "                         lib18,\n"
                           "                         lib20,\n"
                           "                         lib21,\n"
                           "                         lib22)\n")


def test_output_modes():
    """Test setting isort to use various output modes works as expected"""
    test_output_grid = SortImports(file_contents=REALLY_LONG_IMPORT,
                                   multi_line_output=WrapModes.GRID, line_length=40).output
    assert test_output_grid == ("from third_party import (lib1, lib2,\n"
                                "                         lib3, lib4,\n"
                                "                         lib5, lib6,\n"
                                "                         lib7, lib8,\n"
                                "                         lib9, lib10,\n"
                                "                         lib11, lib12,\n"
                                "                         lib13, lib14,\n"
                                "                         lib15, lib16,\n"
                                "                         lib17, lib18,\n"
                                "                         lib20, lib21,\n"
                                "                         lib22)\n")

    test_output_vertical = SortImports(file_contents=REALLY_LONG_IMPORT,
                                       multi_line_output=WrapModes.VERTICAL, line_length=40).output
    assert test_output_vertical == ("from third_party import (lib1,\n"
                                    "                         lib2,\n"
                                    "                         lib3,\n"
                                    "                         lib4,\n"
                                    "                         lib5,\n"
                                    "                         lib6,\n"
                                    "                         lib7,\n"
                                    "                         lib8,\n"
                                    "                         lib9,\n"
                                    "                         lib10,\n"
                                    "                         lib11,\n"
                                    "                         lib12,\n"
                                    "                         lib13,\n"
                                    "                         lib14,\n"
                                    "                         lib15,\n"
                                    "                         lib16,\n"
                                    "                         lib17,\n"
                                    "                         lib18,\n"
                                    "                         lib20,\n"
                                    "                         lib21,\n"
                                    "                         lib22)\n")

    comment_output_vertical = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                                          multi_line_output=WrapModes.VERTICAL, line_length=40).output
    assert comment_output_vertical == ("from third_party import (lib1,  # comment\n"
                                       "                         lib2,\n"
                                       "                         lib3,\n"
                                       "                         lib4,\n"
                                       "                         lib5,\n"
                                       "                         lib6,\n"
                                       "                         lib7,\n"
                                       "                         lib8,\n"
                                       "                         lib9,\n"
                                       "                         lib10,\n"
                                       "                         lib11,\n"
                                       "                         lib12,\n"
                                       "                         lib13,\n"
                                       "                         lib14,\n"
                                       "                         lib15,\n"
                                       "                         lib16,\n"
                                       "                         lib17,\n"
                                       "                         lib18,\n"
                                       "                         lib20,\n"
                                       "                         lib21,\n"
                                       "                         lib22)\n")

    test_output_hanging_indent = SortImports(file_contents=REALLY_LONG_IMPORT,
                                             multi_line_output=WrapModes.HANGING_INDENT,
                                             line_length=40, indent="    ").output
    assert test_output_hanging_indent == ("from third_party import lib1, lib2, \\\n"
                                          "    lib3, lib4, lib5, lib6, lib7, \\\n"
                                          "    lib8, lib9, lib10, lib11, lib12, \\\n"
                                          "    lib13, lib14, lib15, lib16, lib17, \\\n"
                                          "    lib18, lib20, lib21, lib22\n")

    comment_output_hanging_indent = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                                                multi_line_output=WrapModes.HANGING_INDENT,
                                                line_length=40, indent="    ").output
    assert comment_output_hanging_indent == ("from third_party import lib1, \\  # comment\n"
                                             "    lib2, lib3, lib4, lib5, lib6, \\\n"
                                             "    lib7, lib8, lib9, lib10, lib11, \\\n"
                                             "    lib12, lib13, lib14, lib15, lib16, \\\n"
                                             "    lib17, lib18, lib20, lib21, lib22\n")

    test_output_vertical_indent = SortImports(file_contents=REALLY_LONG_IMPORT,
                                              multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
                                              line_length=40, indent="    ").output
    assert test_output_vertical_indent == ("from third_party import (\n"
                                           "    lib1,\n"
                                           "    lib2,\n"
                                           "    lib3,\n"
                                           "    lib4,\n"
                                           "    lib5,\n"
                                           "    lib6,\n"
                                           "    lib7,\n"
                                           "    lib8,\n"
                                           "    lib9,\n"
                                           "    lib10,\n"
                                           "    lib11,\n"
                                           "    lib12,\n"
                                           "    lib13,\n"
                                           "    lib14,\n"
                                           "    lib15,\n"
                                           "    lib16,\n"
                                           "    lib17,\n"
                                           "    lib18,\n"
                                           "    lib20,\n"
                                           "    lib21,\n"
                                           "    lib22\n"
                                           ")\n")

    comment_output_vertical_indent = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                                                 multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
                                                 line_length=40, indent="    ").output
    assert comment_output_vertical_indent == ("from third_party import (  # comment\n"
                                              "    lib1,\n"
                                              "    lib2,\n"
                                              "    lib3,\n"
                                              "    lib4,\n"
                                              "    lib5,\n"
                                              "    lib6,\n"
                                              "    lib7,\n"
                                              "    lib8,\n"
                                              "    lib9,\n"
                                              "    lib10,\n"
                                              "    lib11,\n"
                                              "    lib12,\n"
                                              "    lib13,\n"
                                              "    lib14,\n"
                                              "    lib15,\n"
                                              "    lib16,\n"
                                              "    lib17,\n"
                                              "    lib18,\n"
                                              "    lib20,\n"
                                              "    lib21,\n"
                                              "    lib22\n"
                                              ")\n")

    test_output_vertical_grid = SortImports(file_contents=REALLY_LONG_IMPORT,
                                            multi_line_output=WrapModes.VERTICAL_GRID,
                                            line_length=40, indent="    ").output
    assert test_output_vertical_grid == ("from third_party import (\n"
                                         "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
                                         "    lib7, lib8, lib9, lib10, lib11,\n"
                                         "    lib12, lib13, lib14, lib15, lib16,\n"
                                         "    lib17, lib18, lib20, lib21, lib22)\n")

    comment_output_vertical_grid = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                                               multi_line_output=WrapModes.VERTICAL_GRID,
                                               line_length=40, indent="    ").output
    assert comment_output_vertical_grid == ("from third_party import (  # comment\n"
                                            "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
                                            "    lib7, lib8, lib9, lib10, lib11,\n"
                                            "    lib12, lib13, lib14, lib15, lib16,\n"
                                            "    lib17, lib18, lib20, lib21, lib22)\n")

    test_output_vertical_grid_grouped = SortImports(file_contents=REALLY_LONG_IMPORT,
                                                    multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
                                                    line_length=40, indent="    ").output
    assert test_output_vertical_grid_grouped == ("from third_party import (\n"
                                                 "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
                                                 "    lib7, lib8, lib9, lib10, lib11,\n"
                                                 "    lib12, lib13, lib14, lib15, lib16,\n"
                                                 "    lib17, lib18, lib20, lib21, lib22\n"
                                                 ")\n")

    comment_output_vertical_grid_grouped = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                                                       multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
                                                       line_length=40, indent="    ").output
    assert comment_output_vertical_grid_grouped == ("from third_party import (  # comment\n"
                                                    "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
                                                    "    lib7, lib8, lib9, lib10, lib11,\n"
                                                    "    lib12, lib13, lib14, lib15, lib16,\n"
                                                    "    lib17, lib18, lib20, lib21, lib22\n"
                                                    ")\n")

    output_noqa = SortImports(file_contents=REALLY_LONG_IMPORT_WITH_COMMENT,
                              multi_line_output=WrapModes.NOQA).output
    assert output_noqa == ("from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11,"
                           " lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22  "
                           "# NOQA comment\n")

    test_case = SortImports(file_contents=SINGLE_LINE_LONG_IMPORT,
                            multi_line_output=WrapModes.VERTICAL_GRID_GROUPED_NO_COMMA,
                            line_length=40, indent='    ').output
    test_output_vertical_grid_grouped_doesnt_wrap_early = test_case
    assert test_output_vertical_grid_grouped_doesnt_wrap_early == ("from third_party import (\n"
                                                                   "    lib1, lib2, lib3, lib4, lib5, lib5ab\n"
                                                                   ")\n")


def test_qa_comment_case():
    test_input = "from veryveryveryveryveryveryveryveryveryveryvery import X  # NOQA"
    test_output = SortImports(file_contents=test_input, line_length=40, multi_line_output=WrapModes.NOQA).output
    assert test_output == "from veryveryveryveryveryveryveryveryveryveryvery import X  # NOQA\n"

    test_input = "import veryveryveryveryveryveryveryveryveryveryvery  # NOQA"
    test_output = SortImports(file_contents=test_input, line_length=40, multi_line_output=WrapModes.NOQA).output
    assert test_output == "import veryveryveryveryveryveryveryveryveryveryvery  # NOQA\n"


def test_length_sort():
    """Test setting isort to sort on length instead of alphabetically."""
    test_input = ("import medium_sizeeeeeeeeeeeeee\n"
                  "import shortie\n"
                  "import looooooooooooooooooooooooooooooooooooooong\n"
                  "import medium_sizeeeeeeeeeeeeea\n")
    test_output = SortImports(file_contents=test_input, length_sort=True).output
    assert test_output == ("import shortie\n"
                           "import medium_sizeeeeeeeeeeeeea\n"
                           "import medium_sizeeeeeeeeeeeeee\n"
                           "import looooooooooooooooooooooooooooooooooooooong\n")


def test_length_sort_section():
    """Test setting isort to sort on length instead of alphabetically for a specific section."""
    test_input = ("import medium_sizeeeeeeeeeeeeee\n"
                  "import shortie\n"
                  "import sys\n"
                  "import os\n"
                  "import looooooooooooooooooooooooooooooooooooooong\n"
                  "import medium_sizeeeeeeeeeeeeea\n")
    test_output = SortImports(file_contents=test_input, length_sort_stdlib=True).output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "\n"
                           "import looooooooooooooooooooooooooooooooooooooong\n"
                           "import medium_sizeeeeeeeeeeeeea\n"
                           "import medium_sizeeeeeeeeeeeeee\n"
                           "import shortie\n")


def test_convert_hanging():
    """Ensure that isort will convert hanging indents to correct indent
    method."""
    test_input = ("from third_party import lib1, lib2, \\\n"
                  "    lib3, lib4, lib5, lib6, lib7, \\\n"
                  "    lib8, lib9, lib10, lib11, lib12, \\\n"
                  "    lib13, lib14, lib15, lib16, lib17, \\\n"
                  "    lib18, lib20, lib21, lib22\n")
    test_output = SortImports(file_contents=test_input, multi_line_output=WrapModes.GRID,
                              line_length=40).output
    assert test_output == ("from third_party import (lib1, lib2,\n"
                           "                         lib3, lib4,\n"
                           "                         lib5, lib6,\n"
                           "                         lib7, lib8,\n"
                           "                         lib9, lib10,\n"
                           "                         lib11, lib12,\n"
                           "                         lib13, lib14,\n"
                           "                         lib15, lib16,\n"
                           "                         lib17, lib18,\n"
                           "                         lib20, lib21,\n"
                           "                         lib22)\n")


def test_custom_indent():
    """Ensure setting a custom indent will work as expected."""
    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, multi_line_output=WrapModes.HANGING_INDENT,
                              line_length=40, indent="   ", balanced_wrapping=False).output
    assert test_output == ("from third_party import lib1, lib2, \\\n"
                           "   lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
                           "   lib9, lib10, lib11, lib12, lib13, \\\n"
                           "   lib14, lib15, lib16, lib17, lib18, \\\n"
                           "   lib20, lib21, lib22\n")

    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, multi_line_output=WrapModes.HANGING_INDENT,
                              line_length=40, indent="'  '", balanced_wrapping=False).output
    assert test_output == ("from third_party import lib1, lib2, \\\n"
                           "  lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
                           "  lib9, lib10, lib11, lib12, lib13, \\\n"
                           "  lib14, lib15, lib16, lib17, lib18, \\\n"
                           "  lib20, lib21, lib22\n")

    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, multi_line_output=WrapModes.HANGING_INDENT,
                              line_length=40, indent="tab", balanced_wrapping=False).output
    assert test_output == ("from third_party import lib1, lib2, \\\n"
                           "\tlib3, lib4, lib5, lib6, lib7, lib8, \\\n"
                           "\tlib9, lib10, lib11, lib12, lib13, \\\n"
                           "\tlib14, lib15, lib16, lib17, lib18, \\\n"
                           "\tlib20, lib21, lib22\n")

    test_output = SortImports(file_contents=REALLY_LONG_IMPORT, multi_line_output=WrapModes.HANGING_INDENT,
                              line_length=40, indent=2, balanced_wrapping=False).output
    assert test_output == ("from third_party import lib1, lib2, \\\n"
                           "  lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
                           "  lib9, lib10, lib11, lib12, lib13, \\\n"
                           "  lib14, lib15, lib16, lib17, lib18, \\\n"
                           "  lib20, lib21, lib22\n")


def test_use_parentheses():
    test_input = (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import "
        "    my_custom_function as my_special_function"
    )
    test_output = SortImports(
        file_contents=test_input, line_length=79, use_parentheses=True
    ).output

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function)\n"
    )

    test_output = SortImports(
        file_contents=test_input, line_length=79, use_parentheses=True,
        include_trailing_comma=True,
    ).output

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function,)\n"
    )

    test_output = SortImports(
        file_contents=test_input, line_length=79, use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT
    ).output

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function\n)\n"
    )

    test_output = SortImports(
        file_contents=test_input, line_length=79, use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        include_trailing_comma=True
    ).output

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function,\n)\n"
    )


def test_skip():
    """Ensure skipping a single import will work as expected."""
    test_input = ("import myproject\n"
                  "import django\n"
                  "print('hey')\n"
                  "import sys  # isort:skip this import needs to be placed here\n\n\n\n\n\n\n")

    test_output = SortImports(file_contents=test_input, known_third_party=['django']).output
    assert test_output == ("import django\n"
                           "\n"
                           "import myproject\n"
                           "\n"
                           "print('hey')\n"
                           "import sys  # isort:skip this import needs to be placed here\n")


def test_skip_with_file_name():
    """Ensure skipping a file works even when file_contents is provided."""
    test_input = ("import django\n"
                  "import myproject\n")

    sort_imports = SortImports(file_path='/baz.py', file_contents=test_input, settings_path=os.getcwd(),
                               skip=['baz.py'])
    assert sort_imports.skipped
    assert sort_imports.output is None


def test_skip_within_file():
    """Ensure skipping a whole file works."""
    test_input = ("# isort:skip_file\n"
                  "import django\n"
                  "import myproject\n")
    sort_imports = SortImports(file_contents=test_input, known_third_party=['django'])
    assert sort_imports.skipped
    assert sort_imports.output is None


def test_force_to_top():
    """Ensure forcing a single import to the top of its category works as expected."""
    test_input = ("import lib6\n"
                  "import lib2\n"
                  "import lib5\n"
                  "import lib1\n")
    test_output = SortImports(file_contents=test_input, force_to_top=['lib5']).output
    assert test_output == ("import lib5\n"
                           "import lib1\n"
                           "import lib2\n"
                           "import lib6\n")


def test_add_imports():
    """Ensures adding imports works as expected."""
    test_input = ("import lib6\n"
                  "import lib2\n"
                  "import lib5\n"
                  "import lib1\n\n")
    test_output = SortImports(file_contents=test_input, add_imports=['import lib4', 'import lib7']).output
    assert test_output == ("import lib1\n"
                           "import lib2\n"
                           "import lib4\n"
                           "import lib5\n"
                           "import lib6\n"
                           "import lib7\n")

    # Using simplified syntax
    test_input = ("import lib6\n"
                  "import lib2\n"
                  "import lib5\n"
                  "import lib1\n\n")
    test_output = SortImports(file_contents=test_input, add_imports=['lib4', 'lib7', 'lib8.a']).output
    assert test_output == ("import lib1\n"
                           "import lib2\n"
                           "import lib4\n"
                           "import lib5\n"
                           "import lib6\n"
                           "import lib7\n"
                           "from lib8 import a\n")

    # On a file that has no pre-existing imports
    test_input = ('"""Module docstring"""\n'
                  '\n'
                  'class MyClass(object):\n'
                  '    pass\n')
    test_output = SortImports(file_contents=test_input, add_imports=['from __future__ import print_function']).output
    assert test_output == ('"""Module docstring"""\n'
                           'from __future__ import print_function\n'
                           '\n'
                           '\n'
                           'class MyClass(object):\n'
                           '    pass\n')

    # On a file that has no pre-existing imports, and no doc-string
    test_input = ('class MyClass(object):\n'
                  '    pass\n')
    test_output = SortImports(file_contents=test_input, add_imports=['from __future__ import print_function']).output
    assert test_output == ('from __future__ import print_function\n'
                           '\n'
                           '\n'
                           'class MyClass(object):\n'
                           '    pass\n')

    # On a file with no content what so ever
    test_input = ("")
    test_output = SortImports(file_contents=test_input, add_imports=['lib4']).output
    assert test_output == ("")

    # On a file with no content what so ever, after force_adds is set to True
    test_input = ("")
    test_output = SortImports(file_contents=test_input, add_imports=['lib4'], force_adds=True).output
    assert test_output == ("import lib4\n")


def test_remove_imports():
    """Ensures removing imports works as expected."""
    test_input = ("import lib6\n"
                  "import lib2\n"
                  "import lib5\n"
                  "import lib1")
    test_output = SortImports(file_contents=test_input, remove_imports=['lib2', 'lib6']).output
    assert test_output == ("import lib1\n"
                           "import lib5\n")

    # Using natural syntax
    test_input = ("import lib6\n"
                  "import lib2\n"
                  "import lib5\n"
                  "import lib1\n"
                  "from lib8 import a")
    test_output = SortImports(file_contents=test_input, remove_imports=['import lib2', 'import lib6',
                                                                        'from lib8 import a']).output
    assert test_output == ("import lib1\n"
                           "import lib5\n")


def test_explicitly_local_import():
    """Ensure that explicitly local imports are separated."""
    test_input = ("import lib1\n"
                  "import lib2\n"
                  "import .lib6\n"
                  "from . import lib7")
    assert SortImports(file_contents=test_input).output == ("import lib1\n"
                                                            "import lib2\n"
                                                            "\n"
                                                            "import .lib6\n"
                                                            "from . import lib7\n")


def test_quotes_in_file():
    """Ensure imports within triple quotes don't get imported."""
    test_input = ('import os\n'
                  '\n'
                  '"""\n'
                  'Let us\n'
                  'import foo\n'
                  'okay?\n'
                  '"""\n')
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ('import os\n'
                  '\n'
                  "'\"\"\"'\n"
                  'import foo\n')
    assert SortImports(file_contents=test_input).output == ('import os\n'
                                                            '\n'
                                                            'import foo\n'
                                                            '\n'
                                                            "'\"\"\"'\n")

    test_input = ('import os\n'
                  '\n'
                  '"""Let us"""\n'
                  'import foo\n'
                  '"""okay?"""\n')
    assert SortImports(file_contents=test_input).output == ('import os\n'
                                                            '\n'
                                                            'import foo\n'
                                                            '\n'
                                                            '"""Let us"""\n'
                                                            '"""okay?"""\n')

    test_input = ('import os\n'
                  '\n'
                  '#"""\n'
                  'import foo\n'
                  '#"""')
    assert SortImports(file_contents=test_input).output == ('import os\n'
                                                            '\n'
                                                            'import foo\n'
                                                            '\n'
                                                            '#"""\n'
                                                            '#"""\n')

    test_input = ('import os\n'
                  '\n'
                  "'\\\n"
                  "import foo'\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ('import os\n'
                  '\n'
                  "'''\n"
                  "\\'''\n"
                  'import junk\n'
                  "'''\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_check_newline_in_imports(capsys):
    """Ensure tests works correctly when new lines are in imports."""
    test_input = ('from lib1 import (\n'
                  '    sub1,\n'
                  '    sub2,\n'
                  '    sub3\n)\n')

    SortImports(file_contents=test_input, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20,
                check=True, verbose=True)
    out, err = capsys.readouterr()
    assert 'SUCCESS' in out


def test_forced_separate():
    """Ensure that forcing certain sub modules to show separately works as expected."""
    test_input = ('import sys\n'
                  'import warnings\n'
                  'from collections import OrderedDict\n'
                  '\n'
                  'from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation\n'
                  'from django.core.paginator import InvalidPage\n'
                  'from django.core.urlresolvers import reverse\n'
                  'from django.db import models\n'
                  'from django.db.models.fields import FieldDoesNotExist\n'
                  'from django.utils import six\n'
                  'from django.utils.deprecation import RenameMethodsBase\n'
                  'from django.utils.encoding import force_str, force_text\n'
                  'from django.utils.http import urlencode\n'
                  'from django.utils.translation import ugettext, ugettext_lazy\n'
                  '\n'
                  'from django.contrib.admin import FieldListFilter\n'
                  'from django.contrib.admin.exceptions import DisallowedModelAdminLookup\n'
                  'from django.contrib.admin.options import IncorrectLookupParameters, IS_POPUP_VAR, TO_FIELD_VAR\n')
    assert SortImports(file_contents=test_input, forced_separate=['django.contrib'],
                       known_third_party=['django'], line_length=120, order_by_type=False).output == test_input

    test_input = ('from .foo import bar\n'
                  '\n'
                  'from .y import ca\n')
    assert SortImports(file_contents=test_input, forced_separate=['.y'],
                       line_length=120, order_by_type=False).output == test_input


def test_default_section():
    """Test to ensure changing the default section works as expected."""
    test_input = ("import sys\n"
                  "import os\n"
                  "import myproject.test\n"
                  "import django.settings")
    test_output = SortImports(file_contents=test_input, known_third_party=['django'],
                              default_section="FIRSTPARTY").output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "\n"
                           "import django.settings\n"
                           "\n"
                           "import myproject.test\n")

    test_output_custom = SortImports(file_contents=test_input, known_third_party=['django'],
                                     default_section="STDLIB").output
    assert test_output_custom == ("import myproject.test\n"
                                  "import os\n"
                                  "import sys\n"
                                  "\n"
                                  "import django.settings\n")


def test_first_party_overrides_standard_section():
    """Test to ensure changing the default section works as expected."""
    test_input = ("from HTMLParser import HTMLParseError, HTMLParser\n"
                  "import sys\n"
                  "import os\n"
                  "import this\n"
                  "import profile.test\n")
    test_output = SortImports(file_contents=test_input, known_first_party=['profile']).output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "import this\n"
                           "from HTMLParser import HTMLParseError, HTMLParser\n"
                           "\n"
                           "import profile.test\n")


def test_thirdy_party_overrides_standard_section():
    """Test to ensure changing the default section works as expected."""
    test_input = ("import sys\n"
                  "import os\n"
                  "import this\n"
                  "import profile.test\n")
    test_output = SortImports(file_contents=test_input, known_third_party=['profile']).output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "import this\n"
                           "\n"
                           "import profile.test\n")


def test_known_pattern_path_expansion():
    """Test to ensure patterns ending with path sep gets expanded and nested packages treated as known patterns"""
    test_input = ("from kate_plugin import isort_plugin\n"
                  "import sys\n"
                  "import isort.settings\n"
                  "import this\n"
                  "import os\n")
    test_output = SortImports(
        file_contents=test_input,
        default_section='THIRDPARTY',
        known_first_party=['./', 'this', 'kate_plugin']
    ).output
    assert test_output == ("import os\n"
                            "import sys\n"
                            "\n"
                            "import isort.settings\n"
                            "import this\n"
                            "from kate_plugin import isort_plugin\n")


def test_force_single_line_imports():
    """Test to ensure forcing imports to each have their own line works as expected."""
    test_input = ("from third_party import lib1, lib2, \\\n"
                  "    lib3, lib4, lib5, lib6, lib7, \\\n"
                  "    lib8, lib9, lib10, lib11, lib12, \\\n"
                  "    lib13, lib14, lib15, lib16, lib17, \\\n"
                  "    lib18, lib20, lib21, lib22\n")
    test_output = SortImports(file_contents=test_input, multi_line_output=WrapModes.GRID,
                              line_length=40, force_single_line=True).output
    assert test_output == ("from third_party import lib1\n"
                           "from third_party import lib2\n"
                           "from third_party import lib3\n"
                           "from third_party import lib4\n"
                           "from third_party import lib5\n"
                           "from third_party import lib6\n"
                           "from third_party import lib7\n"
                           "from third_party import lib8\n"
                           "from third_party import lib9\n"
                           "from third_party import lib10\n"
                           "from third_party import lib11\n"
                           "from third_party import lib12\n"
                           "from third_party import lib13\n"
                           "from third_party import lib14\n"
                           "from third_party import lib15\n"
                           "from third_party import lib16\n"
                           "from third_party import lib17\n"
                           "from third_party import lib18\n"
                           "from third_party import lib20\n"
                           "from third_party import lib21\n"
                           "from third_party import lib22\n")


def test_force_single_line_long_imports():
    test_input = ("from veryveryveryveryveryvery import small, big\n")
    test_output = SortImports(file_contents=test_input, multi_line_output=WrapModes.NOQA,
                              line_length=40, force_single_line=True).output
    assert test_output == ("from veryveryveryveryveryvery import big\n"
                           "from veryveryveryveryveryvery import small  # NOQA\n")


def test_titled_imports():
    """Tests setting custom titled/commented import sections."""
    test_input = ("import sys\n"
                  "import unicodedata\n"
                  "import statistics\n"
                  "import os\n"
                  "import myproject.test\n"
                  "import django.settings")
    test_output = SortImports(file_contents=test_input, known_third_party=['django'],
                              import_heading_stdlib="Standard Library", import_heading_firstparty="My Stuff").output
    assert test_output == ("# Standard Library\n"
                           "import os\n"
                           "import statistics\n"
                           "import sys\n"
                           "import unicodedata\n"
                           "\n"
                           "import django.settings\n"
                           "\n"
                           "# My Stuff\n"
                           "import myproject.test\n")
    test_second_run = SortImports(file_contents=test_output, known_third_party=['django'],
                                  import_heading_stdlib="Standard Library", import_heading_firstparty="My Stuff").output
    assert test_second_run == test_output


def test_balanced_wrapping():
    """Tests balanced wrapping mode, where the length of individual lines maintain width."""
    test_input = ("from __future__ import (absolute_import, division, print_function,\n"
                  "                        unicode_literals)")
    test_output = SortImports(file_contents=test_input, line_length=70, balanced_wrapping=True).output
    assert test_output == ("from __future__ import (absolute_import, division,\n"
                           "                        print_function, unicode_literals)\n")


def test_relative_import_with_space():
    """Tests the case where the relation and the module that is being imported from is separated with a space."""
    test_input = ("from ... fields.sproqet import SproqetCollection")
    assert SortImports(file_contents=test_input).output == ("from ...fields.sproqet import SproqetCollection\n")
    test_input = ("from .import foo")
    test_output = ("from . import foo\n")
    assert SortImports(file_contents=test_input).output == test_output
    test_input = ("from.import foo")
    test_output = ("from . import foo\n")
    assert SortImports(file_contents=test_input).output == test_output


def test_multiline_import():
    """Test the case where import spawns multiple lines with inconsistent indentation."""
    test_input = ("from pkg \\\n"
                  "    import stuff, other_suff \\\n"
                  "               more_stuff")
    assert SortImports(file_contents=test_input).output == ("from pkg import more_stuff, other_suff, stuff\n")

    # test again with a custom configuration
    custom_configuration = {'force_single_line': True,
                            'line_length': 120,
                            'known_first_party': ['asdf', 'qwer'],
                            'default_section': 'THIRDPARTY',
                            'forced_separate': 'asdf'}
    expected_output = ("from pkg import more_stuff\n"
                       "from pkg import other_suff\n"
                       "from pkg import stuff\n")
    assert SortImports(file_contents=test_input, **custom_configuration).output == expected_output


def test_single_multiline():
    """Test the case where a single import spawns multiple lines."""
    test_input = ("from os import\\\n"
                  "        getuid\n"
                  "\n"
                  "print getuid()\n")
    output = SortImports(file_contents=test_input).output
    assert output == (
        "from os import getuid\n"
        "\n"
        "print getuid()\n"
    )


def test_atomic_mode():
    # without syntax error, everything works OK
    test_input = ("from b import d, c\n"
                  "from a import f, e\n")
    assert SortImports(file_contents=test_input, atomic=True).output == ("from a import e, f\n"
                                                                          "from b import c, d\n")

    # with syntax error content is not changed
    test_input += "while True print 'Hello world'"  # blatant syntax error
    assert SortImports(file_contents=test_input, atomic=True).output == test_input


def test_order_by_type():
    test_input = "from module import Class, CONSTANT, function"
    assert SortImports(file_contents=test_input,
                       order_by_type=True).output == ("from module import CONSTANT, Class, function\n")

    # More complex sample data
    test_input = "from module import Class, CONSTANT, function, BASIC, Apple"
    assert SortImports(file_contents=test_input,
                       order_by_type=True).output == ("from module import BASIC, CONSTANT, Apple, Class, function\n")

    # Really complex sample data, to verify we don't mess with top level imports, only nested ones
    test_input = ("import StringIO\n"
                  "import glob\n"
                  "import os\n"
                  "import shutil\n"
                  "import tempfile\n"
                  "import time\n"
                  "from subprocess import PIPE, Popen, STDOUT\n")

    assert SortImports(file_contents=test_input, order_by_type=True).output == \
                ("import glob\n"
                 "import os\n"
                 "import shutil\n"
                 "import StringIO\n"
                 "import tempfile\n"
                 "import time\n"
                 "from subprocess import PIPE, STDOUT, Popen\n")


def test_custom_lines_after_import_section():
    """Test the case where the number of lines to output after imports has been explicitly set."""
    test_input = ("from a import b\n"
                  "foo = 'bar'\n")

    # default case is one space if not method or class after imports
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "foo = 'bar'\n")

    # test again with a custom number of lines after the import section
    assert SortImports(file_contents=test_input, lines_after_imports=2).output == ("from a import b\n"
                                                                                   "\n"
                                                                                   "\n"
                                                                                   "foo = 'bar'\n")


def test_smart_lines_after_import_section():
    """Tests the default 'smart' behavior for dealing with lines after the import section"""
    # one space if not method or class after imports
    test_input = ("from a import b\n"
                  "foo = 'bar'\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "foo = 'bar'\n")

    # two spaces if a method or class after imports
    test_input = ("from a import b\n"
                  "def my_function():\n"
                  "    pass\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "\n"
                                                            "def my_function():\n"
                                                            "    pass\n")

    # two spaces if an async method after imports
    test_input = ("from a import b\n"
                  "async def my_function():\n"
                  "    pass\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "\n"
                                                            "async def my_function():\n"
                                                            "    pass\n")

    # two spaces if a method or class after imports - even if comment before function
    test_input = ("from a import b\n"
                  "# comment should be ignored\n"
                  "def my_function():\n"
                  "    pass\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "\n"
                                                            "# comment should be ignored\n"
                                                            "def my_function():\n"
                                                            "    pass\n")

    # ensure logic works with both style comments
    test_input = ("from a import b\n"
                  '"""\n'
                  "    comment should be ignored\n"
                  '"""\n'
                  "def my_function():\n"
                  "    pass\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            "\n"
                                                            '"""\n'
                                                            "    comment should be ignored\n"
                                                            '"""\n'
                                                            "def my_function():\n"
                                                            "    pass\n")

    # Ensure logic doesn't incorrectly skip over assignments to multi-line strings
    test_input = ("from a import b\n"
                  'X = """test\n'
                  '"""\n'
                  "def my_function():\n"
                  "    pass\n")
    assert SortImports(file_contents=test_input).output == ("from a import b\n"
                                                            "\n"
                                                            'X = """test\n'
                                                            '"""\n'
                                                            "def my_function():\n"
                                                            "    pass\n")


def test_settings_combine_instead_of_overwrite():
    """Test to ensure settings combine logically, instead of fully overwriting."""
    assert set(SortImports(known_standard_library=['not_std_library']).config['known_standard_library']) == \
           set(SortImports().config['known_standard_library'] + ['not_std_library'])

    assert set(SortImports(not_known_standard_library=['thread']).config['known_standard_library']) == \
           {item for item in SortImports().config['known_standard_library'] if item != 'thread'}


def test_combined_from_and_as_imports():
    """Test to ensure it's possible to combine from and as imports."""
    test_input = ("from translate.misc.multistring import multistring\n"
                  "from translate.storage import base, factory\n"
                  "from translate.storage.placeables import general, parse as rich_parse\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == test_input
    test_input = ("import os \nimport os as _os")
    test_output = ("import os\nimport os as _os\n")
    assert SortImports(file_contents=test_input, keep_direct_and_as_imports=True).output == test_output


def test_as_imports_with_line_length():
    """Test to ensure it's possible to combine from and as imports."""
    test_input = ("from translate.storage import base as storage_base\n"
                  "from translate.storage.placeables import general, parse as rich_parse\n")
    assert SortImports(file_contents=test_input, combine_as_imports=False, line_length=40).output == \
                  ("from translate.storage import \\\n    base as storage_base\n"
                   "from translate.storage.placeables import \\\n    general\n"
                   "from translate.storage.placeables import \\\n    parse as rich_parse\n")


def test_keep_comments():
    """Test to ensure isort properly keeps comments in tact after sorting."""
    # Straight Import
    test_input = ("import foo  # bar\n")
    assert SortImports(file_contents=test_input).output == test_input

    # Star import
    test_input_star = ("from foo import *  # bar\n")
    assert SortImports(file_contents=test_input_star).output == test_input_star

    # Force Single Line From Import
    test_input = ("from foo import bar  # comment\n")
    assert SortImports(file_contents=test_input, force_single_line=True).output == test_input

    # From import
    test_input = ("from foo import bar  # My Comment\n")
    assert SortImports(file_contents=test_input).output == test_input

    # More complicated case
    test_input = ("from a import b  # My Comment1\n"
                  "from a import c  # My Comment2\n")
    assert SortImports(file_contents=test_input).output == \
                      ("from a import b  # My Comment1\n"
                       "from a import c  # My Comment2\n")

    # Test case where imports comments make imports extend pass the line length
    test_input = ("from a import b # My Comment1\n"
                  "from a import c # My Comment2\n"
                  "from a import d\n")
    assert SortImports(file_contents=test_input, line_length=45).output == \
                      ("from a import b  # My Comment1\n"
                       "from a import c  # My Comment2\n"
                       "from a import d\n")

    # Test case where imports with comments will be beyond line length limit
    test_input = ("from a import b, c  # My Comment1\n"
                  "from a import c, d # My Comment2 is really really really really long\n")
    assert SortImports(file_contents=test_input, line_length=45).output == \
                      ("from a import (  # My Comment1; My Comment2 is really really really really long\n"
                       "    b, c, d)\n")

    # Test that comments are not stripped from 'import ... as ...' by default
    test_input = ("from a import b as bb  # b comment\n"
                  "from a import c as cc  # c comment\n")
    assert SortImports(file_contents=test_input).output == test_input

    # Test that 'import ... as ...' comments are not collected inappropriately
    test_input = ("from a import b as bb  # b comment\n"
                  "from a import c as cc  # c comment\n"
                  "from a import d\n")
    assert SortImports(file_contents=test_input).output == test_input
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == (
        "from a import b as bb, c as cc, d  # b comment; c comment\n"
    )


def test_multiline_split_on_dot():
    """Test to ensure isort correctly handles multiline imports, even when split right after a '.'"""
    test_input = ("from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5.\\\n"
                  "    my_module import my_function")
    assert SortImports(file_contents=test_input, line_length=70).output == \
            ("from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5.my_module import \\\n"
             "    my_function\n")


def test_import_star():
    """Test to ensure isort handles star imports correctly"""
    test_input = ("from blah import *\n"
                  "from blah import _potato\n")
    assert SortImports(file_contents=test_input).output == ("from blah import *\n"
                                                            "from blah import _potato\n")
    assert SortImports(file_contents=test_input, combine_star=True).output == ("from blah import *\n")


def test_include_trailing_comma():
    """Test for the include_trailing_comma option"""
    test_output_grid = SortImports(
        file_contents=SHORT_IMPORT,
        multi_line_output=WrapModes.GRID,
        line_length=40,
        include_trailing_comma=True,
    ).output
    assert test_output_grid == (
        "from third_party import (lib1, lib2,\n"
        "                         lib3, lib4,)\n"
    )

    test_output_vertical = SortImports(
        file_contents=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL,
        line_length=40,
        include_trailing_comma=True,
    ).output
    assert test_output_vertical == (
        "from third_party import (lib1,\n"
        "                         lib2,\n"
        "                         lib3,\n"
        "                         lib4,)\n"
    )

    test_output_vertical_indent = SortImports(
        file_contents=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=40,
        include_trailing_comma=True,
    ).output
    assert test_output_vertical_indent == (
        "from third_party import (\n"
        "    lib1,\n"
        "    lib2,\n"
        "    lib3,\n"
        "    lib4,\n"
        ")\n"
    )

    test_output_vertical_grid = SortImports(
        file_contents=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID,
        line_length=40,
        include_trailing_comma=True,
    ).output
    assert test_output_vertical_grid == (
        "from third_party import (\n"
        "    lib1, lib2, lib3, lib4,)\n"
    )

    test_output_vertical_grid_grouped = SortImports(
        file_contents=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        line_length=40,
        include_trailing_comma=True,
    ).output
    assert test_output_vertical_grid_grouped == (
        "from third_party import (\n"
        "    lib1, lib2, lib3, lib4,\n"
        ")\n"
    )

    test_output_wrap_single_import_with_use_parentheses = SortImports(
        file_contents=SINGLE_FROM_IMPORT,
        line_length=25,
        include_trailing_comma=True,
        use_parentheses=True
    ).output
    assert test_output_wrap_single_import_with_use_parentheses == (
        "from third_party import (\n"
        "    lib1,)\n"
    )

    test_output_wrap_single_import_vertical_indent = SortImports(
        file_contents=SINGLE_FROM_IMPORT,
        line_length=25,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        include_trailing_comma=True,
        use_parentheses=True
    ).output
    assert test_output_wrap_single_import_vertical_indent == (
        "from third_party import (\n"
        "    lib1,\n"
        ")\n"
    )


def test_similar_to_std_library():
    """Test to ensure modules that are named similarly to a standard library import don't end up clobbered"""
    test_input = ("import datetime\n"
                  "\n"
                  "import requests\n"
                  "import times\n")
    assert SortImports(file_contents=test_input, known_third_party=["requests", "times"]).output == test_input


def test_correctly_placed_imports():
    """Test to ensure comments stay on correct placement after being sorted"""
    test_input = ("from a import b # comment for b\n"
                  "from a import c # comment for c\n")
    assert SortImports(file_contents=test_input, force_single_line=True).output == \
                      ("from a import b  # comment for b\n"
                       "from a import c  # comment for c\n")
    assert SortImports(file_contents=test_input).output == ("from a import b  # comment for b\n"
                                                            "from a import c  # comment for c\n")

    # Full example test from issue #143
    test_input = ("from itertools import chain\n"
                  "\n"
                  "from django.test import TestCase\n"
                  "from model_mommy import mommy\n"
                  "\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_item_product\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_item_product_d"
                  "efinition\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_item_product_d"
                  "efinition_platform\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_item_product_p"
                  "latform\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_territory_reta"
                  "il_model\n"
                  "from apps.clientman.commands.download_usage_rights import associate_right_for_territory_reta"
                  "il_model_definition_platform_provider  # noqa\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_item_product\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_item_product_defini"
                  "tion\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_item_product_defini"
                  "tion_platform\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_item_product_platfo"
                  "rm\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_territory_retail_mo"
                  "del\n"
                  "from apps.clientman.commands.download_usage_rights import clear_right_for_territory_retail_mo"
                  "del_definition_platform_provider  # noqa\n"
                  "from apps.clientman.commands.download_usage_rights import create_download_usage_right\n"
                  "from apps.clientman.commands.download_usage_rights import delete_download_usage_right\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_item_product\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_item_product_d"
                  "efinition\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_item_product_d"
                  "efinition_platform\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_item_product_p"
                  "latform\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_territory_reta"
                  "il_model\n"
                  "from apps.clientman.commands.download_usage_rights import disable_download_for_territory_reta"
                  "il_model_definition_platform_provider  # noqa\n"
                  "from apps.clientman.commands.download_usage_rights import get_download_rights_for_item\n"
                  "from apps.clientman.commands.download_usage_rights import get_right\n")
    assert SortImports(file_contents=test_input, force_single_line=True, line_length=140,
                       known_third_party=["django", "model_mommy"]).output == test_input


def test_auto_detection():
    """Initial test to ensure isort auto-detection works correctly - will grow over time as new issues are raised."""

    # Issue 157
    test_input = ("import binascii\n"
                  "import os\n"
                  "\n"
                  "import cv2\n"
                  "import requests\n")
    assert SortImports(file_contents=test_input, known_third_party=["cv2", "requests"]).output == test_input

    # alternative solution
    assert SortImports(file_contents=test_input, default_section="THIRDPARTY").output == test_input


def test_same_line_statements():
    """Ensure isort correctly handles the case where a single line contains multiple statements including an import"""
    test_input = ("import pdb; import nose\n")
    assert SortImports(file_contents=test_input).output == ("import pdb\n"
                                                            "\n"
                                                            "import nose\n")

    test_input = ("import pdb; pdb.set_trace()\n"
                  "import nose; nose.run()\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_long_line_comments():
    """Ensure isort correctly handles comments at the end of extremely long lines"""
    test_input = ("from foo.utils.fabric_stuff.live import check_clean_live, deploy_live, sync_live_envdir, "
                  "update_live_app, update_live_cron  # noqa\n"
                  "from foo.utils.fabric_stuff.stage import check_clean_stage, deploy_stage, sync_stage_envdir, "
                  "update_stage_app, update_stage_cron  # noqa\n")
    assert SortImports(file_contents=test_input).output == \
                ("from foo.utils.fabric_stuff.live import (check_clean_live, deploy_live,  # noqa\n"
                 "                                         sync_live_envdir, update_live_app, update_live_cron)\n"
                 "from foo.utils.fabric_stuff.stage import (check_clean_stage, deploy_stage,  # noqa\n"
                 "                                          sync_stage_envdir, update_stage_app, update_stage_cron)\n")


def test_tab_character_in_import():
    """Ensure isort correctly handles import statements that contain a tab character"""
    test_input = ("from __future__ import print_function\n"
                  "from __future__ import\tprint_function\n")
    assert SortImports(file_contents=test_input).output == "from __future__ import print_function\n"


def test_split_position():
    """Ensure isort splits on import instead of . when possible"""
    test_input = ("from p24.shared.exceptions.master.host_state_flag_unchanged import HostStateUnchangedException\n")
    assert SortImports(file_contents=test_input, line_length=80).output == \
                                            ("from p24.shared.exceptions.master.host_state_flag_unchanged import \\\n"
                                             "    HostStateUnchangedException\n")


def test_place_comments():
    """Ensure manually placing imports works as expected"""
    test_input = ("import sys\n"
                  "import os\n"
                  "import myproject.test\n"
                  "import django.settings\n"
                  "\n"
                  "# isort:imports-thirdparty\n"
                  "# isort:imports-firstparty\n"
                  "print('code')\n"
                  "\n"
                  "# isort:imports-stdlib\n")
    expected_output = ("\n# isort:imports-thirdparty\n"
                       "import django.settings\n"
                       "\n"
                       "# isort:imports-firstparty\n"
                       "import myproject.test\n"
                       "\n"
                       "print('code')\n"
                       "\n"
                       "# isort:imports-stdlib\n"
                       "import os\n"
                       "import sys\n")
    test_output = SortImports(file_contents=test_input, known_third_party=['django']).output
    assert test_output == expected_output
    test_output = SortImports(file_contents=test_output, known_third_party=['django']).output
    assert test_output == expected_output


def test_placement_control():
    """Ensure that most specific placement control match wins"""
    test_input = ("import os\n"
                  "import sys\n"
                  "from bottle import Bottle, redirect, response, run\n"
                  "import p24.imports._argparse as argparse\n"
                  "import p24.imports._subprocess as subprocess\n"
                  "import p24.imports._VERSION as VERSION\n"
                  "import p24.shared.media_wiki_syntax as syntax\n")
    test_output = SortImports(file_contents=test_input,
                known_first_party=['p24', 'p24.imports._VERSION'],
                known_standard_library=['p24.imports'],
                known_third_party=['bottle'],
                default_section="THIRDPARTY").output

    assert test_output == ("import os\n"
                           "import p24.imports._argparse as argparse\n"
                           "import p24.imports._subprocess as subprocess\n"
                           "import sys\n"
                           "\n"
                           "from bottle import Bottle, redirect, response, run\n"
                           "\n"
                           "import p24.imports._VERSION as VERSION\n"
                           "import p24.shared.media_wiki_syntax as syntax\n")


def test_custom_sections():
    """Ensure that most specific placement control match wins"""
    test_input = ("import os\n"
                  "import sys\n"
                  "from django.conf import settings\n"
                  "from bottle import Bottle, redirect, response, run\n"
                  "import p24.imports._argparse as argparse\n"
                  "from django.db import models\n"
                  "import p24.imports._subprocess as subprocess\n"
                  "import pandas as pd\n"
                  "import p24.imports._VERSION as VERSION\n"
                  "import numpy as np\n"
                  "import p24.shared.media_wiki_syntax as syntax\n")
    test_output = SortImports(file_contents=test_input,
                known_first_party=['p24', 'p24.imports._VERSION'],
                import_heading_stdlib='Standard Library',
                import_heading_thirdparty='Third Party',
                import_heading_firstparty='First Party',
                import_heading_django='Django',
                import_heading_pandas='Pandas',
                known_standard_library=['p24.imports'],
                known_third_party=['bottle'],
                known_django=['django'],
                known_pandas=['pandas', 'numpy'],
                default_section="THIRDPARTY",
                sections=["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "PANDAS", "FIRSTPARTY", "LOCALFOLDER"]).output
    assert test_output == ("# Standard Library\n"
                           "import os\n"
                           "import p24.imports._argparse as argparse\n"
                           "import p24.imports._subprocess as subprocess\n"
                           "import sys\n"
                           "\n"
                           "# Django\n"
                           "from django.conf import settings\n"
                           "from django.db import models\n"
                           "\n"
                           "# Third Party\n"
                           "from bottle import Bottle, redirect, response, run\n"
                           "\n"
                           "# Pandas\n"
                           "import numpy as np\n"
                           "import pandas as pd\n"
                           "\n"
                           "# First Party\n"
                           "import p24.imports._VERSION as VERSION\n"
                           "import p24.shared.media_wiki_syntax as syntax\n")


def test_glob_known():
    """Ensure that most specific placement control match wins"""
    test_input = ("import os\n"
                  "from django_whatever import whatever\n"
                  "import sys\n"
                  "from django.conf import settings\n"
                  "from . import another\n")
    test_output = SortImports(file_contents=test_input,
                import_heading_stdlib='Standard Library',
                import_heading_thirdparty='Third Party',
                import_heading_firstparty='First Party',
                import_heading_django='Django',
                import_heading_djangoplugins='Django Plugins',
                import_heading_localfolder='Local',
                known_django=['django'],
                known_djangoplugins=['django_*'],
                default_section="THIRDPARTY",
                sections=["FUTURE", "STDLIB", "DJANGO", "DJANGOPLUGINS", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]).output
    assert test_output == ("# Standard Library\n"
                           "import os\n"
                           "import sys\n"
                           "\n"
                           "# Django\n"
                           "from django.conf import settings\n"
                           "\n"
                           "# Django Plugins\n"
                           "from django_whatever import whatever\n"
                           "\n"
                           "# Local\n"
                           "from . import another\n")


def test_sticky_comments():
    """Test to ensure it is possible to make comments 'stick' above imports"""
    test_input = ("import os\n"
                  "\n"
                  "# Used for type-hinting (ref: https://github.com/davidhalter/jedi/issues/414).\n"
                  "from selenium.webdriver.remote.webdriver import WebDriver  # noqa\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ("from django import forms\n"
                  "# While this couples the geographic forms to the GEOS library,\n"
                  "# it decouples from database (by not importing SpatialBackend).\n"
                  "from django.contrib.gis.geos import GEOSException, GEOSGeometry\n"
                  "from django.utils.translation import ugettext_lazy as _\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_zipimport():
    """Imports ending in "import" shouldn't be clobbered"""
    test_input = "from zipimport import zipimport\n"
    assert SortImports(file_contents=test_input).output == test_input


def test_from_ending():
    """Imports ending in "from" shouldn't be clobbered."""
    test_input = "from foo import get_foo_from, get_foo\n"
    expected_output = "from foo import get_foo, get_foo_from\n"
    assert SortImports(file_contents=test_input).output == expected_output


def test_from_first():
    """Tests the setting from_first works correctly"""
    test_input = "from os import path\nimport os\n"
    assert SortImports(file_contents=test_input, from_first=True).output == test_input


def test_top_comments():
    """Ensure correct behavior with top comments"""
    test_input = ("# -*- encoding: utf-8 -*-\n"
                  "# Test comment\n"
                  "#\n"
                  "from __future__ import unicode_literals\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ("# -*- coding: utf-8 -*-\n"
                  "from django.db import models\n"
                  "from django.utils.encoding import python_2_unicode_compatible\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ("# Comment\n"
                  "import sys\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ("# -*- coding\n"
                  "import sys\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_consistency():
    """Ensures consistency of handling even when dealing with non ordered-by-type imports"""
    test_input = "from sqlalchemy.dialects.postgresql import ARRAY, array\n"
    assert SortImports(file_contents=test_input, order_by_type=True).output == test_input


def test_force_grid_wrap():
    """Ensures removing imports works as expected."""
    test_input = (
      "from bar import lib2\n"
      "from foo import lib6, lib7\n"
    )
    test_output = SortImports(
      file_contents=test_input,
      force_grid_wrap=2,
      multi_line_output=WrapModes.VERTICAL_HANGING_INDENT
      ).output
    assert test_output == """from bar import lib2
from foo import (
    lib6,
    lib7
)
"""
    test_output = SortImports(
      file_contents=test_input,
      force_grid_wrap=3,
      multi_line_output=WrapModes.VERTICAL_HANGING_INDENT
      ).output
    assert test_output == test_input


def test_force_grid_wrap_long():
    """Ensure that force grid wrap still happens with long line length"""
    test_input = (
      "from foo import lib6, lib7\n"
      "from bar import lib2\n"
      "from babar import something_that_is_kind_of_long"
    )
    test_output = SortImports(
      file_contents=test_input,
      force_grid_wrap=2,
      multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
      line_length=9999,
      ).output
    assert test_output == """from babar import something_that_is_kind_of_long
from bar import lib2
from foo import (
    lib6,
    lib7
)
"""


def test_uses_jinja_variables():
    """Test a basic set of imports that use jinja variables"""
    test_input = ("import sys\n"
                  "import os\n"
                  "import myproject.{ test }\n"
                  "import django.{ settings }")
    test_output = SortImports(file_contents=test_input, known_third_party=['django'],
                              known_first_party=['myproject']).output
    assert test_output == ("import os\n"
                           "import sys\n"
                           "\n"
                           "import django.{ settings }\n"
                           "\n"
                           "import myproject.{ test }\n")

    test_input = ("import {{ cookiecutter.repo_name }}\n"
                  "from foo import {{ cookiecutter.bar }}\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_fcntl():
    """Test to ensure fcntl gets correctly recognized as stdlib import"""
    test_input = ("import fcntl\n"
                  "import os\n"
                  "import sys\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_import_split_is_word_boundary_aware():
    """Test to ensure that isort splits words in a boundary aware manner"""
    test_input = ("from mycompany.model.size_value_array_import_func import \\\n"
                "    get_size_value_array_import_func_jobs")
    test_output = SortImports(file_contents=test_input,
      multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
      line_length=79).output
    assert test_output == ("from mycompany.model.size_value_array_import_func import (\n"
                           "    get_size_value_array_import_func_jobs\n"
                           ")\n")


def test_other_file_encodings(tmpdir):
    """Test to ensure file encoding is respected"""
    for encoding in ('latin1', 'utf8'):
        tmp_fname = tmpdir.join('test_{0}.py'.format(encoding))
        file_contents = "# coding: {0}\n\ns = u'ã'\n".format(encoding)
        tmp_fname.write_binary(file_contents.encode(encoding))
        assert SortImports(file_path=str(tmp_fname), settings_path=os.getcwd()).output == file_contents


def test_comment_at_top_of_file():
    """Test to ensure isort correctly handles top of file comments"""
    test_input = ("# Comment one\n"
                  "from django import forms\n"
                  "# Comment two\n"
                  "from django.contrib.gis.geos import GEOSException\n")
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ("# -*- coding: utf-8 -*-\n"
                  "from django.db import models\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_alphabetic_sorting():
    """Test to ensure isort correctly handles single line imports"""
    test_input = ("import unittest\n"
                  "\n"
                  "import ABC\n"
                  "import Zope\n"
                  "from django.contrib.gis.geos import GEOSException\n"
                  "from plone.app.testing import getRoles\n"
                  "from plone.app.testing import ManageRoles\n"
                  "from plone.app.testing import setRoles\n"
                  "from Products.CMFPlone import utils\n"
                  )
    options = {'force_single_line': True,
               'force_alphabetical_sort_within_sections': True, }

    output = SortImports(file_contents=test_input, known_first_party=['django'], **options).output
    assert output == test_input

    test_input = ("# -*- coding: utf-8 -*-\n"
                  "from django.db import models\n")
    assert SortImports(file_contents=test_input).output == test_input


def test_alphabetic_sorting_multi_line():
    """Test to ensure isort correctly handles multiline import see: issue 364"""
    test_input = ("from a import (CONSTANT_A, cONSTANT_B, CONSTANT_C, CONSTANT_D, CONSTANT_E,\n"
                  "               CONSTANT_F, CONSTANT_G, CONSTANT_H, CONSTANT_I, CONSTANT_J)\n")
    options = {'force_alphabetical_sort_within_sections': True, }
    assert SortImports(file_contents=test_input, **options).output == test_input


def test_comments_not_duplicated():
    """Test to ensure comments aren't duplicated: issue 303"""
    test_input = ('from flask import url_for\n'
                  "# Whole line comment\n"
                  'from service import demo  # inline comment\n'
                  'from service import settings\n')
    output = SortImports(file_contents=test_input).output
    assert output.count("# Whole line comment\n") == 1
    assert output.count("# inline comment\n") == 1


def test_top_of_line_comments():
    """Test to ensure top of line comments stay where they should: issue 260"""
    test_input = ('# -*- coding: utf-8 -*-\n'
                  'from django.db import models\n'
                  '#import json as simplejson\n'
                  'from myproject.models import Servidor\n'
                  '\n'
                  'import reversion\n'
                   '\n'
                   'import logging\n')
    output = SortImports(file_contents=test_input).output
    print(output)
    assert output.startswith('# -*- coding: utf-8 -*-\n')


def test_basic_comment():
    """Test to ensure a basic comment wont crash isort"""
    test_input = ('import logging\n'
                  '# Foo\n'
                  'import os\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_shouldnt_add_lines():
    """Ensure that isort doesn't add a blank line when a top of import comment is present, issue #316"""
    test_input = ('"""Text"""\n'
                  '# This is a comment\n'
                 'import pkg_resources\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_sections_parsed_correct(tmpdir):
    """Ensure that modules for custom sections parsed as list from config file and isort result is correct"""
    conf_file_data = (
        '[settings]\n'
        'sections=FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER,COMMON\n'
        'known_common=nose\n'
        'import_heading_common=Common Library\n'
        'import_heading_stdlib=Standard Library\n'
    )
    test_input = (
        'import os\n'
        'from nose import *\n'
        'import nose\n'
        'from os import path'
    )
    correct_output = (
        '# Standard Library\n'
        'import os\n'
        'from os import path\n'
        '\n'
        '# Common Library\n'
        'import nose\n'
        'from nose import *\n'
    )
    tmpdir.join('.isort.cfg').write(conf_file_data)
    assert SortImports(file_contents=test_input, settings_path=str(tmpdir)).output == correct_output


@pytest.mark.skipif(toml is None, reason="Requires toml package to be installed.")
def test_pyproject_conf_file(tmpdir):
    """Ensure that modules for custom sections parsed as list from config file and isort result is correct"""
    conf_file_data = (
        '[build-system]\n'
        'requires = ["setuptools", "wheel"]\n'
        '[tool.poetry]\n'
        'name = "isort"\n'
        'version = "0.1.0"\n'
        'license = "MIT"\n'
        '[tool.isort]\n'
        'lines_between_types=1\n'
        'known_common="nose"\n'
        'import_heading_common="Common Library"\n'
        'import_heading_stdlib="Standard Library"\n'
        'sections="FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER,COMMON"\n'
        'include_trailing_comma = true\n'
    )
    test_input = (
        'import os\n'
        'from nose import *\n'
        'import nose\n'
        'from os import path'
    )
    correct_output = (
        '# Standard Library\n'
        'import os\n'
        '\n'
        'from os import path\n'
        '\n'
        '# Common Library\n'
        'import nose\n'
        '\n'
        'from nose import *\n'
    )
    tmpdir.join('pyproject.toml').write(conf_file_data)
    assert SortImports(file_contents=test_input, settings_path=str(tmpdir)).output == correct_output


def test_alphabetic_sorting_no_newlines():
    '''Test to ensure that alphabetical sort does not erroneously introduce new lines (issue #328)'''
    test_input = "import os\n"
    test_output = SortImports(file_contents=test_input, force_alphabetical_sort_within_sections=True).output
    assert test_input == test_output

    test_input = ('import os\n'
                  'import unittest\n'
                  '\n'
                  'from a import b\n'
                  '\n'
                  '\n'
                  'print(1)\n')
    test_output = SortImports(file_contents=test_input, force_alphabetical_sort_within_sections=True, lines_after_imports=2).output
    assert test_input == test_output


def test_sort_within_section():
    '''Test to ensure its possible to force isort to sort within sections'''
    test_input = ('from Foob import ar\n'
                  'import foo\n'
                  'from foo import bar\n'
                  'from foo.bar import Quux, baz\n')
    test_output = SortImports(file_contents=test_input, force_sort_within_sections=True).output
    assert test_output == test_input

    test_input = ('import foo\n'
                  'from foo import bar\n'
                  'from foo.bar import baz\n'
                  'from foo.bar import Quux\n'
                  'from Foob import ar\n')
    test_output = SortImports(file_contents=test_input, force_sort_within_sections=True, order_by_type=False,
                              force_single_line=True).output
    assert test_output == test_input


def test_sorting_with_two_top_comments():
    '''Test to ensure isort will sort files that contain 2 top comments'''
    test_input = ('#! comment1\n'
                  "''' comment2\n"
                  "'''\n"
                  'import b\n'
                  'import a\n')
    assert SortImports(file_contents=test_input).output == ('#! comment1\n'
                                                            "''' comment2\n"
                                                            "'''\n"
                                                            'import a\n'
                                                            'import b\n')


def test_lines_between_sections():
    """Test to ensure lines_between_sections works"""
    test_input = ('from bar import baz\n'
                  'import os\n')
    assert SortImports(file_contents=test_input, lines_between_sections=0).output == ('import os\n'
                                                                                      'from bar import baz\n')
    assert SortImports(file_contents=test_input, lines_between_sections=2).output == ('import os\n\n\n'
                                                                                      'from bar import baz\n')


def test_forced_sepatate_globs():
    """Test to ensure that forced_separate glob matches lines"""
    test_input = ('import os\n'
                  '\n'
                  'from myproject.foo.models import Foo\n'
                  '\n'
                  'from myproject.utils import util_method\n'
                  '\n'
                  'from myproject.bar.models import Bar\n'
                  '\n'
                  'import sys\n')
    test_output = SortImports(file_contents=test_input, forced_separate=['*.models'],
                              line_length=120).output

    assert test_output == ('import os\n'
                          'import sys\n'
                          '\n'
                          'from myproject.utils import util_method\n'
                          '\n'
                          'from myproject.bar.models import Bar\n'
                          'from myproject.foo.models import Foo\n')


def test_no_additional_lines_issue_358():
    """Test to ensure issue 358 is resovled and running isort multiple times does not add extra newlines"""
    test_input = ('"""This is a docstring"""\n'
                  '# This is a comment\n'
                  'from __future__ import (\n'
                  '    absolute_import,\n'
                  '    division,\n'
                  '    print_function,\n'
                  '    unicode_literals\n'
                  ')\n')
    expected_output = ('"""This is a docstring"""\n'
                       '# This is a comment\n'
                       'from __future__ import (\n'
                       '    absolute_import,\n'
                       '    division,\n'
                       '    print_function,\n'
                       '    unicode_literals\n'
                       ')\n')
    test_output = SortImports(file_contents=test_input, multi_line_output=3, line_length=20).output
    assert test_output == expected_output

    test_output = SortImports(file_contents=test_output, multi_line_output=3, line_length=20).output
    assert test_output == expected_output

    for attempt in range(5):
        test_output = SortImports(file_contents=test_output, multi_line_output=3, line_length=20).output
        assert test_output == expected_output

    test_input = ('"""This is a docstring"""\n'
                  '\n'
                  '# This is a comment\n'
                  'from __future__ import (\n'
                  '    absolute_import,\n'
                  '    division,\n'
                  '    print_function,\n'
                  '    unicode_literals\n'
                  ')\n')
    expected_output = ('"""This is a docstring"""\n'
                       '\n'
                       '# This is a comment\n'
                       'from __future__ import (\n'
                       '    absolute_import,\n'
                       '    division,\n'
                       '    print_function,\n'
                       '    unicode_literals\n'
                       ')\n')
    test_output = SortImports(file_contents=test_input, multi_line_output=3, line_length=20).output
    assert test_output == expected_output

    test_output = SortImports(file_contents=test_output, multi_line_output=3, line_length=20).output
    assert test_output == expected_output

    for attempt in range(5):
        test_output = SortImports(file_contents=test_output, multi_line_output=3, line_length=20).output
        assert test_output == expected_output


def test_import_by_paren_issue_375():
    """Test to ensure isort can correctly handle sorting imports where the paren is directly by the import body"""
    test_input = ('from .models import(\n'
                  '   Foo,\n'
                  '   Bar,\n'
                  ')\n')
    assert SortImports(file_contents=test_input).output == 'from .models import Bar, Foo\n'


def test_import_by_paren_issue_460():
    """Test to ensure isort can doesnt move comments around """
    test_input = """
# First comment
# Second comment
# third comment
import io
import os
"""
    assert SortImports(file_contents=(test_input)).output == test_input


def test_function_with_docstring():
    """Test to ensure isort can correctly sort imports when the first found content is a function with a docstring"""
    add_imports = ['from __future__ import unicode_literals']
    test_input = ('def foo():\n'
                  '    """ Single line triple quoted doctring """\n'
                  '    pass\n')
    expected_output = ('from __future__ import unicode_literals\n'
                       '\n'
                       '\n'
                       'def foo():\n'
                       '    """ Single line triple quoted doctring """\n'
                       '    pass\n')
    assert SortImports(file_contents=test_input, add_imports=add_imports).output == expected_output


def test_plone_style():
    """Test to ensure isort correctly plone style imports"""
    test_input = ("from django.contrib.gis.geos import GEOSException\n"
                  "from plone.app.testing import getRoles\n"
                  "from plone.app.testing import ManageRoles\n"
                  "from plone.app.testing import setRoles\n"
                  "from Products.CMFPlone import utils\n"
                  "\n"
                  "import ABC\n"
                  "import unittest\n"
                  "import Zope\n")
    options = {'force_single_line': True,
               'force_alphabetical_sort': True}
    assert SortImports(file_contents=test_input, **options).output == test_input


def test_third_party_case_sensitive():
    """Modules which match builtins by name but not on case should not be picked up on Windows."""
    test_input = ("import thirdparty\n"
                  "import os\n"
                  "import ABC\n")

    expected_output = ('import os\n'
                       '\n'
                       'import ABC\n'
                       'import thirdparty\n')
    assert SortImports(file_contents=test_input).output == expected_output


def test_exists_case_sensitive_file(tmpdir):
    """Test exists_case_sensitive function for a file."""
    tmpdir.join('module.py').ensure(file=1)
    assert exists_case_sensitive(str(tmpdir.join('module.py')))
    assert not exists_case_sensitive(str(tmpdir.join('MODULE.py')))


def test_exists_case_sensitive_directory(tmpdir):
    """Test exists_case_sensitive function for a directory."""
    tmpdir.join('pkg').ensure(dir=1)
    assert exists_case_sensitive(str(tmpdir.join('pkg')))
    assert not exists_case_sensitive(str(tmpdir.join('PKG')))


def test_sys_path_mutation(tmpdir):
    """Test to ensure sys.path is not modified"""
    tmpdir.mkdir('src').mkdir('a')
    test_input = "from myproject import test"
    options = {'virtual_env': str(tmpdir)}
    expected_length = len(sys.path)
    SortImports(file_contents=test_input, **options).output
    assert len(sys.path) == expected_length


def test_long_single_line():
    """Test to ensure long single lines get handled correctly"""
    output = SortImports(file_contents="from ..views import ("
                                       " _a,"
                                       "_xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx as xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx)",
                         line_length=79).output
    for line in output.split('\n'):
        assert len(line) <= 79

    output = SortImports(file_contents="from ..views import ("
                                       " _a,"
                                       "_xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx as xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx)",
                         line_length=76, combine_as_imports=True).output
    for line in output.split('\n'):
        assert len(line) <= 79


def test_import_inside_class_issue_432():
    """Test to ensure issue 432 is resolved and isort doesn't insert imports in the middle of classes"""
    test_input = ("# coding=utf-8\n"
                  "class Foo:\n"
                  "    def bar(self):\n"
                  "        pass\n")
    expected_output = ("# coding=utf-8\n"
                       "import baz\n"
                       "\n"
                       "\n"
                       "class Foo:\n"
                       "    def bar(self):\n"
                       "        pass\n")
    assert SortImports(file_contents=test_input, add_imports=['import baz']).output == expected_output


def test_wildcard_import_without_space_issue_496():
    """Test to ensure issue #496: wildcard without space, is resolved"""
    test_input = 'from findorserver.coupon.models import*'
    expected_output = 'from findorserver.coupon.models import *\n'
    assert SortImports(file_contents=test_input).output == expected_output


def test_import_line_mangles_issues_491():
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = ('import os  # ([\n'
                  '\n'
                  'print("hi")\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_import_line_mangles_issues_505():
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = ('from sys import *  # (\n'
                  '\n'
                  '\n'
                  'def test():\n'
                  '    print("Test print")\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_import_line_mangles_issues_439():
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = ('import a  # () import\n'
                  'from b import b\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_alias_using_paren_issue_466():
    """Test to ensure issue #466: Alias causes slash incorrectly is resolved"""
    test_input = 'from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper\n'
    expected_output = ('from django.db.backends.mysql.base import (\n'
                       '    DatabaseWrapper as MySQLDatabaseWrapper)\n')
    assert SortImports(file_contents=test_input, line_length=50, use_parentheses=True).output == expected_output

    test_input = 'from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper\n'
    expected_output = ('from django.db.backends.mysql.base import (\n'
                       '    DatabaseWrapper as MySQLDatabaseWrapper\n'
                       ')\n')
    assert SortImports(file_contents=test_input, line_length=50, multi_line_output=5,
                       use_parentheses=True).output == expected_output


def test_strict_whitespace_by_default(capsys):
    test_input = ('import os\n'
                  'from django.conf import settings\n')
    SortImports(file_contents=test_input, check=True)
    out, err = capsys.readouterr()
    assert out == 'ERROR:  Imports are incorrectly sorted.\n'


def test_strict_whitespace_no_closing_newline_issue_676(capsys):
    test_input = ('import os\n'
                  '\n'
                  'from django.conf import settings\n'
                  '\n'
                  'print(1)')
    SortImports(file_contents=test_input, check=True)
    out, err = capsys.readouterr()
    assert out == ''


def test_ignore_whitespace(capsys):
    test_input = ('import os\n'
                  'from django.conf import settings\n')
    SortImports(file_contents=test_input, check=True, ignore_whitespace=True)
    out, err = capsys.readouterr()
    assert out == ''


def test_import_wraps_with_comment_issue_471():
    """Test to ensure issue #471 is resolved"""
    test_input = ('from very_long_module_name import SuperLongClassName  #@UnusedImport'
                  ' -- long string of comments which wrap over')
    expected_output = ('from very_long_module_name import (\n'
                       '    SuperLongClassName)  # @UnusedImport -- long string of comments which wrap over\n')
    assert SortImports(file_contents=test_input, line_length=50, multi_line_output=1,
                       use_parentheses=True).output == expected_output


def test_import_case_produces_inconsistent_results_issue_472():
    """Test to ensure sorting imports with same name but different case produces the same result across platforms"""
    test_input = ('from sqlalchemy.dialects.postgresql import ARRAY\n'
                  'from sqlalchemy.dialects.postgresql import array\n')
    assert SortImports(file_contents=test_input, force_single_line=True).output == test_input

    test_input = 'from scrapy.core.downloader.handlers.http import HttpDownloadHandler, HTTPDownloadHandler\n'
    assert SortImports(file_contents=test_input).output == test_input


def test_inconsistent_behavior_in_python_2_and_3_issue_479():
    """Test to ensure Python 2 and 3 have the same behavior"""
    test_input = ('from future.standard_library import hooks\n'
                  'from workalendar.europe import UnitedKingdom\n')
    assert SortImports(file_contents=test_input,
                       known_first_party=["future"]).output == test_input


def test_sort_within_section_comments_issue_436():
    """Test to ensure sort within sections leaves comments untouched"""
    test_input = ('import os.path\n'
                  'import re\n'
                  '\n'
                  '# report.py exists in ... comment line 1\n'
                  '# this file needs to ...  comment line 2\n'
                  '# it must not be ...      comment line 3\n'
                  'import report\n')
    assert SortImports(file_contents=test_input, force_sort_within_sections=True).output == test_input


def test_sort_within_sections_with_force_to_top_issue_473():
    """Test to ensure it's possible to sort within sections with items forced to top"""
    test_input = ('import z\n'
                  'import foo\n'
                  'from foo import bar\n')
    assert SortImports(file_contents=test_input, force_sort_within_sections=True,
                       force_to_top=['z']).output == test_input


def test_correct_number_of_new_lines_with_comment_issue_435():
    """Test to ensure that injecting a comment in-between imports doesn't mess up the new line spacing"""
    test_input = ('import foo\n'
                  '\n'
                  '# comment\n'
                  '\n'
                  '\n'
                  'def baz():\n'
                  '    pass\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_future_below_encoding_issue_545():
    """Test to ensure future is always below comment"""
    test_input = ('#!/usr/bin/env python\n'
                  'from __future__ import print_function\n'
                  'import logging\n'
                  '\n'
                  'print("hello")\n')
    expected_output = ('#!/usr/bin/env python\n'
                       'from __future__ import print_function\n'
                       '\n'
                       'import logging\n'
                       '\n'
                       'print("hello")\n')
    assert SortImports(file_contents=test_input).output == expected_output


def test_no_extra_lines_issue_557():
    """Test to ensure no extra lines are prepended"""
    test_input = ('import os\n'
                  '\n'
                  'from scrapy.core.downloader.handlers.http import HttpDownloadHandler, HTTPDownloadHandler\n')
    expected_output = ('import os\n'
                       'from scrapy.core.downloader.handlers.http import HttpDownloadHandler, HTTPDownloadHandler\n')
    assert SortImports(file_contents=test_input, force_alphabetical_sort=True,
                       force_sort_within_sections=True).output == expected_output


def test_long_import_wrap_support_with_mode_2():
    """Test to ensure mode 2 still allows wrapped imports with slash"""
    test_input = ('from foobar.foobar.foobar.foobar import \\\n'
                  '    an_even_longer_function_name_over_80_characters\n')
    assert SortImports(file_contents=test_input, multi_line_output=2, line_length=80).output == test_input


def test_pylint_comments_incorrectly_wrapped_issue_571():
    """Test to ensure pylint comments don't get wrapped"""
    test_input = ('from PyQt5.QtCore import QRegExp  # @UnresolvedImport pylint: disable=import-error,'
                  'useless-suppression\n')
    expected_output = ('from PyQt5.QtCore import \\\n'
                       '    QRegExp  # @UnresolvedImport pylint: disable=import-error,useless-suppression\n')
    assert SortImports(file_contents=test_input, line_length=60).output == expected_output


def test_ensure_async_methods_work_issue_537():
    """Test to ensure async methods are correctly identified"""
    test_input = ('from myapp import myfunction\n'
                  '\n'
                  '\n'
                  'async def test_myfunction(test_client, app):\n'
                  '    a = await myfunction(test_client, app)\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_ensure_as_imports_sort_correctly_within_from_imports_issue_590():
    """Test to ensure combination from and as import statements are sorted correct"""
    test_input = ('from os import defpath\n'
                  'from os import pathsep as separator\n')
    assert SortImports(file_contents=test_input, force_sort_within_sections=True).output == test_input

    test_input = ('from os import defpath\n'
                  'from os import pathsep as separator\n')
    assert SortImports(file_contents=test_input).output == test_input

    test_input = ('from os import defpath\n'
                  'from os import pathsep as separator\n')
    assert SortImports(file_contents=test_input, force_single_line=True).output == test_input


def test_ensure_line_endings_are_preserved_issue_493():
    """Test to ensure line endings are not converted"""
    test_input = ('from os import defpath\r\n'
                  'from os import pathsep as separator\r\n')
    assert SortImports(file_contents=test_input).output == test_input
    test_input = ('from os import defpath\r'
                  'from os import pathsep as separator\r')
    assert SortImports(file_contents=test_input).output == test_input
    test_input = ('from os import defpath\n'
                  'from os import pathsep as separator\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_not_splitted_sections():
    whiteline = '\n'
    stdlib_section = 'import unittest\n'
    firstparty_section = 'from app.pkg1 import mdl1\n'
    local_section = 'from .pkg2 import mdl2\n'
    statement = 'foo = bar\n'
    test_input = (
        stdlib_section + whiteline + firstparty_section + whiteline +
        local_section + whiteline + statement
    )

    assert SortImports(file_contents=test_input).output == test_input
    assert SortImports(file_contents=test_input, no_lines_before=['LOCALFOLDER']).output == \
           (
               stdlib_section + whiteline + firstparty_section + local_section +
               whiteline + statement
           )
    # by default STDLIB and FIRSTPARTY sections are split by THIRDPARTY section,
    # so don't merge them if THIRDPARTY imports aren't exist
    assert SortImports(file_contents=test_input, no_lines_before=['FIRSTPARTY']).output == test_input
    # in case when THIRDPARTY section is excluded from sections list, it's ok to merge STDLIB and FIRSTPARTY
    assert SortImports(
        file_contents=test_input,
        sections=['STDLIB', 'FIRSTPARTY', 'LOCALFOLDER'],
        no_lines_before=['FIRSTPARTY'],
    ).output == (
        stdlib_section + firstparty_section + whiteline + local_section +
        whiteline + statement
    )
    # it doesn't change output, because stdlib packages don't have any whitelines before them
    assert SortImports(file_contents=test_input, no_lines_before=['STDLIB']).output == test_input


def test_no_lines_before_empty_section():
    test_input = ('import first\n'
                  'import custom\n')
    assert SortImports(
        file_contents=test_input,
        known_third_party=["first"],
        known_custom=["custom"],
        sections=['THIRDPARTY', 'LOCALFOLDER', 'CUSTOM'],
        no_lines_before=['THIRDPARTY', 'LOCALFOLDER', 'CUSTOM'],
    ).output == test_input


def test_no_inline_sort():
    """Test to ensure multiple `from` imports in one line are not sorted if `--no-inline-sort` flag
    is enabled. If `--force-single-line-imports` flag is enabled, then `--no-inline-sort` is ignored."""
    test_input = 'from foo import a, c, b\n'
    assert SortImports(file_contents=test_input, no_inline_sort=True, force_single_line=False).output == test_input
    assert SortImports(file_contents=test_input, no_inline_sort=False, force_single_line=False).output == 'from foo import a, b, c\n'
    expected = (
        'from foo import a\n'
        'from foo import b\n'
        'from foo import c\n'
    )
    assert SortImports(file_contents=test_input, no_inline_sort=False, force_single_line=True).output == expected
    assert SortImports(file_contents=test_input, no_inline_sort=True, force_single_line=True).output == expected


def test_relative_import_of_a_module():
    """Imports can be dynamically created (PEP302) and is used by modules such as six.  This test ensures that
    these types of imports are still sorted to the correct type instead of being categorized as local."""
    test_input = ('from __future__ import absolute_import\n'
                  '\n'
                  'import itertools\n'
                  '\n'
                  'from six import add_metaclass\n'
                  '\n'
                  'from six.moves import asd\n'
                  )

    expected_results = ('from __future__ import absolute_import\n'
                        '\n'
                        'import itertools\n'
                        '\n'
                        'from six import add_metaclass\n'
                        'from six.moves import asd\n'
                        )

    sorted_result = SortImports(file_contents=test_input, force_single_line=True).output
    assert sorted_result == expected_results


def test_escaped_parens_sort():
    test_input = ('from foo import \\ \n'
                  '(a,\n'
                  'b,\n'
                  'c)\n')
    expected = ('from foo import a, b, c\n')
    assert SortImports(file_contents=test_input).output == expected


def test_is_python_file_ioerror(tmpdir):
    does_not_exist = tmpdir.join('fake.txt')
    assert is_python_file(str(does_not_exist)) is False


def test_is_python_file_shebang(tmpdir):
    path = tmpdir.join('myscript')
    path.write('#!/usr/bin/env python\n')
    assert is_python_file(str(path)) is True


def test_is_python_file_editor_backup(tmpdir):
    path = tmpdir.join('myscript~')
    path.write('#!/usr/bin/env python\n')
    assert is_python_file(str(path)) is False


def test_is_python_typing_stub(tmpdir):
    stub = tmpdir.join('stub.pyi')
    assert is_python_file(str(stub)) is True


def test_to_ensure_imports_are_brought_to_top_issue_651():
    test_input = ('from __future__ import absolute_import, unicode_literals\n'
                  '\n'
                  'VAR = """\n'
                  'multiline text\n'
                  '"""\n'
                  '\n'
                  'from __future__ import unicode_literals\n'
                  'from __future__ import absolute_import\n')
    expected_output = ('from __future__ import absolute_import, unicode_literals\n'
                       '\n'
                       'VAR = """\n'
                       'multiline text\n'
                       '"""\n')
    assert SortImports(file_contents=test_input).output == expected_output


def test_to_ensure_importing_from_imports_module_works_issue_662():
    test_input = ('@wraps(fun)\n'
                  'def __inner(*args, **kwargs):\n'
                  '    from .imports import qualname\n'
                  '    warn(description=description or qualname(fun), deprecation=deprecation, removal=removal)\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_to_ensure_no_unexpected_changes_issue_666():
    test_input = ('from django.conf import settings\n'
                  'from django.core.management import call_command\n'
                  'from django.core.management.base import BaseCommand\n'
                  'from django.utils.translation import ugettext_lazy as _\n'
                  '\n'
                  'TEMPLATE = """\n'
                  '# This file is generated automatically with the management command\n'
                  '#\n'
                  '#    manage.py bis_compile_i18n\n'
                  '#\n'
                  '# please dont change it manually.\n'
                  'from django.utils.translation import ugettext_lazy as _\n'
                  '"""\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_to_ensure_tabs_dont_become_space_issue_665():
    test_input = ('import os\n'
                  '\n'
                  '\n'
                  'def my_method():\n'
                  '\tpass\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_new_lines_are_preserved():
    with NamedTemporaryFile('w', suffix='py', delete=False) as rn_newline:
        pass

    try:
        with io.open(rn_newline.name, mode='w', newline='') as rn_newline_input:
            rn_newline_input.write('import sys\r\nimport os\r\n')

        SortImports(rn_newline.name, settings_path=os.getcwd())
        with io.open(rn_newline.name) as new_line_file:
            print(new_line_file.read())
        with io.open(rn_newline.name, newline='') as rn_newline_file:
            rn_newline_contents = rn_newline_file.read()
        assert rn_newline_contents == 'import os\r\nimport sys\r\n'
    finally:
        os.remove(rn_newline.name)

    with NamedTemporaryFile('w', suffix='py', delete=False) as r_newline:
        pass

    try:
        with io.open(r_newline.name, mode='w', newline='') as r_newline_input:
            r_newline_input.write('import sys\rimport os\r')

        SortImports(r_newline.name, settings_path=os.getcwd())
        with io.open(r_newline.name, newline='') as r_newline_file:
            r_newline_contents = r_newline_file.read()
        assert r_newline_contents == 'import os\rimport sys\r'
    finally:
        os.remove(r_newline.name)

    with NamedTemporaryFile('w', suffix='py', delete=False) as n_newline:
        pass

    try:
        with io.open(n_newline.name, mode='w', newline='') as n_newline_input:
            n_newline_input.write('import sys\nimport os\n')

        SortImports(n_newline.name, settings_path=os.getcwd())
        with io.open(n_newline.name, newline='') as n_newline_file:
            n_newline_contents = n_newline_file.read()
        assert n_newline_contents == 'import os\nimport sys\n'
    finally:
        os.remove(n_newline.name)


def test_requirements_finder(tmpdir):
    subdir = tmpdir.mkdir('subdir').join("lol.txt")
    subdir.write("flask")
    req_file = tmpdir.join('requirements.txt')
    req_file.write(
        "Django==1.11\n"
        "-e git+https://github.com/orsinium/deal.git#egg=deal\n"
    )
    si = SortImports(file_contents="")
    for path in (str(tmpdir), str(subdir)):
        finder = finders.RequirementsFinder(
            config=si.config,
            sections=si.sections,
            path=path
        )

        files = list(finder._get_files())
        assert len(files) == 1  # file finding
        assert files[0].endswith('requirements.txt')  # file finding
        assert set(finder._get_names(str(req_file))) == {'Django', 'deal'}  # file parsing

        assert finder.find("django") == si.sections.THIRDPARTY  # package in reqs
        assert finder.find("flask") is None  # package not in reqs
        assert finder.find("deal") == si.sections.THIRDPARTY  # vcs

        assert len(finder.mapping) > 100
        assert finder._normalize_name('deal') == 'deal'
        assert finder._normalize_name('Django') == 'django'  # lowercase
        assert finder._normalize_name('django_haystack') == 'haystack'  # mapping
        assert finder._normalize_name('Flask-RESTful') == 'flask_restful'  # conver `-`to `_`

    req_file.remove()


def test_forced_separate_is_deterministic_issue_774(tmpdir):

    config_file = tmpdir.join('setup.cfg')
    config_file.write(
        "[isort]\n"
        "forced_separate:\n"
        "   separate1\n"
        "   separate2\n"
        "   separate3\n"
        "   separate4\n"
    )

    test_input = ('import time\n'
                  '\n'
                  'from separate1 import foo\n'
                  '\n'
                  'from separate2 import bar\n'
                  '\n'
                  'from separate3 import baz\n'
                  '\n'
                  'from separate4 import quux\n')

    assert SortImports(file_contents=test_input, settings_path=config_file.strpath).output == test_input


PIPFILE = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[requires]
python_version = "3.5"

[packages]
Django = "~=1.11"
deal = {editable = true, git = "https://github.com/orsinium/deal.git"}

[dev-packages]
"""


def test_pipfile_finder(tmpdir):
    pipfile = tmpdir.join('Pipfile')
    pipfile.write(PIPFILE)
    si = SortImports(file_contents="")
    finder = finders.PipfileFinder(
        config=si.config,
        sections=si.sections,
        path=str(tmpdir)
    )

    assert set(finder._get_names(str(tmpdir))) == {'Django', 'deal'}  # file parsing

    assert finder.find("django") == si.sections.THIRDPARTY  # package in reqs
    assert finder.find("flask") is None  # package not in reqs
    assert finder.find("deal") == si.sections.THIRDPARTY  # vcs

    assert len(finder.mapping) > 100
    assert finder._normalize_name('deal') == 'deal'
    assert finder._normalize_name('Django') == 'django'  # lowercase
    assert finder._normalize_name('django_haystack') == 'haystack'  # mapping
    assert finder._normalize_name('Flask-RESTful') == 'flask_restful'  # conver `-`to `_`

    pipfile.remove()


@pytest.mark.skipif(sys.version_info[0] == 2, reason="Requires Python 3")
def test_monkey_patched_urllib():
    with pytest.raises(ImportError):
        # Previous versions of isort monkey patched urllib which caused unusual
        # importing for other projects.
        from urllib import quote  # noqa: F401


@pytest.mark.skipif(sys.version_info[0] == 2, reason="Requires Python 3")
def test_path_finder(monkeypatch):
    si = SortImports(file_contents="")
    finder = finders.PathFinder(
        config=si.config,
        sections=si.sections,
    )
    third_party_prefix = next(path for path in finder.paths if "site-packages" in path)
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    imaginary_paths = set([
        posixpath.join(finder.stdlib_lib_prefix, "example_1.py"),
        posixpath.join(third_party_prefix, "example_2.py"),
        posixpath.join(third_party_prefix, "example_3.so"),
        posixpath.join(third_party_prefix, "example_4" + ext_suffix),
        posixpath.join(os.getcwd(), "example_5.py"),
    ])
    monkeypatch.setattr("isort.finders.exists_case_sensitive", lambda p: p in imaginary_paths)
    assert finder.find("example_1") == finder.sections.STDLIB
    assert finder.find("example_2") == finder.sections.THIRDPARTY
    assert finder.find("example_3") == finder.sections.THIRDPARTY
    assert finder.find("example_4") == finder.sections.THIRDPARTY
    assert finder.find("example_5") == finder.sections.FIRSTPARTY


def test_argument_parsing():
    from isort.main import parse_args
    args = parse_args(['-dt', '-t', 'foo', '--skip=bar', 'baz.py'])
    assert args['order_by_type'] is False
    assert args['force_to_top'] == ['foo']
    assert args['skip'] == ['bar']
    assert args['files'] == ['baz.py']


@pytest.mark.parametrize('multiprocess', (False, True))
def test_command_line(tmpdir, capfd, multiprocess):
    from isort.main import main
    tmpdir.join("file1.py").write("import re\nimport os\n\nimport contextlib\n\n\nimport isort")
    tmpdir.join("file2.py").write("import collections\nimport time\n\nimport abc\n\n\nimport isort")
    arguments = ["-rc", str(tmpdir), '--settings-path', os.getcwd()]
    if multiprocess:
        arguments.extend(['--jobs', '2'])
    main(arguments)
    assert tmpdir.join("file1.py").read() == "import contextlib\nimport os\nimport re\n\nimport isort\n"
    assert tmpdir.join("file2.py").read() == "import abc\nimport collections\nimport time\n\nimport isort\n"
    if not sys.platform.startswith('win'):
        out, err = capfd.readouterr()
        assert not err
        # it informs us about fixing the files:
        assert str(tmpdir.join("file1.py")) in out
        assert str(tmpdir.join("file2.py")) in out


@pytest.mark.parametrize("quiet", (False, True))
def test_quiet(tmpdir, capfd, quiet):
    if sys.platform.startswith("win"):
        return
    from isort.main import main
    tmpdir.join("file1.py").write("import re\nimport os")
    tmpdir.join("file2.py").write("")
    arguments = ["-rc", str(tmpdir)]
    if quiet:
        arguments.append("-q")
    main(arguments)
    out, err = capfd.readouterr()
    assert not err
    assert bool(out) != quiet


@pytest.mark.parametrize('enabled', (False, True))
def test_safety_excludes(tmpdir, enabled):
    tmpdir.join("victim.py").write("# ...")
    toxdir = tmpdir.mkdir(".tox")
    toxdir.join("verysafe.py").write("# ...")
    tmpdir.mkdir("lib").mkdir("python3.7").join("importantsystemlibrary.py").write("# ...")
    tmpdir.mkdir(".pants.d").join("pants.py").write("import os")
    config = dict(settings.default.copy(), safety_excludes=enabled)
    skipped = []
    codes = [str(tmpdir)],
    main.iter_source_code(codes, config, skipped)

    # if enabled files within nested unsafe directories should be skipped
    file_names = set(os.path.relpath(f, str(tmpdir)) for f in main.iter_source_code([str(tmpdir)], config, skipped))
    if enabled:
        assert file_names == {'victim.py'}
        assert len(skipped) == 3
    else:
        assert file_names == {os.sep.join(('.tox', 'verysafe.py')),
                              os.sep.join(('lib', 'python3.7', 'importantsystemlibrary.py')),
                              os.sep.join(('.pants.d', 'pants.py')),
                              'victim.py'}
        assert not skipped

    # directly pointing to files within unsafe directories shouldn't skip them either way
    file_names = set(os.path.relpath(f, str(toxdir)) for f in main.iter_source_code([str(toxdir)], config, skipped))
    assert file_names == {'verysafe.py'}


@pytest.mark.parametrize('skip_glob_assert', (([], 0, {os.sep.join(('code', 'file.py'))}), (['**/*.py'], 1, {}),
                                              (['*/code/*.py'], 1, {})))
def test_skip_glob(tmpdir, skip_glob_assert):
    skip_glob, skipped_count, file_names = skip_glob_assert
    base_dir = tmpdir.mkdir('build')
    code_dir = base_dir.mkdir('code')
    code_dir.join('file.py').write('import os')

    config = dict(settings.default.copy(), skip_glob=skip_glob)
    skipped = []
    file_names = set(os.path.relpath(f, str(base_dir)) for f in main.iter_source_code([str(base_dir)], config, skipped))
    assert len(skipped) == skipped_count
    assert file_names == file_names


def test_comments_not_removed_issue_576():
    test_input = ('import distutils\n'
                  '# this comment is important and should not be removed\n'
                  'from sys import api_version as api_version\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_reverse_relative_imports_issue_417():
    test_input = ('from . import ipsum\n'
                  'from . import lorem\n'
                  'from .dolor import consecteur\n'
                  'from .sit import apidiscing\n'
                  'from .. import donec\n'
                  'from .. import euismod\n'
                  'from ..mi import iaculis\n'
                  'from ..nec import tempor\n'
                  'from ... import diam\n'
                  'from ... import dui\n'
                  'from ...eu import dignissim\n'
                  'from ...ex import metus\n')
    assert SortImports(file_contents=test_input,
                       force_single_line=True,
                       reverse_relative=True).output == test_input


def test_inconsistent_relative_imports_issue_577():
    test_input = ('from ... import diam\n'
                  'from ... import dui\n'
                  'from ...eu import dignissim\n'
                  'from ...ex import metus\n'
                  'from .. import donec\n'
                  'from .. import euismod\n'
                  'from ..mi import iaculis\n'
                  'from ..nec import tempor\n'
                  'from . import ipsum\n'
                  'from . import lorem\n'
                  'from .dolor import consecteur\n'
                  'from .sit import apidiscing\n')
    assert SortImports(file_contents=test_input, force_single_line=True).output == test_input


def test_unwrap_issue_762():
    test_input = ('from os.path \\\n'
                  'import (join, split)\n')
    assert SortImports(file_contents=test_input).output == 'from os.path import join, split\n'

    test_input = ('from os.\\\n'
                  '    path import (join, split)')
    assert SortImports(file_contents=test_input).output == 'from os.path import join, split\n'


def test_ensure_support_for_non_typed_but_cased_alphabetic_sort_issue_890():
    test_input = ('from pkg import BALL\n'
                  'from pkg import RC\n'
                  'from pkg import Action\n'
                  'from pkg import Bacoo\n'
                  'from pkg import RCNewCode\n'
                  'from pkg import actual\n'
                  'from pkg import rc\n'
                  'from pkg import recorder\n')
    expected_output = ('from pkg import Action\n'
                       'from pkg import BALL\n'
                       'from pkg import Bacoo\n'
                       'from pkg import RC\n'
                       'from pkg import RCNewCode\n'
                       'from pkg import actual\n'
                       'from pkg import rc\n'
                       'from pkg import recorder\n')
    assert SortImports(file_contents=test_input, case_sensitive=True, order_by_type=False,
                       force_single_line=True).output == expected_output


def test_to_ensure_empty_line_not_added_to_file_start_issue_889():
    test_input = ('# comment\n'
                  'import os\n'
                  '# comment2\n'
                  'import sys\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_to_ensure_correctly_handling_of_whitespace_only_issue_811(capsys):
    test_input = ('import os\n'
                  'import sys\n'
                  '\n'
                  '\x0c\n'
                  'def my_function():\n'
                  '    print("hi")\n')
    SortImports(file_contents=test_input, ignore_whitespace=True)
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


def test_settings_path_skip_issue_909(tmpdir):
    base_dir = tmpdir.mkdir('project')
    config_dir = base_dir.mkdir('conf')
    config_dir.join('.isort.cfg').write('[isort]\n'
                                        'skip =\n'
                                        '    file_to_be_skipped.py\n'
                                        'skip_glob =\n'
                                        '    *glob_skip*\n')

    base_dir.join('file_glob_skip.py').write('import os\n'
                                             '\n'
                                             'print("Hello World")\n'
                                             '\n'
                                             'import sys\n')
    base_dir.join('file_to_be_skipped.py').write('import os\n'
                                                 '\n'
                                                 'print("Hello World")'
                                                 '\n'
                                                 'import sys\n')

    test_run_directory = os.getcwd()
    os.chdir(str(base_dir))
    with pytest.raises(Exception):  # without the settings path provided: the command should not skip & identify errors
        check_output(['isort', '--check-only'])
    results = check_output(['isort', '--check-only', '--settings-path=conf/.isort.cfg'])
    os.chdir(str(test_run_directory))

    assert b'skipped 2' in results.lower()


def test_skip_paths_issue_938(tmpdir):
    base_dir = tmpdir.mkdir('project')
    config_dir = base_dir.mkdir('conf')
    config_dir.join('.isort.cfg').write('[isort]\n'
                                        'line_length = 88\n'
                                        'multi_line_output = 4\n'
                                        'lines_after_imports = 2\n'
                                        'skip_glob =\n'
                                        '    migrations/**.py\n')
    base_dir.join('dont_skip.py').write('import os\n'
                                        '\n'
                                        'print("Hello World")'
                                        '\n'
                                        'import sys\n')

    migrations_dir = base_dir.mkdir('migrations')
    migrations_dir.join('file_glob_skip.py').write('import os\n'
                                                   '\n'
                                                   'print("Hello World")\n'
                                                   '\n'
                                                   'import sys\n')

    test_run_directory = os.getcwd()
    os.chdir(str(base_dir))
    results = check_output(['isort', 'dont_skip.py', 'migrations/file_glob_skip.py'])
    os.chdir(str(test_run_directory))

    assert b'skipped' not in results.lower()

    os.chdir(str(base_dir))
    results = check_output(['isort', '--filter-files', '--settings-path=conf/.isort.cfg', 'dont_skip.py', 'migrations/file_glob_skip.py'])
    os.chdir(str(test_run_directory))

    assert b'skipped 1' in results.lower()


def test_standard_library_deprecates_user_issue_778():
    test_input = ('import os\n'
                  '\n'
                  'import user\n')
    assert SortImports(file_contents=test_input).output == test_input


def test_failing_file_check_916():
    test_input = ('#!/usr/bin/env python\n'
                  '# -*- coding: utf-8 -*-\n'
                  'from __future__ import unicode_literals\n')
    expected_output = ('#!/usr/bin/env python\n'
                       '# -*- coding: utf-8 -*-\n'
                       '# FUTURE\n'
                       'from __future__ import unicode_literals\n')
    settings = {'known_future_library': 'future',
                'import_heading_future': 'FUTURE',
                'sections': ['FUTURE', 'STDLIB', 'NORDIGEN', 'FIRSTPARTY', 'THIRDPARTY', 'LOCALFOLDER'],
                'indent': '    ',
                'multi_line_output': 3,
                'lines_after_imports': 2}
    assert SortImports(file_contents=test_input, **settings).output == expected_output
    assert SortImports(file_contents=expected_output, **settings).output == expected_output
    assert not SortImports(file_contents=expected_output, check=True, **settings).incorrectly_sorted


def test_import_heading_issue_905():
    config = {'import_heading_stdlib': 'Standard library imports',
              'import_heading_thirdparty': 'Third party imports',
              'import_heading_firstparty': 'Local imports',
              'known_third_party': ['numpy'],
              'known_first_party': ['oklib']}
    test_input = ('# Standard library imports\n'
                  'import os.path as osp\n'
                  '\n'
                  '# Third party imports\n'
                  'import numpy as np\n'
                  '\n'
                  '# Local imports\n'
                  'from oklib.plot_ok import imagesc\n')
    assert SortImports(file_contents=test_input, **config).output == test_input


def test_pyi_formatting_issue_942(tmpdir):
    test_input = ('import os\n'
                  '\n'
                  '\n'
                  'def my_method():\n')
    expected_py_output = test_input.splitlines()
    expected_pyi_output = ('import os\n'
                           '\n'
                           'def my_method():\n').splitlines()
    assert SortImports(file_contents=test_input).output.splitlines() == expected_py_output
    assert SortImports(file_contents=test_input,
                       extension="pyi").output.splitlines() == expected_pyi_output

    source_py = tmpdir.join('source.py')
    source_py.write(test_input)
    assert SortImports(file_path=str(source_py)).output.splitlines() == expected_py_output

    source_pyi = tmpdir.join('source.pyi')
    source_pyi.write(test_input)
    assert SortImports(file_path=str(source_pyi)).output.splitlines() == expected_pyi_output
