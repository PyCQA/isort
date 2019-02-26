import copy
from typing import List, Optional, Sequence, Tuple


def strip_comments(
    line: str,
    comments: Optional[List[str]] = None
) -> Tuple[str, List[str], bool]:
    """Removes comments from import line."""
    if comments is None:
        comments = []

    new_comments = False
    comment_start = line.find("#")
    if comment_start != -1:
        comments.append(line[comment_start + 1:].strip())
        new_comments = True
        line = line[:comment_start]

    return line, comments, new_comments


def strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
    """Strips # comments that exist at the top of the given lines"""
    lines = copy.copy(lines)
    while lines and lines[0].startswith("#"):
        lines = lines[1:]
    return line_separator.join(lines)


def format_simplified(import_line: str) -> str:
    import_line = import_line.strip()
    if import_line.startswith("from "):
        import_line = import_line.replace("from ", "")
        import_line = import_line.replace(" import ", ".")
    elif import_line.startswith("import "):
        import_line = import_line.replace("import ", "")

    return import_line


def format_natural(import_line: str) -> str:
    import_line = import_line.strip()
    if not import_line.startswith("from ") and not import_line.startswith("import "):
        if "." not in import_line:
            return "import {0}".format(import_line)
        parts = import_line.split(".")
        end = parts.pop(-1)
        return "from {0} import {1}".format(".".join(parts), end)

    return import_line