import ast
from collections.abc import Callable
from pprint import PrettyPrinter
from typing import Any

from isort.exceptions import (
    AssignmentsFormatMismatch,
    LiteralParsingFailure,
    LiteralSortTypeMismatch,
)
from isort.settings import DEFAULT_CONFIG, Config


class ISortPrettyPrinter(PrettyPrinter):
    """an isort customized pretty printer for sorted literals"""

    def __init__(self, config: Config, prefix_length: int = 0):
        self.config = config
        self.available_width = (config.wrap_length or config.line_length) - prefix_length
        super().__init__(width=self.available_width, compact=True)


type_mapping: dict[str, tuple[type, Callable[[Any, ISortPrettyPrinter], str]]] = {}


def assignments(code: str) -> str:
    values = {}
    for line in code.splitlines(keepends=True):
        if not line.strip():
            continue
        if " = " not in line:
            raise AssignmentsFormatMismatch(code)
        variable_name, value = line.split(" = ", 1)
        values[variable_name] = value

    return "".join(
        f"{variable_name} = {values[variable_name]}" for variable_name in sorted(values.keys())
    )


def assignment(code: str, sort_type: str, extension: str, config: Config = DEFAULT_CONFIG) -> str:
    """Sorts the literal present within the provided code against the provided sort type,
    returning the sorted representation of the source code.
    """
    if sort_type == "assignments":
        return assignments(code)
    if sort_type not in type_mapping:
        raise ValueError(
            "Trying to sort using an undefined sort_type. "
            f"Defined sort types are {', '.join(type_mapping.keys())}."
        )

    variable_name, literal = code.split("=")
    variable_name = variable_name.strip()
    literal = literal.lstrip()
    try:
        value = ast.literal_eval(literal)
    except Exception as error:
        raise LiteralParsingFailure(code, error)

    expected_type, sort_function = type_mapping[sort_type]
    if type(value) is not expected_type:
        raise LiteralSortTypeMismatch(type(value), expected_type)

    printer = ISortPrettyPrinter(config, prefix_length=len(f"{variable_name} = "))
    sorted_value_code = f"{variable_name} = {sort_function(value, printer)}"
    if config.formatting_function:
        sorted_value_code = config.formatting_function(
            sorted_value_code, extension, config
        ).rstrip()

    sorted_value_code += code[len(code.rstrip()) :]
    return sorted_value_code


def register_type(
    name: str, kind: type
) -> Callable[[Callable[[Any, ISortPrettyPrinter], str]], Callable[[Any, ISortPrettyPrinter], str]]:
    """Registers a new literal sort type."""

    def wrap(
        function: Callable[[Any, ISortPrettyPrinter], str],
    ) -> Callable[[Any, ISortPrettyPrinter], str]:
        type_mapping[name] = (kind, function)
        return function

    return wrap


def _use_vertical_hanging_indent(printer: ISortPrettyPrinter) -> bool:
    return (
        printer.config.multi_line_output.name == "VERTICAL_HANGING_INDENT"
        and printer.config.use_parentheses
        and printer.config.include_trailing_comma
    )


def _format_items(
    items: list[Any],
    printer: ISortPrettyPrinter,
    opener: str,
    closer: str,
    force_tuple_comma: bool = False,
) -> str:
    rendered_items = [printer.pformat(item) for item in items]
    single_line = f"{opener}{', '.join(rendered_items)}{closer}"
    if force_tuple_comma and len(rendered_items) == 1:
        single_line = f"{opener}{rendered_items[0]},{closer}"

    if not rendered_items or not _use_vertical_hanging_indent(printer):
        return single_line

    if len(single_line) <= printer.available_width:
        return single_line

    indent = printer.config.indent
    lines = [opener]
    lines.extend(f"{indent}{item}," for item in rendered_items)
    lines.append(closer)
    return "\n".join(lines)


def _format_pairs(
    pairs: list[tuple[Any, Any]],
    printer: ISortPrettyPrinter,
    opener: str,
    closer: str,
) -> str:
    rendered_pairs = [f"{printer.pformat(key)}: {printer.pformat(value)}" for key, value in pairs]
    single_line = f"{opener}{', '.join(rendered_pairs)}{closer}"

    if not rendered_pairs or not _use_vertical_hanging_indent(printer):
        return single_line

    if len(single_line) <= printer.available_width:
        return single_line

    indent = printer.config.indent
    lines = [opener]
    lines.extend(f"{indent}{pair}," for pair in rendered_pairs)
    lines.append(closer)
    return "\n".join(lines)


@register_type("dict", dict)
def _dict(value: dict[Any, Any], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(value.items(), key=lambda item: item[1])
    if _use_vertical_hanging_indent(printer):
        return _format_pairs(sorted_items, printer, "{", "}")
    return printer.pformat(dict(sorted_items))


@register_type("list", list)
def _list(value: list[Any], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(value)
    if _use_vertical_hanging_indent(printer):
        return _format_items(sorted_items, printer, "[", "]")
    return printer.pformat(sorted_items)


@register_type("unique-list", list)
def _unique_list(value: list[Any], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(set(value))
    if _use_vertical_hanging_indent(printer):
        return _format_items(sorted_items, printer, "[", "]")
    return printer.pformat(sorted_items)


@register_type("set", set)
def _set(value: set[Any], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(value)
    if _use_vertical_hanging_indent(printer):
        return _format_items(sorted_items, printer, "{", "}")
    return "{" + printer.pformat(tuple(sorted_items))[1:-1] + "}"


@register_type("tuple", tuple)
def _tuple(value: tuple[Any, ...], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(value)
    if _use_vertical_hanging_indent(printer):
        return _format_items(sorted_items, printer, "(", ")", force_tuple_comma=True)
    return printer.pformat(tuple(sorted_items))


@register_type("unique-tuple", tuple)
def _unique_tuple(value: tuple[Any, ...], printer: ISortPrettyPrinter) -> str:
    sorted_items = sorted(set(value))
    if _use_vertical_hanging_indent(printer):
        return _format_items(sorted_items, printer, "(", ")", force_tuple_comma=True)
    return printer.pformat(tuple(sorted_items))
