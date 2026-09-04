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


def test_line_star_import_is_not_wrapped() -> None:
    """Star imports cannot be split in a way that Black accepts (issue #2649)."""
    content = "from very.very.very.very.very.very.very.very.very.long.line import *"
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == content


def test_line_star_cimport_is_not_wrapped() -> None:
    """Star cimports have the same syntactic wrapping restriction."""
    content = "from very.very.very.very.very.very.very.very.very.long.line cimport *"
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == content


def test_line_star_import_with_comment_is_not_wrapped() -> None:
    """Comments remain on an over-long star import that cannot be wrapped."""
    content = "from very.very.very.very.very.very.very.very.very.long.line import *  # noqa: F401"
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == content


def test_line_star_import_in_noqa_mode_is_not_backslash_wrapped() -> None:
    """NOQA mode should prevent backslashes getting inserted for too long star imports."""
    content = "from very.very.very.very.very.very.very.very.very.very.very.long.line import *"
    config = Config(line_length=20, multi_line_output=WrapModes.NOQA)
    assert wrap.line(content=content, line_separator="\n", config=config) == (
        "from very.very.very.very.very.very.very.very.very.very.very.long.line import *  # NOQA"
    )


def test_star_import_is_not_wrapped_end_to_end() -> None:
    """Long star imports remain stable across isort and Black (issue #2649)."""
    source = "from very.very.very.very.very.very.very.very.very.long.line import *\n"
    assert code(source, profile="black") == source
