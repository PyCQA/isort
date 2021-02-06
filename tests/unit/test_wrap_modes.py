import pytest
from hypothesis import given, reject
from hypothesis import strategies as st

import isort
from isort import wrap_modes


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
    assert (
        wrap_modes.noqa(
            **{
                "comment_prefix": "  #",
                "comments": ["NOQA", "THERE"],
                "imports": [],
                "include_trailing_comma": False,
                "indent": "0\x19",
                "line_length": -19659,
                "line_separator": "\n",
                "remove_comments": False,
                "statement": "hi",
                "white_space": " ",
            }
        )
        == "hi  # NOQA THERE"
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


@pytest.mark.parametrize("include_trailing_comma", (False, True))
@pytest.mark.parametrize("line_length", (18, 19))
@pytest.mark.parametrize("multi_line_output", (4, 5))
def test_vertical_grid_size_near_line_length(
    multi_line_output: int,
    line_length: int,
    include_trailing_comma: bool,
):
    separator = " "
    # Cases where the input should be wrapped:
    if (
        # Mode 4 always adds a closing ")", making the imports line 19 chars,
        # if include_trailing_comma is True that becomes 20 chars.
        (multi_line_output == 4 and line_length < 19 + int(include_trailing_comma))
        # Modes 5 and 6 only add a comma, if include_trailing_comma is True,
        # so their lines are 18 or 19 chars long.
        or (multi_line_output != 4 and line_length < 18 + int(include_trailing_comma))
    ):
        separator = "\n    "

    test_input = f"from foo import (\n    aaaa, bbb,{separator}ccc"
    if include_trailing_comma:
        test_input += ","
    if multi_line_output != 4:
        test_input += "\n"
    test_input += ")\n"

    assert (
        isort.code(
            test_input,
            multi_line_output=multi_line_output,
            line_length=line_length,
            include_trailing_comma=include_trailing_comma,
        )
        == test_input
    )


# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_backslash_grid(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.backslash_grid(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_grid(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.grid(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_hanging_indent(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.hanging_indent(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_hanging_indent_with_parentheses(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.hanging_indent_with_parentheses(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_noqa(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.noqa(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical_grid(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical_grid(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical_grid_grouped(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical_grid_grouped(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical_hanging_indent(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical_hanging_indent(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical_hanging_indent_bracket(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical_hanging_indent_bracket(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()


@given(
    statement=st.text(),
    imports=st.lists(st.text()),
    white_space=st.text(),
    indent=st.text(),
    line_length=st.integers(),
    comments=st.lists(st.text()),
    line_separator=st.text(),
    comment_prefix=st.text(),
    include_trailing_comma=st.booleans(),
    remove_comments=st.booleans(),
)
def test_fuzz_vertical_prefix_from_module_import(
    statement,
    imports,
    white_space,
    indent,
    line_length,
    comments,
    line_separator,
    comment_prefix,
    include_trailing_comma,
    remove_comments,
):
    try:
        isort.wrap_modes.vertical_prefix_from_module_import(
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
    except ValueError:
        reject()
