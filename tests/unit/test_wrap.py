import pytest

from isort import code, wrap
from isort.settings import Config
from isort.wrap_modes import WrapModes


def test_import_statement():
    assert wrap.import_statement("", [], []) == ""
    assert (
        wrap.import_statement("from x import ", ["y"], [], config=Config(balanced_wrapping=True))
        == "from x import (y)"
    )
    assert (
        wrap.import_statement("from long_import ", ["verylong"] * 10, [])
        == """from long_import (verylong, verylong, verylong, verylong, verylong, verylong,
                  verylong, verylong, verylong, verylong)"""
    )
    assert wrap.import_statement("from x import ", ["y", "z"], [], explode=True) == (
        "from x import (\n    y,\n    z,\n)"
    )


@pytest.mark.parametrize(
    ("multi_line_output", "expected"),
    [
        (
            WrapModes.VERTICAL_HANGING_INDENT,
            """from a import (
    b as c  # comment that is long enough that this import doesn't fit in one line (parens)
)""",
        ),
        (
            WrapModes.VERTICAL,
            """from a import (
    b as c)  # comment that is long enough that this import doesn't fit in one line (parens)""",
        ),
    ],
)
def test_line__comment_with_brackets__expects_unchanged_comment(multi_line_output, expected):
    content = (
        "from a import b as c  "
        "# comment that is long enough that this import doesn't fit in one line (parens)"
    )
    config = Config(
        multi_line_output=multi_line_output,
        use_parentheses=True,
    )

    assert wrap.line(content=content, line_separator="\n", config=config) == expected


def test_line_star_import_wrapped_with_backslash() -> None:
    """Star imports cannot use parenthesis-based wrapping, so should use backslashes.

    See issue #2267.
    """
    content = "from very.very.very.very.very.very.very.very.very.long.line import *"
    expected = "from very.very.very.very.very.very.very.very.very.long.line import \\\n    *"
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == expected


def test_line_star_cimport_wrapped_with_backslash() -> None:
    """Star cimports should also use backslashes."""
    content = "from very.very.very.very.very.very.very.very.very.long.line cimport *"
    expected = "from very.very.very.very.very.very.very.very.very.long.line cimport \\\n    *"
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == expected


def test_line_star_import_with_comment_wrapped_with_backslash() -> None:
    """When falling back to backslashes for start imports, comments should be preserved."""
    content = "from very.very.very.very.very.very.very.very.very.long.line import *  # noqa: F401"
    config = Config(line_length=20)
    expected = (
        "from very.very.very.very.very.very.very.very.very.long.line import \\\n    *  # noqa: F401"
    )
    assert wrap.line(content=content, line_separator="\n", config=config) == expected


def test_line_star_import_in_noqa_mode_is_not_backslash_wrapped() -> None:
    """NOQA mode should prevent backslashes getting inserted for too long star imports."""
    content = "from very.very.very.very.very.very.very.very.very.very.very.long.line import *"
    config = Config(line_length=20, multi_line_output=WrapModes.NOQA)
    assert wrap.line(content=content, line_separator="\n", config=config) == (
        "from very.very.very.very.very.very.very.very.very.very.very.long.line import *  # NOQA"
    )


def test_star_import_wrapped_end_to_end() -> None:
    """New lines should be preserved at the end of too long start imports."""
    source = "from very.very.very.very.very.very.very.very.very.long.line import *\n"
    expected = "from very.very.very.very.very.very.very.very.very.long.line import \\\n    *\n"
    assert code(source, line_length=20, force_single_line=True) == expected
