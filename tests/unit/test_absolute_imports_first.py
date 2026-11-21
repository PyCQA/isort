import ast
from pathlib import Path

import pytest

import isort
from isort.main import main


@pytest.mark.parametrize("force_sort", [False, True])
@pytest.mark.parametrize("reverse_relative", [False, True])
def test_absolute_imports_first_issue_2146(force_sort: bool, reverse_relative: bool) -> None:
    code = "from ..foo import bar\nfrom .hoge import piyo\nfrom some_package.foo import baz\n"
    relative = ["from ..foo import bar\n", "from .hoge import piyo\n"]
    if reverse_relative:
        relative.reverse()
    expected = "from some_package.foo import baz\n" + "".join(relative)
    config = isort.Config(
        known_local_folder=["some_package"],
        absolute_imports_first=True,
        force_sort_within_sections=force_sort,
        reverse_relative=reverse_relative,
    )
    assert isort.code(code, config=config) == expected
    assert isort.code(expected, config=config) == expected
    assert sorted(ast.dump(node) for node in ast.parse(code).body) == sorted(
        ast.dump(node) for node in ast.parse(expected).body
    )


@pytest.mark.parametrize("force_sort", [False, True])
@pytest.mark.parametrize("length_sort", [False, True])
@pytest.mark.parametrize("reverse_sort", [False, True])
def test_absolute_imports_first_length_and_reverse(
    force_sort: bool, length_sort: bool, reverse_sort: bool
) -> None:
    absolute = "from some_very_long_package import item\n"
    relative = "from .a import other\n"
    expected = relative + absolute if reverse_sort else absolute + relative
    config = isort.Config(
        known_local_folder=["some_very_long_package"],
        absolute_imports_first=True,
        force_sort_within_sections=force_sort,
        length_sort=length_sort,
        reverse_sort=reverse_sort,
    )
    assert isort.code(relative + absolute, config=config) == expected
    assert isort.code(expected, config=config) == expected


@pytest.mark.parametrize("force_sort", [False, True])
def test_absolute_imports_first_comments_and_names(force_sort: bool) -> None:
    code = (
        "from ..relative import zebra, CamelCase, CONST  # relative\n"
        "# absolute module\n"
        "from package.module10 import value10\n"
        "from package.module2 import value2 as alias  # absolute\n"
    )
    expected = (
        "from package.module2 import value2 as alias  # absolute\n"
        "# absolute module\n"
        "from package.module10 import value10\n"
        "from ..relative import CONST, CamelCase, zebra  # relative\n"
    )
    config = isort.Config(
        known_local_folder=["package"],
        absolute_imports_first=True,
        force_sort_within_sections=force_sort,
    )
    assert isort.code(code, config=config) == expected
    assert isort.code(expected, config=config) == expected


def test_absolute_imports_first_preserves_style_grouping() -> None:
    code = "from .local import value\nfrom package import item\nimport package.extra\n"
    assert (
        isort.code(
            code,
            known_local_folder=["package"],
            absolute_imports_first=True,
            from_first=True,
            lines_between_types=1,
        )
        == "from package import item\nfrom .local import value\n\nimport package.extra\n"
    )


def test_absolute_imports_first_preserves_explicit_priorities() -> None:
    assert (
        isort.code(
            "from . import top\nfrom .local import value\nfrom package import item\n",
            known_local_folder=["package"],
            absolute_imports_first=True,
            force_sort_within_sections=True,
            force_to_top=["."],
        )
        == "from . import top\nfrom package import item\nfrom .local import value\n"
    )
    assert (
        isort.code(
            "from .local import *\nfrom package import item\n",
            known_local_folder=["package"],
            absolute_imports_first=True,
            star_first=True,
        )
        == "from .local import *\nfrom package import item\n"
    )


def test_absolute_imports_first_preserves_only_sections() -> None:
    code = "from .local import value\nfrom package import item\n"
    assert (
        isort.code(
            code,
            known_local_folder=["package"],
            absolute_imports_first=True,
            only_sections=True,
        )
        == code
    )


@pytest.mark.parametrize("force_sort", [False, True])
def test_absolute_imports_first_lazy_groups(force_sort: bool) -> None:
    code = (
        "lazy from .local import lazy_value\n"
        "from .local import value\n"
        "lazy from package import lazy_item\n"
        "from package import item\n"
    )
    expected = (
        "from package import item\n"
        "from .local import value\n"
        "lazy from package import lazy_item\n"
        "lazy from .local import lazy_value\n"
    )
    config = isort.Config(
        known_local_folder=["package"],
        absolute_imports_first=True,
        force_sort_within_sections=force_sort,
    )
    assert isort.code(code, config=config) == expected
    assert isort.code(expected, config=config) == expected


def test_absolute_imports_first_config_and_cli(tmp_path: Path) -> None:
    code = "from .local import value\nfrom package import item\n"
    expected = "from package import item\nfrom .local import value\n"
    settings = tmp_path / "pyproject.toml"
    settings.write_text(
        '[tool.isort]\nknown_local_folder = ["package"]\nabsolute_imports_first = true\n'
    )
    assert isort.code(code, settings_path=tmp_path) == expected
    settings.unlink()
    source = tmp_path / "example.py"
    source.write_text(code)
    main(["--absolute-imports-first", "--known-local-folder", "package", str(source)])
    assert source.read_text() == expected


def test_absolute_imports_first_default() -> None:
    code = "from .local import value\nfrom package import item\n"
    assert isort.code(code, known_local_folder=["package"]) == code
