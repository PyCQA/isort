from hypothesis import given, reject
from hypothesis import strategies as st

import isort.comments


@given(
    comments=st.one_of(st.none(), st.lists(st.text())),
    original_string=st.text(),
    removed=st.booleans(),
    comment_prefix=st.text(),
)
def test_fuzz_add_to_line(comments, original_string, removed, comment_prefix):
    try:
        isort.comments.add_to_line(
            comments=comments,
            original_string=original_string,
            removed=removed,
            comment_prefix=comment_prefix,
        )
    except ValueError:
        reject()
