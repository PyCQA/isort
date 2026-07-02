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
    with pytest.raises(
        ValueError, match=r"Trying to sort using an undefined sort_type. Defined"
    ):
        isort.literal.assignment("x = [1, 2, 3", "tuple-list-not-exist", "py")


def test_value_assignment_assignments():
    assert (
        isort.literal.assignment("b = 1\na = 2\n", "assignments", "py")
        == "a = 2\nb = 1\n"
    )


def test_tuple_sort_uses_black_profile_wrapping():
    code = (
        'data = ("therearesuperlong", "therearesuperlong", "therearesuperlong", '
        '"therearesuperlong", "therearesuperlong")\n'
    )
    assert (
        isort.literal.assignment(code, "tuple", "py", Config(profile="black"))
        == """data = (
    'therearesuperlong',
    'therearesuperlong',
    'therearesuperlong',
    'therearesuperlong',
    'therearesuperlong',
)
"""
    )


def test_code_tuple_sort_uses_black_profile_wrapping():
    code = (
        "# isort: tuple\n"
        'data = ("therearesuperlong", "therearesuperlong", "therearesuperlong", '
        '"therearesuperlong", "therearesuperlong")\n'
    )
    assert isort.code(code, profile="black") == (
        "# isort: tuple\n"
        "data = (\n"
        "    'therearesuperlong',\n"
        "    'therearesuperlong',\n"
        "    'therearesuperlong',\n"
        "    'therearesuperlong',\n"
        "    'therearesuperlong',\n"
        ")\n"
    )


def test_assignments_invalid_section():
    with pytest.raises(exceptions.AssignmentsFormatMismatch):
        isort.literal.assignment("\n\nx = 1\nx++", "assignments", "py")
