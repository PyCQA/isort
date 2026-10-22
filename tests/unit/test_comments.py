from hypothesis import given
from hypothesis import strategies as st

import isort.comments


def test_add_to_line() -> None:
    assert (
        isort.comments.add_to_line([], "import os  # comment", removed=True).strip() == "import os"
    )


def test_is_pragma_comment() -> None:
    for comment in (
        "noqa",
        "noqa: F401",
        "type: ignore",
        "type:ignore",
        "type:   ignore[attr-defined]",
        "explanation  # noqa: F401",
        "TYPE: IGNORE",
    ):
        assert isort.comments.is_pragma_comment(comment), comment

    for comment in ("", "type: int", "check type: ignore later", "noqa_false"):
        assert not isort.comments.is_pragma_comment(comment), comment


# These tests were written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


@given(
    comments=st.one_of(st.none(), st.lists(st.text())),
    original_string=st.text(),
    removed=st.booleans(),
    comment_prefix=st.text(),
)
def test_fuzz_add_to_line(
    comments: list[str] | None, original_string: str, removed: bool, comment_prefix: str
) -> None:
    isort.comments.add_to_line(
        comments=comments,
        original_string=original_string,
        removed=removed,
        comment_prefix=comment_prefix,
    )


@given(line=st.text())
def test_fuzz_parse(line: str) -> None:
    isort.comments.parse(line=line)
