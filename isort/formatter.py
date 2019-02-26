import copy
from typing import Sequence, Tuple


def partition_comment(line: str) -> Tuple[str, str]:
    comment = ''
    comment_start = line.find("#")
    if comment_start != -1:
        comment = line[comment_start + 1:].strip()
        line = line[:comment_start]
    return line, comment


def strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
    """Strips # comments that exist at the top of the given lines"""
    lines = copy.copy(lines)
    while lines and lines[0].startswith("#"):
        lines = lines[1:]
    return line_separator.join(lines)


def strip_syntax(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")

    syntactic_symbols_to_remove = ['\\', '(', ')', ',']
    for symbol in syntactic_symbols_to_remove:
        import_string = import_string.replace(symbol, " ")

    import_tokens = import_string.split()
    for key in ('from', 'import'):
        if key in import_tokens:
            import_tokens.remove(key)

    import_string = ' '.join(import_tokens)
    import_string = import_string.replace("[[i]]", "_import")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


def is_single_module_name(line: str) -> bool:
    return bool(line) and ' ' not in line


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
