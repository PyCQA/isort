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


def test_line__star_import_not_wrapped():
    # A ``from ... import *`` statement cannot be split across lines, so even
    # when it exceeds ``line_length`` it must be returned unchanged instead of
    # being word-wrapped into invalid Python. See issue #2267.
    content = (
        "from very.very.very.very.very.very.very.very.very.very.very.long.line import *"
    )
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == content


def test_line__star_import_with_comment_not_wrapped():
    content = (
        "from very.very.very.very.very.very.very.very.very.very.very.long.line import *"
        "  # noqa: F401"
    )
    config = Config(line_length=20)
    assert wrap.line(content=content, line_separator="\n", config=config) == content


def test_star_import_not_wrapped_end_to_end():
    source = (
        "from very.very.very.very.very.very.very.very.very.very.very.very.long.line import *\n"
    )
    result = code(source, line_length=20, force_single_line=True)
    # The wildcard import must stay on a single line and remain valid Python.
    assert "import *" in result.splitlines()[0]
    assert result.strip() == source.strip()
