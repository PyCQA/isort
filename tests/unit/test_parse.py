from hypothesis import given
from hypothesis import strategies as st

from isort import parse
from isort.settings import Config

TEST_CONTENTS = """
import xyz
import abc
import (\\ # one
    one as \\ # two
    three)
import \\
    zebra as \\ # one
    not_bacon
from x import (\\ # one
    one as \\ # two
    three)


def function():
    pass
"""


def test_file_contents():
    (
        in_lines,
        out_lines,
        import_index,
        _,
        _,
        _,
        _,
        _,
        change_count,
        original_line_count,
        _,
        _,
        _,
    ) = parse.file_contents(TEST_CONTENTS, config=Config(default_section=""))
    assert "\n".join(in_lines) == TEST_CONTENTS
    assert "import" not in "\n".join(out_lines)
    assert import_index == 1
    assert change_count == -11
    assert original_line_count == len(in_lines)


# These tests were written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


@given(contents=st.text())
def test_fuzz__infer_line_separator(contents):
    parse._infer_line_separator(contents=contents)


@given(import_string=st.text())
def test_fuzz__strip_syntax(import_string):
    parse._strip_syntax(import_string=import_string)


@given(line=st.text(), config=st.builds(Config))
def test_fuzz_import_type(line, config):
    parse.import_type(line=line, config=config)


@given(
    line=st.text(),
    in_quote=st.text(),
    index=st.integers(),
    section_comments=st.lists(st.text()).map(tuple),
    needs_import=st.booleans(),
)
def test_fuzz_skip_line(line, in_quote, index, section_comments, needs_import):
    parse.skip_line(
        line=line,
        in_quote=in_quote,
        index=index,
        section_comments=section_comments,
        needs_import=needs_import,
    )
