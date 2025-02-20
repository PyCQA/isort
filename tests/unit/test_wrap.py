import pytest

from isort import wrap
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
            WrapModes.VERTICAL_HANGING_INDENT,  # type: ignore
            """from a import (
    b as c  # comment that is long enough that this import doesn't fit in one line (parens)
)""",
        ),
        (
            WrapModes.VERTICAL,  # type: ignore
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
