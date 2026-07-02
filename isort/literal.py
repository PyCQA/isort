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
from isort.wrap_modes import WrapModes


class ISortPrettyPrinter(PrettyPrinter):
    """an isort customized pretty printer for sorted literals"""

    def __init__(self, config: Config):
        super().__init__(width=config.line_length, compact=True)


type_mapping: dict[str, tuple[type, Callable[[Any, PrettyPrinter], str]]] = {}


def _flat_printer() -> PrettyPrinter:
    return PrettyPrinter(width=1_000_000, compact=True)


def _literal_items(
    sort_type: str, value: Any, printer: PrettyPrinter
) -> tuple[str, str, list[str]]:
    if sort_type == "dict":
        return (
            "{",
            "}",
            [
                f"{printer.pformat(key)}: {printer.pformat(item_value)}"
                for key, item_value in sorted(value.items(), key=lambda item: item[1])
            ],
        )
    if sort_type in {"list", "unique-list"}:
        items = sorted(set(value)) if sort_type == "unique-list" else sorted(value)
        return "[", "]", [printer.pformat(item) for item in items]
    if sort_type == "set":
        return "{", "}", [printer.pformat(item) for item in sorted(value)]
    if sort_type in {"tuple", "unique-tuple"}:
        items = sorted(set(value)) if sort_type == "unique-tuple" else sorted(value)
        return "(", ")", [printer.pformat(item) for item in items]
    raise ValueError(
        "Trying to sort using an undefined sort_type. "
        f"Defined sort types are {', '.join(type_mapping.keys())}."
    )


def _vertical_assignment(
    variable_name: str, sort_type: str, value: Any, config: Config
) -> str:
    start, end, items = _literal_items(sort_type, value, _flat_printer())
    lines = [f"{variable_name} = {start}"]
    force_trailing_comma = config.include_trailing_comma or (
        sort_type == "tuple" and len(items) == 1
    )
    for index, item in enumerate(items):
        comma = "," if force_trailing_comma or index < len(items) - 1 else ""
        lines.append(f"{config.indent}{item}{comma}")

    lines.append(end)
    return "\n".join(lines)


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
        f"{variable_name} = {values[variable_name]}"
        for variable_name in sorted(values.keys())
    )


def assignment(
    code: str, sort_type: str, extension: str, config: Config = DEFAULT_CONFIG
) -> str:
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

    flat_printer = _flat_printer()
    flat_sorted_value_code = f"{variable_name} = {sort_function(value, flat_printer)}"
    if (
        len(flat_sorted_value_code) > (config.wrap_length or config.line_length)
        and config.use_parentheses
        and config.multi_line_output == WrapModes.VERTICAL_HANGING_INDENT  # type: ignore[attr-defined]
    ):
        sorted_value_code = _vertical_assignment(
            variable_name, sort_type, value, config
        )
    else:
        printer = ISortPrettyPrinter(config)
        sorted_value_code = f"{variable_name} = {sort_function(value, printer)}"

    if config.formatting_function:
        sorted_value_code = config.formatting_function(
            sorted_value_code, extension, config
        ).rstrip()

    sorted_value_code += code[len(code.rstrip()) :]
    return sorted_value_code


def register_type(
    name: str, kind: type
) -> Callable[
    [Callable[[Any, PrettyPrinter], str]], Callable[[Any, PrettyPrinter], str]
]:
    """Registers a new literal sort type."""

    def wrap(
        function: Callable[[Any, PrettyPrinter], str],
    ) -> Callable[[Any, PrettyPrinter], str]:
        type_mapping[name] = (kind, function)
        return function

    return wrap


@register_type("dict", dict)
def _dict(value: dict[Any, Any], printer: PrettyPrinter) -> str:
    return printer.pformat(dict(sorted(value.items(), key=lambda item: item[1])))


@register_type("list", list)
def _list(value: list[Any], printer: PrettyPrinter) -> str:
    return printer.pformat(sorted(value))


@register_type("unique-list", list)
def _unique_list(value: list[Any], printer: PrettyPrinter) -> str:
    return printer.pformat(sorted(set(value)))


@register_type("set", set)
def _set(value: set[Any], printer: PrettyPrinter) -> str:
    return "{" + printer.pformat(tuple(sorted(value)))[1:-1] + "}"


@register_type("tuple", tuple)
def _tuple(value: tuple[Any, ...], printer: PrettyPrinter) -> str:
    return printer.pformat(tuple(sorted(value)))


@register_type("unique-tuple", tuple)
def _unique_tuple(value: tuple[Any, ...], printer: PrettyPrinter) -> str:
    return printer.pformat(tuple(sorted(set(value))))
