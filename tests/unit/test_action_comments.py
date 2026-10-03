"""Tests for isort action comments, such as isort: skip"""

import pytest

import isort


def test_isort_off_and_on() -> None:
    """Test so ensure isort: off action comment and associated on action comment work together"""

    # as top of file comment
    assert (
        isort.code(
            """# isort: off
import a
import a

# isort: on
import a
import a
"""
        )
        == """# isort: off
import a
import a

# isort: on
import a
"""
    )
    # as middle comment
    assert (
        isort.code(
            """
import a
import a

# isort: off
import a
import a
"""
        )
        == """
import a

# isort: off
import a
import a
"""
    )


def test_skip_sort_reexports() -> None:
    code = """my_list = [\"bee\", \"Albatross\", \"Dinosaur\", \"cat\"]
__all__ = my_list  # isort: skip
"""

    assert isort.code(code, sort_reexports=True) == code


@pytest.mark.parametrize("float_to_top", [False, True])
@pytest.mark.parametrize("line_ending", ["\n", "\r\n"])
@pytest.mark.parametrize("import_prefix", ["import ", "from example import ", "from . import "])
def test_local_redundant_alias_preservation(
    float_to_top: bool, line_ending: str, import_prefix: str
) -> None:
    """Alias removal can be disabled locally without disabling import sorting."""
    source = (
        f"{import_prefix}before as before\n"
        "# isort: remove-redundant-aliases-off\n"
        f"{import_prefix}zebra as zebra\n"
        f"{import_prefix}apple as apple\n"
        "# isort: remove-redundant-aliases-on\n"
        f"{import_prefix}after as after\n"
    ).replace("\n", line_ending)
    expected = (
        f"{import_prefix}before\n\n"
        "# isort: remove-redundant-aliases-off\n"
        f"{import_prefix}apple as apple\n"
        f"{import_prefix}zebra as zebra\n\n"
        "# isort: remove-redundant-aliases-on\n"
        f"{import_prefix}after\n"
    ).replace("\n", line_ending)
    config = isort.Config(remove_redundant_aliases=True, float_to_top=float_to_top)
    result = isort.code(source, config=config)
    assert result == expected
    assert isort.code(result, config=config) == result
    assert config.remove_redundant_aliases


def test_local_alias_directives_restore_global_setting() -> None:
    source = (
        "# isort: remove-redundant-aliases-off\n"
        "import apple as apple\n\n"
        "# isort: remove-redundant-aliases-on\n"
        "import zebra as zebra\n"
    )
    for float_to_top in (False, True):
        assert isort.code(source, float_to_top=float_to_top) == source
        assert (
            isort.code(
                source.split("# isort: remove-redundant-aliases-on", 1)[0],
                remove_redundant_aliases=True,
                float_to_top=float_to_top,
            )
            == source.split("# isort: remove-redundant-aliases-on", 1)[0].rstrip() + "\n"
        )


def test_local_alias_directives_in_strings_and_disabled_sections() -> None:
    source = (
        '"""\n# isort: remove-redundant-aliases-off\n"""\n'
        "# isort: off\n"
        "# isort: remove-redundant-aliases-off\n"
        "import zebra as zebra\n"
        "# isort: on\n"
        "import apple as apple\n"
    )
    for float_to_top in (False, True):
        result = isort.code(source, remove_redundant_aliases=True, float_to_top=float_to_top)
        assert "import zebra as zebra" in result
        assert "import apple as apple" not in result
        assert "import apple" in result
        assert (
            isort.code(result, remove_redundant_aliases=True, float_to_top=float_to_top) == result
        )
