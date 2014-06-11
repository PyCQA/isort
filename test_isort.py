"""test_isort.py.

Tests all major functionality of the isort library
Should be ran using py.test by simply running by.test in the isort project directory

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

from pies.overrides import *

from isort.isort import SortImports
from isort.settings import WrapModes

REALLY_LONG_IMPORT = ("from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11,"
                      "lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22")
REALLY_LONG_IMPORT_WITH_COMMENT = ("from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, "
                                   "lib10, lib11, lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22"
                                   " # comment")


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


def test_titled_imports():
    """Tests setting custom titled/commented import sections."""
    test_input = ("import sys\n"
                  "import os\n"
                  "import myproject.test\n"
                  "import django.settings")
    test_output = SortImports(file_contents=test_input, known_third_party=['django'],
                              import_heading_stdlib="Standard Library", import_heading_firstparty="My Stuff").output
    assert test_output == ("# Standard Library\n"
                           "import os\n"
                           "import sys\n"
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


def test_atomic_mode():
    # without syntax error, everything works OK
    test_input = ("from b import d, c\n"
                  "from a import f, e\n")
    assert SortImports(file_contents=test_input, atomic=True).output == ("from a import e, f\n"
                                                                          "from b import c, d\n")

    # with syntax error content is not changed
    test_input += "while True print 'Hello world'" # blatant syntax error
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


def test_settings_combine_instead_of_overwrite():
    """Test to ensure settings combine logically, instead of fully overwriting."""
    assert set(SortImports(known_standard_library=['not_std_library']).config['known_standard_library']) == \
           set(SortImports().config['known_standard_library'] + ['not_std_library'])

    assert set(SortImports(not_known_standard_library=['thread']).config['known_standard_library']) == \
           set(item for item in SortImports().config['known_standard_library'] if item != 'thread')


def test_combined_from_and_as_imports():
    """Test to ensure it's possible to combine from and as imports."""
    test_input = ("from translate.misc.multistring import multistring\n"
                  "from translate.storage import base, factory\n"
                  "from translate.storage.placeables import general, parse as rich_parse\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == test_input


def test_as_imports_with_line_length():
    """Test to ensure it's possible to combine from and as imports."""
    test_input = ("from translate.storage import base as storage_base\n"
                  "from translate.storage.placeables import general, parse as rich_parse\n")
    assert SortImports(file_contents=test_input, combine_as_imports=False, line_length=40).output == \
                  ("from translate. \\\n    storage import base as storage_base\n"
                  "from translate.storage. \\\n    placeables import parse as rich_parse\n"
                  "from translate.storage. \\\n    placeables import general\n")


def test_keep_comments():
    """Test to ensure isort properly keeps comments in tact after sorting."""
    # Straight Import
    test_input = ("import foo  # bar\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == test_input

    # Star import
    test_input_star = ("from foo import *  # bar\n")
    assert SortImports(file_contents=test_input_star, combine_as_imports=True).output == test_input_star

    # Force Single Line From Import
    test_input = ("from foo import bar  # comment\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True, force_single_line=True).output == test_input

    # From import
    test_input = ("from foo import bar  # My Comment\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == test_input

    # More complicated case
    test_input = ("from a import b  # My Comment1\n"
                  "from a import c  # My Comment2\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True).output == \
                      ("from a import b  # My Comment1\n"
                       "from a import c  # My Comment2\n")

    # Test case where imports comments make imports extend pass the line length
    test_input = ("from a import b # My Comment1\n"
                  "from a import c # My Comment2\n"
                  "from a import d\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True, line_length=45).output == \
                      ("from a import b  # My Comment1\n"
                       "from a import c  # My Comment2\n"
                       "from a import d\n")

    # Test case where imports with comments will be beyond line length limit
    test_input = ("from a import b, c  # My Comment1\n"
                  "from a import c, d # My Comment2 is really really really really long\n")
    assert SortImports(file_contents=test_input, combine_as_imports=True, line_length=45).output == \
                      ("from a import (b,  # My Comment1; My Comment2 is really really really really long\n"
                       "               c, d)\n")


def test_multiline_split_on_dot():
    """Test to ensure isort correctly handles multiline imports, even when split right after a '.'"""
    test_input = ("from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5.\\\n"
                  "    my_module import my_function")
    assert SortImports(file_contents=test_input, line_length=70).output == \
            ("from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5. \\\n"
             "    my_module import my_function\n")


def test_import_star():
    """Test to ensure isort handles star imports correctly"""
    test_input = ("from blah import *\n"
                  "from blah import _potato\n")
    assert SortImports(file_contents=test_input).output == ("from blah import *\n"
                                                            "from blah import _potato\n")
    assert SortImports(file_contents=test_input, combine_star=True).output == ("from blah import *\n")


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
