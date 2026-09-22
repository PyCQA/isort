import pytest
from hypothesis import given, reject
from hypothesis import strategies as st

import isort
from isort import wrap_modes
from isort.wrap_modes import WrapModes, _wrap_modes


def test_wrap_mode_interface():
    assert (
        wrap_modes._wrap_mode_interface("statement", [], "", "", 80, [], "", "", True, True) == ""
    )


def test_auto_saved():
    """hypothesis_auto tests cases that have been saved to ensure they run each test cycle"""
    assert (
        wrap_modes.noqa(
            comment_prefix="-\U000bf82c\x0c\U0004608f\x10%",
            comments=[],
            imports=[],
            include_trailing_comma=False,
            indent="0\x19",
            line_length=-19659,
            line_separator="\x15\x0b\U00086494\x1d\U000e00a2\U000ee216\U0006708a\x03\x1f",
            remove_comments=False,
            statement="\U00092452",
            white_space="\U000a7322\U000c20e3-\U0010eae4\x07\x14\U0007d486",
        )
        == "\U00092452-\U000bf82c\x0c\U0004608f\x10% NOQA"
    )
    assert (
        wrap_modes.noqa(
            comment_prefix='\x12\x07\U0009e994🁣"\U000ae787\x0e',
            comments=["\x00\U0001ae99\U0005c3e7\U0004d08e", "\x1e", "", ""],
            imports=["*"],
            include_trailing_comma=True,
            indent="",
            line_length=31492,
            line_separator="\U00071610\U0005bfbc",
            remove_comments=False,
            statement="",
            white_space="\x08\x01ⷓ\x16%\U0006cd8c",
        )
        == '*\x12\x07\U0009e994🁣"\U000ae787\x0e \x00\U0001ae99\U0005c3e7\U0004d08e \x1e  '
    )
    assert (
        wrap_modes.noqa(
            comment_prefix="  #",
            comments=["NOQA", "THERE"],
            imports=[],
            include_trailing_comma=False,
            indent="0\x19",
            line_length=-19659,
            line_separator="\n",
            remove_comments=False,
            statement="hi",
            white_space=" ",
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


@pytest.mark.parametrize("include_trailing_comma", [False, True])
@pytest.mark.parametrize("line_length", [18, 19])
@pytest.mark.parametrize("multi_line_output", [4, 5])
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


def test_vertical_hanging_indent_long_comment_respects_line_length():
    """A long comment that exceeds line_length is placed on its own line."""
    assert (
        wrap_modes.vertical_hanging_indent(
            statement="from os.path import ",
            imports=["getsize", "join"],
            white_space="    ",
            indent="    ",
            line_length=88,
            comments=[
                " this is a really really really really really really"
                " really really really really really really long comment"
            ],
            line_separator="\n",
            comment_prefix="  #",
            include_trailing_comma=True,
            remove_comments=False,
        )
        == "from os.path import (\n"
        "    #  this is a really really really really really really really really"
        " really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        ")"
    )


def test_vertical_hanging_indent_short_comment_stays_on_opening_line():
    """A short comment that fits within line_length stays on the opening line."""
    assert (
        wrap_modes.vertical_hanging_indent(
            statement="from os.path import ",
            imports=["getsize", "join"],
            white_space="    ",
            indent="    ",
            line_length=88,
            comments=[" short comment"],
            line_separator="\n",
            comment_prefix="  #",
            include_trailing_comma=True,
            remove_comments=False,
        )
        == "from os.path import (  #  short comment\n    getsize,\n    join,\n)"
    )


def test_vertical_hanging_indent_non_directive_type_comment_moves_off():
    """A long comment containing 'type:' but not a 'type: ignore' directive moves off."""
    assert (
        wrap_modes.vertical_hanging_indent(
            statement="from os.path import ",
            imports=["getsize", "join"],
            white_space="    ",
            indent="    ",
            line_length=88,
            comments=[
                " check type: int and more really really really really really really"
                " really really really really really really long comment"
            ],
            line_separator="\n",
            comment_prefix="  #",
            include_trailing_comma=True,
            remove_comments=False,
        )
        == "from os.path import (\n"
        "    #  check type: int and more really really really really really really really really"
        " really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        ")"
    )


def test_vertical_hanging_indent_multi_fragment_comments_each_on_own_line():
    """Each comment fragment renders on its own # line to respect line_length."""
    result = wrap_modes.vertical_hanging_indent(
        statement="from os.path import ",
        imports=["getsize", "join"],
        white_space="    ",
        indent="    ",
        line_length=88,
        comments=[
            " this is a really really really really really really really really",
            " really really really really really really long comment",
        ],
        line_separator="\n",
        comment_prefix="  #",
        include_trailing_comma=True,
        remove_comments=False,
    )
    assert result == (
        "from os.path import (\n"
        "    #  this is a really really really really really really really really\n"
        "    #  really really really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        ")"
    )
    for line in result.split("\n"):
        assert len(line) <= 88, f"line exceeds 88: {line!r}"


def test_vertical_hanging_indent_mixed_functional_and_plain_comments():
    """A functional comment stays on the opening line while plain fragments move off.

    Guards against the whole-list ``any()`` gate that kept an over-long plain
    comment merged once a single ``noqa`` fragment was present (see #2124).
    """
    result = wrap_modes.vertical_hanging_indent(
        statement="from os.path import ",
        imports=["getsize", "join"],
        white_space="    ",
        indent="    ",
        line_length=88,
        comments=[
            "noqa: F401",
            " this is a really really really really really really really really",
            " really really really really really really long comment",
        ],
        line_separator="\n",
        comment_prefix="  #",
        include_trailing_comma=True,
        remove_comments=False,
    )
    assert result == (
        "from os.path import (  # noqa: F401\n"
        "    #  this is a really really really really really really really really\n"
        "    #  really really really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        ")"
    )
    for line in result.split("\n"):
        assert len(line) <= 88, f"line exceeds 88: {line!r}"


def test_vertical_hanging_indent_opening_comment_never_moves():
    """An opening-line comment keeps its placement even over line_length.

    Only body comments may move; the opening line is reproduced byte-identical.
    """
    result = wrap_modes.vertical_hanging_indent(
        statement="from habitat_baselines.common.obs_transformers import ",
        imports=["apply_obs_transforms_batch", "apply_obs_transforms_obs_space"],
        white_space="    ",
        indent="    ",
        line_length=79,
        comments=["get_active_obs_transforms,"],
        opening_comments=["get_active_obs_transforms,"],
        line_separator="\n",
        comment_prefix="  #",
        include_trailing_comma=True,
        remove_comments=False,
    )
    assert result == (
        "from habitat_baselines.common.obs_transformers import (  # get_active_obs_transforms,\n"
        "    apply_obs_transforms_batch,\n"
        "    apply_obs_transforms_obs_space,\n"
        ")"
    )


def test_vertical_hanging_indent_opening_plus_body_comments():
    """Opening comment stays while an over-long body comment moves off."""
    result = wrap_modes.vertical_hanging_indent(
        statement="from os.path import ",
        imports=["getsize", "join"],
        white_space="    ",
        indent="    ",
        line_length=88,
        comments=[
            "opening note",
            " this is a really really really really really really really really",
            " really really really really really really long comment",
        ],
        opening_comments=["opening note"],
        line_separator="\n",
        comment_prefix="  #",
        include_trailing_comma=True,
        remove_comments=False,
    )
    assert result == (
        "from os.path import (  # opening note\n"
        "    #  this is a really really really really really really really really\n"
        "    #  really really really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        ")"
    )


def test_vertical_hanging_indent_bracket_long_comment_respects_line_length():
    """The bracket consumer stays valid when comments move off the opening line."""
    result = wrap_modes.vertical_hanging_indent_bracket(
        statement="from os.path import ",
        imports=["getsize", "join"],
        white_space="    ",
        indent="    ",
        line_length=88,
        comments=[
            " this is a really really really really really really really really",
            " really really really really really really long comment",
        ],
        line_separator="\n",
        comment_prefix="  #",
        include_trailing_comma=True,
        remove_comments=False,
    )
    assert result == (
        "from os.path import (\n"
        "    #  this is a really really really really really really really really\n"
        "    #  really really really really really really long comment\n"
        "    getsize,\n"
        "    join,\n"
        "    )"
    )
    for line in result.split("\n"):
        assert len(line) <= 88, f"line exceeds 88: {line!r}"


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


@pytest.mark.parametrize("include_trailing_comma", [True, False])
def test_hanging_indent__with_include_trailing_comma__expect_same_result(include_trailing_comma):
    result = isort.wrap_modes.hanging_indent(
        statement="from datetime import ",
        imports=["datetime", "time", "timedelta", "timezone", "tzinfo"],
        white_space=" ",
        indent="    ",
        line_length=50,
        comments=[],
        line_separator="\n",
        comment_prefix=" #",
        include_trailing_comma=include_trailing_comma,
        remove_comments=False,
    )

    assert result == "from datetime import datetime, time, timedelta, \\\n    timezone, tzinfo"


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


def test_enum_matches_order_of_definitions():
    """Before isort 9.0.0 WrapModes was dynamically generated, this tests for breaking changes."""

    old_enum_logic = {wrap_mode: index for index, wrap_mode in enumerate(_wrap_modes.keys())}
    new_enum_logic = {wrap_mode.name: wrap_mode.value for wrap_mode in WrapModes}
    assert old_enum_logic == new_enum_logic, (
        "WrapModes enum order has changed, this is a breaking change."
    )
