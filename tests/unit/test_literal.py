import pytest

import isort.literal
from isort import exceptions


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


def test_value_assignment_dict():
    assert (
        isort.literal.assignment("x = {3: 'c', 1: 'a', 2: 'b'}", "dict", "py")
        == "x = {1: 'a', 2: 'b', 3: 'c'}"
    )


def test_value_assignment_unique_tuple():
    assert (
        isort.literal.assignment("x = ('a', 'b', '1', '1')", "unique-tuple", "py")
        == "x = ('1', 'a', 'b')"
    )
