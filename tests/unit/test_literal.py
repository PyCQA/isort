import pytest

import isort
import isort.literal
from isort import exceptions
from isort.settings import Config


def test_value_mismatch():
    with pytest.raises(exceptions.LiteralSortTypeMismatch):
        isort.literal.assignment("x = [1, 2, 3]", "set", "py")


def test_invalid_syntax():
    with pytest.raises(exceptions.LiteralParsingFailure):
        isort.literal.assignment("x = [1, 2, 3", "list", "py")


def test_invalid_sort_type():
    with pytest.raises(ValueError, match=r"Trying to sort using an undefined sort_type. Defined"):
        isort.literal.assignment("x = [1, 2, 3", "tuple-list-not-exist", "py")


def test_value_assignment_assignments():
    assert isort.literal.assignment("b = 1\na = 2\n", "assignments", "py") == "a = 2\nb = 1\n"


def test_assignments_invalid_section():
    with pytest.raises(exceptions.AssignmentsFormatMismatch):
        isort.literal.assignment("\n\nx = 1\nx++", "assignments", "py")


def test_list_uses_double_quotes():
    assert isort.literal.assignment("x = ['b', 'a']", "list", "py") == 'x = ["a", "b"]'


def test_list_preserves_bracket_type_tuple():
    assert isort.literal.assignment("x = ('b', 'a')", "tuple", "py") == 'x = ("a", "b")'


def test_single_element_tuple_keeps_trailing_comma():
    assert isort.literal.assignment("x = ('a',)", "tuple", "py") == 'x = ("a",)'


def test_set_bracket_and_quotes():
    assert isort.literal.assignment("x = {'b', 'a'}", "set", "py") == 'x = {"a", "b"}'


def test_long_list_wraps_vertical_hanging_indent():
    code = (
        "__all__ = ['" + "', '".join(f"name_{i:02d}" for i in range(12)) + "']"
    )
    result = isort.literal.assignment(code, "list", "py", config=Config(profile="black"))
    expected = "__all__ = [\n" + "".join(
        f'    "name_{i:02d}",\n' for i in range(12)
    ) + "]"
    assert result == expected


def test_wrap_without_trailing_comma():
    code = "__all__ = ['" + "', '".join(f"name_{i:02d}" for i in range(12)) + "']"
    result = isort.literal.assignment(
        code, "list", "py", config=Config(line_length=20, include_trailing_comma=False)
    )
    assert result.endswith('"name_11"\n]')  # no trailing comma before the closing bracket


def test_quote_fallback_for_embedded_quote():
    # value containing a double quote but no single quote -> single quotes (black rule)
    assert isort.literal.assignment('x = [\'a"b\']', "list", "py") == "x = ['a\"b']"


def test_black_quote_prefers_double_quotes():
    assert isort.literal._black_quote("foo") == '"foo"'


def test_black_quote_uses_single_when_value_has_double_quote_only():
    assert isort.literal._black_quote('a"b') == "'a\"b'"


def test_black_quote_escapes_double_when_value_has_both_quotes():
    assert isort.literal._black_quote("a'b\"c") == '"a\'b\\"c"'


def test_black_quote_falls_back_to_repr_for_control_chars():
    assert isort.literal._black_quote("a\tb") == repr("a\tb")


def test_list_of_non_strings_uses_repr():
    assert isort.literal.assignment("x = [3, 1, 2]", "list", "py") == "x = [1, 2, 3]"


def test_unique_tuple_dedupes_and_sorts():
    assert isort.literal.assignment("x = ('b', 'a', 'a')", "unique-tuple", "py") == 'x = ("a", "b")'


def test_single_element_tuple_wraps_and_keeps_comma():
    long_name = "z" * 100
    result = isort.literal.assignment(f"x = ('{long_name}',)", "tuple", "py")
    assert result == f'x = (\n    "{long_name}",\n)'


def test_dict_sorts_by_value_with_double_quotes():
    # dict is now formatted config-aware too (no more pprint); sorted by value
    assert (
        isort.literal.assignment("x = {'a': 'z', 'b': 'y'}", "dict", "py")
        == 'x = {"b": "y", "a": "z"}'
    )


def test_dict_non_string_values_use_repr():
    assert (
        isort.literal.assignment("x = {'b': 2, 'a': 1}", "dict", "py") == 'x = {"a": 1, "b": 2}'
    )


def test_long_dict_wraps_vertical_hanging_indent():
    pairs = {f"key_{i:02d}": f"value_{i:02d}" for i in range(10)}
    code = "d = {" + ", ".join(f"'{k}': '{v}'" for k, v in pairs.items()) + "}"
    result = isort.literal.assignment(code, "dict", "py", config=Config(profile="black"))
    expected = "d = {\n" + "".join(
        f'    "key_{i:02d}": "value_{i:02d}",\n' for i in range(10)
    ) + "}"
    assert result == expected


def test_value_assignment_dict():
    assert (
        isort.literal.assignment("x = {3: 'c', 1: 'a', 2: 'b'}", "dict", "py")
        == 'x = {1: "a", 2: "b", 3: "c"}'
    )


def test_value_assignment_unique_tuple():
    assert (
        isort.literal.assignment("x = ('a', 'b', '1', '1')", "unique-tuple", "py")
        == 'x = ("1", "a", "b")'
    )
