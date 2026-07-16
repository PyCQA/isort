import ast
import re
from collections.abc import Callable
from typing import Any

from isort.exceptions import (
    AssignmentsFormatMismatch,
    LiteralParsingFailure,
    LiteralSortTypeMismatch,
)
from isort.settings import DEFAULT_CONFIG, Config

type_mapping: dict[str, tuple[type, Callable[[Any, Config, int, bool], str]]] = {}


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

    prefix_length = len(f"{variable_name} = ")
    has_trailing_comma = bool(re.search(r",\s*[\)\]\}]\s*$", literal))
    sorted_value_code = (
        f"{variable_name} = {sort_function(value, config, prefix_length, has_trailing_comma)}"
    )
    if config.formatting_function:
        sorted_value_code = config.formatting_function(
            sorted_value_code, extension, config
        ).rstrip()

    sorted_value_code += code[len(code.rstrip()) :]
    return sorted_value_code


def register_type(
    name: str, kind: type
) -> Callable[[Callable[[Any, Config, int, bool], str]], Callable[[Any, Config, int, bool], str]]:
    """Registers a new literal sort type."""

    def wrap(
        function: Callable[[Any, Config, int, bool], str],
    ) -> Callable[[Any, Config, int, bool], str]:
        type_mapping[name] = (kind, function)
        return function

    return wrap


def _black_quote(value: str) -> str:
    """Quote a string the way black does: prefer double quotes, fall back to single
    only when it avoids escaping. Values with backslashes or control characters defer
    to repr() so requoting can never produce invalid source.
    """
    if any(char in value for char in ("\\", "\n", "\r", "\t")):
        # deliberate: repr() sacrifices black-quote-normalization here to guarantee valid source
        return repr(value)
    if '"' in value and "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    return '"' + value.replace('"', '\\"') + '"'


def _repr_element(value: Any) -> str:
    """Render a single sorted element: strings via black's quote rule, everything else
    via repr() (so ints and other literals in ``# isort: list`` etc. keep working).
    """
    if isinstance(value, str):
        return _black_quote(value)
    return repr(value)


def _format_collection(
    elements: list[str],
    open_bracket: str,
    close_bracket: str,
    config: Config,
    prefix_length: int,
    single_element_comma: bool = False,
    trailing_comma: bool = False,
) -> str:
    """Render already-rendered, sorted ``elements`` as ``open ... close`` honoring the
    config: a single line when it fits within ``line_length`` (accounting for the
    ``prefix_length`` of the ``<name> = `` prefix), otherwise a vertical-hanging-indent
    block. ``single_element_comma`` forces the mandatory trailing comma that a
    one-element tuple needs to stay a tuple.
    """
    only_element_needs_comma = single_element_comma and len(elements) == 1
    force_multiline = trailing_comma and config.include_trailing_comma and len(elements) > 1
    inner = ", ".join(elements)
    if only_element_needs_comma:
        inner += ","
    single_line = f"{open_bracket}{inner}{close_bracket}"
    if not force_multiline and prefix_length + len(single_line) <= config.line_length:
        return single_line

    indent = config.indent
    trailing = "," if (config.include_trailing_comma or only_element_needs_comma) else ""
    body = (",\n" + indent).join(elements)
    return f"{open_bracket}\n{indent}{body}{trailing}\n{close_bracket}"


@register_type("dict", dict)
def _dict(value: dict[Any, Any], config: Config, prefix_length: int, trailing_comma: bool) -> str:
    items = [
        f"{_repr_element(key)}: {_repr_element(item)}"
        for key, item in sorted(value.items(), key=lambda item: item[1])
    ]
    return _format_collection(items, "{", "}", config, prefix_length, trailing_comma=trailing_comma)


@register_type("list", list)
def _list(value: list[Any], config: Config, prefix_length: int, trailing_comma: bool) -> str:
    elements = [_repr_element(item) for item in sorted(value)]
    return _format_collection(elements, "[", "]", config, prefix_length, trailing_comma=trailing_comma)


@register_type("unique-list", list)
def _unique_list(value: list[Any], config: Config, prefix_length: int, trailing_comma: bool) -> str:
    elements = [_repr_element(item) for item in sorted(set(value))]
    return _format_collection(elements, "[", "]", config, prefix_length, trailing_comma=trailing_comma)


@register_type("set", set)
def _set(value: set[Any], config: Config, prefix_length: int, trailing_comma: bool) -> str:
    elements = [_repr_element(item) for item in sorted(value)]
    return _format_collection(elements, "{", "}", config, prefix_length, trailing_comma=trailing_comma)


@register_type("tuple", tuple)
def _tuple(value: tuple[Any, ...], config: Config, prefix_length: int, trailing_comma: bool) -> str:
    elements = [_repr_element(item) for item in sorted(value)]
    return _format_collection(
        elements,
        "(",
        ")",
        config,
        prefix_length,
        single_element_comma=True,
        trailing_comma=trailing_comma,
    )


@register_type("unique-tuple", tuple)
def _unique_tuple(
    value: tuple[Any, ...], config: Config, prefix_length: int, trailing_comma: bool
) -> str:
    elements = [_repr_element(item) for item in sorted(set(value))]
    return _format_collection(
        elements,
        "(",
        ")",
        config,
        prefix_length,
        single_element_comma=True,
        trailing_comma=trailing_comma,
    )
