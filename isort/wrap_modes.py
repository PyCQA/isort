"""Defines all wrap modes that can be used when outputting formatted imports"""

import enum
from collections.abc import Callable, Sequence
from typing import Protocol

import isort.comments

_wrap_modes: dict[str, Callable[..., str]] = {}


def from_string(value: object) -> "WrapModes":
    value = str(value)
    return getattr(WrapModes, value, None) or WrapModes(int(value))


def formatter_from_string(name: str) -> Callable[..., str]:
    return _wrap_modes.get(name.upper(), grid)


class _Wrapper(Protocol):
    __name__: str

    def __call__(
        self,
        statement: str,
        imports: list[str],
        white_space: str,
        indent: str,
        line_length: int,
        comments: Sequence[str],
        line_separator: str,
        comment_prefix: str,
        include_trailing_comma: bool,
        remove_comments: bool,
    ) -> str: ...


def _wrap_mode(function: _Wrapper) -> _Wrapper:
    """Registers an individual wrap mode. Function name and order are significant."""
    _wrap_modes[function.__name__.upper()] = function
    return function


@_wrap_mode
def grid(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
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
        next_statement = isort.comments.add_to_line(
            comments,
            statement + ", " + next_import,
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        if len(next_statement.split(line_separator)[-1]) + 1 > line_length:
            lines = [f"{white_space}{next_import.split(' ')[0]}"]
            for part in next_import.split(" ")[1:]:
                new_line = f"{lines[-1]} {part}"
                if len(new_line) + 1 > line_length:
                    lines.append(f"{white_space}{part}")
                else:
                    lines[-1] = new_line
            next_import = line_separator.join(lines)
            statement = (
                isort.comments.add_to_line(
                    comments,
                    f"{statement},",
                    removed=remove_comments,
                    comment_prefix=comment_prefix,
                )
                + f"{line_separator}{next_import}"
            )
            comments = []
        else:
            statement += ", " + next_import
    return f"{statement}{',' if include_trailing_comma else ''})"


@_wrap_mode
def vertical(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    first_import = (
        isort.comments.add_to_line(
            comments,
            imports.pop(0) + ",",
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        + line_separator
        + white_space
    )

    _imports = ("," + line_separator + white_space).join(imports)
    _comma_maybe = "," if include_trailing_comma else ""
    return f"{statement}({first_import}{_imports}{_comma_maybe})"


def _hanging_indent_end_line(line: str) -> str:
    if not line.endswith(" "):
        line += " "
    return line + "\\"


def _add_syntax(statement: str, suffix: str, line_separator: str) -> str:
    # Appended after a trailing comment, punctuation is commented out instead of emitted.
    head, separator, last_line = statement.rpartition(line_separator)
    code, comment_start, comment = last_line.partition("#")
    if not comment_start:
        return statement + suffix
    spacing = code[len(code.rstrip()) :] or "  "
    return f"{head}{separator}{code.rstrip()}{suffix}{spacing}{comment_start}{comment}"


@_wrap_mode
def hanging_indent(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    line_length_limit = line_length - 3

    next_import = imports.pop(0)
    next_statement = statement + next_import
    # Check for first import
    if len(next_statement) > line_length_limit:
        next_statement = _hanging_indent_end_line(statement) + line_separator + indent + next_import

    statement = next_statement
    while imports:
        next_import = imports.pop(0)
        next_statement = statement + ", " + next_import
        if len(next_statement.split(line_separator)[-1]) > line_length_limit:
            next_statement = (
                _hanging_indent_end_line(statement + ",") + f"{line_separator}{indent}{next_import}"
            )
        statement = next_statement

    if comments:
        statement_with_comments = isort.comments.add_to_line(
            comments,
            statement,
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        if len(statement_with_comments.split(line_separator)[-1]) <= (line_length_limit + 2):
            return statement_with_comments
        return (
            _hanging_indent_end_line(statement)
            + line_separator
            + isort.comments.add_to_line(
                comments,
                indent,
                removed=remove_comments,
                comment_prefix=comment_prefix.lstrip(),
            )
        )
    return statement


@_wrap_mode
def vertical_hanging_indent(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    _line_with_comments = isort.comments.add_to_line(
        comments,
        "",
        removed=remove_comments,
        comment_prefix=comment_prefix,
    )
    _imports = ("," + line_separator + indent).join(imports)
    _comma_maybe = "," if include_trailing_comma else ""
    return (
        f"{statement}({_line_with_comments}{line_separator}"
        f"{indent}{_imports}{_comma_maybe}{line_separator})"
    )


def _vertical_grid_common(
    need_trailing_char: bool,
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    statement += (
        isort.comments.add_to_line(
            comments,
            "(",
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        + line_separator
        + indent
        + imports.pop(0)
    )
    while imports:
        next_import = imports.pop(0)
        next_statement = f"{statement}, {next_import}"
        current_line_length = len(next_statement.rsplit(line_separator, maxsplit=1)[-1])
        if imports or include_trailing_comma:
            # We need to account for a comma after this import.
            current_line_length += 1
        if not imports and need_trailing_char:
            # We need to account for a closing ) we're going to add.
            current_line_length += 1
        if current_line_length > line_length:
            next_statement = f"{statement},{line_separator}{indent}{next_import}"
        statement = next_statement
    if include_trailing_comma:
        statement += ","
    return statement


@_wrap_mode
def vertical_grid(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return (
        _vertical_grid_common(
            need_trailing_char=True,
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
        + ")"
    )


@_wrap_mode
def vertical_grid_grouped(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    return (
        _vertical_grid_common(
            need_trailing_char=False,
            statement=statement,
            imports=imports,
            white_space=white_space,
            indent=indent,
            line_length=line_length,
            comments=comments,
            line_separator=line_separator,
            comment_prefix=comment_prefix,
            include_trailing_comma=include_trailing_comma,
            remove_comments=remove_comments,
        )
        + line_separator
        + ")"
    )


@_wrap_mode
def vertical_grid_grouped_no_comma(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    # This is a deprecated alias for vertical_grid_grouped above. This function
    # needs to exist for backwards compatibility but should never get called.
    raise NotImplementedError


@_wrap_mode
def noqa(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    _imports = ", ".join(imports)
    retval = f"{statement}{_imports}"
    comment_str = " ".join(comments)
    if comments:
        if len(retval) + len(comment_prefix) + 1 + len(comment_str) <= line_length:
            return f"{retval}{comment_prefix} {comment_str}"
        if "NOQA" in comment_str.split():
            return f"{retval}{comment_prefix} {comment_str}"
        return f"{retval}{comment_prefix} NOQA {comment_str}"

    if len(retval) <= line_length:
        return retval
    return f"{retval}{comment_prefix} NOQA"


@_wrap_mode
def vertical_hanging_indent_bracket(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""
    statement = vertical_hanging_indent(
        statement=statement,
        imports=imports,
        white_space=white_space,
        indent=indent,
        line_length=line_length,
        comments=comments,
        line_separator=line_separator,
        comment_prefix=comment_prefix,
        include_trailing_comma=include_trailing_comma,
        remove_comments=remove_comments,
    )
    return f"{statement[:-1]}{indent})"


@_wrap_mode
def vertical_prefix_from_module_import(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    prefix_statement = statement
    output_statement = prefix_statement + imports.pop(0)

    statement = output_statement
    statement_with_comments = ""
    for next_import in imports:
        statement = statement + ", " + next_import
        statement_with_comments = isort.comments.add_to_line(
            comments,
            statement,
            removed=remove_comments,
            comment_prefix=comment_prefix,
        )
        if len(statement_with_comments.split(line_separator)[-1]) + 1 > line_length:
            statement = (
                isort.comments.add_to_line(
                    comments,
                    output_statement,
                    removed=remove_comments,
                    comment_prefix=comment_prefix,
                )
                + f"{line_separator}{prefix_statement}{next_import}"
            )
            comments = []
        output_statement = statement

    if comments and statement_with_comments:
        output_statement = statement_with_comments
    return output_statement


@_wrap_mode
def hanging_indent_with_parentheses(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    if not imports:
        return ""

    line_length_limit = line_length - 1

    statement += "("
    next_import = imports.pop(0)
    next_statement = statement + next_import
    # Check for first import
    if len(next_statement) > line_length_limit:
        next_statement = (
            isort.comments.add_to_line(
                comments,
                statement,
                removed=remove_comments,
                comment_prefix=comment_prefix,
            )
            + f"{line_separator}{indent}{next_import}"
        )
        comments = []
    statement = next_statement
    while imports:
        next_import = imports.pop(0)
        if (
            line_separator not in statement and "#" in statement
        ):  # pragma: no cover # TODO: fix, this is because of test run inconsistency.
            line, trailing_comments = statement.split("#", 1)
            next_statement = f"{line.rstrip()}, {next_import}{comment_prefix}{trailing_comments}"
        else:
            next_statement = isort.comments.add_to_line(
                comments,
                statement + ", " + next_import,
                removed=remove_comments,
                comment_prefix=comment_prefix,
            )
        current_line = next_statement.split(line_separator)[-1]
        if len(current_line) > line_length_limit:
            next_statement = (
                _add_syntax(
                    isort.comments.add_to_line(
                        comments,
                        statement,
                        removed=remove_comments,
                        comment_prefix=comment_prefix,
                    ),
                    ",",
                    line_separator,
                )
                + f"{line_separator}{indent}{next_import}"
            )
            comments = []
        statement = next_statement
    if include_trailing_comma:
        statement = _add_syntax(statement, ",", line_separator)
    return _add_syntax(statement, ")", line_separator)


@_wrap_mode
def backslash_grid(
    statement: str,
    imports: list[str],
    white_space: str,
    indent: str,
    line_length: int,
    comments: Sequence[str],
    line_separator: str,
    comment_prefix: str,
    include_trailing_comma: bool,
    remove_comments: bool,
) -> str:
    indent = white_space[:-1]
    return hanging_indent(
        statement=statement,
        imports=imports,
        white_space=white_space,
        indent=indent,
        line_length=line_length,
        comments=comments,
        line_separator=line_separator,
        comment_prefix=comment_prefix,
        include_trailing_comma=include_trailing_comma,
        remove_comments=remove_comments,
    )


class WrapModes(enum.IntEnum):
    GRID = 0
    VERTICAL = 1
    HANGING_INDENT = 2
    VERTICAL_HANGING_INDENT = 3
    VERTICAL_GRID = 4
    VERTICAL_GRID_GROUPED = 5
    VERTICAL_GRID_GROUPED_NO_COMMA = 6
    NOQA = 7
    VERTICAL_HANGING_INDENT_BRACKET = 8
    VERTICAL_PREFIX_FROM_MODULE_IMPORT = 9
    HANGING_INDENT_WITH_PARENTHESES = 10
    BACKSLASH_GRID = 11
