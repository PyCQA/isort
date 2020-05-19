"""Defines all wrap modes that can be used when outputting formatted imports"""
import enum
from inspect import signature
from typing import Any, Callable, Dict, List

import isort.comments

_wrap_modes: Dict[str, Callable[[Any], str]] = {}


def from_string(value: str) -> "WrapModes":
    return getattr(WrapModes, str(value), None) or WrapModes(int(value))


def formatter_from_string(name: str):
    return _wrap_modes.get(name.upper(), grid)


def _wrap_mode_interface(
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
    """Defines the common interface used by all wrap mode functions"""
    return ""


def _wrap_mode(function):
    """Registers an individual wrap mode. Function name and order are significant and used for
       creating enum.
    """
    _wrap_modes[function.__name__.upper()] = function
    function.__signature__ = signature(_wrap_mode_interface)
    function.__annotations__ = _wrap_mode_interface.__annotations__
    return function


@_wrap_mode
def grid(**interface):
    if not interface["imports"]:
        return ""

    interface["statement"] += "(" + interface["imports"].pop(0)
    while interface["imports"]:
        next_import = interface["imports"].pop(0)
        next_statement = isort.comments.add_to_line(
            interface["comments"],
            interface["statement"] + ", " + next_import,
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        if (
            len(next_statement.split(interface["line_separator"])[-1]) + 1
            > interface["line_length"]
        ):
            lines = [f"{interface['white_space']}{next_import.split(' ')[0]}"]
            for part in next_import.split(" ")[1:]:
                new_line = f"{lines[-1]} {part}"
                if len(new_line) + 1 > interface["line_length"]:
                    lines.append(f"{interface['white_space']}{part}")
                else:
                    lines[-1] = new_line
            next_import = interface["line_separator"].join(lines)
            interface["statement"] = (
                isort.comments.add_to_line(
                    interface["comments"],
                    f"{interface['statement']},",
                    removed=interface["remove_comments"],
                    comment_prefix=interface["comment_prefix"],
                )
                + f"{interface['line_separator']}{next_import}"
            )
            interface["comments"] = []
        else:
            interface["statement"] += ", " + next_import
    return interface["statement"] + ("," if interface["include_trailing_comma"] else "") + ")"


@_wrap_mode
def vertical(**interface):
    if not interface["imports"]:
        return ""

    first_import = (
        isort.comments.add_to_line(
            interface["comments"],
            interface["imports"].pop(0) + ",",
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        + interface["line_separator"]
        + interface["white_space"]
    )

    _imports = ("," + interface["line_separator"] + interface["white_space"]).join(
        interface["imports"]
    )
    _comma_maybe = "," if interface["include_trailing_comma"] else ""
    return f"{interface['statement']}({first_import}{_imports}{_comma_maybe})"


@_wrap_mode
def hanging_indent(**interface):
    if not interface["imports"]:
        return ""
    next_import = interface["imports"].pop(0)
    next_statement = interface["statement"] + next_import
    # Check for first import
    if len(next_statement) + 3 > interface["line_length"]:
        next_statement = (
            isort.comments.add_to_line(
                interface["comments"],
                f"{interface['statement']}\\",
                removed=interface["remove_comments"],
                comment_prefix=interface["comment_prefix"],
            )
            + f"{interface['line_separator']}{interface['indent']}{next_import}"
        )
        interface["comments"] = []
    interface["statement"] = next_statement
    while interface["imports"]:
        next_import = interface["imports"].pop(0)
        next_statement = isort.comments.add_to_line(
            interface["comments"],
            interface["statement"] + ", " + next_import,
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        if (
            len(next_statement.split(interface["line_separator"])[-1]) + 3
            > interface["line_length"]
        ):
            next_statement = (
                isort.comments.add_to_line(
                    interface["comments"],
                    f"{interface['statement']}, \\",
                    removed=interface["remove_comments"],
                    comment_prefix=interface["comment_prefix"],
                )
                + f"{interface['line_separator']}{interface['indent']}{next_import}"
            )
            interface["comments"] = []
        interface["statement"] = next_statement
    return interface["statement"]


@_wrap_mode
def vertical_hanging_indent(**interface):
    _line_with_comments = isort.comments.add_to_line(
        interface["comments"],
        "",
        removed=interface["remove_comments"],
        comment_prefix=interface["comment_prefix"],
    )
    _imports = ("," + interface["line_separator"] + interface["indent"]).join(interface["imports"])
    _comma_maybe = "," if interface["include_trailing_comma"] else ""
    return (
        f"{interface['statement']}({_line_with_comments}{interface['line_separator']}"
        f"{interface['indent']}{_imports}{_comma_maybe}{interface['line_separator']})"
    )


def vertical_grid_common(need_trailing_char: bool, **interface):
    if not interface["imports"]:
        return ""

    interface["statement"] += (
        isort.comments.add_to_line(
            interface["comments"],
            "(",
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        + interface["line_separator"]
        + interface["indent"]
        + interface["imports"].pop(0)
    )
    while interface["imports"]:
        next_import = interface["imports"].pop(0)
        next_statement = f"{interface['statement']}, {next_import}"
        current_line_length = len(next_statement.split(interface["line_separator"])[-1])
        if interface["imports"] or need_trailing_char:
            # If we have more interface["imports"] we need to account for a comma after this import
            # We might also need to account for a closing ) we're going to add.
            current_line_length += 1
        if current_line_length > interface["line_length"]:
            next_statement = (
                f"{interface['statement']},{interface['line_separator']}"
                f"{interface['indent']}{next_import}"
            )
        interface["statement"] = next_statement
    if interface["include_trailing_comma"]:
        interface["statement"] += ","
    return interface["statement"]


@_wrap_mode
def vertical_grid(**interface) -> str:
    return (
        vertical_grid_common(
            statement=interface["statement"],
            imports=interface["imports"],
            white_space=interface["white_space"],
            indent=interface["indent"],
            line_length=interface["line_length"],
            comments=interface["comments"],
            line_separator=interface["line_separator"],
            comment_prefix=interface["comment_prefix"],
            include_trailing_comma=interface["include_trailing_comma"],
            remove_comments=interface["remove_comments"],
            need_trailing_char=True,
        )
        + ")"
    )


@_wrap_mode
def vertical_grid_grouped(**interface):
    return (
        vertical_grid_common(
            statement=interface["statement"],
            imports=interface["imports"],
            white_space=interface["white_space"],
            indent=interface["indent"],
            line_length=interface["line_length"],
            comments=interface["comments"],
            line_separator=interface["line_separator"],
            comment_prefix=interface["comment_prefix"],
            include_trailing_comma=interface["include_trailing_comma"],
            remove_comments=interface["remove_comments"],
            need_trailing_char=True,
        )
        + interface["line_separator"]
        + ")"
    )


@_wrap_mode
def vertical_grid_grouped_no_comma(**interface):
    return (
        vertical_grid_common(
            statement=interface["statement"],
            imports=interface["imports"],
            white_space=interface["white_space"],
            indent=interface["indent"],
            line_length=interface["line_length"],
            comments=interface["comments"],
            line_separator=interface["line_separator"],
            comment_prefix=interface["comment_prefix"],
            include_trailing_comma=interface["include_trailing_comma"],
            remove_comments=interface["remove_comments"],
            need_trailing_char=False,
        )
        + interface["line_separator"]
        + ")"
    )


@_wrap_mode
def noqa(**interface):
    _imports = ", ".join(interface["imports"])
    retval = f"{interface['statement']}{_imports}"
    comment_str = " ".join(interface["comments"])
    if interface["comments"]:
        if (
            len(retval) + len(interface["comment_prefix"]) + 1 + len(comment_str)
            <= interface["line_length"]
        ):
            return f"{retval}{interface['comment_prefix']} {comment_str}"
        elif "NOQA" in interface["comments"]:
            return f"{retval}{interface['comment_prefix']} {comment_str}"
        else:
            return f"{retval}{interface['comment_prefix']} NOQA {comment_str}"
    else:
        if len(retval) <= interface["line_length"]:
            return retval
        else:
            return f"{retval}{interface['comment_prefix']} NOQA"


@_wrap_mode
def vertical_hanging_indent_bracket(**interface):
    if not interface["imports"]:
        return ""
    statement = vertical_hanging_indent(**interface)
    return f'{statement[:-1]}{interface["indent"]})'


@_wrap_mode
def vertical_prefix_from_module_import(**interface):
    if not interface["imports"]:
        return ""
    prefix_statement = interface["statement"]
    interface["statement"] += interface["imports"].pop(0)
    while interface["imports"]:
        next_import = interface["imports"].pop(0)
        next_statement = isort.comments.add_to_line(
            interface["comments"],
            interface["statement"] + ", " + next_import,
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        if (
            len(next_statement.split(interface["line_separator"])[-1]) + 1
            > interface["line_length"]
        ):
            next_statement = (
                isort.comments.add_to_line(
                    interface["comments"],
                    f"{interface['statement']}",
                    removed=interface["remove_comments"],
                    comment_prefix=interface["comment_prefix"],
                )
                + f"{interface['line_separator']}{prefix_statement}{next_import}"
            )
            interface["comments"] = []
        interface["statement"] = next_statement
    return interface["statement"]


WrapModes = enum.Enum(  # type: ignore
    "WrapModes", {wrap_mode: index for index, wrap_mode in enumerate(_wrap_modes.keys())}
)
