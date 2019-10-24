from typing import List, Optional

from . import parse


def with_comments(
    comments: Optional[List[str]],
    original_string: str = "",
    removed: bool = False,
    comment_prefix: str = "",
) -> str:
    """Returns a string with comments added if removed is not set."""
    if removed:
        return parse.import_comment(original_string)[0]

    if not comments:
        return original_string
    else:
        return "{}{} {}".format(
            parse.import_comment(original_string)[0], comment_prefix, "; ".join(comments)
        )
