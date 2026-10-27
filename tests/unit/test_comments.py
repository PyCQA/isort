from hypothesis import given
from hypothesis import strategies as st

import isort.comments


def test_add_to_line() -> None:
    assert (
        isort.comments.add_to_line([], "import os  # comment", removed=True).strip() == "import os"
    )


def test_add_to_line_drops_an_empty_comment_instead_of_leaving_a_separator() -> None:
    """A bare ``#`` carries no text, so merging it must not leave ``"; "`` behind."""
    assert (
        isort.comments.add_to_line(["x", ""], "from sys import a, b", comment_prefix="  #")
        == "from sys import a, b  # x"
    )
    assert (
        isort.comments.add_to_line(["", "x"], "from sys import a, b", comment_prefix="  #")
        == "from sys import a, b  # x"
    )
    # A lone bare ``#`` is still a comment and has to survive.
    assert (
        isort.comments.add_to_line([""], "from sys import a", comment_prefix="  #")
        == "from sys import a  #"
    )


def test_merging_a_bare_comment_is_idempotent() -> None:
    """isort must not rewrite its own output when a bare ``#`` gets merged."""
    first = isort.code("from sys import a  # x\nfrom sys import b  #\n")
    assert first == "from sys import a, b  # x\n"
    assert isort.code(first) == first


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
