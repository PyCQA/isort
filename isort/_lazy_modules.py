"""Find and sort static module-level lazy-module list declarations."""

import ast
import tokenize
from collections.abc import Iterator
from io import StringIO
from typing import NamedTuple

from . import literal, place, sorting
from .parse import _infer_line_separator
from .settings import Config


class Declaration(NamedTuple):
    end: int
    before: str
    after: str


def _statements(source: str) -> Iterator[list[tokenize.TokenInfo]]:
    indent = 0
    statement: list[tokenize.TokenInfo] = []
    for token in tokenize.generate_tokens(StringIO(source).readline):
        if token.type == tokenize.INDENT:
            indent += 1
        elif token.type == tokenize.DEDENT:
            indent -= 1
        elif indent:
            continue
        elif token.type == tokenize.NEWLINE:
            if statement:
                yield [*statement, token]
                statement = []
        elif token.type not in {tokenize.ENDMARKER, tokenize.ENCODING}:
            if statement or token.type not in {tokenize.COMMENT, tokenize.NL}:
                statement.append(token)


def _simple_statements(tokens: list[tokenize.TokenInfo]) -> Iterator[list[tokenize.TokenInfo]]:
    first = next(token for token in tokens if token.type not in {tokenize.COMMENT, tokenize.NL})
    if first.string in {
        "if",
        "elif",
        "else",
        "for",
        "while",
        "with",
        "try",
        "except",
        "finally",
        "def",
        "class",
        "async",
    }:
        return
    meaningful = [
        token
        for token in tokens
        if token.type not in {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
    ]
    if (
        first.string in {"match", "case", "cdef", "cpdef"}
        and len(meaningful) > 1
        and meaningful[1].string not in {"=", ":"}
    ):
        return

    depth = 0
    statement: list[tokenize.TokenInfo] = []
    for token in tokens:
        if token.type == tokenize.OP:
            if token.string in "([{":
                depth += 1
            elif token.string in ")]}":
                depth -= 1
            elif token.string == ";" and depth == 0:
                yield statement
                statement = []
                continue
        statement.append(token)
    if statement:
        yield statement


def _is_target(tokens: list[tokenize.TokenInfo]) -> bool:
    while len(tokens) > 2 and tokens[0].string == "(" and tokens[-1].string == ")":
        tokens = tokens[1:-1]
    return (
        len(tokens) == 1
        and tokens[0].type == tokenize.NAME
        and tokens[0].string == "__lazy_modules__"
    )


def _rhs(tokens: list[tokenize.TokenInfo]) -> list[tokenize.TokenInfo]:
    meaningful = [
        token
        for token in tokens
        if token.type not in {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
    ]
    depth = 0
    annotation: int | None = None
    for index, token in enumerate(meaningful):
        if token.type != tokenize.OP:
            continue
        if token.string in "([{":
            depth += 1
        elif token.string in ")]}":
            depth -= 1
        elif depth == 0:
            if token.string == ":" and annotation is None:
                annotation = index
            elif token.string == "=":
                target_end = index if annotation is None else annotation
                if not _is_target(meaningful[:target_end]) or (
                    annotation is not None and index == annotation + 1
                ):
                    return []
                return meaningful[index + 1 :]
    return []


def _sort_names(names: list[str], config: Config) -> list[str]:
    groups: dict[str, list[str]] = {}
    for name in names:
        section = place.module(name, config)
        if config.no_sections and section != "FUTURE":
            section = "no_sections"
        groups.setdefault(section, []).append(name)

    sections = (
        ("FUTURE", "no_sections")
        if config.no_sections
        else (*config.sections, *config.forced_separate)
    )
    ordered: list[str] = []
    for section in dict.fromkeys([*sections, *groups]):
        group = groups.get(section, [])
        if not config.only_sections:
            group = sorting.sort(
                config,
                group,
                key=lambda name: sorting.module_key(
                    name, config, section_name=section, straight_import=True
                ),
                reverse=config.reverse_sort,
            )
        ordered.extend(group)
    return ordered


def find_declarations(source: str, config: Config) -> dict[int, Declaration]:
    """Return replacements keyed by the original physical line's character offset."""
    offsets = [0]
    for line in StringIO(source):
        offsets.append(offsets[-1] + len(line))

    def offset(position: tuple[int, int]) -> int:
        row, column = position
        return offsets[row - 1] + column

    declarations: dict[int, Declaration] = {}
    try:
        for statement in _statements(source):
            start = offsets[statement[0].start[0] - 1]
            end = offsets[statement[-1].start[0]]
            before = source[start:end]
            replacements: list[tuple[int, int, str]] = []
            for tokens in _simple_statements(statement):
                rhs = _rhs(tokens)
                if not rhs:
                    continue
                rhs_start, rhs_end = offset(rhs[0].start), offset(rhs[-1].end)
                if any(
                    token.type == tokenize.COMMENT and rhs_start <= offset(token.start) < rhs_end
                    for token in tokens
                ):
                    continue
                value_source = source[rhs_start:rhs_end]
                try:
                    value = ast.parse(value_source, mode="eval").body
                except (SyntaxError, ValueError, UnicodeError):
                    continue
                if not isinstance(value, ast.List):
                    continue
                names = [
                    element.value
                    for element in value.elts
                    if isinstance(element, ast.Constant) and isinstance(element.value, str)
                ]
                if len(names) != len(value.elts):
                    continue
                ordered = _sort_names(names, config)
                if names == ordered:
                    continue
                replacement = literal._format_collection(
                    [
                        literal._repr_element(name) if name.isprintable() else repr(name)
                        for name in ordered
                    ],
                    "[",
                    "]",
                    config,
                    rhs[0].start[1],
                    config.include_trailing_comma and literal._has_trailing_comma(value_source),
                    _infer_line_separator(before, config.line_ending),
                )
                replacements.append((rhs_start - start, rhs_end - start, replacement))
            after = before
            for value_start, value_end, replacement in reversed(replacements):
                after = after[:value_start] + replacement + after[value_end:]
            if after != before:
                declarations[start] = Declaration(end, before, after)
    except (tokenize.TokenError, IndentationError):
        return {}
    return declarations
