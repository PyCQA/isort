"""Length sorting must work with both natural and native ordering."""

import pytest

import isort
from isort import Config


@pytest.mark.parametrize("sort_order", ["natural", "native"])
@pytest.mark.parametrize("reverse_sort", [False, True])
@pytest.mark.parametrize("from_import", [False, True])
def test_length_sort_across_digit_boundaries(
    sort_order: str, reverse_sort: bool, from_import: bool
) -> None:
    names = ["z", "yy", "x" * 9, "w" * 10, "v" * 99, "u" * 100]
    lines = [f"from {name} import value\n" if from_import else f"import {name}\n" for name in names]
    source = "".join(reversed(lines))
    expected = "".join(reversed(lines) if reverse_sort else lines)
    config = Config(
        length_sort=True, sort_order=sort_order, reverse_sort=reverse_sort, line_length=1000
    )

    result = isort.code(source, config=config)
    assert result == expected
    assert isort.check_code(result, config=config)


@pytest.mark.parametrize("sort_order", ["natural", "native"])
@pytest.mark.parametrize("reverse_sort", [False, True])
def test_length_sort_imported_names(sort_order: str, reverse_sort: bool) -> None:
    names = ["z", "yy", "x" * 9, "w" * 10, "v" * 99, "u" * 100]
    source = f"from example import {', '.join(reversed(names))}\n"
    expected_names = list(reversed(names)) if reverse_sort else names
    config = Config(
        length_sort=True, sort_order=sort_order, reverse_sort=reverse_sort, line_length=1000
    )

    result = isort.code(source, config=config)
    assert result == f"from example import {', '.join(expected_names)}\n"
    assert isort.check_code(result, config=config)


@pytest.mark.parametrize("sort_order", ["natural", "native"])
def test_length_sort_straight_preserves_from_order(sort_order: str) -> None:
    source = "import aaaaaaaaaa\nimport z\nfrom z import z, aaaaaaaaaa\nfrom aaaaaaaaaa import x\n"
    config = Config(length_sort_straight=True, sort_order=sort_order)

    assert isort.code(source, config=config) == (
        "import z\nimport aaaaaaaaaa\nfrom aaaaaaaaaa import x\nfrom z import aaaaaaaaaa, z\n"
    )


@pytest.mark.parametrize("sort_order", ["natural", "native"])
def test_length_sort_sections_preserves_other_sections(sort_order: str) -> None:
    source = "import collections\nimport os\nimport aaaaaaaaaa\nimport z\n"
    config = Config(length_sort_sections=("stdlib",), sort_order=sort_order)

    assert isort.code(source, config=config) == (
        "import os\nimport collections\n\nimport aaaaaaaaaa\nimport z\n"
    )


@pytest.mark.parametrize("sort_order", ["natural", "native"])
@pytest.mark.parametrize("reverse_sort", [False, True])
def test_length_sort_within_sections(sort_order: str, reverse_sort: bool) -> None:
    lines = ["import z\n", "from z import a\n", "import aaaaaaaaaaa\n"]
    config = Config(
        length_sort=True,
        force_sort_within_sections=True,
        sort_order=sort_order,
        reverse_sort=reverse_sort,
    )

    result = isort.code("".join(reversed(lines)), config=config)
    assert result == "".join(reversed(lines) if reverse_sort else lines)
    assert isort.check_code(result, config=config)


@pytest.mark.parametrize(
    ("sort_order", "expected"),
    [("natural", "a2b, a12"), ("native", "a12, a2b")],
)
def test_length_sort_preserves_tie_breaking(sort_order: str, expected: str) -> None:
    assert (
        isort.code("from example import a12, a2b\n", length_sort=True, sort_order=sort_order)
        == f"from example import {expected}\n"
    )


@pytest.mark.parametrize("sort_order", ["natural", "native"])
def test_length_sort_preserves_type_and_force_to_top_order(sort_order: str) -> None:
    config = Config(
        length_sort=True, sort_order=sort_order, force_to_top=("priority_name",), line_length=1000
    )
    source = "from example import z, Aaaaaaaaaa, ZZ, AAAAAAAAAA, Z, aaaaaaaaaa, priority_name\n"

    assert isort.code(source, config=config) == (
        "from example import priority_name, ZZ, AAAAAAAAAA, Z, Aaaaaaaaaa, z, aaaaaaaaaa\n"
    )
