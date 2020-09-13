from hypothesis import given
from hypothesis import strategies as st

import isort.comments


def test_add_to_line():
    assert (
        isort.comments.add_to_line([], "import os  # comment", removed=True).strip() == "import os"
    )


# These tests were written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


@given(
    comments=st.one_of(st.none(), st.lists(st.text())),
    original_string=st.text(),
    removed=st.booleans(),
    comment_prefix=st.text(),
)
def test_fuzz_add_to_line(comments, original_string, removed, comment_prefix):
    isort.comments.add_to_line(
        comments=comments,
        original_string=original_string,
        removed=removed,
        comment_prefix=comment_prefix,
    )


@given(line=st.text())
def test_fuzz_parse(line):
    isort.comments.parse(line=line)
