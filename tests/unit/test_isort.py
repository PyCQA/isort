"""Tests all major functionality of the isort library

Should be ran using py.test by simply running py.test in the isort project directory
"""
import os
import os.path
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Iterator, List, Set, Tuple

import py
import pytest
import isort
from isort import main, api, sections
from isort.settings import WrapModes, Config
from isort.utils import exists_case_sensitive
from isort.exceptions import FileSkipped, ExistingSyntaxErrors

try:
    import toml
except ImportError:
    toml = None

TEST_DEFAULT_CONFIG = """
[*.{py,pyi}]
max_line_length = 120
indent_style = space
indent_size = 4
known_first_party = isort
known_third_party = kate
known_something_else = something_entirely_different
sections = FUTURE, STDLIB, THIRDPARTY, FIRSTPARTY, LOCALFOLDER, SOMETHING_ELSE
ignore_frosted_errors = E103
skip = build,.tox,venv
balanced_wrapping = true
"""
SHORT_IMPORT = "from third_party import lib1, lib2, lib3, lib4"
SINGLE_FROM_IMPORT = "from third_party import lib1"
SINGLE_LINE_LONG_IMPORT = "from third_party import lib1, lib2, lib3, lib4, lib5, lib5ab"
REALLY_LONG_IMPORT = (
    "from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11,"
    "lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22"
)
REALLY_LONG_IMPORT_WITH_COMMENT = (
    "from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, "
    "lib10, lib11, lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22"
    " # comment"
)


@pytest.fixture(scope="session", autouse=True)
def default_settings_path(tmpdir_factory) -> Iterator[str]:
    config_dir = tmpdir_factory.mktemp("config")
    config_file = config_dir.join(".editorconfig").strpath

    with open(config_file, "w") as editorconfig:
        editorconfig.write(TEST_DEFAULT_CONFIG)

    assert Config(config_file).known_other

    with config_dir.as_cwd():
        yield config_dir.strpath


def test_happy_path() -> None:
    """Test the most basic use case, straight imports no code, simply not organized by category."""
    test_input = "import sys\nimport os\nimport myproject.test\nimport django.settings"
    test_output = isort.code(test_input, known_first_party=["myproject"])
    assert test_output == (
        "import os\n" "import sys\n" "\n" "import django.settings\n" "\n" "import myproject.test\n"
    )


def test_code_intermixed() -> None:
    """Defines what should happen when isort encounters imports intermixed with
    code.

    (it should pull them all to the top)

    """
    test_input = (
        "import sys\n"
        "print('yo')\n"
        "print('I like to put code between imports cause I want stuff to break')\n"
        "import myproject.test\n"
    )
    test_output = isort.code(test_input)
    assert test_output == (
        "import sys\n"
        "\n"
        "print('yo')\n"
        "print('I like to put code between imports cause I want stuff to break')\n"
        "import myproject.test\n"
    )


def test_correct_space_between_imports() -> None:
    """Ensure after imports a correct amount of space (in newlines) is
    enforced.

    (2 for method, class, or decorator definitions 1 for anything else)

    """
    test_input_method = "import sys\ndef my_method():\n    print('hello world')\n"
    test_output_method = isort.code(test_input_method)
    assert test_output_method == ("import sys\n\n\ndef my_method():\n    print('hello world')\n")

    test_input_decorator = (
        "import sys\n" "@my_decorator\n" "def my_method():\n" "    print('hello world')\n"
    )
    test_output_decorator = isort.code(test_input_decorator)
    assert test_output_decorator == (
        "import sys\n" "\n" "\n" "@my_decorator\n" "def my_method():\n" "    print('hello world')\n"
    )

    test_input_class = "import sys\nclass MyClass(object):\n    pass\n"
    test_output_class = isort.code(test_input_class)
    assert test_output_class == "import sys\n\n\nclass MyClass(object):\n    pass\n"

    test_input_other = "import sys\nprint('yo')\n"
    test_output_other = isort.code(test_input_other)
    assert test_output_other == "import sys\n\nprint('yo')\n"

    test_input_inquotes = (
        "import sys\n"
        "@my_decorator('''hello\nworld''')\n"
        "def my_method():\n"
        "    print('hello world')\n"
    )
    test_output_inquotes = api.sort_code_string(test_input_inquotes)
    assert (
        test_output_inquotes == "import sys\n"
        "\n\n"
        "@my_decorator('''hello\nworld''')\n"
        "def my_method():\n"
        "    print('hello world')\n"
    )
    test_input_assign = "import sys\nVAR = 1\n"
    test_output_assign = api.sort_code_string(test_input_assign)
    assert test_output_assign == "import sys\n\nVAR = 1\n"

    test_input_assign = "import sys\nVAR = 1\ndef y():\n"
    test_output_assign = api.sort_code_string(test_input_assign)
    assert test_output_assign == "import sys\n\nVAR = 1\ndef y():\n"

    test_input = """
import os

x = "hi"
def x():
    pass
"""
    assert isort.code(test_input) == test_input


def test_sort_on_number() -> None:
    """Ensure numbers get sorted logically (10 > 9 not the other way around)"""
    test_input = "import lib10\nimport lib9\n"
    test_output = isort.code(test_input)
    assert test_output == "import lib9\nimport lib10\n"


def test_line_length() -> None:
    """Ensure isort enforces the set line_length."""
    assert len(isort.code(REALLY_LONG_IMPORT, line_length=80).split("\n")[0]) <= 80
    assert len(isort.code(REALLY_LONG_IMPORT, line_length=120).split("\n")[0]) <= 120

    test_output = isort.code(REALLY_LONG_IMPORT, line_length=42)
    assert test_output == (
        "from third_party import (lib1, lib2, lib3,\n"
        "                         lib4, lib5, lib6,\n"
        "                         lib7, lib8, lib9,\n"
        "                         lib10, lib11,\n"
        "                         lib12, lib13,\n"
        "                         lib14, lib15,\n"
        "                         lib16, lib17,\n"
        "                         lib18, lib20,\n"
        "                         lib21, lib22)\n"
    )

    test_input = (
        "from django.contrib.gis.gdal.field import (\n"
        "    OFTDate, OFTDateTime, OFTInteger, OFTInteger64, OFTReal, OFTString,\n"
        "    OFTTime,\n"
        ")\n"
    )  # Test case described in issue #654
    assert (
        isort.code(
            code=test_input,
            include_trailing_comma=True,
            line_length=79,
            multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
            balanced_wrapping=False,
        )
        == test_input
    )

    test_output = isort.code(code=REALLY_LONG_IMPORT, line_length=42, wrap_length=32)
    assert test_output == (
        "from third_party import (lib1,\n"
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
        "                         lib22)\n"
    )

    test_input = (
        "from .test import a_very_long_function_name_that_exceeds_the_normal_pep8_line_length\n"
    )
    with pytest.raises(ValueError):
        test_output = isort.code(code=REALLY_LONG_IMPORT, line_length=80, wrap_length=99)
    test_output = isort.code(REALLY_LONG_IMPORT, line_length=100, wrap_length=99) == test_input

    # Test Case described in issue #1015
    test_output = isort.code(
        REALLY_LONG_IMPORT, line_length=25, multi_line_output=WrapModes.HANGING_INDENT
    )
    assert test_output == (
        "from third_party import \\\n"
        "    lib1, lib2, lib3, \\\n"
        "    lib4, lib5, lib6, \\\n"
        "    lib7, lib8, lib9, \\\n"
        "    lib10, lib11, \\\n"
        "    lib12, lib13, \\\n"
        "    lib14, lib15, \\\n"
        "    lib16, lib17, \\\n"
        "    lib18, lib20, \\\n"
        "    lib21, lib22\n"
    )


def test_output_modes() -> None:
    """Test setting isort to use various output modes works as expected"""
    test_output_grid = isort.code(
        code=REALLY_LONG_IMPORT, multi_line_output=WrapModes.GRID, line_length=40
    )
    assert test_output_grid == (
        "from third_party import (lib1, lib2,\n"
        "                         lib3, lib4,\n"
        "                         lib5, lib6,\n"
        "                         lib7, lib8,\n"
        "                         lib9, lib10,\n"
        "                         lib11, lib12,\n"
        "                         lib13, lib14,\n"
        "                         lib15, lib16,\n"
        "                         lib17, lib18,\n"
        "                         lib20, lib21,\n"
        "                         lib22)\n"
    )

    test_output_vertical = isort.code(
        code=REALLY_LONG_IMPORT, multi_line_output=WrapModes.VERTICAL, line_length=40
    )
    assert test_output_vertical == (
        "from third_party import (lib1,\n"
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
        "                         lib22)\n"
    )

    comment_output_vertical = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT, multi_line_output=WrapModes.VERTICAL, line_length=40
    )
    assert comment_output_vertical == (
        "from third_party import (lib1,  # comment\n"
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
        "                         lib22)\n"
    )

    test_output_hanging_indent = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent="    ",
    )
    assert test_output_hanging_indent == (
        "from third_party import lib1, lib2, \\\n"
        "    lib3, lib4, lib5, lib6, lib7, \\\n"
        "    lib8, lib9, lib10, lib11, lib12, \\\n"
        "    lib13, lib14, lib15, lib16, lib17, \\\n"
        "    lib18, lib20, lib21, lib22\n"
    )

    comment_output_hanging_indent = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent="    ",
    )
    assert comment_output_hanging_indent == (
        "from third_party import lib1, \\  # comment\n"
        "    lib2, lib3, lib4, lib5, lib6, \\\n"
        "    lib7, lib8, lib9, lib10, lib11, \\\n"
        "    lib12, lib13, lib14, lib15, lib16, \\\n"
        "    lib17, lib18, lib20, lib21, lib22\n"
    )

    test_output_vertical_indent = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=40,
        indent="    ",
    )
    assert test_output_vertical_indent == (
        "from third_party import (\n"
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
        ")\n"
    )

    comment_output_vertical_indent = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=40,
        indent="    ",
    )
    assert comment_output_vertical_indent == (
        "from third_party import (  # comment\n"
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
        ")\n"
    )

    test_output_vertical_grid = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID,
        line_length=40,
        indent="    ",
    )
    assert test_output_vertical_grid == (
        "from third_party import (\n"
        "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
        "    lib7, lib8, lib9, lib10, lib11,\n"
        "    lib12, lib13, lib14, lib15, lib16,\n"
        "    lib17, lib18, lib20, lib21, lib22)\n"
    )

    comment_output_vertical_grid = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.VERTICAL_GRID,
        line_length=40,
        indent="    ",
    )
    assert comment_output_vertical_grid == (
        "from third_party import (  # comment\n"
        "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
        "    lib7, lib8, lib9, lib10, lib11,\n"
        "    lib12, lib13, lib14, lib15, lib16,\n"
        "    lib17, lib18, lib20, lib21, lib22)\n"
    )

    test_output_vertical_grid_grouped = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        line_length=40,
        indent="    ",
    )
    assert test_output_vertical_grid_grouped == (
        "from third_party import (\n"
        "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
        "    lib7, lib8, lib9, lib10, lib11,\n"
        "    lib12, lib13, lib14, lib15, lib16,\n"
        "    lib17, lib18, lib20, lib21, lib22\n"
        ")\n"
    )

    comment_output_vertical_grid_grouped = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        line_length=40,
        indent="    ",
    )
    assert comment_output_vertical_grid_grouped == (
        "from third_party import (  # comment\n"
        "    lib1, lib2, lib3, lib4, lib5, lib6,\n"
        "    lib7, lib8, lib9, lib10, lib11,\n"
        "    lib12, lib13, lib14, lib15, lib16,\n"
        "    lib17, lib18, lib20, lib21, lib22\n"
        ")\n"
    )

    output_noqa = isort.code(code=REALLY_LONG_IMPORT_WITH_COMMENT, multi_line_output=WrapModes.NOQA)
    assert output_noqa == (
        "from third_party import lib1, lib2, lib3, lib4, lib5, lib6, lib7,"
        " lib8, lib9, lib10, lib11,"
        " lib12, lib13, lib14, lib15, lib16, lib17, lib18, lib20, lib21, lib22  "
        "# NOQA comment\n"
    )

    test_case = isort.code(
        code=SINGLE_LINE_LONG_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED_NO_COMMA,
        line_length=40,
        indent="    ",
    )
    test_output_vertical_grid_grouped_doesnt_wrap_early = test_case
    assert test_output_vertical_grid_grouped_doesnt_wrap_early == (
        "from third_party import (\n    lib1, lib2, lib3, lib4, lib5, lib5ab\n)\n"
    )

    test_output_prefix_from_module = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.VERTICAL_PREFIX_FROM_MODULE_IMPORT,
        line_length=40,
    )
    assert test_output_prefix_from_module == (
        "from third_party import lib1, lib2\n"
        "from third_party import lib3, lib4\n"
        "from third_party import lib5, lib6\n"
        "from third_party import lib7, lib8\n"
        "from third_party import lib9, lib10\n"
        "from third_party import lib11, lib12\n"
        "from third_party import lib13, lib14\n"
        "from third_party import lib15, lib16\n"
        "from third_party import lib17, lib18\n"
        "from third_party import lib20, lib21\n"
        "from third_party import lib22\n"
    )

    test_output_prefix_from_module_with_comment = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.VERTICAL_PREFIX_FROM_MODULE_IMPORT,
        line_length=40,
        indent="    ",
    )
    assert test_output_prefix_from_module_with_comment == (
        "from third_party import lib1  # comment\n"
        "from third_party import lib2, lib3\n"
        "from third_party import lib4, lib5\n"
        "from third_party import lib6, lib7\n"
        "from third_party import lib8, lib9\n"
        "from third_party import lib10, lib11\n"
        "from third_party import lib12, lib13\n"
        "from third_party import lib14, lib15\n"
        "from third_party import lib16, lib17\n"
        "from third_party import lib18, lib20\n"
        "from third_party import lib21, lib22\n"
    )

    test_output_hanging_indent_with_parentheses = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT_WITH_PARENTHESES,
        line_length=40,
        indent="    ",
    )
    assert test_output_hanging_indent_with_parentheses == (
        "from third_party import (lib1, lib2,\n"
        "    lib3, lib4, lib5, lib6, lib7, lib8,\n"
        "    lib9, lib10, lib11, lib12, lib13,\n"
        "    lib14, lib15, lib16, lib17, lib18,\n"
        "    lib20, lib21, lib22)\n"
    )

    comment_output_hanging_indent_with_parentheses = isort.code(
        code=REALLY_LONG_IMPORT_WITH_COMMENT,
        multi_line_output=WrapModes.HANGING_INDENT_WITH_PARENTHESES,
        line_length=40,
        indent="    ",
    )
    assert comment_output_hanging_indent_with_parentheses == (
        "from third_party import (lib1,  # comment\n"
        "    lib2, lib3, lib4, lib5, lib6, lib7,\n"
        "    lib8, lib9, lib10, lib11, lib12,\n"
        "    lib13, lib14, lib15, lib16, lib17,\n"
        "    lib18, lib20, lib21, lib22)\n"
    )

    test_input = (
        "def a():\n"
        "    from allennlp.modules.text_field_embedders.basic_text_field_embedder"
        " import BasicTextFieldEmbedder"
    )
    test_output = isort.code(test_input, line_length=100)
    assert test_output == (
        "def a():\n"
        "    from allennlp.modules.text_field_embedders.basic_text_field_embedder import \\\n"
        "        BasicTextFieldEmbedder"
    )

    test_input = (
        "class A:\n"
        "    def a():\n"
        "        from allennlp.common.registrable import Registrable"
        "  # import here to avoid circular imports\n"
        "\n\n"
        "class B:\n"
        "    def b():\n"
        "        from allennlp.common.registrable import Registrable"
        "  # import here to avoid circular imports\n"
    )
    test_output = isort.code(test_input, line_length=100)
    assert test_output == test_input


def test_qa_comment_case() -> None:
    test_input = "from veryveryveryveryveryveryveryveryveryveryvery import X  # NOQA"
    test_output = isort.code(code=test_input, line_length=40, multi_line_output=WrapModes.NOQA)
    assert test_output == "from veryveryveryveryveryveryveryveryveryveryvery import X  # NOQA\n"

    test_input = "import veryveryveryveryveryveryveryveryveryveryvery  # NOQA"
    test_output = isort.code(code=test_input, line_length=40, multi_line_output=WrapModes.NOQA)
    assert test_output == "import veryveryveryveryveryveryveryveryveryveryvery  # NOQA\n"


def test_length_sort() -> None:
    """Test setting isort to sort on length instead of alphabetically."""
    test_input = (
        "import medium_sizeeeeeeeeeeeeee\n"
        "import shortie\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
        "import medium_sizeeeeeeeeeeeeea\n"
    )
    test_output = isort.code(test_input, length_sort=True)
    assert test_output == (
        "import shortie\n"
        "import medium_sizeeeeeeeeeeeeea\n"
        "import medium_sizeeeeeeeeeeeeee\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
    )


def test_length_sort_straight() -> None:
    """Test setting isort to sort straight imports on length instead of alphabetically."""
    test_input = (
        "import medium_sizeeeeeeeeeeeeee\n"
        "import shortie\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
        "from medium_sizeeeeeeeeeeeeee import b\n"
        "from shortie import c\n"
        "from looooooooooooooooooooooooooooooooooooooong import a\n"
    )
    test_output = isort.code(test_input, length_sort_straight=True)
    assert test_output == (
        "import shortie\n"
        "import medium_sizeeeeeeeeeeeeee\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
        "from looooooooooooooooooooooooooooooooooooooong import a\n"
        "from medium_sizeeeeeeeeeeeeee import b\n"
        "from shortie import c\n"
    )


def test_length_sort_section() -> None:
    """Test setting isort to sort on length instead of alphabetically for a specific section."""
    test_input = (
        "import medium_sizeeeeeeeeeeeeee\n"
        "import shortie\n"
        "import datetime\n"
        "import sys\n"
        "import os\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
        "import medium_sizeeeeeeeeeeeeea\n"
    )
    test_output = isort.code(test_input, length_sort_sections=("stdlib",))
    assert test_output == (
        "import os\n"
        "import sys\n"
        "import datetime\n"
        "\n"
        "import looooooooooooooooooooooooooooooooooooooong\n"
        "import medium_sizeeeeeeeeeeeeea\n"
        "import medium_sizeeeeeeeeeeeeee\n"
        "import shortie\n"
    )


def test_convert_hanging() -> None:
    """Ensure that isort will convert hanging indents to correct indent
    method."""
    test_input = (
        "from third_party import lib1, lib2, \\\n"
        "    lib3, lib4, lib5, lib6, lib7, \\\n"
        "    lib8, lib9, lib10, lib11, lib12, \\\n"
        "    lib13, lib14, lib15, lib16, lib17, \\\n"
        "    lib18, lib20, lib21, lib22\n"
    )
    test_output = isort.code(code=test_input, multi_line_output=WrapModes.GRID, line_length=40)
    assert test_output == (
        "from third_party import (lib1, lib2,\n"
        "                         lib3, lib4,\n"
        "                         lib5, lib6,\n"
        "                         lib7, lib8,\n"
        "                         lib9, lib10,\n"
        "                         lib11, lib12,\n"
        "                         lib13, lib14,\n"
        "                         lib15, lib16,\n"
        "                         lib17, lib18,\n"
        "                         lib20, lib21,\n"
        "                         lib22)\n"
    )


def test_custom_indent() -> None:
    """Ensure setting a custom indent will work as expected."""
    test_output = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent="   ",
        balanced_wrapping=False,
    )
    assert test_output == (
        "from third_party import lib1, lib2, \\\n"
        "   lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
        "   lib9, lib10, lib11, lib12, lib13, \\\n"
        "   lib14, lib15, lib16, lib17, lib18, \\\n"
        "   lib20, lib21, lib22\n"
    )

    test_output = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent="'  '",
        balanced_wrapping=False,
    )
    assert test_output == (
        "from third_party import lib1, lib2, \\\n"
        "  lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
        "  lib9, lib10, lib11, lib12, lib13, \\\n"
        "  lib14, lib15, lib16, lib17, lib18, \\\n"
        "  lib20, lib21, lib22\n"
    )

    test_output = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent="tab",
        balanced_wrapping=False,
    )
    assert test_output == (
        "from third_party import lib1, lib2, \\\n"
        "\tlib3, lib4, lib5, lib6, lib7, lib8, \\\n"
        "\tlib9, lib10, lib11, lib12, lib13, \\\n"
        "\tlib14, lib15, lib16, lib17, lib18, \\\n"
        "\tlib20, lib21, lib22\n"
    )

    test_output = isort.code(
        code=REALLY_LONG_IMPORT,
        multi_line_output=WrapModes.HANGING_INDENT,
        line_length=40,
        indent=2,
        balanced_wrapping=False,
    )
    assert test_output == (
        "from third_party import lib1, lib2, \\\n"
        "  lib3, lib4, lib5, lib6, lib7, lib8, \\\n"
        "  lib9, lib10, lib11, lib12, lib13, \\\n"
        "  lib14, lib15, lib16, lib17, lib18, \\\n"
        "  lib20, lib21, lib22\n"
    )


def test_use_parentheses() -> None:
    test_input = (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import "
        "    my_custom_function as my_special_function"
    )
    test_output = isort.code(test_input, line_length=79, use_parentheses=True)

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function)\n"
    )

    test_output = isort.code(
        code=test_input, line_length=79, use_parentheses=True, include_trailing_comma=True
    )

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function,)\n"
    )

    test_output = isort.code(
        code=test_input,
        line_length=79,
        use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
    )

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function\n)\n"
    )

    test_output = isort.code(
        code=test_input,
        line_length=79,
        use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        include_trailing_comma=True,
    )

    assert test_output == (
        "from fooooooooooooooooooooooooo.baaaaaaaaaaaaaaaaaaarrrrrrr import (\n"
        "    my_custom_function as my_special_function,\n)\n"
    )


def test_skip() -> None:
    """Ensure skipping a single import will work as expected."""
    test_input = (
        "import myproject\n"
        "import django\n"
        "print('hey')\n"
        "import sys  # isort: skip this import needs to be placed here\n\n\n\n\n\n\n"
    )

    test_output = isort.code(test_input, known_first_party=["myproject"])
    assert test_output == (
        "import django\n"
        "\n"
        "import myproject\n"
        "\n"
        "print('hey')\n"
        "import sys  # isort: skip this import needs to be placed here\n"
    )


def test_skip_with_file_name() -> None:
    """Ensure skipping a file works even when file_contents is provided."""
    test_input = "import django\nimport myproject\n"
    with pytest.raises(FileSkipped):
        isort.code(
            file_path=Path("/baz.py"), code=test_input, settings_path=os.getcwd(), skip=["baz.py"]
        )


def test_skip_within_file() -> None:
    """Ensure skipping a whole file works."""
    test_input = "# isort: skip_file\nimport django\nimport myproject\n"
    with pytest.raises(FileSkipped):
        isort.code(test_input, known_third_party=["django"])


def test_force_to_top() -> None:
    """Ensure forcing a single import to the top of its category works as expected."""
    test_input = "import lib6\nimport lib2\nimport lib5\nimport lib1\n"
    test_output = isort.code(test_input, force_to_top=["lib5"])
    assert test_output == "import lib5\nimport lib1\nimport lib2\nimport lib6\n"


def test_add_imports() -> None:
    """Ensures adding imports works as expected."""
    test_input = "import lib6\nimport lib2\nimport lib5\nimport lib1\n\n"
    test_output = isort.code(code=test_input, add_imports=["import lib4", "import lib7"])
    assert test_output == (
        "import lib1\n"
        "import lib2\n"
        "import lib4\n"
        "import lib5\n"
        "import lib6\n"
        "import lib7\n"
    )

    # Using simplified syntax
    test_input = "import lib6\nimport lib2\nimport lib5\nimport lib1\n\n"
    test_output = isort.code(code=test_input, add_imports=["lib4", "lib7", "lib8.a"])
    assert test_output == (
        "import lib1\n"
        "import lib2\n"
        "import lib4\n"
        "import lib5\n"
        "import lib6\n"
        "import lib7\n"
        "from lib8 import a\n"
    )

    # On a file that has no pre-existing imports
    test_input = '"""Module docstring"""\n' "class MyClass(object):\n    pass\n"
    test_output = isort.code(code=test_input, add_imports=["from __future__ import print_function"])
    assert test_output == (
        '"""Module docstring"""\n'
        "from __future__ import print_function\n"
        "\n"
        "\n"
        "class MyClass(object):\n"
        "    pass\n"
    )

    # On a file that has no pre-existing imports, and no doc-string
    test_input = "class MyClass(object):\n    pass\n"
    test_output = isort.code(code=test_input, add_imports=["from __future__ import print_function"])
    assert test_output == (
        "from __future__ import print_function\n" "\n" "\n" "class MyClass(object):\n" "    pass\n"
    )

    # On a file with no content what so ever
    test_input = ""
    test_output = isort.code(test_input, add_imports=["lib4"])
    assert test_output == ("")

    # On a file with no content what so ever, after force_adds is set to True
    test_input = ""
    test_output = isort.code(code=test_input, add_imports=["lib4"], force_adds=True)
    assert test_output == ("import lib4\n")


def test_remove_imports() -> None:
    """Ensures removing imports works as expected."""
    test_input = "import lib6\nimport lib2\nimport lib5\nimport lib1"
    test_output = isort.code(test_input, remove_imports=["lib2", "lib6"])
    assert test_output == "import lib1\nimport lib5\n"

    # Using natural syntax
    test_input = (
        "import lib6\n" "import lib2\n" "import lib5\n" "import lib1\n" "from lib8 import a"
    )
    test_output = isort.code(
        code=test_input, remove_imports=["import lib2", "import lib6", "from lib8 import a"]
    )
    assert test_output == "import lib1\nimport lib5\n"

    # From imports
    test_input = "from x import y"
    test_output = isort.code(test_input, remove_imports=["x"])
    assert test_output == ""

    test_input = "from x import y"
    test_output = isort.code(test_input, remove_imports=["x.y"])
    assert test_output == ""


def test_comments_above():
    """Test to ensure comments above an import will stay in place"""
    test_input = "import os\n\nfrom x import y\n\n# comment\nfrom z import __version__, api\n"
    assert isort.code(test_input, ensure_newline_before_comments=True) == test_input


def test_explicitly_local_import() -> None:
    """Ensure that explicitly local imports are separated."""
    test_input = "import lib1\nimport lib2\nimport .lib6\nfrom . import lib7"
    assert isort.code(test_input) == (
        "import lib1\nimport lib2\n\nimport .lib6\nfrom . import lib7\n"
    )
    assert isort.code(test_input, old_finders=True) == (
        "import lib1\nimport lib2\n\nimport .lib6\nfrom . import lib7\n"
    )


def test_quotes_in_file() -> None:
    """Ensure imports within triple quotes don't get imported."""
    test_input = "import os\n\n" '"""\n' "Let us\nimport foo\nokay?\n" '"""\n'
    assert isort.code(test_input) == test_input

    test_input = "import os\n\n" '\'"""\'\n' "import foo\n"
    assert isort.code(test_input) == test_input

    test_input = "import os\n\n" '"""Let us"""\n' "import foo\n\n" '"""okay?"""\n'
    assert isort.code(test_input) == test_input

    test_input = "import os\n\n" '#"""\n' "import foo\n" '#"""'
    assert isort.code(test_input) == ('import os\n\nimport foo\n\n#"""\n#"""\n')

    test_input = "import os\n\n'\\\nimport foo'\n"
    assert isort.code(test_input) == test_input

    test_input = "import os\n\n'''\n\\'''\nimport junk\n'''\n"
    assert isort.code(test_input) == test_input


def test_check_newline_in_imports(capsys) -> None:
    """Ensure tests works correctly when new lines are in imports."""
    test_input = "from lib1 import (\n    sub1,\n    sub2,\n    sub3\n)\n"

    assert api.check_code_string(
        code=test_input,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=20,
        verbose=True,
    )
    out, _ = capsys.readouterr()
    assert "SUCCESS" in out

    # if the verbose is only on modified outputs no output will be given
    assert api.check_code_string(
        code=test_input,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=20,
        verbose=True,
        only_modified=True,
    )
    out, _ = capsys.readouterr()
    assert not out

    # we can make the input invalid to again see output
    test_input = "from lib1 import (\n    sub2,\n    sub1,\n    sub3\n)\n"
    assert not api.check_code_string(
        code=test_input,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=20,
        verbose=True,
        only_modified=True,
    )
    out, _ = capsys.readouterr()
    assert out


def test_forced_separate() -> None:
    """Ensure that forcing certain sub modules to show separately works as expected."""
    test_input = (
        "import sys\n"
        "import warnings\n"
        "from collections import OrderedDict\n"
        "\n"
        "from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation\n"
        "from django.core.paginator import InvalidPage\n"
        "from django.core.urlresolvers import reverse\n"
        "from django.db import models\n"
        "from django.db.models.fields import FieldDoesNotExist\n"
        "from django.utils import six\n"
        "\n"
        "from django.utils.deprecation import RenameMethodsBase\n"
        "from django.utils.encoding import force_str, force_text\n"
        "from django.utils.http import urlencode\n"
        "from django.utils.translation import ugettext, ugettext_lazy\n"
        "\n"
        "from django.contrib.admin import FieldListFilter\n"
        "from django.contrib.admin.exceptions import DisallowedModelAdminLookup\n"
        "from django.contrib.admin.options import IncorrectLookupParameters, IS_POPUP_VAR, "
        "TO_FIELD_VAR\n"
    )
    assert (
        isort.code(
            code=test_input,
            forced_separate=["django.utils.*", "django.contrib"],
            known_third_party=["django"],
            line_length=120,
            order_by_type=False,
        )
        == test_input
    )
    assert (
        isort.code(
            code=test_input,
            forced_separate=["django.utils.*", "django.contrib"],
            known_third_party=["django"],
            line_length=120,
            order_by_type=False,
            old_finders=True,
        )
        == test_input
    )

    test_input = "from .foo import bar\n\nfrom .y import ca\n"
    assert (
        isort.code(code=test_input, forced_separate=[".y"], line_length=120, order_by_type=False)
        == test_input
    )
    assert (
        isort.code(
            code=test_input,
            forced_separate=[".y"],
            line_length=120,
            order_by_type=False,
            old_finders=True,
        )
        == test_input
    )


def test_default_section() -> None:
    """Test to ensure changing the default section works as expected."""
    test_input = "import sys\nimport os\nimport myproject.test\nimport django.settings"
    test_output = isort.code(
        code=test_input, known_third_party=["django"], default_section="FIRSTPARTY"
    )
    assert test_output == (
        "import os\n" "import sys\n" "\n" "import django.settings\n" "\n" "import myproject.test\n"
    )

    test_output_custom = isort.code(
        code=test_input, known_third_party=["django"], default_section="STDLIB"
    )
    assert test_output_custom == (
        "import myproject.test\n" "import os\n" "import sys\n" "\n" "import django.settings\n"
    )


def test_first_party_overrides_standard_section() -> None:
    """Test to ensure changing the default section works as expected."""
    test_input = (
        "from HTMLParser import HTMLParseError, HTMLParser\n"
        "import sys\n"
        "import os\n"
        "import profile.test\n"
    )
    test_output = isort.code(code=test_input, known_first_party=["profile"], py_version="27")
    assert test_output == (
        "import os\n"
        "import sys\n"
        "from HTMLParser import HTMLParseError, HTMLParser\n"
        "\n"
        "import profile.test\n"
    )


def test_thirdy_party_overrides_standard_section() -> None:
    """Test to ensure changing the default section works as expected."""
    test_input = "import sys\nimport os\nimport profile.test\n"
    test_output = isort.code(test_input, known_third_party=["profile"])
    assert test_output == "import os\nimport sys\n\nimport profile.test\n"


def test_known_pattern_path_expansion(tmpdir) -> None:
    """Test to ensure patterns ending with path sep gets expanded
    and nested packages treated as known patterns.
    """
    src_dir = tmpdir.mkdir("src")
    src_dir.mkdir("foo")
    src_dir.mkdir("bar")
    test_input = (
        "from kate_plugin import isort_plugin\n"
        "import sys\n"
        "from foo import settings\n"
        "import bar\n"
        "import this\n"
        "import os\n"
    )
    test_output = isort.code(
        code=test_input,
        default_section="THIRDPARTY",
        known_first_party=["src/", "this", "kate_plugin"],
        directory=str(tmpdir),
    )
    test_output_old_finder = isort.code(
        code=test_input,
        default_section="FIRSTPARTY",
        old_finders=True,
        known_first_party=["src/", "this", "kate_plugin"],
        directory=str(tmpdir),
    )
    assert (
        test_output_old_finder
        == test_output
        == (
            "import os\n"
            "import sys\n"
            "\n"
            "import bar\n"
            "import this\n"
            "from foo import settings\n"
            "from kate_plugin import isort_plugin\n"
        )
    )


def test_force_single_line_imports() -> None:
    """Test to ensure forcing imports to each have their own line works as expected."""
    test_input = (
        "from third_party import lib1, lib2, \\\n"
        "    lib3, lib4, lib5, lib6, lib7, \\\n"
        "    lib8, lib9, lib10, lib11, lib12, \\\n"
        "    lib13, lib14, lib15, lib16, lib17, \\\n"
        "    lib18, lib20, lib21, lib22\n"
    )
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.GRID, line_length=40, force_single_line=True
    )
    assert test_output == (
        "from third_party import lib1\n"
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
        "from third_party import lib22\n"
    )

    test_input = (
        "from third_party import lib_a, lib_b, lib_d\n" "from third_party.lib_c import lib1\n"
    )
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.GRID, line_length=40, force_single_line=True
    )
    assert test_output == (
        "from third_party import lib_a\n"
        "from third_party import lib_b\n"
        "from third_party import lib_d\n"
        "from third_party.lib_c import lib1\n"
    )


def test_force_single_line_long_imports() -> None:
    test_input = "from veryveryveryveryveryvery import small, big\n"
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.NOQA, line_length=40, force_single_line=True
    )
    assert test_output == (
        "from veryveryveryveryveryvery import big\n"
        "from veryveryveryveryveryvery import small  # NOQA\n"
    )


def test_force_single_line_imports_and_sort_within_sections() -> None:
    test_input = (
        "from third_party import lib_a, lib_b, lib_d\n" "from third_party.lib_c import lib1\n"
    )
    test_output = isort.code(
        code=test_input,
        multi_line_output=WrapModes.GRID,
        line_length=40,
        force_single_line=True,
        force_sort_within_sections=True,
    )
    assert test_output == (
        "from third_party import lib_a\n"
        "from third_party import lib_b\n"
        "from third_party import lib_d\n"
        "from third_party.lib_c import lib1\n"
    )
    test_output = isort.code(
        code=test_input,
        multi_line_output=WrapModes.GRID,
        line_length=40,
        force_single_line=True,
        force_sort_within_sections=True,
        lexicographical=True,
    )
    assert test_output == (
        "from third_party import lib_a\n"
        "from third_party import lib_b\n"
        "from third_party.lib_c import lib1\n"
        "from third_party import lib_d\n"
    )

    # Ensure force_sort_within_sections can work with length sort
    # See: https://github.com/pycqa/isort/issues/1038
    test_input = """import sympy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
"""
    test_output = (
        isort.code(code=test_input, force_sort_within_sections=True, length_sort=True) == test_input
    )


def test_titled_imports() -> None:
    """Tests setting custom titled/commented import sections."""
    test_input = (
        "import sys\n"
        "import unicodedata\n"
        "import statistics\n"
        "import os\n"
        "import myproject.test\n"
        "import django.settings"
    )
    test_output = isort.code(
        code=test_input,
        known_first_party=["myproject"],
        import_heading_stdlib="Standard Library",
        import_heading_firstparty="My Stuff",
    )
    assert test_output == (
        "# Standard Library\n"
        "import os\n"
        "import statistics\n"
        "import sys\n"
        "import unicodedata\n"
        "\n"
        "import django.settings\n"
        "\n"
        "# My Stuff\n"
        "import myproject.test\n"
    )
    test_second_run = isort.code(
        code=test_output,
        known_first_party=["myproject"],
        import_heading_stdlib="Standard Library",
        import_heading_firstparty="My Stuff",
    )
    assert test_second_run == test_output


def test_balanced_wrapping() -> None:
    """Tests balanced wrapping mode, where the length of individual lines maintain width."""
    test_input = (
        "from __future__ import (absolute_import, division, print_function,\n"
        "                        unicode_literals)"
    )
    test_output = isort.code(code=test_input, line_length=70, balanced_wrapping=True)
    assert test_output == (
        "from __future__ import (absolute_import, division,\n"
        "                        print_function, unicode_literals)\n"
    )


def test_relative_import_with_space() -> None:
    """Tests the case where the relation and the module that is being imported from is separated
    with a space.
    """
    test_input = "from ... fields.sproqet import SproqetCollection"
    assert isort.code(test_input) == ("from ...fields.sproqet import SproqetCollection\n")
    test_input = "from .import foo"
    test_output = "from . import foo\n"
    assert isort.code(test_input) == test_output
    test_input = "from.import foo"
    test_output = "from . import foo\n"
    assert isort.code(test_input) == test_output


def test_multiline_import() -> None:
    """Test the case where import spawns multiple lines with inconsistent indentation."""
    test_input = "from pkg \\\n    import stuff, other_suff \\\n               more_stuff"
    assert isort.code(test_input) == ("from pkg import more_stuff, other_suff, stuff\n")

    # test again with a custom configuration
    custom_configuration = {
        "force_single_line": True,
        "line_length": 120,
        "known_first_party": ["asdf", "qwer"],
        "default_section": "THIRDPARTY",
        "forced_separate": "asdf",
    }  # type: Dict[str, Any]
    expected_output = (
        "from pkg import more_stuff\n" "from pkg import other_suff\n" "from pkg import stuff\n"
    )
    assert isort.code(test_input, **custom_configuration) == expected_output


def test_single_multiline() -> None:
    """Test the case where a single import spawns multiple lines."""
    test_input = "from os import\\\n        getuid\n\nprint getuid()\n"
    output = isort.code(test_input)
    assert output == ("from os import getuid\n\nprint getuid()\n")


def test_atomic_mode() -> None:
    # without syntax error, everything works OK
    test_input = "from b import d, c\nfrom a import f, e\n"
    assert isort.code(test_input, atomic=True) == ("from a import e, f\nfrom b import c, d\n")

    # with syntax error content is not changed
    test_input += "while True print 'Hello world'"  # blatant syntax error
    with pytest.raises(ExistingSyntaxErrors):
        isort.code(test_input, atomic=True)


def test_order_by_type() -> None:
    test_input = "from module import Class, CONSTANT, function"
    assert isort.code(test_input, order_by_type=True) == (
        "from module import CONSTANT, Class, function\n"
    )

    # More complex sample data
    test_input = "from module import Class, CONSTANT, function, BASIC, Apple"
    assert isort.code(test_input, order_by_type=True) == (
        "from module import BASIC, CONSTANT, Apple, Class, function\n"
    )

    # Really complex sample data, to verify we don't mess with top level imports, only nested ones
    test_input = (
        "import StringIO\n"
        "import glob\n"
        "import os\n"
        "import shutil\n"
        "import tempfile\n"
        "import time\n"
        "from subprocess import PIPE, Popen, STDOUT\n"
    )

    assert isort.code(test_input, order_by_type=True, py_version="27") == (
        "import glob\n"
        "import os\n"
        "import shutil\n"
        "import StringIO\n"
        "import tempfile\n"
        "import time\n"
        "from subprocess import PIPE, STDOUT, Popen\n"
    )


def test_custom_lines_after_import_section() -> None:
    """Test the case where the number of lines to output after imports has been explicitly set."""
    test_input = "from a import b\nfoo = 'bar'\n"

    # default case is one space if not method or class after imports
    assert isort.code(test_input) == ("from a import b\n\nfoo = 'bar'\n")

    # test again with a custom number of lines after the import section
    assert isort.code(test_input, lines_after_imports=2) == ("from a import b\n\n\nfoo = 'bar'\n")


def test_smart_lines_after_import_section() -> None:
    """Tests the default 'smart' behavior for dealing with lines after the import section"""
    # one space if not method or class after imports
    test_input = "from a import b\nfoo = 'bar'\n"
    assert isort.code(test_input) == ("from a import b\n\nfoo = 'bar'\n")

    # two spaces if a method or class after imports
    test_input = "from a import b\ndef my_function():\n    pass\n"
    assert isort.code(test_input) == ("from a import b\n\n\ndef my_function():\n    pass\n")

    # two spaces if an async method after imports
    test_input = "from a import b\nasync def my_function():\n    pass\n"
    assert isort.code(test_input) == ("from a import b\n\n\nasync def my_function():\n    pass\n")

    # two spaces if a method or class after imports - even if comment before function
    test_input = (
        "from a import b\n" "# comment should be ignored\n" "def my_function():\n" "    pass\n"
    )
    assert isort.code(test_input) == (
        "from a import b\n"
        "\n"
        "\n"
        "# comment should be ignored\n"
        "def my_function():\n"
        "    pass\n"
    )

    # the same logic does not apply to doc strings
    test_input = (
        "from a import b\n"
        '"""\n'
        "    comment should be ignored\n"
        '"""\n'
        "def my_function():\n"
        "    pass\n"
    )
    assert isort.code(test_input) == (
        "from a import b\n"
        "\n"
        '"""\n'
        "    comment should be ignored\n"
        '"""\n'
        "def my_function():\n"
        "    pass\n"
    )

    # Ensure logic doesn't incorrectly skip over assignments to multi-line strings
    test_input = 'from a import b\nX = """test\n"""\ndef my_function():\n    pass\n'
    assert isort.code(test_input) == (
        "from a import b\n" "\n" 'X = """test\n' '"""\n' "def my_function():\n" "    pass\n"
    )


def test_settings_overwrite() -> None:
    """Test to ensure settings overwrite instead of trying to combine."""
    assert Config(known_standard_library=["not_std_library"]).known_standard_library == frozenset(
        {"not_std_library"}
    )
    assert Config(known_first_party=["thread"]).known_first_party == frozenset({"thread"})


def test_combined_from_and_as_imports() -> None:
    """Test to ensure it's possible to combine from and as imports."""
    test_input = (
        "from translate.misc.multistring import multistring\n"
        "from translate.storage import base, factory\n"
        "from translate.storage.placeables import general, parse as rich_parse\n"
    )
    assert isort.code(test_input, combine_as_imports=True) == test_input
    test_input = "import os \nimport os as _os"
    test_output = "import os\nimport os as _os\n"
    assert isort.code(test_input) == test_output


def test_as_imports_with_line_length() -> None:
    """Test to ensure it's possible to combine from and as imports."""
    test_input = (
        "from translate.storage import base as storage_base\n"
        "from translate.storage.placeables import general, parse as rich_parse\n"
    )
    assert isort.code(code=test_input, combine_as_imports=False, line_length=40) == (
        "from translate.storage import \\\n    base as storage_base\n"
        "from translate.storage.placeables import \\\n    general\n"
        "from translate.storage.placeables import \\\n    parse as rich_parse\n"
    )


def test_keep_comments() -> None:
    """Test to ensure isort properly keeps comments in tact after sorting."""
    # Straight Import
    test_input = "import foo  # bar\n"
    assert isort.code(test_input) == test_input

    # Star import
    test_input_star = "from foo import *  # bar\n"
    assert isort.code(test_input_star) == test_input_star

    # Force Single Line From Import
    test_input = "from foo import bar  # comment\n"
    assert isort.code(test_input, force_single_line=True) == test_input

    # From import
    test_input = "from foo import bar  # My Comment\n"
    assert isort.code(test_input) == test_input

    # More complicated case
    test_input = "from a import b  # My Comment1\nfrom a import c  # My Comment2\n"
    assert isort.code(test_input) == (
        "from a import b  # My Comment1\nfrom a import c  # My Comment2\n"
    )

    # Test case where imports comments make imports extend pass the line length
    test_input = (
        "from a import b # My Comment1\n" "from a import c # My Comment2\n" "from a import d\n"
    )
    assert isort.code(test_input, line_length=45) == (
        "from a import b  # My Comment1\n" "from a import c  # My Comment2\n" "from a import d\n"
    )

    # Test case where imports with comments will be beyond line length limit
    test_input = (
        "from a import b, c  # My Comment1\n"
        "from a import c, d # My Comment2 is really really really really long\n"
    )
    assert isort.code(test_input, line_length=45) == (
        "from a import (  # My Comment1; My Comment2 is really really really really long\n"
        "    b, c, d)\n"
    )

    # Test that comments are not stripped from 'import ... as ...' by default
    test_input = "from a import b as bb  # b comment\nfrom a import c as cc  # c comment\n"
    assert isort.code(test_input) == test_input

    # Test that 'import ... as ...' comments are not collected inappropriately
    test_input = (
        "from a import b as bb  # b comment\n"
        "from a import c as cc  # c comment\n"
        "from a import d\n"
    )
    assert isort.code(test_input) == test_input
    assert isort.code(test_input, combine_as_imports=True) == (
        "from a import b as bb, c as cc, d  # b comment; c comment\n"
    )


def test_multiline_split_on_dot() -> None:
    """Test to ensure isort correctly handles multiline imports,
    even when split right after a '.'
    """
    test_input = (
        "from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5.\\\n"
        "    my_module import my_function"
    )
    assert isort.code(test_input, line_length=70) == (
        "from my_lib.my_package.test.level_1.level_2.level_3.level_4.level_5.my_module import \\\n"
        "    my_function\n"
    )


def test_import_star() -> None:
    """Test to ensure isort handles star imports correctly"""
    test_input = "from blah import *\nfrom blah import _potato\n"
    assert isort.code(test_input) == ("from blah import *\nfrom blah import _potato\n")
    assert isort.code(test_input, combine_star=True) == ("from blah import *\n")


def test_include_trailing_comma() -> None:
    """Test for the include_trailing_comma option"""
    test_output_grid = isort.code(
        code=SHORT_IMPORT,
        multi_line_output=WrapModes.GRID,
        line_length=40,
        include_trailing_comma=True,
    )
    assert test_output_grid == (
        "from third_party import (lib1, lib2,\n" "                         lib3, lib4,)\n"
    )

    test_output_vertical = isort.code(
        code=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL,
        line_length=40,
        include_trailing_comma=True,
    )
    assert test_output_vertical == (
        "from third_party import (lib1,\n"
        "                         lib2,\n"
        "                         lib3,\n"
        "                         lib4,)\n"
    )

    test_output_vertical_indent = isort.code(
        code=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=40,
        include_trailing_comma=True,
    )
    assert test_output_vertical_indent == (
        "from third_party import (\n" "    lib1,\n" "    lib2,\n" "    lib3,\n" "    lib4,\n" ")\n"
    )

    test_output_vertical_grid = isort.code(
        code=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID,
        line_length=40,
        include_trailing_comma=True,
    )
    assert test_output_vertical_grid == (
        "from third_party import (\n    lib1, lib2, lib3, lib4,)\n"
    )

    test_output_vertical_grid_grouped = isort.code(
        code=SHORT_IMPORT,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
        line_length=40,
        include_trailing_comma=True,
    )
    assert test_output_vertical_grid_grouped == (
        "from third_party import (\n    lib1, lib2, lib3, lib4,\n)\n"
    )

    test_output_wrap_single_import_with_use_parentheses = isort.code(
        code=SINGLE_FROM_IMPORT, line_length=25, include_trailing_comma=True, use_parentheses=True
    )
    assert test_output_wrap_single_import_with_use_parentheses == (
        "from third_party import (\n    lib1,)\n"
    )

    test_output_wrap_single_import_vertical_indent = isort.code(
        code=SINGLE_FROM_IMPORT,
        line_length=25,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        include_trailing_comma=True,
        use_parentheses=True,
    )
    assert test_output_wrap_single_import_vertical_indent == (
        "from third_party import (\n    lib1,\n)\n"
    )

    trailing_comma_with_comment = (
        "from six.moves.urllib.parse import urlencode  "
        "# pylint: disable=no-name-in-module,import-error"
    )
    expected_trailing_comma_with_comment = (
        "from six.moves.urllib.parse import (\n"
        "    urlencode,  # pylint: disable=no-n"
        "ame-in-module,import-error\n)\n"
    )
    trailing_comma_with_comment = isort.code(
        code=trailing_comma_with_comment,
        line_length=80,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        include_trailing_comma=True,
        use_parentheses=True,
    )
    assert trailing_comma_with_comment == expected_trailing_comma_with_comment
    # The next time around, it should be equal
    trailing_comma_with_comment = isort.code(
        code=trailing_comma_with_comment,
        line_length=80,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        include_trailing_comma=True,
        use_parentheses=True,
    )
    assert trailing_comma_with_comment == expected_trailing_comma_with_comment


def test_similar_to_std_library() -> None:
    """Test to ensure modules that are named similarly to a standard library import
    don't end up clobbered
    """
    test_input = "import datetime\n\nimport requests\nimport times\n"
    assert isort.code(test_input, known_third_party=["requests", "times"]) == test_input


def test_correctly_placed_imports() -> None:
    """Test to ensure comments stay on correct placement after being sorted"""
    test_input = "from a import b # comment for b\nfrom a import c # comment for c\n"
    assert isort.code(test_input, force_single_line=True) == (
        "from a import b  # comment for b\nfrom a import c  # comment for c\n"
    )
    assert isort.code(test_input) == (
        "from a import b  # comment for b\nfrom a import c  # comment for c\n"
    )

    # Full example test from issue #143
    test_input = (
        "from itertools import chain\n"
        "\n"
        "from django.test import TestCase\n"
        "from model_mommy import mommy\n"
        "\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_item_product\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_item_product_d"
        "efinition\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_item_product_d"
        "efinition_platform\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_item_product_p"
        "latform\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_territory_reta"
        "il_model\n"
        "from apps.clientman.commands.download_usage_rights import "
        "associate_right_for_territory_reta"
        "il_model_definition_platform_provider  # noqa\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_item_product\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_item_product_defini"
        "tion\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_item_product_defini"
        "tion_platform\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_item_product_platfo"
        "rm\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_territory_retail_mo"
        "del\n"
        "from apps.clientman.commands.download_usage_rights import "
        "clear_right_for_territory_retail_mo"
        "del_definition_platform_provider  # noqa\n"
        "from apps.clientman.commands.download_usage_rights import "
        "create_download_usage_right\n"
        "from apps.clientman.commands.download_usage_rights import "
        "delete_download_usage_right\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_item_product\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_item_product_d"
        "efinition\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_item_product_d"
        "efinition_platform\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_item_product_p"
        "latform\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_territory_reta"
        "il_model\n"
        "from apps.clientman.commands.download_usage_rights import "
        "disable_download_for_territory_reta"
        "il_model_definition_platform_provider  # noqa\n"
        "from apps.clientman.commands.download_usage_rights import "
        "get_download_rights_for_item\n"
        "from apps.clientman.commands.download_usage_rights import "
        "get_right\n"
    )
    assert (
        isort.code(
            code=test_input,
            force_single_line=True,
            line_length=140,
            known_third_party=["django", "model_mommy"],
            default_section=sections.FIRSTPARTY,
        )
        == test_input
    )


def test_auto_detection() -> None:
    """Initial test to ensure isort auto-detection works correctly -
    will grow over time as new issues are raised.
    """

    # Issue 157
    test_input = "import binascii\nimport os\n\nimport cv2\nimport requests\n"
    assert isort.code(test_input, known_third_party=["cv2", "requests"]) == test_input

    # alternative solution
    assert isort.code(test_input, default_section="THIRDPARTY") == test_input


def test_same_line_statements() -> None:
    """Ensure isort correctly handles the case where a single line
    contains multiple statements including an import
    """
    test_input = "import pdb; import nose\n"
    assert isort.code(test_input) == ("import pdb\n\nimport nose\n")

    test_input = "import pdb; pdb.set_trace()\nimport nose; nose.run()\n"
    assert isort.code(test_input) == test_input


def test_long_line_comments() -> None:
    """Ensure isort correctly handles comments at the end of extremely long lines"""
    test_input = (
        "from foo.utils.fabric_stuff.live import check_clean_live, deploy_live, "
        "sync_live_envdir, "
        "update_live_app, update_live_cron  # noqa\n"
        "from foo.utils.fabric_stuff.stage import check_clean_stage, deploy_stage, "
        "sync_stage_envdir, "
        "update_stage_app, update_stage_cron  # noqa\n"
    )
    assert isort.code(code=test_input, line_length=100, balanced_wrapping=True) == (
        "from foo.utils.fabric_stuff.live import (check_clean_live, deploy_live,  # noqa\n"
        "                                         sync_live_envdir, update_live_app, "
        "update_live_cron)\n"
        "from foo.utils.fabric_stuff.stage import (check_clean_stage, deploy_stage,  # noqa\n"
        "                                          sync_stage_envdir, update_stage_app, "
        "update_stage_cron)\n"
    )


def test_tab_character_in_import() -> None:
    """Ensure isort correctly handles import statements that contain a tab character"""
    test_input = (
        "from __future__ import print_function\n" "from __future__ import\tprint_function\n"
    )
    assert isort.code(test_input) == "from __future__ import print_function\n"


def test_split_position() -> None:
    """Ensure isort splits on import instead of . when possible"""
    test_input = (
        "from p24.shared.exceptions.master.host_state_flag_unchanged "
        "import HostStateUnchangedException\n"
    )
    assert isort.code(test_input, line_length=80) == (
        "from p24.shared.exceptions.master.host_state_flag_unchanged import \\\n"
        "    HostStateUnchangedException\n"
    )


def test_place_comments() -> None:
    """Ensure manually placing imports works as expected"""
    test_input = (
        "import sys\n"
        "import os\n"
        "import myproject.test\n"
        "import django.settings\n"
        "\n"
        "# isort: imports-thirdparty\n"
        "# isort: imports-firstparty\n"
        "# isort:imports-stdlib\n"
        "\n"
    )
    expected_output = (
        "\n# isort: imports-thirdparty\n"
        "import django.settings\n"
        "\n"
        "# isort: imports-firstparty\n"
        "import myproject.test\n"
        "\n"
        "# isort:imports-stdlib\n"
        "import os\n"
        "import sys\n"
    )
    test_output = isort.code(test_input, known_first_party=["myproject"])
    assert test_output == expected_output
    test_output = isort.code(test_output, known_first_party=["myproject"])
    assert test_output == expected_output


def test_placement_control() -> None:
    """Ensure that most specific placement control match wins"""
    test_input = (
        "import os\n"
        "import sys\n"
        "from bottle import Bottle, redirect, response, run\n"
        "import p24.imports._argparse as argparse\n"
        "import p24.imports._subprocess as subprocess\n"
        "import p24.imports._VERSION as VERSION\n"
        "import p24.shared.media_wiki_syntax as syntax\n"
    )
    test_output = isort.code(
        code=test_input,
        known_first_party=["p24", "p24.imports._VERSION"],
        known_standard_library=["p24.imports", "os", "sys"],
        known_third_party=["bottle"],
        default_section="THIRDPARTY",
    )

    assert test_output == (
        "import os\n"
        "import p24.imports._argparse as argparse\n"
        "import p24.imports._subprocess as subprocess\n"
        "import sys\n"
        "\n"
        "from bottle import Bottle, redirect, response, run\n"
        "\n"
        "import p24.imports._VERSION as VERSION\n"
        "import p24.shared.media_wiki_syntax as syntax\n"
    )


def test_custom_sections() -> None:
    """Ensure that most specific placement control match wins"""
    test_input = (
        "import os\n"
        "import sys\n"
        "from django.conf import settings\n"
        "from bottle import Bottle, redirect, response, run\n"
        "import p24.imports._argparse as argparse\n"
        "from django.db import models\n"
        "import p24.imports._subprocess as subprocess\n"
        "import pandas as pd\n"
        "import p24.imports._VERSION as VERSION\n"
        "import numpy as np\n"
        "import p24.shared.media_wiki_syntax as syntax\n"
    )
    test_output = isort.code(
        code=test_input,
        known_first_party=["p24", "p24.imports._VERSION"],
        import_heading_stdlib="Standard Library",
        import_heading_thirdparty="Third Party",
        import_heading_firstparty="First Party",
        import_heading_django="Django",
        import_heading_pandas="Pandas",
        known_standard_library=["p24.imports", "os", "sys"],
        known_third_party=["bottle"],
        known_django=["django"],
        known_pandas=["pandas", "numpy"],
        default_section="THIRDPARTY",
        sections=[
            "FUTURE",
            "STDLIB",
            "DJANGO",
            "THIRDPARTY",
            "PANDAS",
            "FIRSTPARTY",
            "LOCALFOLDER",
        ],
    )
    assert test_output == (
        "# Standard Library\n"
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
        "import p24.shared.media_wiki_syntax as syntax\n"
    )


def test_glob_known() -> None:
    """Ensure that most specific placement control match wins"""
    test_input = (
        "import os\n"
        "from django_whatever import whatever\n"
        "import sys\n"
        "from django.conf import settings\n"
        "from . import another\n"
    )
    test_output = isort.code(
        code=test_input,
        import_heading_stdlib="Standard Library",
        import_heading_thirdparty="Third Party",
        import_heading_firstparty="First Party",
        import_heading_django="Django",
        import_heading_djangoplugins="Django Plugins",
        import_heading_localfolder="Local",
        known_django=["django"],
        known_djangoplugins=["django_*"],
        default_section="THIRDPARTY",
        sections=[
            "FUTURE",
            "STDLIB",
            "DJANGO",
            "DJANGOPLUGINS",
            "THIRDPARTY",
            "FIRSTPARTY",
            "LOCALFOLDER",
        ],
    )
    assert test_output == (
        "# Standard Library\n"
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
        "from . import another\n"
    )


def test_sticky_comments() -> None:
    """Test to ensure it is possible to make comments 'stick' above imports"""
    test_input = (
        "import os\n"
        "\n"
        "# Used for type-hinting (ref: https://github.com/davidhalter/jedi/issues/414).\n"
        "from selenium.webdriver.remote.webdriver import WebDriver  # noqa\n"
    )
    assert isort.code(test_input) == test_input

    test_input = (
        "from django import forms\n"
        "# While this couples the geographic forms to the GEOS library,\n"
        "# it decouples from database (by not importing SpatialBackend).\n"
        "from django.contrib.gis.geos import GEOSException, GEOSGeometry\n"
        "from django.utils.translation import ugettext_lazy as _\n"
    )
    assert isort.code(test_input) == test_input


def test_zipimport() -> None:
    """Imports ending in "import" shouldn't be clobbered"""
    test_input = "from zipimport import zipimport\n"
    assert isort.code(test_input) == test_input


def test_from_ending() -> None:
    """Imports ending in "from" shouldn't be clobbered."""
    test_input = "from foo import get_foo_from, get_foo\n"
    expected_output = "from foo import get_foo, get_foo_from\n"
    assert isort.code(test_input) == expected_output


def test_from_first() -> None:
    """Tests the setting from_first works correctly"""
    test_input = "from os import path\nimport os\n"
    assert isort.code(test_input, from_first=True) == test_input


def test_top_comments() -> None:
    """Ensure correct behavior with top comments"""
    test_input = (
        "# -*- encoding: utf-8 -*-\n"
        "# Test comment\n"
        "#\n"
        "from __future__ import unicode_literals\n"
    )
    assert isort.code(test_input) == test_input

    test_input = (
        "# -*- coding: utf-8 -*-\n"
        "from django.db import models\n"
        "from django.utils.encoding import python_2_unicode_compatible\n"
    )
    assert isort.code(test_input) == test_input

    test_input = "# Comment\nimport sys\n"
    assert isort.code(test_input) == test_input

    test_input = "# -*- coding\nimport sys\n"
    assert isort.code(test_input) == test_input


def test_consistency() -> None:
    """Ensures consistency of handling even when dealing with non ordered-by-type imports"""
    test_input = "from sqlalchemy.dialects.postgresql import ARRAY, array\n"
    assert isort.code(test_input, order_by_type=True) == test_input


def test_force_grid_wrap() -> None:
    """Ensures removing imports works as expected."""
    test_input = "from bar import lib2\nfrom foo import lib6, lib7\n"
    test_output = isort.code(
        code=test_input, force_grid_wrap=2, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT
    )
    assert (
        test_output
        == """from bar import lib2
from foo import (
    lib6,
    lib7
)
"""
    )
    test_output = isort.code(
        code=test_input, force_grid_wrap=3, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT
    )
    assert test_output == test_input


def test_force_grid_wrap_long() -> None:
    """Ensure that force grid wrap still happens with long line length"""
    test_input = (
        "from foo import lib6, lib7\n"
        "from bar import lib2\n"
        "from babar import something_that_is_kind_of_long"
    )
    test_output = isort.code(
        code=test_input,
        force_grid_wrap=2,
        multi_line_output=WrapModes.VERTICAL_HANGING_INDENT,
        line_length=9999,
    )
    assert (
        test_output
        == """from babar import something_that_is_kind_of_long
from bar import lib2
from foo import (
    lib6,
    lib7
)
"""
    )


def test_uses_jinja_variables() -> None:
    """Test a basic set of imports that use jinja variables"""
    test_input = (
        "import sys\n" "import os\n" "import myproject.{ test }\n" "import django.{ settings }"
    )
    test_output = isort.code(
        code=test_input, known_third_party=["django"], known_first_party=["myproject"]
    )
    assert test_output == (
        "import os\n"
        "import sys\n"
        "\n"
        "import django.{ settings }\n"
        "\n"
        "import myproject.{ test }\n"
    )

    test_input = "import {{ cookiecutter.repo_name }}\n" "from foo import {{ cookiecutter.bar }}\n"
    assert isort.code(test_input) == test_input


def test_fcntl() -> None:
    """Test to ensure fcntl gets correctly recognized as stdlib import"""
    test_input = "import fcntl\nimport os\nimport sys\n"
    assert isort.code(test_input) == test_input


def test_import_split_is_word_boundary_aware() -> None:
    """Test to ensure that isort splits words in a boundary aware manner"""
    test_input = (
        "from mycompany.model.size_value_array_import_func import \\\n"
        "    get_size_value_array_import_func_jobs"
    )
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=79
    )
    assert test_output == (
        "from mycompany.model.size_value_array_import_func import (\n"
        "    get_size_value_array_import_func_jobs\n"
        ")\n"
    )


def test_other_file_encodings(tmpdir) -> None:
    """Test to ensure file encoding is respected"""
    for encoding in ("latin1", "utf8"):
        tmp_fname = tmpdir.join(f"test_{encoding}.py")
        file_contents = f"# coding: {encoding}\n\ns = u'ã'\n"
        tmp_fname.write_binary(file_contents.encode(encoding))
        api.sort_file(Path(tmp_fname), file_path=Path(tmp_fname), settings_path=os.getcwd())
        assert tmp_fname.read_text(encoding) == file_contents


def test_encoding_not_in_comment(tmpdir) -> None:
    """Test that 'encoding' not in a comment is ignored"""
    tmp_fname = tmpdir.join("test_encoding.py")
    file_contents = "class Foo\n    coding: latin1\n\ns = u'ã'\n"
    tmp_fname.write_binary(file_contents.encode("utf8"))
    assert (
        isort.code(
            Path(tmp_fname).read_text("utf8"), file_path=Path(tmp_fname), settings_path=os.getcwd()
        )
        == file_contents
    )


def test_encoding_not_in_first_two_lines(tmpdir) -> None:
    """Test that 'encoding' not in the first two lines is ignored"""
    tmp_fname = tmpdir.join("test_encoding.py")
    file_contents = "\n\n# -*- coding: latin1\n\ns = u'ã'\n"
    tmp_fname.write_binary(file_contents.encode("utf8"))
    assert (
        isort.code(
            Path(tmp_fname).read_text("utf8"), file_path=Path(tmp_fname), settings_path=os.getcwd()
        )
        == file_contents
    )


def test_comment_at_top_of_file() -> None:
    """Test to ensure isort correctly handles top of file comments"""
    test_input = (
        "# Comment one\n"
        "from django import forms\n"
        "# Comment two\n"
        "from django.contrib.gis.geos import GEOSException\n"
    )
    assert isort.code(test_input) == test_input

    test_input = "# -*- coding: utf-8 -*-\nfrom django.db import models\n"
    assert isort.code(test_input) == test_input


def test_alphabetic_sorting() -> None:
    """Test to ensure isort correctly handles single line imports"""
    test_input = (
        "import unittest\n"
        "\n"
        "import ABC\n"
        "import Zope\n"
        "from django.contrib.gis.geos import GEOSException\n"
        "from plone.app.testing import getRoles\n"
        "from plone.app.testing import ManageRoles\n"
        "from plone.app.testing import setRoles\n"
        "from Products.CMFPlone import utils\n"
    )
    options = {
        "force_single_line": True,
        "force_alphabetical_sort_within_sections": True,
    }  # type: Dict[str, Any]

    output = isort.code(test_input, **options)
    assert output == test_input

    test_input = "# -*- coding: utf-8 -*-\nfrom django.db import models\n"
    assert isort.code(test_input) == test_input


def test_alphabetic_sorting_multi_line() -> None:
    """Test to ensure isort correctly handles multiline import see: issue 364"""
    test_input = (
        "from a import (CONSTANT_A, cONSTANT_B, CONSTANT_C, CONSTANT_D, CONSTANT_E,\n"
        "               CONSTANT_F, CONSTANT_G, CONSTANT_H, CONSTANT_I, CONSTANT_J)\n"
    )
    options = {"force_alphabetical_sort_within_sections": True}  # type: Dict[str, Any]
    assert isort.code(test_input, **options) == test_input


def test_comments_not_duplicated() -> None:
    """Test to ensure comments aren't duplicated: issue 303"""
    test_input = (
        "from flask import url_for\n"
        "# Whole line comment\n"
        "from service import demo  # inline comment\n"
        "from service import settings\n"
    )
    output = isort.code(test_input)
    assert output.count("# Whole line comment\n") == 1
    assert output.count("# inline comment\n") == 1


def test_top_of_line_comments() -> None:
    """Test to ensure top of line comments stay where they should: issue 260"""
    test_input = (
        "# -*- coding: utf-8 -*-\n"
        "from django.db import models\n"
        "#import json as simplejson\n"
        "from myproject.models import Servidor\n"
        "\n"
        "import reversion\n"
        "\n"
        "import logging\n"
    )
    output = isort.code(test_input)
    print(output)
    assert output.startswith("# -*- coding: utf-8 -*-\n")


def test_basic_comment() -> None:
    """Test to ensure a basic comment wont crash isort"""
    test_input = "import logging\n# Foo\nimport os\n"
    assert isort.code(test_input) == test_input


def test_shouldnt_add_lines() -> None:
    """Ensure that isort doesn't add a blank line when a top of import comment is present,
    See: issue #316
    """
    test_input = '"""Text"""\n' "# This is a comment\nimport pkg_resources\n"
    assert isort.code(test_input) == test_input


def test_sections_parsed_correct(tmpdir) -> None:
    """Ensure that modules for custom sections parsed as list from config file and
    isort result is correct
    """
    conf_file_data = (
        "[settings]\n"
        "sections=FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER,COMMON\n"
        "known_common=nose\n"
        "import_heading_common=Common Library\n"
        "import_heading_stdlib=Standard Library\n"
    )
    test_input = "import os\nfrom nose import *\nimport nose\nfrom os import path"
    correct_output = (
        "# Standard Library\n"
        "import os\n"
        "from os import path\n"
        "\n"
        "# Common Library\n"
        "import nose\n"
        "from nose import *\n"
    )
    tmpdir.join(".isort.cfg").write(conf_file_data)
    assert isort.code(test_input, settings_path=str(tmpdir)) == correct_output


@pytest.mark.skipif(toml is None, reason="Requires toml package to be installed.")
def test_pyproject_conf_file(tmpdir) -> None:
    """Ensure that modules for custom sections parsed as list from config file and
    isort result is correct
    """
    conf_file_data = (
        "[build-system]\n"
        'requires = ["setuptools", "wheel"]\n'
        "[tool.poetry]\n"
        'name = "isort"\n'
        'version = "0.1.0"\n'
        'license = "MIT"\n'
        "[tool.isort]\n"
        "lines_between_types=1\n"
        'known_common="nose"\n'
        'known_first_party="foo"\n'
        'import_heading_common="Common Library"\n'
        'import_heading_stdlib="Standard Library"\n'
        'sections="FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER,COMMON"\n'
        "include_trailing_comma = true\n"
    )
    test_input = "import os\nfrom nose import *\nimport nose\nfrom os import path\nimport foo"
    correct_output = (
        "# Standard Library\n"
        "import os\n"
        "\n"
        "from os import path\n"
        "\n"
        "import foo\n"
        "\n"
        "# Common Library\n"
        "import nose\n"
        "\n"
        "from nose import *\n"
    )
    tmpdir.join("pyproject.toml").write(conf_file_data)
    assert isort.code(test_input, settings_path=str(tmpdir)) == correct_output


def test_alphabetic_sorting_no_newlines() -> None:
    """Test to ensure that alphabetical sort does not
    erroneously introduce new lines (issue #328)
    """
    test_input = "import os\n"
    test_output = isort.code(code=test_input, force_alphabetical_sort_within_sections=True)
    assert test_input == test_output

    test_input = "import os\n" "import unittest\n" "\n" "from a import b\n" "\n" "\n" "print(1)\n"
    test_output = isort.code(
        code=test_input, force_alphabetical_sort_within_sections=True, lines_after_imports=2
    )
    assert test_input == test_output


def test_sort_within_section() -> None:
    """Test to ensure its possible to force isort to sort within sections"""
    test_input = (
        "from Foob import ar\n"
        "import foo\n"
        "from foo import bar\n"
        "from foo.bar import Quux, baz\n"
    )
    test_output = isort.code(test_input, force_sort_within_sections=True)
    assert test_output == test_input

    test_input = (
        "import foo\n"
        "from foo import bar\n"
        "from foo.bar import baz\n"
        "from foo.bar import Quux\n"
        "from Foob import ar\n"
    )
    test_output = isort.code(
        code=test_input,
        force_sort_within_sections=True,
        order_by_type=False,
        force_single_line=True,
    )
    assert test_output == test_input


def test_sorting_with_two_top_comments() -> None:
    """Test to ensure isort will sort files that contain 2 top comments"""
    test_input = "#! comment1\n''' comment2\n'''\nimport b\nimport a\n"
    assert isort.code(test_input) == ("#! comment1\n''' comment2\n'''\nimport a\nimport b\n")


def test_lines_between_sections() -> None:
    """Test to ensure lines_between_sections works"""
    test_input = "from bar import baz\nimport os\n"
    assert isort.code(test_input, lines_between_sections=0) == ("import os\nfrom bar import baz\n")
    assert isort.code(test_input, lines_between_sections=2) == (
        "import os\n\n\nfrom bar import baz\n"
    )


def test_forced_sepatate_globs() -> None:
    """Test to ensure that forced_separate glob matches lines"""
    test_input = (
        "import os\n"
        "\n"
        "from myproject.foo.models import Foo\n"
        "\n"
        "from myproject.utils import util_method\n"
        "\n"
        "from myproject.bar.models import Bar\n"
        "\n"
        "import sys\n"
    )
    test_output = isort.code(code=test_input, forced_separate=["*.models"], line_length=120)

    assert test_output == (
        "import os\n"
        "import sys\n"
        "\n"
        "from myproject.utils import util_method\n"
        "\n"
        "from myproject.bar.models import Bar\n"
        "from myproject.foo.models import Foo\n"
    )


def test_no_additional_lines_issue_358() -> None:
    """Test to ensure issue 358 is resolved and running isort multiple times
    does not add extra newlines
    """
    test_input = (
        '"""This is a docstring"""\n'
        "# This is a comment\n"
        "from __future__ import (\n"
        "    absolute_import,\n"
        "    division,\n"
        "    print_function,\n"
        "    unicode_literals\n"
        ")\n"
    )
    expected_output = (
        '"""This is a docstring"""\n'
        "# This is a comment\n"
        "from __future__ import (\n"
        "    absolute_import,\n"
        "    division,\n"
        "    print_function,\n"
        "    unicode_literals\n"
        ")\n"
    )
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
    )
    assert test_output == expected_output

    test_output = isort.code(
        code=test_output, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
    )
    assert test_output == expected_output

    for _attempt in range(5):
        test_output = isort.code(
            code=test_output, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
        )
        assert test_output == expected_output

    test_input = (
        '"""This is a docstring"""\n'
        "\n"
        "# This is a comment\n"
        "from __future__ import (\n"
        "    absolute_import,\n"
        "    division,\n"
        "    print_function,\n"
        "    unicode_literals\n"
        ")\n"
    )
    expected_output = (
        '"""This is a docstring"""\n'
        "\n"
        "# This is a comment\n"
        "from __future__ import (\n"
        "    absolute_import,\n"
        "    division,\n"
        "    print_function,\n"
        "    unicode_literals\n"
        ")\n"
    )
    test_output = isort.code(
        code=test_input, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
    )
    assert test_output == expected_output

    test_output = isort.code(
        code=test_output, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
    )
    assert test_output == expected_output

    for _attempt in range(5):
        test_output = isort.code(
            code=test_output, multi_line_output=WrapModes.VERTICAL_HANGING_INDENT, line_length=20
        )
        assert test_output == expected_output


def test_import_by_paren_issue_375() -> None:
    """Test to ensure isort can correctly handle sorting imports where the
    paren is directly by the import body
    """
    test_input = "from .models import(\n   Foo,\n   Bar,\n)\n"
    assert isort.code(test_input) == "from .models import Bar, Foo\n"


def test_import_by_paren_issue_460() -> None:
    """Test to ensure isort can doesnt move comments around """
    test_input = """
# First comment
# Second comment
# third comment
import io
import os
"""
    assert isort.code((test_input)) == test_input


def test_function_with_docstring() -> None:
    """Test to ensure isort can correctly sort imports when the first found content is a
    function with a docstring
    """
    add_imports = ["from __future__ import unicode_literals"]
    test_input = "def foo():\n" '    """ Single line triple quoted doctring """\n' "    pass\n"
    expected_output = (
        "from __future__ import unicode_literals\n"
        "\n"
        "\n"
        "def foo():\n"
        '    """ Single line triple quoted doctring """\n'
        "    pass\n"
    )
    assert isort.code(test_input, add_imports=add_imports) == expected_output


def test_plone_style() -> None:
    """Test to ensure isort correctly plone style imports"""
    test_input = (
        "from django.contrib.gis.geos import GEOSException\n"
        "from plone.app.testing import getRoles\n"
        "from plone.app.testing import ManageRoles\n"
        "from plone.app.testing import setRoles\n"
        "from Products.CMFPlone import utils\n"
        "\n"
        "import ABC\n"
        "import unittest\n"
        "import Zope\n"
    )
    options = {"force_single_line": True, "force_alphabetical_sort": True}  # type: Dict[str, Any]
    assert isort.code(test_input, **options) == test_input


def test_third_party_case_sensitive() -> None:
    """Modules which match builtins by name but not on case should not be picked up on Windows."""
    test_input = "import thirdparty\nimport os\nimport ABC\n"

    expected_output = "import os\n\nimport ABC\nimport thirdparty\n"
    assert isort.code(test_input) == expected_output


def test_exists_case_sensitive_file(tmpdir) -> None:
    """Test exists_case_sensitive function for a file."""
    tmpdir.join("module.py").ensure(file=1)
    assert exists_case_sensitive(str(tmpdir.join("module.py")))
    assert not exists_case_sensitive(str(tmpdir.join("MODULE.py")))


def test_exists_case_sensitive_directory(tmpdir) -> None:
    """Test exists_case_sensitive function for a directory."""
    tmpdir.join("pkg").ensure(dir=1)
    assert exists_case_sensitive(str(tmpdir.join("pkg")))
    assert not exists_case_sensitive(str(tmpdir.join("PKG")))


def test_sys_path_mutation(tmpdir) -> None:
    """Test to ensure sys.path is not modified"""
    tmpdir.mkdir("src").mkdir("a")
    test_input = "from myproject import test"
    options = {"virtual_env": str(tmpdir)}  # type: Dict[str, Any]
    expected_length = len(sys.path)
    isort.code(test_input, **options)
    assert len(sys.path) == expected_length
    isort.code(test_input, old_finders=True, **options)


def test_long_single_line() -> None:
    """Test to ensure long single lines get handled correctly"""
    output = isort.code(
        code="from ..views import ("
        " _a,"
        "_xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx as xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx)",
        line_length=79,
    )
    for line in output.split("\n"):
        assert len(line) <= 79

    output = isort.code(
        code="from ..views import ("
        " _a,"
        "_xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx as xxxxxx_xxxxxxx_xxxxxxxx_xxx_xxxxxxx)",
        line_length=79,
        combine_as_imports=True,
    )
    for line in output.split("\n"):
        assert len(line) <= 79


def test_import_inside_class_issue_432() -> None:
    """Test to ensure issue 432 is resolved and isort
    doesn't insert imports in the middle of classes
    """
    test_input = "# coding=utf-8\nclass Foo:\n    def bar(self):\n        pass\n"
    expected_output = (
        "# coding=utf-8\n"
        "import baz\n"
        "\n"
        "\n"
        "class Foo:\n"
        "    def bar(self):\n"
        "        pass\n"
    )
    assert isort.code(test_input, add_imports=["import baz"]) == expected_output


def test_wildcard_import_without_space_issue_496() -> None:
    """Test to ensure issue #496: wildcard without space, is resolved"""
    test_input = "from findorserver.coupon.models import*"
    expected_output = "from findorserver.coupon.models import *\n"
    assert isort.code(test_input) == expected_output


def test_import_line_mangles_issues_491() -> None:
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = "import os  # ([\n\n" 'print("hi")\n'
    assert isort.code(test_input) == test_input


def test_import_line_mangles_issues_505() -> None:
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = "from sys import *  # (\n\n\ndef test():\n" '    print("Test print")\n'
    assert isort.code(test_input) == test_input


def test_import_line_mangles_issues_439() -> None:
    """Test to ensure comment on import with parens doesn't cause issues"""
    test_input = "import a  # () import\nfrom b import b\n"
    assert isort.code(test_input) == test_input


def test_alias_using_paren_issue_466() -> None:
    """Test to ensure issue #466: Alias causes slash incorrectly is resolved"""
    test_input = (
        "from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper\n"
    )
    expected_output = (
        "from django.db.backends.mysql.base import (\n"
        "    DatabaseWrapper as MySQLDatabaseWrapper)\n"
    )
    assert isort.code(test_input, line_length=50, use_parentheses=True) == expected_output

    test_input = (
        "from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper\n"
    )
    expected_output = (
        "from django.db.backends.mysql.base import (\n"
        "    DatabaseWrapper as MySQLDatabaseWrapper\n"
        ")\n"
    )
    assert (
        isort.code(
            code=test_input,
            line_length=50,
            multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
            use_parentheses=True,
        )
        == expected_output
    )


def test_long_alias_using_paren_issue_957() -> None:
    test_input = (
        "from package import module as very_very_very_very_very_very_very"
        "_very_very_very_long_alias\n"
    )
    expected_output = (
        "from package import (\n"
        "    module as very_very_very_very_very_very_very_very_very_very_long_alias\n"
        ")\n"
    )
    out = isort.code(
        code=test_input,
        line_length=50,
        use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
    )
    assert out == expected_output

    test_input = (
        "from deep.deep.deep.deep.deep.deep.deep.deep.deep.package import module as "
        "very_very_very_very_very_very_very_very_very_very_long_alias\n"
    )
    expected_output = (
        "from deep.deep.deep.deep.deep.deep.deep.deep.deep.package import (\n"
        "    module as very_very_very_very_very_very_very_very_very_very_long_alias\n"
        ")\n"
    )
    out = isort.code(
        code=test_input,
        line_length=50,
        use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
    )
    assert out == expected_output

    test_input = (
        "from deep.deep.deep.deep.deep.deep.deep.deep.deep.package "
        "import very_very_very_very_very_very_very_very_very_very_long_module as very_very_very_"
        "very_very_very_very_very_very_very_long_alias\n"
    )
    expected_output = (
        "from deep.deep.deep.deep.deep.deep.deep.deep.deep.package import (\n"
        "    very_very_very_very_very_very_very_very_very_very_long_module as very_very_very_very"
        "_very_very_very_very_very_very_long_alias\n"
        ")\n"
    )
    out = isort.code(
        code=test_input,
        line_length=50,
        use_parentheses=True,
        multi_line_output=WrapModes.VERTICAL_GRID_GROUPED,
    )
    assert out == expected_output


def test_strict_whitespace_by_default(capsys) -> None:
    test_input = "import os\nfrom django.conf import settings\n"
    assert not api.check_code_string(test_input)
    _, err = capsys.readouterr()
    assert "ERROR" in err
    assert err.endswith("Imports are incorrectly sorted and/or formatted.\n")


def test_strict_whitespace_no_closing_newline_issue_676(capsys) -> None:
    test_input = "import os\n\nfrom django.conf import settings\n\nprint(1)"
    assert api.check_code_string(test_input)
    out, _ = capsys.readouterr()
    assert out == ""


def test_ignore_whitespace(capsys) -> None:
    test_input = "import os\nfrom django.conf import settings\n"
    assert api.check_code_string(test_input, ignore_whitespace=True)
    out, _ = capsys.readouterr()
    assert out == ""


def test_import_wraps_with_comment_issue_471() -> None:
    """Test to ensure issue #471 is resolved"""
    test_input = (
        "from very_long_module_name import SuperLongClassName  #@UnusedImport"
        " -- long string of comments which wrap over"
    )
    expected_output = (
        "from very_long_module_name import (\n"
        "    SuperLongClassName)  # @UnusedImport -- long string of comments which wrap over\n"
    )
    assert (
        isort.code(code=test_input, line_length=50, multi_line_output=1, use_parentheses=True)
        == expected_output
    )


def test_import_case_produces_inconsistent_results_issue_472() -> None:
    """Test to ensure sorting imports with same name but different case produces
    the same result across platforms
    """
    test_input = (
        "from sqlalchemy.dialects.postgresql import ARRAY\n"
        "from sqlalchemy.dialects.postgresql import array\n"
    )
    assert isort.code(test_input, force_single_line=True) == test_input

    test_input = (
        "from scrapy.core.downloader.handlers.http import "
        "HttpDownloadHandler, HTTPDownloadHandler\n"
    )
    assert isort.code(test_input, line_length=100) == test_input


def test_inconsistent_behavior_in_python_2_and_3_issue_479() -> None:
    """Test to ensure Python 2 and 3 have the same behavior"""
    test_input = (
        "from workalendar.europe import UnitedKingdom\n"
        "\n"
        "from future.standard_library import hooks\n"
    )
    assert isort.code(test_input, known_first_party=["future"]) == test_input


def test_sort_within_section_comments_issue_436() -> None:
    """Test to ensure sort within sections leaves comments untouched"""
    test_input = (
        "import os.path\n"
        "import re\n"
        "\n"
        "# report.py exists in ... comment line 1\n"
        "# this file needs to ...  comment line 2\n"
        "# it must not be ...      comment line 3\n"
        "import report\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input


def test_sort_within_sections_with_force_to_top_issue_473() -> None:
    """Test to ensure it's possible to sort within sections with items forced to top"""
    test_input = "import z\nimport foo\nfrom foo import bar\n"
    assert (
        isort.code(code=test_input, force_sort_within_sections=True, force_to_top=["z"])
        == test_input
    )


def test_correct_number_of_new_lines_with_comment_issue_435() -> None:
    """Test to ensure that injecting a comment in-between imports
    doesn't mess up the new line spacing
    """
    test_input = "import foo\n\n# comment\n\n\ndef baz():\n    pass\n"
    assert isort.code(test_input) == test_input


def test_future_below_encoding_issue_545() -> None:
    """Test to ensure future is always below comment"""
    test_input = (
        "#!/usr/bin/env python\n"
        "from __future__ import print_function\n"
        "import logging\n"
        "\n"
        'print("hello")\n'
    )
    expected_output = (
        "#!/usr/bin/env python\n"
        "from __future__ import print_function\n"
        "\n"
        "import logging\n"
        "\n"
        'print("hello")\n'
    )
    assert isort.code(test_input) == expected_output


def test_no_extra_lines_issue_557() -> None:
    """Test to ensure no extra lines are prepended"""
    test_input = (
        "import os\n"
        "\n"
        "from scrapy.core.downloader.handlers.http import "
        "HttpDownloadHandler, HTTPDownloadHandler\n"
    )
    expected_output = (
        "import os\n"
        "from scrapy.core.downloader.handlers.http import HttpDownloadHandler, "
        "HTTPDownloadHandler\n"
    )
    assert (
        isort.code(
            code=test_input,
            force_alphabetical_sort=True,
            force_sort_within_sections=True,
            line_length=100,
        )
        == expected_output
    )


def test_long_import_wrap_support_with_mode_2() -> None:
    """Test to ensure mode 2 still allows wrapped imports with slash"""
    test_input = (
        "from foobar.foobar.foobar.foobar import \\\n"
        "    an_even_longer_function_name_over_80_characters\n"
    )
    assert (
        isort.code(code=test_input, multi_line_output=WrapModes.HANGING_INDENT, line_length=80)
        == test_input
    )


def test_pylint_comments_incorrectly_wrapped_issue_571() -> None:
    """Test to ensure pylint comments don't get wrapped"""
    test_input = (
        "from PyQt5.QtCore import QRegExp  # @UnresolvedImport pylint: disable=import-error,"
        "useless-suppression\n"
    )
    expected_output = (
        "from PyQt5.QtCore import \\\n"
        "    QRegExp  # @UnresolvedImport pylint: disable=import-error,useless-suppression\n"
    )
    assert isort.code(test_input, line_length=60) == expected_output


def test_ensure_async_methods_work_issue_537() -> None:
    """Test to ensure async methods are correctly identified"""
    test_input = (
        "from myapp import myfunction\n"
        "\n"
        "\n"
        "async def test_myfunction(test_client, app):\n"
        "    a = await myfunction(test_client, app)\n"
    )
    assert isort.code(test_input) == test_input


def test_ensure_as_imports_sort_correctly_within_from_imports_issue_590() -> None:
    """Test to ensure combination from and as import statements are sorted correct"""
    test_input = "from os import defpath\nfrom os import pathsep as separator\n"
    assert isort.code(test_input, force_sort_within_sections=True) == test_input

    test_input = "from os import defpath\nfrom os import pathsep as separator\n"
    assert isort.code(test_input) == test_input

    test_input = "from os import defpath\nfrom os import pathsep as separator\n"
    assert isort.code(test_input, force_single_line=True) == test_input


def test_ensure_line_endings_are_preserved_issue_493() -> None:
    """Test to ensure line endings are not converted"""
    test_input = "from os import defpath\r\nfrom os import pathsep as separator\r\n"
    assert isort.code(test_input) == test_input
    test_input = "from os import defpath\rfrom os import pathsep as separator\r"
    assert isort.code(test_input) == test_input
    test_input = "from os import defpath\nfrom os import pathsep as separator\n"
    assert isort.code(test_input) == test_input


def test_not_splitted_sections() -> None:
    whiteline = "\n"
    stdlib_section = "import unittest\n"
    firstparty_section = "from app.pkg1 import mdl1\n"
    local_section = "from .pkg2 import mdl2\n"
    statement = "foo = bar\n"
    test_input = (
        stdlib_section
        + whiteline
        + firstparty_section
        + whiteline
        + local_section
        + whiteline
        + statement
    )

    assert isort.code(test_input, known_first_party=["app"]) == test_input
    assert isort.code(test_input, no_lines_before=["LOCALFOLDER"], known_first_party=["app"]) == (
        stdlib_section + whiteline + firstparty_section + local_section + whiteline + statement
    )
    # by default STDLIB and FIRSTPARTY sections are split by THIRDPARTY section,
    # so don't merge them if THIRDPARTY imports aren't exist
    assert (
        isort.code(test_input, no_lines_before=["FIRSTPARTY"], known_first_party=["app"])
        == test_input
    )
    # in case when THIRDPARTY section is excluded from sections list,
    # it's ok to merge STDLIB and FIRSTPARTY
    assert (
        isort.code(
            code=test_input,
            sections=["STDLIB", "FIRSTPARTY", "LOCALFOLDER"],
            no_lines_before=["FIRSTPARTY"],
            known_first_party=["app"],
        )
        == (stdlib_section + firstparty_section + whiteline + local_section + whiteline + statement)
    )
    # it doesn't change output, because stdlib packages don't have any whitelines before them
    assert (
        isort.code(test_input, no_lines_before=["STDLIB"], known_first_party=["app"]) == test_input
    )


def test_no_lines_before_empty_section() -> None:
    test_input = "import first\nimport custom\n"
    assert (
        isort.code(
            code=test_input,
            known_third_party=["first"],
            known_custom=["custom"],
            sections=["THIRDPARTY", "LOCALFOLDER", "CUSTOM"],
            no_lines_before=["THIRDPARTY", "LOCALFOLDER", "CUSTOM"],
        )
        == test_input
    )


def test_no_inline_sort() -> None:
    """Test to ensure multiple `from` imports in one line are not sorted if `--no-inline-sort` flag
    is enabled.
    If `--force-single-line-imports` flag is enabled, then `--no-inline-sort` is ignored.
    """
    test_input = "from foo import a, c, b\n"
    assert isort.code(test_input, no_inline_sort=True, force_single_line=False) == test_input
    assert (
        isort.code(test_input, no_inline_sort=False, force_single_line=False)
        == "from foo import a, b, c\n"
    )
    expected = "from foo import a\nfrom foo import b\nfrom foo import c\n"
    assert isort.code(test_input, no_inline_sort=False, force_single_line=True) == expected
    assert isort.code(test_input, no_inline_sort=True, force_single_line=True) == expected


def test_relative_import_of_a_module() -> None:
    """Imports can be dynamically created (PEP302) and is used by modules such as six.
    This test ensures that these types of imports are still sorted to the correct type
    instead of being categorized as local.
    """
    test_input = (
        "from __future__ import absolute_import\n"
        "\n"
        "import itertools\n"
        "\n"
        "from six import add_metaclass\n"
        "\n"
        "from six.moves import asd\n"
    )

    expected_results = (
        "from __future__ import absolute_import\n"
        "\n"
        "import itertools\n"
        "\n"
        "from six import add_metaclass\n"
        "from six.moves import asd\n"
    )

    sorted_result = isort.code(test_input, force_single_line=True)
    assert sorted_result == expected_results


def test_escaped_parens_sort() -> None:
    test_input = "from foo import \\ \n(a,\nb,\nc)\n"
    expected = "from foo import a, b, c\n"
    assert isort.code(test_input) == expected


def test_escaped_parens_sort_with_comment() -> None:
    test_input = "from foo import \\ \n(a,\nb,# comment\nc)\n"
    expected = "from foo import b  # comment\nfrom foo import a, c\n"
    assert isort.code(test_input) == expected


def test_escaped_parens_sort_with_first_comment() -> None:
    test_input = "from foo import \\ \n(a,# comment\nb,\nc)\n"
    expected = "from foo import a  # comment\nfrom foo import b, c\n"
    assert isort.code(test_input) == expected


def test_escaped_no_parens_sort_with_first_comment() -> None:
    test_input = "from foo import a, \\\nb, \\\nc # comment\n"
    expected = "from foo import c  # comment\nfrom foo import a, b\n"
    assert isort.code(test_input) == expected


@pytest.mark.skip(reason="TODO: Duplicates currently not handled.")
def test_to_ensure_imports_are_brought_to_top_issue_651() -> None:
    test_input = (
        "from __future__ import absolute_import, unicode_literals\n"
        "\n"
        'VAR = """\n'
        "multiline text\n"
        '"""\n'
        "\n"
        "from __future__ import unicode_literals\n"
        "from __future__ import absolute_import\n"
    )
    expected_output = (
        "from __future__ import absolute_import, unicode_literals\n"
        "\n"
        'VAR = """\n'
        "multiline text\n"
        '"""\n'
    )
    assert isort.code(test_input) == expected_output


def test_to_ensure_importing_from_imports_module_works_issue_662() -> None:
    test_input = (
        "@wraps(fun)\n"
        "def __inner(*args, **kwargs):\n"
        "    from .imports import qualname\n"
        "\n"
        "    warn(description=description or qualname(fun), deprecation=deprecation, "
        "removal=removal)\n"
    )
    assert isort.code(test_input) == test_input


def test_to_ensure_no_unexpected_changes_issue_666() -> None:
    test_input = (
        "from django.conf import settings\n"
        "from django.core.management import call_command\n"
        "from django.core.management.base import BaseCommand\n"
        "from django.utils.translation import ugettext_lazy as _\n"
        "\n"
        'TEMPLATE = """\n'
        "# This file is generated automatically with the management command\n"
        "#\n"
        "#    manage.py bis_compile_i18n\n"
        "#\n"
        "# please dont change it manually.\n"
        "from django.utils.translation import ugettext_lazy as _\n"
        '"""\n'
    )
    assert isort.code(test_input) == test_input


def test_to_ensure_tabs_dont_become_space_issue_665() -> None:
    test_input = "import os\n\n\ndef my_method():\n\tpass\n"
    assert isort.code(test_input) == test_input


def test_new_lines_are_preserved() -> None:
    with NamedTemporaryFile("w", suffix="py", delete=False) as rn_newline:
        pass

    try:
        with open(rn_newline.name, mode="w", newline="") as rn_newline_input:
            rn_newline_input.write("import sys\r\nimport os\r\n")

        api.sort_file(rn_newline.name, settings_path=os.getcwd())
        with open(rn_newline.name) as new_line_file:
            print(new_line_file.read())
        with open(rn_newline.name, newline="") as rn_newline_file:
            rn_newline_contents = rn_newline_file.read()
        assert rn_newline_contents == "import os\r\nimport sys\r\n"
    finally:
        os.remove(rn_newline.name)

    with NamedTemporaryFile("w", suffix="py", delete=False) as r_newline:
        pass

    try:
        with open(r_newline.name, mode="w", newline="") as r_newline_input:
            r_newline_input.write("import sys\rimport os\r")

        api.sort_file(r_newline.name, settings_path=os.getcwd())
        with open(r_newline.name, newline="") as r_newline_file:
            r_newline_contents = r_newline_file.read()
        assert r_newline_contents == "import os\rimport sys\r"
    finally:
        os.remove(r_newline.name)

    with NamedTemporaryFile("w", suffix="py", delete=False) as n_newline:
        pass

    try:
        with open(n_newline.name, mode="w", newline="") as n_newline_input:
            n_newline_input.write("import sys\nimport os\n")

        api.sort_file(n_newline.name, settings_path=os.getcwd())
        with open(n_newline.name, newline="") as n_newline_file:
            n_newline_contents = n_newline_file.read()
        assert n_newline_contents == "import os\nimport sys\n"
    finally:
        os.remove(n_newline.name)


def test_forced_separate_is_deterministic_issue_774(tmpdir) -> None:

    config_file = tmpdir.join("setup.cfg")
    config_file.write(
        "[isort]\n"
        "forced_separate:\n"
        "   separate1\n"
        "   separate2\n"
        "   separate3\n"
        "   separate4\n"
    )

    test_input = (
        "import time\n"
        "\n"
        "from separate1 import foo\n"
        "\n"
        "from separate2 import bar\n"
        "\n"
        "from separate3 import baz\n"
        "\n"
        "from separate4 import quux\n"
    )

    assert isort.code(test_input, settings_file=config_file.strpath) == test_input


def test_monkey_patched_urllib() -> None:
    with pytest.raises(ImportError):
        # Previous versions of isort monkey patched urllib which caused unusual
        # importing for other projects.
        from urllib import quote  # type: ignore  # noqa: F401


def test_argument_parsing() -> None:
    from isort.main import parse_args

    args = parse_args(["--dt", "-t", "foo", "--skip=bar", "baz.py", "--os"])
    assert args["order_by_type"] is False
    assert args["force_to_top"] == ["foo"]
    assert args["skip"] == ["bar"]
    assert args["files"] == ["baz.py"]
    assert args["only_sections"] is True


@pytest.mark.parametrize("multiprocess", (False, True))
def test_command_line(tmpdir, capfd, multiprocess: bool) -> None:
    from isort.main import main

    tmpdir.join("file1.py").write("import re\nimport os\n\nimport contextlib\n\n\nimport isort")
    tmpdir.join("file2.py").write(
        ("import collections\nimport time\n\nimport abc" "\n\n\nimport isort")
    )
    arguments = [str(tmpdir), "--settings-path", os.getcwd()]
    if multiprocess:
        arguments.extend(["--jobs", "2"])
    main(arguments)
    assert (
        tmpdir.join("file1.py").read()
        == "import contextlib\nimport os\nimport re\n\nimport isort\n"
    )
    assert (
        tmpdir.join("file2.py").read()
        == "import abc\nimport collections\nimport time\n\nimport isort\n"
    )
    if not (sys.platform.startswith("win") or sys.platform.startswith("darwin")):
        out, err = capfd.readouterr()
        assert not [error for error in err.split("\n") if error and "warning:" not in error]
        # it informs us about fixing the files:
        assert str(tmpdir.join("file1.py")) in out
        assert str(tmpdir.join("file2.py")) in out


@pytest.mark.parametrize("quiet", (False, True))
def test_quiet(tmpdir, capfd, quiet: bool) -> None:
    if sys.platform.startswith("win"):
        return
    from isort.main import main

    tmpdir.join("file1.py").write("import re\nimport os")
    tmpdir.join("file2.py").write("")
    arguments = [str(tmpdir)]
    if quiet:
        arguments.append("-q")
    main(arguments)
    out, err = capfd.readouterr()
    assert not err
    assert bool(out) != quiet


@pytest.mark.parametrize("enabled", (False, True))
def test_safety_skips(tmpdir, enabled: bool) -> None:
    tmpdir.join("victim.py").write("# ...")
    toxdir = tmpdir.mkdir(".tox")
    toxdir.join("verysafe.py").write("# ...")
    tmpdir.mkdir("_build").mkdir("python3.7").join("importantsystemlibrary.py").write("# ...")
    tmpdir.mkdir(".pants.d").join("pants.py").write("import os")
    if enabled:
        config = Config(directory=str(tmpdir))
    else:
        config = Config(skip=[], directory=str(tmpdir))
    skipped: List[str] = []
    broken: List[str] = []
    codes = [str(tmpdir)]
    main.iter_source_code(codes, config, skipped, broken)

    # if enabled files within nested unsafe directories should be skipped
    file_names = {
        os.path.relpath(f, str(tmpdir))
        for f in main.iter_source_code([str(tmpdir)], config, skipped, broken)
    }
    if enabled:
        assert file_names == {"victim.py"}
        assert len(skipped) == 3
    else:
        assert file_names == {
            os.sep.join((".tox", "verysafe.py")),
            os.sep.join(("_build", "python3.7", "importantsystemlibrary.py")),
            os.sep.join((".pants.d", "pants.py")),
            "victim.py",
        }
        assert not skipped

    # directly pointing to files within unsafe directories shouldn't skip them either way
    file_names = {
        os.path.relpath(f, str(toxdir))
        for f in main.iter_source_code(
            [str(toxdir)], Config(directory=str(toxdir)), skipped, broken
        )
    }
    assert file_names == {"verysafe.py"}


@pytest.mark.parametrize(
    "skip_glob_assert",
    (
        ([], 0, {os.sep.join(("code", "file.py"))}),
        (["**/*.py"], 1, set()),
        (["*/code/*.py"], 1, set()),
    ),
)
def test_skip_glob(tmpdir, skip_glob_assert: Tuple[List[str], int, Set[str]]) -> None:
    skip_glob, skipped_count, file_names_expected = skip_glob_assert
    base_dir = tmpdir.mkdir("build")
    code_dir = base_dir.mkdir("code")
    code_dir.join("file.py").write("import os")

    config = Config(skip_glob=skip_glob, directory=str(base_dir))
    skipped: List[str] = []
    broken: List[str] = []
    file_names = {
        os.path.relpath(f, str(base_dir))
        for f in main.iter_source_code([str(base_dir)], config, skipped, broken)
    }
    assert len(skipped) == skipped_count
    assert file_names == file_names_expected


def test_broken(tmpdir) -> None:
    base_dir = tmpdir.mkdir("broken")

    config = Config(directory=str(base_dir))
    skipped: List[str] = []
    broken: List[str] = []
    file_names = {
        os.path.relpath(f, str(base_dir))
        for f in main.iter_source_code(["not-exist"], config, skipped, broken)
    }
    assert len(broken) == 1
    assert file_names == set()


def test_comments_not_removed_issue_576() -> None:
    test_input = (
        "import distutils\n"
        "# this comment is important and should not be removed\n"
        "from sys import api_version as api_version\n"
    )
    assert isort.code(test_input) == test_input


def test_reverse_relative_imports_issue_417() -> None:
    test_input = (
        "from . import ipsum\n"
        "from . import lorem\n"
        "from .dolor import consecteur\n"
        "from .sit import apidiscing\n"
        "from .. import donec\n"
        "from .. import euismod\n"
        "from ..mi import iaculis\n"
        "from ..nec import tempor\n"
        "from ... import diam\n"
        "from ... import dui\n"
        "from ...eu import dignissim\n"
        "from ...ex import metus\n"
    )
    assert isort.code(test_input, force_single_line=True, reverse_relative=True) == test_input


def test_inconsistent_relative_imports_issue_577() -> None:
    test_input = (
        "from ... import diam\n"
        "from ... import dui\n"
        "from ...eu import dignissim\n"
        "from ...ex import metus\n"
        "from .. import donec\n"
        "from .. import euismod\n"
        "from ..mi import iaculis\n"
        "from ..nec import tempor\n"
        "from . import ipsum\n"
        "from . import lorem\n"
        "from .dolor import consecteur\n"
        "from .sit import apidiscing\n"
    )
    assert isort.code(test_input, force_single_line=True) == test_input


def test_unwrap_issue_762() -> None:
    test_input = "from os.path \\\nimport (join, split)\n"
    assert isort.code(test_input) == "from os.path import join, split\n"

    test_input = "from os.\\\n    path import (join, split)"
    assert isort.code(test_input) == "from os.path import join, split\n"


def test_multiple_as_imports() -> None:
    test_input = "from a import b as b\nfrom a import b as bb\nfrom a import b as bb_\n"
    test_output = isort.code(test_input)
    assert test_output == test_input
    test_output = isort.code(test_input, combine_as_imports=True)
    assert test_output == "from a import b as b, b as bb, b as bb_\n"
    test_output = isort.code(test_input)
    assert test_output == test_input
    test_output = isort.code(code=test_input, combine_as_imports=True)
    assert test_output == "from a import b as b, b as bb, b as bb_\n"

    test_input = (
        "from a import b\n"
        "from a import b as b\n"
        "from a import b as bb\n"
        "from a import b as bb_\n"
    )
    test_output = isort.code(test_input)
    assert test_output == test_input
    test_output = isort.code(code=test_input, combine_as_imports=True)
    assert test_output == "from a import b, b as b, b as bb, b as bb_\n"

    test_input = (
        "from a import b as e\n"
        "from a import b as c\n"
        "from a import b\n"
        "from a import b as f\n"
    )
    test_output = isort.code(test_input)
    assert (
        test_output
        == "from a import b\nfrom a import b as c\nfrom a import b as e\nfrom a import b as f\n"
    )
    test_output = isort.code(code=test_input, no_inline_sort=True)
    assert (
        test_output
        == "from a import b\nfrom a import b as c\nfrom a import b as e\nfrom a import b as f\n"
    )
    test_output = isort.code(code=test_input, combine_as_imports=True)
    assert test_output == "from a import b, b as c, b as e, b as f\n"
    test_output = isort.code(code=test_input, combine_as_imports=True, no_inline_sort=True)
    assert test_output == "from a import b, b as e, b as c, b as f\n"

    test_input = "import a as a\nimport a as aa\nimport a as aa_\n"
    test_output = isort.code(code=test_input, combine_as_imports=True)
    assert test_output == test_input

    assert test_output == "import a as a\nimport a as aa\nimport a as aa_\n"
    test_output = isort.code(code=test_input, combine_as_imports=True)
    assert test_output == test_input


def test_all_imports_from_single_module() -> None:
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import b as d\n"
        "from a import z, x, y\n"
        "from a import b\n"
        "from a import w, i as j\n"
        "from a import b as c, g as h\n"
        "from a import e as f\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=False,
        force_single_line=False,
        no_inline_sort=False,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as c\n"
        "from a import b as d\n"
        "from a import e as f\n"
        "from a import g as h\n"
        "from a import i as j\n"
        "from a import w, x, y, z\n"
    )
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import z, x, y\n"
        "from a import b\n"
        "from a import w\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=True,
        combine_as_imports=False,
        force_single_line=False,
        no_inline_sort=False,
    )
    assert test_output == "import a\nfrom a import *\n"
    test_input += """
from a import b as c
from a import b as d
from a import e as f
from a import g as h
from a import i as j
"""
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=True,
        force_single_line=False,
        no_inline_sort=False,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b, b as c, b as d, e as f, g as h, i as j, w, x, y, z\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=False,
        force_single_line=True,
        no_inline_sort=False,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as c\n"
        "from a import b as d\n"
        "from a import e as f\n"
        "from a import g as h\n"
        "from a import i as j\n"
        "from a import w\n"
        "from a import x\n"
        "from a import y\n"
        "from a import z\n"
    )
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as d\n"
        "from a import b as c\n"
        "from a import z, x, y, w\n"
        "from a import i as j\n"
        "from a import g as h\n"
        "from a import e as f\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=False,
        force_single_line=False,
        no_inline_sort=True,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as c\n"
        "from a import b as d\n"
        "from a import z, x, y, w\n"
        "from a import i as j\n"
        "from a import g as h\n"
        "from a import e as f\n"
    )
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import z, x, y\n"
        "from a import b\n"
        "from a import w\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=True,
        combine_as_imports=True,
        force_single_line=False,
        no_inline_sort=False,
    )
    assert test_output == "import a\nfrom a import *\n"
    test_output = isort.code(
        code=test_input,
        combine_star=True,
        combine_as_imports=False,
        force_single_line=True,
        no_inline_sort=False,
    )
    assert test_output == "import a\nfrom a import *\n"
    test_output = isort.code(
        code=test_input,
        combine_star=True,
        combine_as_imports=False,
        force_single_line=False,
        no_inline_sort=True,
    )
    assert test_output == "import a\nfrom a import *\n"
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=True,
        force_single_line=True,
        no_inline_sort=False,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import w\n"
        "from a import x\n"
        "from a import y\n"
        "from a import z\n"
    )
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as d\n"
        "from a import b as c\n"
        "from a import z, x, y, w\n"
        "from a import i as j\n"
        "from a import g as h\n"
        "from a import e as f\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=True,
        force_single_line=False,
        no_inline_sort=True,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b, b as d, b as c, z, x, y, w, i as j, g as h, e as f\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=False,
        combine_as_imports=False,
        force_single_line=True,
        no_inline_sort=True,
    )
    assert test_output == (
        "import a\n"
        "from a import *\n"
        "from a import b\n"
        "from a import b as c\n"
        "from a import b as d\n"
        "from a import e as f\n"
        "from a import g as h\n"
        "from a import i as j\n"
        "from a import w\n"
        "from a import x\n"
        "from a import y\n"
        "from a import z\n"
    )
    test_input = (
        "import a\n"
        "from a import *\n"
        "from a import z, x, y\n"
        "from a import b\n"
        "from a import w\n"
    )
    test_output = isort.code(
        code=test_input,
        combine_star=True,
        combine_as_imports=True,
        force_single_line=True,
        no_inline_sort=False,
    )
    assert test_output == "import a\nfrom a import *\n"


def test_noqa_issue_679() -> None:
    """Test to ensure that NOQA notation is being observed as expected
    if honor_noqa is set to `True`
    """
    test_input = """
import os

import requestsss
import zed # NOQA
import ujson # NOQA

import foo"""
    test_output = """
import os

import foo
import requestsss
import ujson  # NOQA
import zed  # NOQA
"""
    test_output_honor_noqa = """
import os

import foo
import requestsss

import zed # NOQA
import ujson # NOQA
"""
    assert isort.code(test_input) == test_output
    assert isort.code(test_input.lower()) == test_output.lower()
    assert isort.code(test_input, honor_noqa=True) == test_output_honor_noqa
    assert isort.code(test_input.lower(), honor_noqa=True) == test_output_honor_noqa.lower()


def test_extract_multiline_output_wrap_setting_from_a_config_file(tmpdir: py.path.local) -> None:
    editorconfig_contents = ["root = true", " [*.py]", "multi_line_output = 5"]
    config_file = tmpdir.join(".editorconfig")
    config_file.write("\n".join(editorconfig_contents))

    config = Config(settings_path=str(tmpdir))
    assert config.multi_line_output == WrapModes.VERTICAL_GRID_GROUPED


def test_ensure_support_for_non_typed_but_cased_alphabetic_sort_issue_890() -> None:
    test_input = (
        "from pkg import BALL\n"
        "from pkg import RC\n"
        "from pkg import Action\n"
        "from pkg import Bacoo\n"
        "from pkg import RCNewCode\n"
        "from pkg import actual\n"
        "from pkg import rc\n"
        "from pkg import recorder\n"
    )
    expected_output = (
        "from pkg import Action\n"
        "from pkg import BALL\n"
        "from pkg import Bacoo\n"
        "from pkg import RC\n"
        "from pkg import RCNewCode\n"
        "from pkg import actual\n"
        "from pkg import rc\n"
        "from pkg import recorder\n"
    )
    assert (
        isort.code(
            code=test_input, case_sensitive=True, order_by_type=False, force_single_line=True
        )
        == expected_output
    )


def test_to_ensure_empty_line_not_added_to_file_start_issue_889() -> None:
    test_input = "# comment\nimport os\n# comment2\nimport sys\n"
    assert isort.code(test_input) == test_input


def test_to_ensure_correctly_handling_of_whitespace_only_issue_811(capsys) -> None:
    test_input = (
        "import os\n" "import sys\n" "\n" "\x0c\n" "def my_function():\n" '    print("hi")\n'
    )
    isort.code(test_input, ignore_whitespace=True)
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_standard_library_deprecates_user_issue_778() -> None:
    test_input = "import os\n\nimport user\n"
    assert isort.code(test_input) == test_input


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_settings_path_skip_issue_909(tmpdir) -> None:
    base_dir = tmpdir.mkdir("project")
    config_dir = base_dir.mkdir("conf")
    config_dir.join(".isort.cfg").write(
        "[isort]\n" "skip =\n" "    file_to_be_skipped.py\n" "skip_glob =\n" "    *glob_skip*\n"
    )

    base_dir.join("file_glob_skip.py").write(
        "import os\n\n" 'print("Hello World")\n' "\nimport sys\nimport os\n"
    )
    base_dir.join("file_to_be_skipped.py").write(
        "import os\n\n" 'print("Hello World")' "\nimport sys\nimport os\n"
    )

    test_run_directory = os.getcwd()
    os.chdir(str(base_dir))
    with pytest.raises(
        Exception
    ):  # without the settings path provided: the command should not skip & identify errors
        subprocess.run(["isort", ".", "--check-only"], check=True)
    result = subprocess.run(
        ["isort", ".", "--check-only", "--settings-path=conf/.isort.cfg"],
        stdout=subprocess.PIPE,
        check=True,
    )
    os.chdir(str(test_run_directory))

    assert b"skipped 2" in result.stdout.lower()


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_skip_paths_issue_938(tmpdir) -> None:
    base_dir = tmpdir.mkdir("project")
    config_dir = base_dir.mkdir("conf")
    config_dir.join(".isort.cfg").write(
        "[isort]\n"
        "line_length = 88\n"
        "multi_line_output = 4\n"
        "lines_after_imports = 2\n"
        "skip_glob =\n"
        "    migrations/**.py\n"
    )
    base_dir.join("dont_skip.py").write("import os\n\n" 'print("Hello World")' "\nimport sys\n")

    migrations_dir = base_dir.mkdir("migrations")
    migrations_dir.join("file_glob_skip.py").write(
        "import os\n\n" 'print("Hello World")\n' "\nimport sys\n"
    )

    test_run_directory = os.getcwd()
    os.chdir(str(base_dir))
    result = subprocess.run(
        ["isort", "dont_skip.py", "migrations/file_glob_skip.py"],
        stdout=subprocess.PIPE,
        check=True,
    )
    os.chdir(str(test_run_directory))

    assert b"skipped" not in result.stdout.lower()

    os.chdir(str(base_dir))
    result = subprocess.run(
        [
            "isort",
            "--filter-files",
            "--settings-path=conf/.isort.cfg",
            "dont_skip.py",
            "migrations/file_glob_skip.py",
        ],
        stdout=subprocess.PIPE,
        check=True,
    )
    os.chdir(str(test_run_directory))

    assert b"skipped 1" in result.stdout.lower()


def test_failing_file_check_916() -> None:
    test_input = (
        "#!/usr/bin/env python\n"
        "# -*- coding: utf-8 -*-\n"
        "from __future__ import unicode_literals\n"
    )
    expected_output = (
        "#!/usr/bin/env python\n"
        "# -*- coding: utf-8 -*-\n"
        "# FUTURE\n"
        "from __future__ import unicode_literals\n"
    )
    settings = {
        "import_heading_future": "FUTURE",
        "sections": ["FUTURE", "STDLIB", "NORDIGEN", "FIRSTPARTY", "THIRDPARTY", "LOCALFOLDER"],
        "indent": "    ",
        "multi_line_output": 3,
        "lines_after_imports": 2,
    }  # type: Dict[str, Any]
    assert isort.code(test_input, **settings) == expected_output
    assert isort.code(expected_output, **settings) == expected_output
    assert api.check_code_string(expected_output, **settings)


def test_import_heading_issue_905() -> None:
    config = {
        "import_heading_stdlib": "Standard library imports",
        "import_heading_thirdparty": "Third party imports",
        "import_heading_firstparty": "Local imports",
        "known_third_party": ["numpy"],
        "known_first_party": ["oklib"],
    }  # type: Dict[str, Any]
    test_input = (
        "# Standard library imports\n"
        "from os import path as osp\n"
        "\n"
        "# Third party imports\n"
        "import numpy as np\n"
        "\n"
        "# Local imports\n"
        "from oklib.plot_ok import imagesc\n"
    )
    assert isort.code(test_input, **config) == test_input


def test_isort_keeps_comments_issue_691() -> None:
    test_input = (
        "import os\n"
        "# This will make sure the app is always imported when\n"
        "# Django starts so that shared_task will use this app.\n"
        "from .celery import app as celery_app  # noqa\n"
        "\n"
        "PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))\n"
        "\n"
        "def path(*subdirectories):\n"
        "    return os.path.join(PROJECT_DIR, *subdirectories)\n"
    )
    expected_output = (
        "import os\n"
        "\n"
        "# This will make sure the app is always imported when\n"
        "# Django starts so that shared_task will use this app.\n"
        "from .celery import app as celery_app  # noqa\n"
        "\n"
        "PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))\n"
        "\n"
        "def path(*subdirectories):\n"
        "    return os.path.join(PROJECT_DIR, *subdirectories)\n"
    )
    assert isort.code(test_input) == expected_output


def test_isort_ensures_blank_line_between_import_and_comment() -> None:
    config = {
        "ensure_newline_before_comments": True,
        "lines_between_sections": 0,
        "known_one": ["one"],
        "known_two": ["two"],
        "known_three": ["three"],
        "known_four": ["four"],
        "sections": [
            "FUTURE",
            "STDLIB",
            "FIRSTPARTY",
            "THIRDPARTY",
            "LOCALFOLDER",
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
        ],
    }  # type: Dict[str, Any]
    test_input = (
        "import os\n"
        "# noinspection PyUnresolvedReferences\n"
        "import one.a\n"
        "# noinspection PyUnresolvedReferences\n"
        "import one.b\n"
        "# noinspection PyUnresolvedReferences\n"
        "import two.a as aa\n"
        "# noinspection PyUnresolvedReferences\n"
        "import two.b as bb\n"
        "# noinspection PyUnresolvedReferences\n"
        "from three.a import a\n"
        "# noinspection PyUnresolvedReferences\n"
        "from three.b import b\n"
        "# noinspection PyUnresolvedReferences\n"
        "from four.a import a as aa\n"
        "# noinspection PyUnresolvedReferences\n"
        "from four.b import b as bb\n"
    )
    expected_output = (
        "import os\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "import one.a\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "import one.b\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "import two.a as aa\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "import two.b as bb\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "from three.a import a\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "from three.b import b\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "from four.a import a as aa\n"
        "\n"
        "# noinspection PyUnresolvedReferences\n"
        "from four.b import b as bb\n"
    )
    assert isort.code(test_input, **config) == expected_output


def test_pyi_formatting_issue_942(tmpdir) -> None:
    test_input = "import os\n\n\ndef my_method():\n"
    expected_py_output = test_input.splitlines()
    expected_pyi_output = "import os\n\ndef my_method():\n".splitlines()
    assert isort.code(test_input).splitlines() == expected_py_output
    assert isort.code(test_input, extension="pyi").splitlines() == expected_pyi_output

    source_py = tmpdir.join("source.py")
    source_py.write(test_input)
    assert (
        isort.code(code=Path(source_py).read_text(), file_path=Path(source_py)).splitlines()
        == expected_py_output
    )

    source_pyi = tmpdir.join("source.pyi")
    source_pyi.write(test_input)
    assert (
        isort.code(
            code=Path(source_pyi).read_text(), extension="pyi", file_path=Path(source_pyi)
        ).splitlines()
        == expected_pyi_output
    )

    # Ensure it works for direct file API as well (see: issue #1284)
    source_pyi = tmpdir.join("source.pyi")
    source_pyi.write(test_input)
    api.sort_file(Path(source_pyi))

    assert source_pyi.read().splitlines() == expected_pyi_output


def test_move_class_issue_751() -> None:
    test_input = (
        "# -*- coding: utf-8 -*-"
        "\n"
        "# Define your item pipelines here"
        "#"
        "# Don't forget to add your pipeline to the ITEM_PIPELINES setting"
        "# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html"
        "from datetime import datetime"
        "from .items import WeiboMblogItem"
        "\n"
        "class WeiboMblogPipeline(object):"
        "    def process_item(self, item, spider):"
        "        if isinstance(item, WeiboMblogItem):"
        "            item = self._process_item(item, spider)"
        "        return item"
        "\n"
        "    def _process_item(self, item, spider):"
        "        item['inserted_at'] = datetime.now()"
        "        return item"
        "\n"
    )
    assert isort.code(test_input) == test_input


def test_python_version() -> None:
    from isort.main import parse_args

    # test that the py_version can be added as flag
    args = parse_args(["--py=27"])
    assert args["py_version"] == "27"

    args = parse_args(["--python-version=3"])
    assert args["py_version"] == "3"

    test_input = "import os\n\nimport user\n"
    assert isort.code(test_input, py_version="3") == test_input

    # user is part of the standard library in python 2
    output_python_2 = "import os\nimport user\n"
    assert isort.code(test_input, py_version="27") == output_python_2

    test_input = "import os\nimport xml"

    print(isort.code(test_input, py_version="all"))


def test_isort_with_single_character_import() -> None:
    """Tests to ensure isort handles single capatilized single character imports
    as class objects by default

    See Issue #376: https://github.com/pycqa/isort/issues/376
    """
    test_input = "from django.db.models import CASCADE, SET_NULL, Q\n"
    assert isort.code(test_input) == test_input


def test_isort_nested_imports() -> None:
    """Ensure imports in a nested block get sorted correctly"""
    test_input = """
    def import_test():
        import sys
        import os

        # my imports
        from . import def
        from . import abc

        return True
    """
    assert (
        isort.code(test_input)
        == """
    def import_test():
        import os
        import sys

        # my imports
        from . import abc, def

        return True
    """
    )


def test_isort_off() -> None:
    """Test that isort can be turned on and off at will using comments"""
    test_input = """import os

# isort: off
import sys
import os
# isort: on

from . import local
"""
    assert isort.code(test_input) == test_input


def test_isort_split() -> None:
    """Test the ability to split isort import sections"""
    test_input = """import os
import sys

# isort: split

import os
import sys
"""
    assert isort.code(test_input) == test_input

    test_input = """import c

import b  # isort: split

import a
import c
"""
    assert isort.code(test_input) == test_input


def test_comment_look_alike():
    """Test to ensure isort will handle what looks like a single line comment
    at the end of a multi-line comment.
    """
    test_input = '''
"""This is a multi-line comment

ending with what appears to be a single line comment
# Single Line Comment"""
import sys
import os
'''
    assert (
        isort.code(test_input)
        == '''
"""This is a multi-line comment

ending with what appears to be a single line comment
# Single Line Comment"""
import os
import sys
'''
    )


def test_cimport_support():
    """Test to ensure cimports (Cython style imports) work"""
    test_input = """
import os
import sys
import cython
import platform
import traceback
import time
import types
import re
import copy
import inspect # used by JavascriptBindings.__SetObjectMethods()
import urllib
import json
import datetime
import random

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

if sys.version_info.major == 2:
    from urllib import pathname2url as urllib_pathname2url
else:
    from urllib.request import pathname2url as urllib_pathname2url

from cpython.version cimport PY_MAJOR_VERSION
import weakref

# We should allow multiple string types: str, unicode, bytes.
# PyToCefString() can handle them all.
# Important:
#   If you set it to basestring, Cython will accept exactly(!)
#   str/unicode in Py2 and str in Py3. This won't work in Py3
#   as we might want to pass bytes as well. Also it will
#   reject string subtypes, so using it in publi API functions
#   would be a bad idea.
ctypedef object py_string

# You can't use "void" along with cpdef function returning None, it is planned to be
# added to Cython in the future, creating this virtual type temporarily. If you
# change it later to "void" then don't forget to add "except *".
ctypedef object py_void
ctypedef long WindowHandle

from cpython cimport PyLong_FromVoidPtr

from cpython cimport bool as py_bool
from libcpp cimport bool as cpp_bool

from libcpp.map cimport map as cpp_map
from multimap cimport multimap as cpp_multimap
from libcpp.pair cimport pair as cpp_pair
from libcpp.vector cimport vector as cpp_vector

from libcpp.string cimport string as cpp_string
from wstring cimport wstring as cpp_wstring

from libc.string cimport strlen
from libc.string cimport memcpy

# preincrement and dereference must be "as" otherwise not seen.
from cython.operator cimport preincrement as preinc, dereference as deref

# from cython.operator cimport address as addr # Address of an c++ object?

from libc.stdlib cimport calloc, malloc, free
from libc.stdlib cimport atoi

# When pyx file cimports * from a pxd file and that pxd cimports * from another pxd
# then these names will be visible in pyx file.

# Circular imports are allowed in form "cimport ...", but won't work if you do
# "from ... cimport *", this is important to know in pxd files.

from libc.stdint cimport uint64_t
from libc.stdint cimport uintptr_t

cimport ctime

IF UNAME_SYSNAME == "Windows":
    from windows cimport *
    from dpi_aware_win cimport *
ELIF UNAME_SYSNAME == "Linux":
    from linux cimport *
ELIF UNAME_SYSNAME == "Darwin":
    from mac cimport *

from cpp_utils cimport *
from task cimport *

from cef_string cimport *
cdef extern from *:
    ctypedef CefString ConstCefString "const CefString"

from cef_types_wrappers cimport *
from cef_task cimport *
from cef_runnable cimport *

from cef_platform cimport *

from cef_ptr cimport *
from cef_app cimport *
from cef_browser cimport *
cimport cef_browser_static
from cef_client cimport *
from client_handler cimport *
from cef_frame cimport *

# cannot cimport *, that would cause name conflicts with constants.
cimport cef_types
ctypedef cef_types.cef_paint_element_type_t PaintElementType
ctypedef cef_types.cef_jsdialog_type_t JSDialogType
from cef_types cimport CefKeyEvent
from cef_types cimport CefMouseEvent
from cef_types cimport CefScreenInfo

# cannot cimport *, name conflicts
IF UNAME_SYSNAME == "Windows":
    cimport cef_types_win
ELIF UNAME_SYSNAME == "Darwin":
    cimport cef_types_mac
ELIF UNAME_SYSNAME == "Linux":
    cimport cef_types_linux

from cef_time cimport *
from cef_drag cimport *

import os

IF CEF_VERSION == 1:
    from cef_v8 cimport *
    cimport cef_v8_static
    cimport cef_v8_stack_trace
    from v8function_handler cimport *
    from cef_request_cef1 cimport *
    from cef_web_urlrequest_cef1 cimport *
    cimport cef_web_urlrequest_static_cef1
    from web_request_client_cef1 cimport *
    from cef_stream cimport *
    cimport cef_stream_static
    from cef_response_cef1 cimport *
    from cef_stream cimport *
    from cef_content_filter cimport *
    from content_filter_handler cimport *
    from cef_download_handler cimport *
    from download_handler cimport *
    from cef_cookie_cef1 cimport *
    cimport cef_cookie_manager_namespace
    from cookie_visitor cimport *
    from cef_render_handler cimport *
    from cef_drag_data cimport *

IF UNAME_SYSNAME == "Windows":
    IF CEF_VERSION == 1:
        from http_authentication cimport *

IF CEF_VERSION == 3:
    from cef_values cimport *
    from cefpython_app cimport *
    from cef_process_message cimport *
    from cef_web_plugin_cef3 cimport *
    from cef_request_handler_cef3 cimport *
    from cef_request_cef3 cimport *
    from cef_cookie_cef3 cimport *
    from cef_string_visitor cimport *
    cimport cef_cookie_manager_namespace
    from cookie_visitor cimport *
    from string_visitor cimport *
    from cef_callback_cef3 cimport *
    from cef_response_cef3 cimport *
    from cef_resource_handler_cef3 cimport *
    from resource_handler_cef3 cimport *
    from cef_urlrequest_cef3 cimport *
    from web_request_client_cef3 cimport *
    from cef_command_line cimport *
    from cef_request_context cimport *
    from cef_request_context_handler cimport *
    from request_context_handler cimport *
    from cef_jsdialog_handler cimport *
"""
    expected_output = """
import copy
import datetime
import inspect  # used by JavascriptBindings.__SetObjectMethods()
import json
import os
import platform
import random
import re
import sys
import time
import traceback
import types
import urllib

import cython

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

if sys.version_info.major == 2:
    from urllib import pathname2url as urllib_pathname2url
else:
    from urllib.request import pathname2url as urllib_pathname2url

from cpython.version cimport PY_MAJOR_VERSION

import weakref

# We should allow multiple string types: str, unicode, bytes.
# PyToCefString() can handle them all.
# Important:
#   If you set it to basestring, Cython will accept exactly(!)
#   str/unicode in Py2 and str in Py3. This won't work in Py3
#   as we might want to pass bytes as well. Also it will
#   reject string subtypes, so using it in publi API functions
#   would be a bad idea.
ctypedef object py_string

# You can't use "void" along with cpdef function returning None, it is planned to be
# added to Cython in the future, creating this virtual type temporarily. If you
# change it later to "void" then don't forget to add "except *".
ctypedef object py_void
ctypedef long WindowHandle

cimport ctime
from cpython cimport PyLong_FromVoidPtr
from cpython cimport bool as py_bool
# preincrement and dereference must be "as" otherwise not seen.
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from libc.stdint cimport uint64_t, uintptr_t
from libc.stdlib cimport atoi, calloc, free, malloc
from libc.string cimport memcpy, strlen
from libcpp cimport bool as cpp_bool
from libcpp.map cimport map as cpp_map
from libcpp.pair cimport pair as cpp_pair
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from multimap cimport multimap as cpp_multimap
from wstring cimport wstring as cpp_wstring

# from cython.operator cimport address as addr # Address of an c++ object?


# When pyx file cimports * from a pxd file and that pxd cimports * from another pxd
# then these names will be visible in pyx file.

# Circular imports are allowed in form "cimport ...", but won't work if you do
# "from ... cimport *", this is important to know in pxd files.



IF UNAME_SYSNAME == "Windows":
    from dpi_aware_win cimport *
    from windows cimport *
ELIF UNAME_SYSNAME == "Linux":
    from linux cimport *
ELIF UNAME_SYSNAME == "Darwin":
    from mac cimport *

from cef_string cimport *
from cpp_utils cimport *
from task cimport *


cdef extern from *:
    ctypedef CefString ConstCefString "const CefString"

cimport cef_browser_static
# cannot cimport *, that would cause name conflicts with constants.
cimport cef_types
from cef_app cimport *
from cef_browser cimport *
from cef_client cimport *
from cef_frame cimport *
from cef_platform cimport *
from cef_ptr cimport *
from cef_runnable cimport *
from cef_task cimport *
from cef_types_wrappers cimport *
from client_handler cimport *

ctypedef cef_types.cef_paint_element_type_t PaintElementType
ctypedef cef_types.cef_jsdialog_type_t JSDialogType
from cef_types cimport CefKeyEvent, CefMouseEvent, CefScreenInfo

# cannot cimport *, name conflicts
IF UNAME_SYSNAME == "Windows":
    cimport cef_types_win
ELIF UNAME_SYSNAME == "Darwin":
    cimport cef_types_mac
ELIF UNAME_SYSNAME == "Linux":
    cimport cef_types_linux

from cef_drag cimport *
from cef_time cimport *

import os

IF CEF_VERSION == 1:
    cimport cef_cookie_manager_namespace
    cimport cef_stream_static
    cimport cef_v8_stack_trace
    cimport cef_v8_static
    cimport cef_web_urlrequest_static_cef1
    from cef_content_filter cimport *
    from cef_cookie_cef1 cimport *
    from cef_download_handler cimport *
    from cef_drag_data cimport *
    from cef_render_handler cimport *
    from cef_request_cef1 cimport *
    from cef_response_cef1 cimport *
    from cef_stream cimport *
    from cef_v8 cimport *
    from cef_web_urlrequest_cef1 cimport *
    from content_filter_handler cimport *
    from cookie_visitor cimport *
    from download_handler cimport *
    from v8function_handler cimport *
    from web_request_client_cef1 cimport *

IF UNAME_SYSNAME == "Windows":
    IF CEF_VERSION == 1:
        from http_authentication cimport *

IF CEF_VERSION == 3:
    cimport cef_cookie_manager_namespace
    from cef_callback_cef3 cimport *
    from cef_command_line cimport *
    from cef_cookie_cef3 cimport *
    from cef_jsdialog_handler cimport *
    from cef_process_message cimport *
    from cef_request_cef3 cimport *
    from cef_request_context cimport *
    from cef_request_context_handler cimport *
    from cef_request_handler_cef3 cimport *
    from cef_resource_handler_cef3 cimport *
    from cef_response_cef3 cimport *
    from cef_string_visitor cimport *
    from cef_urlrequest_cef3 cimport *
    from cef_values cimport *
    from cef_web_plugin_cef3 cimport *
    from cefpython_app cimport *
    from cookie_visitor cimport *
    from request_context_handler cimport *
    from resource_handler_cef3 cimport *
    from string_visitor cimport *
    from web_request_client_cef3 cimport *
"""
    assert isort.code(test_input).strip() == expected_output.strip()
    assert isort.code(test_input, old_finders=True).strip() == expected_output.strip()


def test_cdef_support():
    assert (
        isort.code(
            code="""
from cpython.version cimport PY_MAJOR_VERSION

cdef extern from *:
    ctypedef CefString ConstCefString "const CefString"
"""
        )
        == """
from cpython.version cimport PY_MAJOR_VERSION


cdef extern from *:
    ctypedef CefString ConstCefString "const CefString"
"""
    )

    assert (
        isort.code(
            code="""
from cpython.version cimport PY_MAJOR_VERSION

cpdef extern from *:
    ctypedef CefString ConstCefString "const CefString"
"""
        )
        == """
from cpython.version cimport PY_MAJOR_VERSION


cpdef extern from *:
    ctypedef CefString ConstCefString "const CefString"
"""
    )


def test_top_level_import_order() -> None:
    test_input = (
        "from rest_framework import throttling, viewsets\n"
        "from rest_framework.authentication import TokenAuthentication\n"
    )
    assert isort.code(test_input, force_sort_within_sections=True) == test_input


def test_noqa_issue_1065() -> None:
    test_input = """
#
# USER SIGNALS
#

from flask_login import user_logged_in, user_logged_out  # noqa

from flask_security.signals import (  # noqa
    password_changed as user_reset_password,  # noqa
    user_confirmed,  # noqa
    user_registered,  # noqa
)  # noqa

from flask_principal import identity_changed as user_identity_changed  # noqa
"""
    expected_output = """
#
# USER SIGNALS
#

from flask_login import user_logged_in, user_logged_out  # noqa
from flask_principal import identity_changed as user_identity_changed  # noqa
from flask_security.signals import password_changed as user_reset_password  # noqa
from flask_security.signals import user_confirmed  # noqa
from flask_security.signals import user_registered  # noqa
"""
    assert isort.code(test_input, line_length=100) == expected_output


def test_single_line_exclusions():
    test_input = """
# start comment
from os import path, system
from typing import List, TypeVar
"""
    expected_output = """
# start comment
from os import path
from os import system
from typing import List, TypeVar
"""
    assert (
        isort.code(code=test_input, force_single_line=True, single_line_exclusions=("typing",))
        == expected_output
    )


def test_nested_comment_handling():
    test_input = """
if True:
    import foo

# comment for bar
"""
    assert isort.code(test_input) == test_input

    # If comments appear inside import sections at same indentation they can be re-arranged.
    test_input = """
if True:
    import sys

    # os import
    import os
"""
    expected_output = """
if True:
    # os import
    import os
    import sys
"""
    assert isort.code(test_input) == expected_output

    # Comments shouldn't be unexpectedly rearranged. See issue #1090.
    test_input = """
def f():
    # comment 1
    # comment 2

    # comment 3
    # comment 4
    from a import a
    from b import b

"""
    assert isort.code(test_input) == test_input

    # Whitespace shouldn't be adjusted for nested imports. See issue #1090.
    test_input = """
try:
     import foo
 except ImportError:
     import bar
"""
    assert isort.code(test_input) == test_input


def test_comments_top_of_file():
    """Test to ensure comments at top of file are correctly handled. See issue #1091."""
    test_input = """# comment 1

# comment 2
# comment 3
# comment 4
from foo import *
"""
    assert isort.code(test_input) == test_input

    test_input = """# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

from .items import WeiboMblogItem


class WeiboMblogPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, WeiboMblogItem):
            item = self._process_item(item, spider)
        return item

    def _process_item(self, item, spider):
        item['inserted_at'] = datetime.now()
        return item
"""
    assert isort.code(test_input) == test_input


def test_multiple_aliases():
    """Test to ensure isort will retain multiple aliases. See issue #1037"""
    test_input = """import datetime
import datetime as datetime
import datetime as dt
import datetime as dt2
"""
    assert isort.code(code=test_input) == test_input


def test_parens_in_comment():
    """Test to ensure isort can handle parens placed in comments. See issue #1103"""
    test_input = """from foo import ( # (some text in brackets)
    bar,
)
"""
    expected_output = "from foo import bar  # (some text in brackets)\n"
    assert isort.code(test_input) == expected_output


def test_as_imports_mixed():
    """Test to ensure as imports can be mixed with non as. See issue #908"""
    test_input = """from datetime import datetime
import datetime.datetime as dt
"""
    expected_output = """import datetime.datetime as dt
from datetime import datetime
"""
    assert isort.code(test_input) == expected_output


def test_no_sections_with_future():
    """Test to ensure no_sections works with future. See issue #807"""
    test_input = """from __future__ import print_function
import os
    """
    expected_output = """from __future__ import print_function

import os
"""
    assert isort.code(test_input, no_sections=True) == expected_output


def test_no_sections_with_as_import():
    """Test to ensure no_sections work with as import."""
    test_input = """import oumpy as np
import sympy
"""
    assert isort.code(test_input, no_sections=True) == test_input


def test_no_lines_too_long():
    """Test to ensure no lines end up too long. See issue: #1015"""
    test_input = """from package1 import first_package, \
second_package
from package2 import \\
    first_package
    """
    expected_output = """from package1 import \\
    first_package, \\
    second_package
from package2 import \\
    first_package
"""
    assert isort.code(test_input, line_length=25, multi_line_output=2) == expected_output


def test_python_future_category():
    """Test to ensure a manual python future category will work as needed to install aliases

    see: Issue #1005
    """
    test_input = """from __future__ import absolute_import

# my future comment
from future import standard_library

standard_library.install_aliases()

import os
import re
import time

from logging.handlers import SysLogHandler

from builtins import len, object, str

from katlogger import log_formatter, log_rollover

from .query_elastic import QueryElastic
"""
    expected_output = """from __future__ import absolute_import

# my future comment
from future import standard_library

standard_library.install_aliases()

# Python Standard Library
import os
import re
import time

from builtins import len, object, str
from logging.handlers import SysLogHandler

# CAM Packages
from katlogger import log_formatter, log_rollover

# Explicitly Local
from .query_elastic import QueryElastic
"""
    assert (
        isort.code(
            code=test_input,
            force_grid_wrap=False,
            include_trailing_comma=True,
            indent=4,
            line_length=90,
            multi_line_output=3,
            lines_between_types=1,
            sections=[
                "FUTURE_LIBRARY",
                "FUTURE_THIRDPARTY",
                "STDLIB",
                "THIRDPARTY",
                "FIRSTPARTY",
                "LOCALFOLDER",
            ],
            import_heading_stdlib="Python Standard Library",
            import_heading_thirdparty="Third Library",
            import_heading_firstparty="CAM Packages",
            import_heading_localfolder="Explicitly Local",
            known_first_party=["katlogger"],
            known_future_thirdparty=["future"],
        )
        == expected_output
    )


def test_combine_star_comments_above():
    input_text = """from __future__ import absolute_import

# my future comment
from future import *, something
"""
    expected_output = """from __future__ import absolute_import

# my future comment
from future import *
"""
    assert isort.code(input_text, combine_star=True) == expected_output


def test_deprecated_settings():
    """Test to ensure isort warns when deprecated settings are used, but doesn't fail to run"""
    with pytest.warns(UserWarning):
        assert isort.code("hi", not_skip=True)


def test_deprecated_settings_no_warn_in_quiet_mode(recwarn):
    """Test to ensure isort does NOT warn in quiet mode even though settings are deprecated"""
    assert isort.code("hi", not_skip=True, quiet=True)
    assert not recwarn


def test_only_sections() -> None:
    """Test to ensure that the within sections relative position of imports are maintained"""
    test_input = (
        "import sys\n"
        "\n"
        "import numpy as np\n"
        "\n"
        "import os\n"
        "from os import path as ospath\n"
        "\n"
        "import pandas as pd\n"
        "\n"
        "import math\n"
        "import .views\n"
        "from collections import defaultdict\n"
    )

    assert (
        isort.code(test_input, only_sections=True)
        == (
            "import sys\n"
            "import os\n"
            "import math\n"
            "from os import path as ospath\n"
            "from collections import defaultdict\n"
            "\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "\n"
            "import .views\n"
        )
        == isort.code(test_input, only_sections=True, force_single_line=True)
    )

    # test to ensure that from_imports remain intact with only_sections
    test_input = "from foo import b, a, c\n"

    assert isort.code(test_input, only_sections=True) == test_input
