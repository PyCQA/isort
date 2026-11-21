import ast
from pathlib import Path

import pytest

import isort
from isort import main
from isort.settings import Config
from isort.wrap_modes import WrapModes

MODULE = "package.subpackage.component.another_component.final_module"


def assert_valid_and_stable(source: str, config: Config) -> str:
    output = isort.code(source, config=config)
    default_output = isort.code(source, config=Config(config=config, wrap_long_from_imports=False))
    assert ast.dump(ast.parse(output)) == ast.dump(ast.parse(default_output))
    assert isort.code(output, config=config) == output
    return output


def test_long_from_import_issue_1531() -> None:
    source = (
        "from monkey_island.cc.services.zero_trust.scoutsuite.data_parsing."
        "rule_path_building.rule_path_creators.vpc_rule_path_creator import \\\n"
        "    VPCRulePathCreator\n"
    )
    assert isort.code(source, line_length=120) == source

    output = assert_valid_and_stable(source, Config(line_length=120, wrap_long_from_imports=True))
    assert max(map(len, output.splitlines())) <= 120
    assert ".\\\n" in output


@pytest.mark.parametrize("mode", [mode for mode in WrapModes if mode is not WrapModes.NOQA])
def test_long_from_import_wrap_modes(mode: WrapModes) -> None:
    source = f"from {MODULE} import alpha, beta, gamma\n"
    output = assert_valid_and_stable(
        source, Config(line_length=40, multi_line_output=mode, wrap_long_from_imports=True)
    )
    assert ".\\\n" in output
    assert max(map(len, output.splitlines())) <= 40


@pytest.mark.parametrize("use_parentheses", [False, True])
@pytest.mark.parametrize(
    "imported",
    [
        "alpha",
        "alpha as alias",
        "alpha  # comment",
        "alpha as alias  # noqa: F401",
        "*",
        "*  # star comment",
        "*  # noqa: F403",
        "*  # type: ignore",
    ],
)
def test_long_from_import_comments_and_aliases(imported: str, use_parentheses: bool) -> None:
    source = f"from {MODULE} import {imported}\n"
    output = assert_valid_and_stable(
        source,
        Config(
            line_length=40,
            use_parentheses=use_parentheses,
            wrap_long_from_imports=True,
        ),
    )
    assert ".\\\n" in output
    assert output.count("#") == source.count("#")
    assert all(not line.rstrip().endswith("\\") or "#" not in line for line in output.splitlines())


def test_long_from_import_relative_and_indented() -> None:
    source = f"def function():\n    from ...{MODULE} import alpha\n"
    output = assert_valid_and_stable(source, Config(line_length=40, wrap_long_from_imports=True))
    assert "from ...package." in output
    assert ".\\\n        " in output
    assert max(map(len, output.splitlines())) <= 40


def test_long_from_import_wrap_length_and_line_ending() -> None:
    source = f"from {MODULE} import alpha, beta\r\n"
    output = assert_valid_and_stable(
        source,
        Config(line_length=50, wrap_length=35, wrap_long_from_imports=True),
    )
    assert ".\\\r\n" in output
    assert max(map(len, output.splitlines())) <= 35


@pytest.mark.parametrize(
    "source",
    ["from short.module import alpha\n", f"from {'x' * 80} import alpha\n"],
)
def test_long_from_import_unneeded_or_unbreakable(source: str) -> None:
    config = Config(line_length=40, wrap_long_from_imports=True)
    output = assert_valid_and_stable(source, config)
    assert output == isort.code(source, line_length=40)


def test_long_from_import_noqa_mode() -> None:
    source = f"from {MODULE} import alpha\n"
    output = assert_valid_and_stable(
        source,
        Config(line_length=40, multi_line_output=WrapModes.NOQA, wrap_long_from_imports=True),
    )
    assert output == isort.code(source, line_length=40, multi_line_output=WrapModes.NOQA)


def test_long_from_import_cli(tmp_path: Path) -> None:
    source = f"from {MODULE} import alpha\n"
    source_file = tmp_path / "module.py"
    source_file.write_text(source)
    args = [str(source_file), "--line-length", "40", "--wrap-long-from-imports"]

    main.main(args)
    output = source_file.read_text()
    assert ".\\\n" in output
    assert ast.dump(ast.parse(output)) == ast.dump(ast.parse(source))
    main.main([*args, "--check-only"])
    assert source_file.read_text() == output


def test_long_from_import_config_file(tmp_path: Path) -> None:
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("[tool.isort]\nline_length = 40\nwrap_long_from_imports = true\n")
    config = Config(settings_file=str(config_file))
    assert config.wrap_long_from_imports
    output = assert_valid_and_stable(f"from {MODULE} import alpha\n", config)
    assert ".\\\n" in output


@pytest.mark.parametrize(("prefix", "keyword"), [("lazy from", "import"), ("from", "cimport")])
def test_long_from_import_other_syntax(prefix: str, keyword: str) -> None:
    # The running interpreter need not support lazy imports or Cython syntax.
    source = f"{prefix} {MODULE} {keyword} alpha\n"
    config = Config(line_length=40, wrap_long_from_imports=True)
    output = isort.code(source, config=config)
    assert ".\\\n" in output
    assert isort.code(output, config=config) == output
    assert isort.code(output) == isort.code(source)


def test_long_from_import_long_component() -> None:
    source = f"from {'x' * 80}.package.module import alpha\n"
    output = assert_valid_and_stable(source, Config(line_length=40, wrap_long_from_imports=True))
    assert f"from {'x' * 80}.\\\n" in output
    assert "package.module import" in output
