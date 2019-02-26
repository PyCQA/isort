import copy
from typing import List, Optional, Sequence, Tuple


def strip_comments(line: str,
                   comments: Optional[List[str]] = None
                   ) -> Tuple[str, List[str], bool]:
    """
    Removes comments from import line.
    'import a  # comment' -> 'import a'
    """
    if comments is None:
        comments = []

    new_comment_found = False
    comment_start = line.find("#")
    if comment_start != -1:  # comment found
        comments.append(line[comment_start + 1:].strip())
        new_comment_found = True
        line = line[:comment_start]

    return line, comments, new_comment_found


def strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
    """Strips # comments that exist at the top of the given lines"""
    lines = copy.copy(lines)
    while lines and lines[0].startswith("#"):
        lines = lines[1:]
    return line_separator.join(lines)


def strip_syntax(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")
    for remove_syntax in ['\\', '(', ')', ',']:
        import_string = import_string.replace(remove_syntax, " ")

    import_list = import_string.split()
    for key in ('from', 'import'):
        if key in import_list:
            import_list.remove(key)

    import_string = ' '.join(import_list)
    import_string = import_string.replace("[[i]]", "_import")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


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
