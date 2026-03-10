"""Shared low-level parsing utilities used by both parse.py and identify.py."""

import re
from collections.abc import Callable


def _infer_line_separator(contents: str) -> str:
    if "\r\n" in contents:
        return "\r\n"
    if "\r" in contents:
        return "\r"
    return "\n"


def normalize_line(raw_line: str) -> tuple[str, str]:
    """Normalizes import related statements in the provided line.

    Returns (normalized_line: str, raw_line: str)
    """
    line = re.sub(r"from(\.+)cimport ", r"from \g<1> cimport ", raw_line)
    line = re.sub(r"from(\.+)import ", r"from \g<1> import ", line)
    line = line.replace("import*", "import *")
    line = re.sub(r" (\.+)import ", r" \g<1> import ", line)
    line = re.sub(r" (\.+)cimport ", r" \g<1> cimport ", line)
    line = line.replace("\t", " ")
    return line, raw_line


def strip_syntax(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")
    import_string = import_string.replace("_cimport", "[[ci]]")
    for remove_syntax in ["\\", "(", ")", ","]:
        import_string = import_string.replace(remove_syntax, " ")
    import_list = import_string.split()
    for key in ("from", "import", "cimport"):
        if key in import_list:
            import_list.remove(key)
    import_string = " ".join(import_list)
    import_string = import_string.replace("[[i]]", "_import")
    import_string = import_string.replace("[[ci]]", "_cimport")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


def skip_line(
    line: str,
    in_quote: str,
    index: int,
    section_comments: tuple[str, ...],
    needs_import: bool = True,
) -> tuple[bool, str]:
    """Determine if a given line should be skipped.

    Returns back a tuple containing:

    (skip_line: bool,
     in_quote: str,)
    """
    should_skip = bool(in_quote)
    if '"' in line or "'" in line:
        char_index = 0
        while char_index < len(line):
            if line[char_index] == "\\":
                char_index += 1
            elif in_quote:
                if line[char_index : char_index + len(in_quote)] == in_quote:
                    in_quote = ""
            elif line[char_index] in ("'", '"'):
                long_quote = line[char_index : char_index + 3]
                if long_quote in ('"""', "'''"):
                    in_quote = long_quote
                    char_index += 2
                else:
                    in_quote = line[char_index]
            elif line[char_index] == "#":
                break
            char_index += 1

    if ";" in line.split("#")[0] and needs_import:
        for part in (part.strip() for part in line.split(";")):
            if (
                part
                and not part.startswith("from ")
                and not part.startswith(("import ", "cimport "))
            ):
                should_skip = True

    return (bool(should_skip or in_quote), in_quote)


def collect_import_continuation(
    line: str,
    import_string: str,
    get_next_line: Callable[[], tuple[str, str | None]],
    line_separator: str = "\n",
) -> tuple[str, str, list[tuple[str, str | None, bool]]]:
    """Collect continuation lines for a multi-line import statement.

    Handles both parenthesised imports ``from X import (`` + newline + ``    Y, Z)``
    and backslash-continued imports ``import Y, \\`` + newline + ``    Z``.

    Args:
        line: The first (already comment-stripped) line of the import.
        import_string: The import string accumulated so far for this line.
        get_next_line: Callable that returns ``(stripped_line, comment_or_None)``
            for the next input line.  Must raise :exc:`StopIteration` when the
            input is exhausted.
        line_separator: Separator used when joining continuation lines
            (default: ``"\\n"``).

    Returns:
        ``(final_line, complete_import_string, extra_lines)``

        *extra_lines* is a list of ``(line, comment, appended_with_separator)``
        tuples for every additional line consumed.  The boolean flag is
        ``True`` when the line was appended to *import_string* with
        *line_separator*, and ``False`` when it was joined inline with ``" "``
        (backslash-join branch).  Callers that track per-line comments or
        raw-line lists can inspect this list to reconstruct their own state.
    """
    extra_lines: list[tuple[str, str | None, bool]] = []

    if "(" in line.split("#", 1)[0]:
        while not line.split("#")[0].strip().endswith(")"):
            try:
                line, comment = get_next_line()
            except StopIteration:
                break
            extra_lines.append((line, comment, True))
            import_string += line_separator + line
    else:
        while line.strip().endswith("\\"):
            try:
                line, comment = get_next_line()
            except StopIteration:
                break
            line = line.lstrip()

            # Still need to check for parentheses after an escaped line
            if "(" in line.split("#")[0] and ")" not in line.split("#")[0]:
                extra_lines.append((line, comment, True))
                import_string += line_separator + line

                while not line.split("#")[0].strip().endswith(")"):
                    try:
                        line, comment = get_next_line()
                    except StopIteration:
                        break
                    extra_lines.append((line, comment, True))
                    import_string += line_separator + line
            else:
                if import_string.strip().endswith(
                    (" import", " cimport")
                ) or line.strip().startswith(("import ", "cimport ")):
                    extra_lines.append((line, comment, True))
                    import_string += line_separator + line
                else:
                    extra_lines.append((line, comment, False))
                    import_string = import_string.rstrip().rstrip("\\") + " " + line.lstrip()

    return line, import_string, extra_lines


def normalize_from_import_string(
    import_string: str, cimports: bool | None = None
) -> tuple[str, bool]:
    """Normalize a ``from … import …`` string, handling line-continuation characters.

    Removes ``import(``, backslash continuations and embedded newlines, then
    reconstructs the canonical ``from X import Y, Z`` form.

    Returns ``(normalized_string, is_cimport)``.

    *cimports* controls whether to split on ``" cimport "`` or ``" import "``:

    * Pass ``None`` (the default) to auto-detect from the normalized string.
      This is the appropriate choice when ``cimports`` has not yet been
      determined (e.g. in ``parse.file_contents``).
    * Pass an explicit ``bool`` when the caller has already determined whether
      this is a cimport statement from an earlier inspection of the line
      (e.g. in ``identify.imports``).  The caller is responsible for ensuring
      the value is consistent with the actual import string.
    """
    import_string = (
        import_string.replace("import(", "import (")
        .replace("\\", " ")
        .replace("\n", " ")
    )
    if cimports is None:
        cimports = " cimport " in import_string
    parts = import_string.split(" cimport " if cimports else " import ")
    from_import = parts[0].split(" ")
    return (
        (" cimport " if cimports else " import ").join(
            [from_import[0] + " " + "".join(from_import[1:]), *parts[1:]]
        ),
        cimports,
    )

