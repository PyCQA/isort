"""Defines parsing functions used by isort for parsing import definitions"""
from typing import Tuple


def import_comment(line: str) -> Tuple[str, str]:
    """Parses import lines for comments and returns back the
    import statement and the associated comment.
    """
    comment_start = line.find("#")
    if comment_start != -1:
        return (line[:comment_start], line[comment_start + 1 :].strip())

    return (line, "")
