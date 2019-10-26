"""Defines all wrap modes that can be used when outputting formatted imports"""
import copy
import enum
import re
from inspect import signature
from typing import Any, Callable, Dict, List, Sequence

from . import settings
from .output import with_comments

_wrap_modes = {}


def from_string(value: str) -> "WrapModes":
    return getattr(WrapModes, str(value), None) or WrapModes(int(value))


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
        next_statement = with_comments(
            interface["comments"],
            interface["statement"] + ", " + next_import,
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        if (
            len(next_statement.split(interface["line_separator"])[-1]) + 1
            > interface["line_length"]
        ):
            lines = ["{}{}".format(interface["white_space"], next_import.split(" ")[0])]
            for part in next_import.split(" ")[1:]:
                new_line = "{} {}".format(lines[-1], part)
                if len(new_line) + 1 > interface["line_length"]:
                    lines.append("{}{}".format(interface["white_space"], part))
                else:
                    lines[-1] = new_line
            next_import = interface["line_separator"].join(lines)
            interface["statement"] = with_comments(
                interface["comments"],
                "{},".format(interface["statement"]),
                removed=interface["remove_comments"],
                comment_prefix=interface["comment_prefix"],
            ) + "{}{}".format(interface["line_separator"], next_import)
            interface["comments"] = []
        else:
            interface["statement"] += ", " + next_import
    return interface["statement"] + ("," if interface["include_trailing_comma"] else "") + ")"


@_wrap_mode
def vertical(**interface):
    if not interface["imports"]:
        return ""

    first_import = (
        with_comments(
            interface["comments"],
            interface["imports"].pop(0) + ",",
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        + interface["line_separator"]
        + interface["white_space"]
    )
    return "{}({}{}{})".format(
        interface["statement"],
        first_import,
        ("," + interface["line_separator"] + interface["white_space"]).join(interface["imports"]),
        "," if interface["include_trailing_comma"] else "",
    )


@_wrap_mode
def hanging_indent(**interface):
    if not interface["imports"]:
        return ""

    interface["statement"] += interface["imports"].pop(0)
    while interface["imports"]:
        next_import = interface["imports"].pop(0)
        next_statement = with_comments(
            interface["comments"],
            interface["statement"] + ", " + next_import,
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        )
        if (
            len(next_statement.split(interface["line_separator"])[-1]) + 3
            > interface["line_length"]
        ):
            next_statement = with_comments(
                interface["comments"],
                "{}, \\".format(interface["statement"]),
                removed=interface["remove_comments"],
                comment_prefix=interface["comment_prefix"],
            ) + "{}{}{}".format(interface["line_separator"], interface["indent"], next_import)
            interface["comments"] = []
        interface["statement"] = next_statement
    return interface["statement"]


@_wrap_mode
def vertical_hanging_indent(**interface):
    return "{0}({1}{2}{3}{4}{5}{2})".format(
        interface["statement"],
        with_comments(
            interface["comments"],
            "",
            removed=interface["remove_comments"],
            comment_prefix=interface["comment_prefix"],
        ),
        interface["line_separator"],
        interface["indent"],
        ("," + interface["line_separator"] + interface["indent"]).join(interface["imports"]),
        "," if interface["include_trailing_comma"] else "",
    )


def vertical_grid_common(need_trailing_char: bool, **interface):
    if not interface["imports"]:
        return ""

    interface["statement"] += (
        with_comments(
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
        next_statement = "{}, {}".format(interface["statement"], next_import)
        current_line_length = len(next_statement.split(interface["line_separator"])[-1])
        if interface["imports"] or need_trailing_char:
            # If we have more interface["imports"] we need to account for a comma after this import
            # We might also need to account for a closing ) we're going to add.
            current_line_length += 1
        if current_line_length > interface["line_length"]:
            next_statement = "{},{}{}{}".format(
                interface["statement"],
                interface["line_separator"],
                interface["indent"],
                next_import,
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
    retval = "{}{}".format(interface["statement"], ", ".join(interface["imports"]))
    comment_str = " ".join(interface["comments"])
    if interface["comments"]:
        if (
            len(retval) + len(interface["comment_prefix"]) + 1 + len(comment_str)
            <= interface["line_length"]
        ):
            return "{}{} {}".format(retval, interface["comment_prefix"], comment_str)
    else:
        if len(retval) <= interface["line_length"]:
            return retval
    if interface["comments"]:
        if "NOQA" in interface["comments"]:
            return "{}{} {}".format(retval, interface["comment_prefix"], comment_str)
        else:
            return "{}{} NOQA {}".format(retval, interface["comment_prefix"], comment_str)
    else:
        return "{}{} NOQA".format(retval, interface["comment_prefix"])


WrapModes = enum.Enum(  # type: ignore
    "WrapModes", {wrap_mode: index for index, wrap_mode in enumerate(_wrap_modes.keys())}
)


def wrap(
    import_start: str,
    from_imports: List[str],
    comments: Sequence[str],
    config: Dict[str, Any],
    line_separator: str,
) -> str:
    formatter = _wrap_modes.get(config["multi_line_output"].name.upper(), grid)
    dynamic_indent = " " * (len(import_start) + 1)
    indent = config["indent"]
    line_length = config["wrap_length"] or config["line_length"]
    import_statement = formatter(
        statement=import_start,
        imports=copy.copy(from_imports),
        white_space=dynamic_indent,
        indent=indent,
        line_length=line_length,
        comments=comments,
        line_separator=line_separator,
        comment_prefix=config["comment_prefix"],
        include_trailing_comma=config["include_trailing_comma"],
        remove_comments=config["ignore_comments"],
    )
    if config["balanced_wrapping"]:
        lines = import_statement.split(line_separator)
        line_count = len(lines)
        if len(lines) > 1:
            minimum_length = min(len(line) for line in lines[:-1])
        else:
            minimum_length = 0
        new_import_statement = import_statement
        while len(lines[-1]) < minimum_length and len(lines) == line_count and line_length > 10:
            import_statement = new_import_statement
            line_length -= 1
            new_import_statement = formatter(
                statement=import_start,
                imports=copy.copy(from_imports),
                white_space=dynamic_indent,
                indent=indent,
                line_length=line_length,
                comments=comments,
                line_separator=line_separator,
                comment_prefix=config["comment_prefix"],
                include_trailing_comma=config["include_trailing_comma"],
                remove_comments=config["ignore_comments"],
            )
            lines = new_import_statement.split(line_separator)
    if import_statement.count(line_separator) == 0:
        return wrap_line(import_statement, line_separator, config)
    return import_statement


def wrap_line(line: str, line_separator: str, config: Dict[str, Any]) -> str:
    """Returns a line wrapped to the specified line-length, if possible."""
    wrap_mode = config["multi_line_output"]
    if len(line) > config["line_length"] and wrap_mode != WrapModes.NOQA:  # type: ignore
        line_without_comment = line
        comment = None
        if "#" in line:
            line_without_comment, comment = line.split("#", 1)
        for splitter in ("import ", ".", "as "):
            exp = r"\b" + re.escape(splitter) + r"\b"
            if re.search(exp, line_without_comment) and not line_without_comment.strip().startswith(
                splitter
            ):
                line_parts = re.split(exp, line_without_comment)
                if comment:
                    line_parts[-1] = "{}{}  #{}".format(
                        line_parts[-1].strip(),
                        "," if config["include_trailing_comma"] else "",
                        comment,
                    )
                next_line = []
                while (len(line) + 2) > (
                    config["wrap_length"] or config["line_length"]
                ) and line_parts:
                    next_line.append(line_parts.pop())
                    line = splitter.join(line_parts)
                if not line:
                    line = next_line.pop()

                cont_line = wrap_line(
                    config["indent"] + splitter.join(next_line).lstrip(), line_separator, config
                )
                if config["use_parentheses"]:
                    if splitter == "as ":
                        output = "{}{}{}".format(line, splitter, cont_line.lstrip())
                    else:
                        output = "{}{}({}{}{}{})".format(
                            line,
                            splitter,
                            line_separator,
                            cont_line,
                            "," if config["include_trailing_comma"] and not comment else "",
                            line_separator
                            if wrap_mode
                            in {
                                WrapModes.VERTICAL_HANGING_INDENT,  # type: ignore
                                WrapModes.VERTICAL_GRID_GROUPED,  # type: ignore
                            }
                            else "",
                        )
                    lines = output.split(line_separator)
                    if config["comment_prefix"] in lines[-1] and lines[-1].endswith(")"):
                        line, comment = lines[-1].split(config["comment_prefix"], 1)
                        lines[-1] = line + ")" + config["comment_prefix"] + comment[:-1]
                    return line_separator.join(lines)
                return "{}{}\\{}{}".format(line, splitter, line_separator, cont_line)
    elif len(line) > config["line_length"] and wrap_mode == WrapModes.NOQA:  # type: ignore
        if "# NOQA" not in line:
            return "{}{} NOQA".format(line, config["comment_prefix"])

    return line
