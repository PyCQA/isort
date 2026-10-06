import ast
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from isort.exceptions import (
    AssignmentsFormatMismatch,
    LiteralParsingFailure,
    LiteralSortTypeMismatch,
)
from isort.parse import _infer_line_separator
from isort.settings import DEFAULT_CONFIG, Config

type_mapping: dict[str, tuple[type, Callable[[Any, Config, int, bool, str], str]]] = {}


@dataclass(frozen=True, slots=True)
class _FString:
    source: str
    sort_key: str


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

    variable_name, literal = code.split("=", 1)
    variable_name = variable_name.strip()
    literal = literal.lstrip()
    try:
        parsed = ast.parse(literal, mode="eval")
        try:
            value = ast.literal_eval(parsed.body)
        except ValueError:
            value = _evaluate_collection_with_fstrings(parsed.body, literal)
    except Exception as error:
        raise LiteralParsingFailure(code, error)

    # Preserve anything that followed the literal (e.g. a trailing comment like
    # ``__all__ = ["b", "a"]  # exports``). The value node's end position marks
    # where the parsed literal stops, so everything after it is kept verbatim.
    end_lineno = parsed.body.end_lineno or 1
    end_col_offset = parsed.body.end_col_offset or 0
    lines = literal.splitlines(keepends=True)
    value_end = sum(len(line) for line in lines[: end_lineno - 1]) + end_col_offset
    preserve_trailing_comma = config.include_trailing_comma and _has_trailing_comma(
        literal[:value_end]
    )

    expected_type, sort_function = type_mapping[sort_type]
    if type(value) is not expected_type:
        raise LiteralSortTypeMismatch(type(value), expected_type)

    line_separator = _infer_line_separator(code, config.line_ending)

    prefix_length = len(f"{variable_name} = ")
    variable_value = sort_function(
        value, config, prefix_length, preserve_trailing_comma, line_separator
    )
    sorted_value_code = f"{variable_name} = {variable_value}"
    if config.formatting_function:
        sorted_value_code = config.formatting_function(
            sorted_value_code, extension, config
        ).rstrip()

    sorted_value_code += literal[value_end:]
    return sorted_value_code


def register_type(
    name: str, kind: type
) -> Callable[
    [Callable[[Any, Config, int, bool, str], str]], Callable[[Any, Config, int, bool, str], str]
]:
    """Registers a new literal sort type."""

    def wrap(
        function: Callable[[Any, Config, int, bool, str], str],
    ) -> Callable[[Any, Config, int, bool, str], str]:
        type_mapping[name] = (kind, function)
        return function

    return wrap


def _has_trailing_comma(literal: str) -> bool:
    """Return True when a bracketed source literal uses a final trailing comma."""
    literal = literal.rstrip()
    if "\n" not in literal or not literal:
        return False

    close_bracket = {"(": ")", "[": "]", "{": "}"}.get(literal[0])
    if close_bracket is None or not literal.endswith(close_bracket):
        return False

    return literal[:-1].rstrip().endswith(",")


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
    if isinstance(value, _FString):
        return value.source
    if isinstance(value, str):
        return _black_quote(value)
    return repr(value)


def _sort_key(value: Any) -> Any:
    if isinstance(value, _FString):
        return value.sort_key
    return value


def _fstring_sort_key(node: ast.JoinedStr, source: str) -> str:
    parts: list[str] = []
    for value in node.values:
        if isinstance(value, ast.Constant):
            if not isinstance(value.value, str):
                raise ValueError("unexpected non-string value in f-string")
            parts.append(value.value)
            continue
        if not isinstance(value, ast.FormattedValue):
            raise ValueError("unexpected value in f-string")

        expression = ast.get_source_segment(source, value.value) or ast.unparse(value.value)
        conversion = f"!{chr(value.conversion)}" if value.conversion >= 0 else ""
        if value.format_spec is not None and not isinstance(value.format_spec, ast.JoinedStr):
            raise ValueError("unexpected format specifier in f-string")
        format_spec = (
            f":{_fstring_sort_key(value.format_spec, source)}" if value.format_spec else ""
        )
        parts.append(f"{{{expression}{conversion}{format_spec}}}")
    return "".join(parts)


def _evaluate_collection_with_fstrings(node: ast.expr, source: str) -> Any:
    if isinstance(node, ast.List):
        collection_kind = "list"
    elif isinstance(node, ast.Set):
        collection_kind = "set"
    elif isinstance(node, ast.Tuple):
        collection_kind = "tuple"
    else:
        raise ValueError("f-strings are only supported in list, set, and tuple literals")

    values = []
    for element in node.elts:
        if isinstance(element, ast.JoinedStr):
            element_source = ast.get_source_segment(source, element)
            if element_source is None:
                raise ValueError("could not recover f-string source")
            values.append(_FString(element_source, _fstring_sort_key(element, source)))
        else:
            values.append(ast.literal_eval(element))
    if collection_kind == "list":
        return values
    if collection_kind == "set":
        return set(values)
    return tuple(values)


def _format_collection(
    elements: list[str],
    open_bracket: str,
    close_bracket: str,
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
    single_element_comma: bool = False,
) -> str:
    """Render already-rendered, sorted ``elements`` as ``open ... close`` honoring the
    config: a single line when it fits within ``line_length`` (accounting for the
    ``prefix_length`` of the ``<name> = `` prefix), otherwise a vertical-hanging-indent
    block. ``single_element_comma`` forces the mandatory trailing comma that a
    one-element tuple needs to stay a tuple.
    """
    only_element_needs_comma = single_element_comma and len(elements) == 1
    inner = ", ".join(elements)
    if only_element_needs_comma:
        inner += ","
    single_line = f"{open_bracket}{inner}{close_bracket}"
    if not preserve_trailing_comma and prefix_length + len(single_line) <= config.line_length:
        return single_line

    indent = config.indent
    trailing = (
        ","
        if (preserve_trailing_comma or config.include_trailing_comma or only_element_needs_comma)
        else ""
    )
    body = ("," + line_separator + indent).join(elements)
    return f"{open_bracket}{line_separator}{indent}{body}{trailing}{line_separator}{close_bracket}"


@register_type("dict", dict)
def _dict(
    value: dict[Any, Any],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    items = [
        f"{_repr_element(key)}: {_repr_element(item)}"
        for key, item in sorted(value.items(), key=lambda item: item[1])
    ]
    return _format_collection(
        items, "{", "}", config, prefix_length, preserve_trailing_comma, line_separator
    )


@register_type("list", list)
def _list(
    value: list[Any],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    elements = [_repr_element(item) for item in sorted(value, key=_sort_key)]
    return _format_collection(
        elements, "[", "]", config, prefix_length, preserve_trailing_comma, line_separator
    )


@register_type("unique-list", list)
def _unique_list(
    value: list[Any],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    elements = [_repr_element(item) for item in sorted(set(value), key=_sort_key)]
    return _format_collection(
        elements, "[", "]", config, prefix_length, preserve_trailing_comma, line_separator
    )


@register_type("set", set)
def _set(
    value: set[Any],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    elements = [_repr_element(item) for item in sorted(value, key=_sort_key)]
    return _format_collection(
        elements, "{", "}", config, prefix_length, preserve_trailing_comma, line_separator
    )


@register_type("tuple", tuple)
def _tuple(
    value: tuple[Any, ...],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    elements = [_repr_element(item) for item in sorted(value, key=_sort_key)]
    return _format_collection(
        elements,
        "(",
        ")",
        config,
        prefix_length,
        preserve_trailing_comma,
        line_separator,
        single_element_comma=True,
    )


@register_type("unique-tuple", tuple)
def _unique_tuple(
    value: tuple[Any, ...],
    config: Config,
    prefix_length: int,
    preserve_trailing_comma: bool,
    line_separator: str,
) -> str:
    elements = [_repr_element(item) for item in sorted(set(value))]
    return _format_collection(
        elements,
        "(",
        ")",
        config,
        prefix_length,
        preserve_trailing_comma,
        line_separator,
        single_element_comma=True,
    )
