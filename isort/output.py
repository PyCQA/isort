from typing import List, Optional

from . import parse


def grid(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    statement += "(" + imports.pop(0)
    while imports:
        next_import = imports.pop(0)
        next_statement = with_comments(
            comments,
            statement + ", " + next_import,
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        if len(next_statement.split(line_separator)[-1]) + 1 > line_length:
            lines = ["{}{}".format(white_space, next_import.split(" ")[0])]
            for part in next_import.split(" ")[1:]:
                new_line = "{} {}".format(lines[-1], part)
                if len(new_line) + 1 > line_length:
                    lines.append("{}{}".format(white_space, part))
                else:
                    lines[-1] = new_line
            next_import = line_separator.join(lines)
            statement = with_comments(
                comments,
                "{},".format(statement),
                removed=remove_comments,
                comment_prefix=comment_prefix,
            ) + "{}{}".format(line_separator, next_import)
            comments = []
        else:
            statement += ", " + next_import
    return statement + ("," if include_trailing_comma else "") + ")"


def vertical(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    first_import = (
        with_comments(
            comments, imports.pop(0) + ",", removed=remove_comments, comment_prefix=comment_prefix
        )
        + line_separator
        + white_space
    )
    return "{}({}{}{})".format(
        statement,
        first_import,
        ("," + line_separator + white_space).join(imports),
        "," if include_trailing_comma else "",
    )


def hanging_indent(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    statement += imports.pop(0)
    while imports:
        next_import = imports.pop(0)
        next_statement = with_comments(
            comments,
            statement + ", " + next_import,
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        if len(next_statement.split(line_separator)[-1]) + 3 > line_length:
            next_statement = with_comments(
                comments,
                "{}, \\".format(statement),
                removed=remove_comments,
                comment_prefix=comment_prefix,
            ) + "{}{}{}".format(line_separator, indent, next_import)
            comments = []
        statement = next_statement
    return statement


def vertical_hanging_indent(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return "{0}({1}{2}{3}{4}{5}{2})".format(
        statement,
        with_comments(comments, "", removed=remove_comments, comment_prefix=comment_prefix),
        line_separator,
        indent,
        ("," + line_separator + indent).join(imports),
        "," if include_trailing_comma else "",
    )


def vertical_grid_common(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
    need_trailing_char: bool,
) -> str:
    if not imports:
        return ""

    statement += (
        with_comments(comments, "(", removed=remove_comments, comment_prefix=comment_prefix)
        + line_separator
        + indent
        + imports.pop(0)
    )
    while imports:
        next_import = imports.pop(0)
        next_statement = "{}, {}".format(statement, next_import)
        current_line_length = len(next_statement.split(line_separator)[-1])
        if imports or need_trailing_char:
            # If we have more imports we need to account for a comma after this import
            # We might also need to account for a closing ) we're going to add.
            current_line_length += 1
        if current_line_length > line_length:
            next_statement = "{},{}{}{}".format(statement, line_separator, indent, next_import)
        statement = next_statement
    if include_trailing_comma:
        statement += ","
    return statement


def vertical_grid(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return (
        vertical_grid_common(
            statement,
            imports,
            white_space,
            indent,
            line_length,
            comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
            need_trailing_char=True,
        )
        + ")"
    )


def vertical_grid_grouped(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return (
        vertical_grid_common(
            statement,
            imports,
            white_space,
            indent,
            line_length,
            comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
            need_trailing_char=True,
        )
        + line_separator
        + ")"
    )


def vertical_grid_grouped_no_comma(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return (
        vertical_grid_common(
            statement,
            imports,
            white_space,
            indent,
            line_length,
            comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
            need_trailing_char=False,
        )
        + line_separator
        + ")"
    )


def noqa(
    statement: str,
    imports: List[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: List[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    retval = "{}{}".format(statement, ", ".join(imports))
    comment_str = " ".join(comments)
    if comments:
        if len(retval) + len(comment_prefix) + 1 + len(comment_str) <= line_length:
            return "{}{} {}".format(retval, comment_prefix, comment_str)
    else:
        if len(retval) <= line_length:
            return retval
    if comments:
        if "NOQA" in comments:
            return "{}{} {}".format(retval, comment_prefix, comment_str)
        else:
            return "{}{} NOQA {}".format(retval, comment_prefix, comment_str)
    else:
        return "{}{} NOQA".format(retval, comment_prefix)


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
