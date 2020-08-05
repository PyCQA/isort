import pytest

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
    with pytest.raises(ValueError):
        isort.literal.assignment("x = [1, 2, 3", "tuple-list-not-exist", "py")


def test_value_assignment():
    assert isort.literal.assignment("x = ['b', 'a']", "list", "py") == "x = ['a', 'b']"
    assert (
        isort.literal.assignment("x = ['b', 'a']", "list", "py", Config(formatter="example"))
        == 'x = ["a", "b"]'
    )


def test_assignments_invalid_section():
    with pytest.raises(exceptions.AssignmentsFormatMismatch):
        isort.literal.assignment("x++", "assignments", "py")
