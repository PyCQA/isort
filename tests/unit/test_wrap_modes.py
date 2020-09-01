from hypothesis_auto import auto_pytest_magic

import isort
from isort import wrap_modes

auto_pytest_magic(wrap_modes.grid, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.vertical, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.hanging_indent, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.vertical_hanging_indent, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.vertical_grid, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.vertical_grid_grouped, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.vertical_grid_grouped_no_comma, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.noqa, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.noqa, auto_allow_exceptions_=(ValueError,), comments=["NOQA"])
auto_pytest_magic(
    wrap_modes.vertical_prefix_from_module_import, auto_allow_exceptions_=(ValueError,)
)
auto_pytest_magic(wrap_modes.vertical_hanging_indent_bracket, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(
    wrap_modes.vertical_hanging_indent_bracket,
    auto_allow_exceptions_=(ValueError,),
    imports=["one", "two"],
)
auto_pytest_magic(wrap_modes.hanging_indent_with_parentheses, auto_allow_exceptions_=(ValueError,))
auto_pytest_magic(wrap_modes.backslash_grid, auto_allow_exceptions_=(ValueError,))


def test_wrap_mode_interface():
    assert (
        wrap_modes._wrap_mode_interface("statement", [], "", "", 80, [], "", "", True, True) == ""
    )


def test_auto_saved():
    """hypothesis_auto tests cases that have been saved to ensure they run each test cycle"""
    assert (
        wrap_modes.noqa(
            **{
                "comment_prefix": "-\U000bf82c\x0c\U0004608f\x10%",
                "comments": [],
                "imports": [],
                "include_trailing_comma": False,
                "indent": "0\x19",
                "line_length": -19659,
                "line_separator": "\x15\x0b\U00086494\x1d\U000e00a2\U000ee216\U0006708a\x03\x1f",
                "remove_comments": False,
                "statement": "\U00092452",
                "white_space": "\U000a7322\U000c20e3-\U0010eae4\x07\x14\U0007d486",
            }
        )
        == "\U00092452-\U000bf82c\x0c\U0004608f\x10% NOQA"
    )
    assert (
        wrap_modes.noqa(
            **{
                "comment_prefix": '\x12\x07\U0009e994🁣"\U000ae787\x0e',
                "comments": ["\x00\U0001ae99\U0005c3e7\U0004d08e", "\x1e", "", ""],
                "imports": ["*"],
                "include_trailing_comma": True,
                "indent": "",
                "line_length": 31492,
                "line_separator": "\U00071610\U0005bfbc",
                "remove_comments": False,
                "statement": "",
                "white_space": "\x08\x01ⷓ\x16%\U0006cd8c",
            }
        )
        == '*\x12\x07\U0009e994🁣"\U000ae787\x0e \x00\U0001ae99\U0005c3e7\U0004d08e \x1e  '
    )


def test_backslash_grid():
    """Tests the backslash_grid grid wrap mode, ensuring it matches formatting expectations.
    See: https://github.com/PyCQA/isort/issues/1434
    """
    assert (
        isort.code(
            """
from kopf.engines import loggers, posting
from kopf.reactor import causation, daemons, effects, handling, lifecycles, registries
from kopf.storage import finalizers, states
from kopf.structs import (bodies, configuration, containers, diffs,
                          handlers as handlers_, patches, resources)
""",
            multi_line_output=11,
            line_length=88,
            combine_as_imports=True,
        )
        == """
from kopf.engines import loggers, posting
from kopf.reactor import causation, daemons, effects, handling, lifecycles, registries
from kopf.storage import finalizers, states
from kopf.structs import bodies, configuration, containers, diffs, \\
                         handlers as handlers_, patches, resources
"""
    )
