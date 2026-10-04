"""Tests configured ordering of static lazy-module declarations."""

import ast
import json
from io import StringIO, UnsupportedOperation
from typing import Any
from unittest.mock import patch

import pytest

import isort
from isort import api
from isort.exceptions import LiteralParsingFailure
from isort.main import main
from isort.settings import Config


def _config(**options: Any) -> Config:
    return Config(sort_lazy_modules=True, known_first_party=["mylocal"], **options)


def test_lazy_modules_follow_configured_sections() -> None:
    source = '__lazy_modules__ = ["requests", "os", "mylocal"]\n'
    expected = '__lazy_modules__ = ["os", "requests", "mylocal"]\n'

    assert (
        isort.code(source, config=Config(sort_lazy_modules=True, known_first_party=["mylocal"]))
        == expected
    )


def test_lazy_modules_remain_unchanged_by_default() -> None:
    source = '__lazy_modules__ = ["requests", "os", "mylocal"]\n'
    assert not Config().sort_lazy_modules
    assert isort.code(source) == source
    assert isort.code(source, config=Config(sort_reexports=True)) == source


def test_annotated_assignment_preserves_unicode_prefix_and_suffix() -> None:
    prefix = '__lazy_modules__ : Annotated[list[str], "\u03bb=module"] = '
    suffix = '  # selected modules\nsentinel = ["z", "a"]\n'
    source = prefix + '["requests", "os", "mylocal"]' + suffix
    expected = prefix + '[\n    "os",\n    "requests",\n    "mylocal"\n]' + suffix
    assert isort.code(source, config=_config()) == expected


def test_lazy_modules_do_not_match_other_assignment_scopes() -> None:
    sources = [
        'def f(__lazy_modules__=["requests", "os"]):\n    pass\n',
        'def f(\n__lazy_modules__=["requests", "os"]\n):\n    pass\n',
        'consume(\n__lazy_modules__=["requests", "os"],\n)\n',
        'if True: __lazy_modules__ = ["requests", "os"]\n',
        'if True: pass; __lazy_modules__ = ["requests", "os"]\n',
        'if True:\n    __lazy_modules__ = ["requests", "os"]\n',
        'class Example:\n    __lazy_modules__ = ["requests", "os"]\n',
        'def f():\n    __lazy_modules__ = ["requests", "os"]\n',
        'other = __lazy_modules__ = ["requests", "os"]\n',
        '__lazy_modules__ = other = ["requests", "os"]\n',
        '__lazy_modules__.value = ["requests", "os"]\n',
        '__lazy_modules__[0] = ["requests", "os"]\n',
        'match value:\n    case _: __lazy_modules__ = ["requests", "os"]\n',
    ]
    for source in sources:
        assert isort.code(source, config=_config()) == source


def test_declaration_ends_before_following_statements() -> None:
    source = (
        '__lazy_modules__ = [\n    "requests",\n    "os",\n]\n'
        'sentinel = ["z", "a"]\n'
        '__lazy_modules__ = ["requests", "os"]; untouched = ["z", "a"]\n'
    )
    expected = (
        '__lazy_modules__ = ["os", "requests"]\n'
        'sentinel = ["z", "a"]\n'
        '__lazy_modules__ = ["os", "requests"]; untouched = ["z", "a"]\n'
    )
    assert isort.code(source, config=_config()) == expected


def test_semicolon_prefix_and_parenthesized_target() -> None:
    source = 'match = 1; (__lazy_modules__) = ["requests", "os"]\n'
    expected = 'match = 1; (__lazy_modules__) = ["os", "requests"]\n'
    assert isort.code(source, config=_config()) == expected


def test_duplicates_are_retained() -> None:
    source = '__lazy_modules__ = ["requests", "os", "os", "requests"]\n'
    expected = '__lazy_modules__ = ["os", "os", "requests", "requests"]\n'
    assert isort.code(source, config=_config()) == expected


def test_empty_single_and_already_ordered_lists_preserve_source() -> None:
    for value in ("[]", "['os']", "['os', 'requests']"):
        source = f"__lazy_modules__ = {value}\n"
        assert isort.code(source, config=_config()) == source


def test_configured_module_order_within_sections() -> None:
    cases: list[tuple[list[str], dict[str, Any], list[str]]] = [
        (["pkg10", "pkg2", "pkg1"], {}, ["pkg1", "pkg2", "pkg10"]),
        (["pkg10", "pkg2", "pkg1"], {"sort_order": "native"}, ["pkg1", "pkg10", "pkg2"]),
        (["beta", "alpha", "Alpha"], {}, ["alpha", "Alpha", "beta"]),
        (["beta", "alpha", "Alpha"], {"case_sensitive": True}, ["Alpha", "alpha", "beta"]),
        (["pkg2", "pkg1", "pkg10"], {"force_to_top": ["pkg10"]}, ["pkg10", "pkg1", "pkg2"]),
        (["longname", "b", "aa"], {"length_sort_straight": True}, ["b", "aa", "longname"]),
    ]
    for names, options, expected in cases:
        source = f"__lazy_modules__ = {json.dumps(names)}\n"
        expected_source = f"__lazy_modules__ = {json.dumps(expected)}\n"
        assert isort.code(source, config=_config(**options)) == expected_source


def test_section_order_and_section_controls() -> None:
    cases: list[tuple[list[str], dict[str, Any], list[str]]] = [
        (["requests", "os", "mylocal"], {"no_sections": True}, ["mylocal", "os", "requests"]),
        (
            ["requests", "os", "mylocal"],
            {"sections": ["FIRSTPARTY", "THIRDPARTY", "STDLIB", "FUTURE", "LOCALFOLDER"]},
            ["mylocal", "requests", "os"],
        ),
        (
            ["requests", "os", "numpy", "mylocal", "abc"],
            {"only_sections": True},
            ["os", "abc", "requests", "numpy", "mylocal"],
        ),
        (
            ["numpy", "sys", "os", "requests", "mylocal"],
            {"reverse_sort": True},
            ["sys", "os", "requests", "numpy", "mylocal"],
        ),
    ]
    for names, options, expected in cases:
        source = f"__lazy_modules__ = {json.dumps(names)}\n"
        expected_source = f"__lazy_modules__ = {json.dumps(expected)}\n"
        assert isort.code(source, config=_config(**options)) == expected_source


def test_collection_formatting_and_declaration_tail_comment() -> None:
    source = '__lazy_modules__ = [\n    "requests",\n    "os",\n]  # modules\n'
    expected = '__lazy_modules__ = [\n    "os",\n    "requests",\n]  # modules\n'
    assert isort.code(source, config=_config(include_trailing_comma=True)) == expected


def test_lazy_module_assignment_uses_configured_formatter() -> None:
    calls: list[tuple[str, str, object]] = []

    def formatter(code: str, extension: str, config: object) -> str:
        calls.append((code, extension, config))
        return code.replace('"', "'") + "\n"

    config = _config(formatting_function=formatter)
    source = (
        'untouched = 1; __lazy_modules__: list[str] = ["requests", "os"]'
        '; sentinel = ["z", "a"]  # keep this comment\n'
    )
    expected = source.replace('["requests", "os"]', "['os', 'requests']")
    assert isort.code(source, extension="pyi", config=config) == expected
    assert calls == [('__lazy_modules__: list[str] = ["os", "requests"]', "pyi", config)]


def test_configured_formatter_is_not_called_for_ineligible_declarations() -> None:
    def formatter(code: str, extension: str, config: object) -> str:
        raise AssertionError("Ineligible declarations must not be formatted")

    sources = [
        '# isort: off\n__lazy_modules__ = ["requests", "os"]\n',
        '__lazy_modules__ = ["requests", "os"]  # isort: skip\n',
        '__lazy_modules__ = ["requests",  # element comment\n    "os"]\n',
        "__lazy_modules__ = choose_modules()\n",
        'def f():\n    __lazy_modules__ = ["requests", "os"]\n',
    ]
    for source in sources:
        assert isort.code(source, config=_config(formatting_function=formatter)) == source


def test_explicit_literal_directive_formats_once_with_existing_order() -> None:
    calls: list[str] = []

    def formatter(code: str, extension: str, config: object) -> str:
        calls.append(code)
        return code.replace('"', "'")

    source = '# isort: list\n__lazy_modules__ = ["requests", "os", "mylocal"]\n\n'
    expected = "# isort: list\n__lazy_modules__ = ['mylocal', 'os', 'requests']\n\n"
    assert isort.code(source, config=_config(formatting_function=formatter)) == expected
    assert calls == ['__lazy_modules__ = ["mylocal", "os", "requests"]']


def test_already_ordered_lists_still_apply_configured_formatter() -> None:
    def formatter(code: str, extension: str, config: object) -> str:
        return code.replace("'", '"')

    config = _config(formatting_function=formatter)
    source = "__lazy_modules__ = ['os', 'requests']\n"
    expected = '__lazy_modules__ = ["os", "requests"]\n'
    assert isort.code(source, config=config) == expected
    assert not isort.check_code(source, config=config)
    assert isort.check_code(expected, config=config)
    assert isort.code(expected, config=config) == expected


def test_formatters_visit_multiple_declarations_in_source_order() -> None:
    calls: list[str] = []

    def formatter(code: str, extension: str, config: object) -> str:
        calls.append(code)
        return code + "\n\n"

    source = (
        '__lazy_modules__ = ["requests", "os"]; '
        '__lazy_modules__ = ["mylocal", "os"]  # selected modules\r\n'
    )
    expected = source.replace('["requests", "os"]', '["os", "requests"]').replace(
        '["mylocal", "os"]', '["os", "mylocal"]'
    )
    assert isort.code(source, config=_config(formatting_function=formatter)) == expected
    assert calls == [
        '__lazy_modules__ = ["os", "requests"]',
        '__lazy_modules__ = ["os", "mylocal"]',
    ]


def test_configured_formatter_failures_propagate() -> None:
    def formatter(code: str, extension: str, config: object) -> str:
        raise ValueError("formatter failure")

    with pytest.raises(ValueError, match=r"^formatter failure$"):
        isort.code(
            '__lazy_modules__ = ["requests", "os"]\n',
            config=_config(formatting_function=formatter),
        )


def test_internal_comments_and_dynamic_values_preserve_existing_processing() -> None:
    declarations = [
        '__lazy_modules__ = ["requests",  # belongs to requests\n    "os"]\n',
        '__lazy_modules__ = [\n    "requests",\n    # belongs to os\n    "os",\n]\n',
        "__lazy_modules__ = select_modules()\n",
        '__lazy_modules__ = ["requests", "os"] + extra_modules\n',
        "__lazy_modules__ = [name for name in modules]\n",
        '__lazy_modules__ = ["requests", 1]\n',
        '__lazy_modules__ = {"requests", "os"}\n',
    ]
    imports = (
        "import z\nimport a\n# isort: off\nimport y\nimport b\n# isort: on\nimport d\nimport c\n"
    )
    for declaration in declarations:
        source = declaration + imports
        assert isort.code(source, config=_config()) == isort.code(source)


def test_off_on_and_per_declaration_skip_keep_existing_priority() -> None:
    source = (
        '# isort: off\n__lazy_modules__ = ["requests", "os"]\nimport z\nimport a\n'
        '# isort: on\n__lazy_modules__ = ["requests", "os"]\n'
        '__lazy_modules__ = ["requests", "os"]  # isort: skip\n'
    )
    expected = source.replace(
        '# isort: on\n__lazy_modules__ = ["requests", "os"]\n',
        '# isort: on\n__lazy_modules__ = ["os", "requests"]\n',
    )
    assert isort.code(source, config=_config()) == expected


def test_annotation_action_comments_are_left_to_existing_core() -> None:
    source = (
        "__lazy_modules__: (\n    # isort: off\n    list[str]\n"
        '    # isort: on\n) = ["requests", "os"]\nimport z\nimport a\n'
    )
    assert isort.code(source, config=_config()) == isort.code(source)


def test_annotation_import_addition_controls_keep_existing_processing() -> None:
    for directive in ("dont-add-imports", "dont-add-import: import sys"):
        source = (
            f"__lazy_modules__: (\n    # isort: {directive}\n    list[str]\n"
            ') = ["requests", "os"]\nimport requests\n'
        )
        options: dict[str, Any] = {"append_only": True, "add_imports": ["sys"]}
        expected = isort.code(source, config=Config(**options))
        assert "\nimport sys\n" not in expected
        assert isort.code(source, config=_config(**options)) == expected


def test_nonprintable_strings_remain_valid_literals() -> None:
    for name in ("\x00", "\x01", "\x0b", "\x0c", "\ud800"):
        names = ["z", name, "a"]
        source = f"__lazy_modules__ = {json.dumps(names)}\n"
        result = isort.code(source, config=_config(src_paths=[]))
        statement = ast.parse(result).body[0]
        assert isinstance(statement, ast.Assign)
        value = ast.literal_eval(statement.value)
        assert sorted(value) == sorted(names)
        assert isort.code(result, config=_config(src_paths=[])) == result


def test_closing_list_action_comment_keeps_existing_control_semantics() -> None:
    for directive in ("off", "on", "skip"):
        source = (
            '__lazy_modules__ = [\n    "requests",\n    "os",\n]'
            f"  # isort: {directive}\nimport z\nimport a\n"
        )
        expected_input = (
            source
            if directive == "skip"
            else source.replace('[\n    "requests",\n    "os",\n]', '["os", "requests"]')
        )
        assert isort.code(source, config=_config()) == isort.code(expected_input)


def test_explicit_literal_directive_uses_existing_alphabetical_order() -> None:
    source = '# isort: list\n__lazy_modules__ = ["requests", "os", "mylocal"]\n\n'
    expected = '# isort: list\n__lazy_modules__ = ["mylocal", "os", "requests"]\n\n'
    assert isort.code(source, config=_config()) == expected


def test_explicit_directive_keeps_its_existing_type_and_failure_semantics() -> None:
    source = '# isort: unique-list\n__lazy_modules__ = ["requests", "os", "os"]\n\n'
    expected = '# isort: unique-list\n__lazy_modules__ = ["os", "requests"]\n\n'
    assert isort.code(source, config=_config()) == expected
    try:
        isort.code("# isort: list\n__lazy_modules__ = select_modules()\n", config=_config())
    except LiteralParsingFailure:
        pass
    else:
        raise AssertionError("Explicit list directives must retain their parsing failures")


def test_float_to_top_preserves_lazy_declaration_processing() -> None:
    source = 'banner = 1\nimport z\nimport a\n__lazy_modules__ = ["requests", "os"]\n'
    expected = isort.code(source, config=Config(float_to_top=True)).replace(
        '["requests", "os"]', '["os", "requests"]'
    )
    assert isort.code(source, config=_config(float_to_top=True)) == expected


def test_nonseekable_input_and_check_report_list_only_changes() -> None:
    class Nonseekable(StringIO):
        def seek(self, offset: int, whence: int = 0) -> int:
            raise UnsupportedOperation("nonseekable input")

        def tell(self) -> int:
            raise UnsupportedOperation("nonseekable input")

    source = '__lazy_modules__ = ["requests", "os"]\n'
    expected = '__lazy_modules__ = ["os", "requests"]\n'
    output = StringIO()
    assert api.sort_stream(Nonseekable(source), output, config=_config())
    assert output.getvalue() == expected
    assert not isort.check_code(source, config=_config())
    assert isort.check_code(expected, config=_config())
    assert isort.code(expected, config=_config()) == expected


def test_eof_crlf_and_unicode_line_separator_preserve_offsets() -> None:
    sources = [
        '__lazy_modules__ = ["requests", "os"]',
        '__lazy_modules__ = [\r\n    "requests",\r\n    "os",\r\n]\r\n',
        'metadata = "\u2028"\n__lazy_modules__ = ["requests", "os"]\n',
    ]
    expected = [
        '__lazy_modules__ = ["os", "requests"]',
        '__lazy_modules__ = ["os", "requests"]\r\n',
        'metadata = "\u2028"\n__lazy_modules__ = ["os", "requests"]\n',
    ]
    for source, result in zip(sources, expected, strict=True):
        assert isort.code(source, config=_config()) == result
        assert isort.code(result, config=_config()) == result


def test_unrelated_new_python_syntax_does_not_require_whole_module_ast() -> None:
    source = 'lazy import os\n\ntype Modules = list[str]\n__lazy_modules__ = ["requests", "os"]\n'
    expected = source.replace('["requests", "os"]', '["os", "requests"]')
    assert isort.code(source, config=_config(py_version="315")) == expected


def test_cli_flag_sorts_stdin() -> None:
    source = '__lazy_modules__ = ["requests", "os"]\n'
    output = StringIO()
    with patch("sys.stdin", StringIO(source)), patch("sys.stdout", output):
        main(["--sort-lazy-modules", "-"])
    assert output.getvalue() == '__lazy_modules__ = ["os", "requests"]\n'
