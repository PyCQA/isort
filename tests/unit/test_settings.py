import os
import sys
from pathlib import Path

import pytest

from isort import code, exceptions, place_module, settings
from isort.settings import Config
from isort.wrap_modes import WrapModes


class TestConfig:
    instance = Config()

    def test_init(self) -> None:
        assert Config()

    def test_init_unsupported_settings_fails_gracefully(self) -> None:
        with pytest.raises(exceptions.UnsupportedSettings):
            Config(apply=True)
        with pytest.raises(exceptions.UnsupportedSettings) as error:
            Config(apply=True)
        assert error.value.unsupported_settings == {"apply": {"value": True, "source": "runtime"}}

    def test_known_settings(self) -> None:
        assert Config(known_third_party=["one"]).known_third_party == frozenset({"one"})
        assert Config(known_thirdparty=["two"]).known_third_party == frozenset({"two"})
        assert Config(
            known_third_party=["one"], known_thirdparty=["two"]
        ).known_third_party == frozenset({"one"})

    def test_invalid_settings_path(self) -> None:
        with pytest.raises(exceptions.InvalidSettingsPath):
            Config(settings_path="this_couldnt_possibly_actually_exists/could_it")

    def test_invalid_pyversion(self) -> None:
        with pytest.raises(ValueError, match=r"The python version 10 is not supported."):
            Config(py_version=10)

    def test_invalid_profile(self) -> None:
        with pytest.raises(exceptions.ProfileDoesNotExist):
            Config(profile="blackandwhitestylemixedwithpep8")

    def test_is_skipped(self) -> None:
        assert Config().is_skipped(Path("C:\\path\\isort.py"))
        assert Config(skip=["/path/isort.py"]).is_skipped(Path("C:\\path\\isort.py"))

    def test_is_supported_filetype(self) -> None:
        assert self.instance.is_supported_filetype("file.py")
        assert self.instance.is_supported_filetype("file.pyi")
        assert self.instance.is_supported_filetype("file.pyx")
        assert self.instance.is_supported_filetype("file.pxd")
        assert not self.instance.is_supported_filetype("file.pyc")
        assert not self.instance.is_supported_filetype("file.txt")
        assert not self.instance.is_supported_filetype("file.pex")

    def test_is_supported_filetype_ioerror(self, tmp_path: Path) -> None:
        does_not_exist = tmp_path / "fake.txt"
        assert not self.instance.is_supported_filetype(str(does_not_exist))

    def test_is_supported_filetype_shebang(self, tmp_path: Path) -> None:
        path = tmp_path / "myscript"
        path.write_text("#!/usr/bin/env python\n")
        assert self.instance.is_supported_filetype(str(path))

    def test_is_supported_filetype_editor_backup(self, tmp_path: Path) -> None:
        path = tmp_path / "myscript~"
        path.write_text("#!/usr/bin/env python\n")
        assert not self.instance.is_supported_filetype(str(path))

    def test_is_supported_filetype_defaults(self, tmp_path: Path) -> None:
        assert self.instance.is_supported_filetype(str(tmp_path / "stub.pyi"))
        assert self.instance.is_supported_filetype(str(tmp_path / "source.py"))
        assert self.instance.is_supported_filetype(str(tmp_path / "source.pyx"))

    def test_is_supported_filetype_configuration(self, tmp_path: Path) -> None:
        config = Config(supported_extensions=("pyx",), blocked_extensions=("py",))
        assert config.is_supported_filetype(str(tmp_path / "stub.pyx"))
        assert not config.is_supported_filetype(str(tmp_path / "stub.py"))

    @pytest.mark.skipif(
        sys.platform == "win32", reason="cannot create fifo file on Windows platform"
    )
    def test_is_supported_filetype_fifo(self, tmp_path: Path) -> None:
        fifo_file = str(tmp_path / "fifo_file")
        os.mkfifo(fifo_file)
        assert not self.instance.is_supported_filetype(fifo_file)

    def test_src_paths_are_combined_and_deduplicated(self) -> None:
        src_paths = ["src", "tests"]
        src_full_paths = (Path(os.getcwd()) / f for f in src_paths)
        assert sorted(Config(src_paths=src_paths * 2).src_paths) == sorted(src_full_paths)

    def test_src_paths_supports_glob_expansion(self, tmp_path: Path) -> None:
        libs = tmp_path / "libs"
        libs.mkdir()
        requests = libs / "requests"
        requests.mkdir()
        beautifulpasta = libs / "beautifulpasta"
        beautifulpasta.mkdir()
        assert sorted(Config(directory=tmp_path, src_paths=["libs/*"]).src_paths) == sorted(
            (beautifulpasta, requests)
        )

    def test_deprecated_multi_line_output(self) -> None:
        assert Config(multi_line_output=6).multi_line_output == WrapModes.VERTICAL_GRID_GROUPED  # noqa


def test_as_list() -> None:
    assert settings._as_list([" one "]) == ["one"]
    assert settings._as_list("one,two") == ["one", "two"]


def _write_simple_settings(tmp_file: Path) -> None:
    tmp_file.write_text(
        """
[isort]
force_grid_wrap=true
""",
        "utf8",
    )


def test_find_config(tmp_path: Path) -> None:
    tmp_config = tmp_path / ".isort.cfg"

    # can't find config if it has no relevant section
    tmp_config.write_text(
        """
[section]
force_grid_wrap=true
""",
        "utf8",
    )
    assert not settings._find_config(str(tmp_path))[1]

    # or if it is malformed
    tmp_config.write_text("""arstoyrsyan arienrsaeinrastyngpuywnlguyn354q^%$)(%_)@$""", "utf8")
    assert not settings._find_config(str(tmp_path))[1]

    # can when it has either a file format, or generic relevant section
    _write_simple_settings(tmp_config)
    assert settings._find_config(str(tmp_path))[1]


def test_find_config_deep(tmp_path: Path) -> None:
    # can't find config if it is further up than MAX_CONFIG_SEARCH_DEPTH
    dirs = [f"dir{i}" for i in range(settings.MAX_CONFIG_SEARCH_DEPTH + 1)]
    tmp_dirs = tmp_path.joinpath(*dirs)
    tmp_dirs.mkdir(parents=True)
    tmp_config = tmp_path / "dir0" / ".isort.cfg"
    _write_simple_settings(tmp_config)
    assert not settings._find_config(str(tmp_dirs))[1]
    # but can find config if it is MAX_CONFIG_SEARCH_DEPTH up
    one_parent_up = os.path.split(str(tmp_dirs))[0]
    assert settings._find_config(one_parent_up)[1]


@pytest.mark.parametrize(
    ("marker", "is_directory", "is_repository"),
    [
        (".git", True, True),
        (".git", False, True),
        (".hg", True, True),
        (".hg", False, False),
        (None, False, False),
    ],
)
def test_find_config_stops_at_repository_boundary(
    tmp_path: Path, marker: str | None, is_directory: bool, is_repository: bool
) -> None:
    outer_config = tmp_path / ".isort.cfg"
    _write_simple_settings(outer_config)
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    if is_directory and marker is not None:
        (project / marker).mkdir()
    elif marker:
        (project / marker).write_text("gitdir: ../main/.git/worktrees/project\n", encoding="utf8")

    root, config = settings._find_config(str(nested))
    if is_repository:
        assert root == str(project)
        assert config == {}
    else:
        assert root == str(tmp_path)
        assert config["source"] == str(outer_config)


@pytest.mark.parametrize("config_location", ["outer", "project", "nested"])
def test_find_config_in_git_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config_location: str
) -> None:
    outer_config = tmp_path / ".isort.cfg"
    outer_config.write_text("[settings]\nline_length = 42\n", encoding="utf8")
    project = tmp_path / "project"
    nested = project / "nested"
    nested.mkdir(parents=True)
    (project / ".git").write_text("gitdir: ../main/.git/worktrees/project\n", encoding="utf8")
    (project / "local_module.py").touch()
    monkeypatch.chdir(project)

    if config_location != "outer":
        config_directory = project if config_location == "project" else nested
        config_file = config_directory / ".isort.cfg"
        config_file.write_text("[settings]\nline_length = 88\n", encoding="utf8")
        assert settings._find_config(str(nested))[1]["source"] == str(config_file)
    else:
        config = Config(settings_path=str(nested))
        assert config.line_length == settings.DEFAULT_CONFIG.line_length
        assert place_module("local_module", config=config) == "FIRSTPARTY"
        source = "import third_party\n\nimport local_module\n"
        assert code(source, config=config) == source


def test_get_config_data(tmp_path: Path) -> None:
    test_config = tmp_path / "test_config.editorconfig"
    test_config.write_text(
        """
root = true

[*.{js,py}]
indent_style=tab
indent_size=tab

[*.py]
force_grid_wrap=false
comment_prefix="text"

[*.{java}]
indent_style = space
""",
        "utf8",
    )
    loaded_settings = settings._get_config_data(
        str(test_config), sections=settings.CONFIG_SECTIONS[".editorconfig"]
    )
    assert loaded_settings
    assert loaded_settings["comment_prefix"] == "text"
    assert loaded_settings["force_grid_wrap"] == 0
    assert loaded_settings["indent"] == "\t"
    assert isinstance(loaded_settings["source"], str)
    assert str(tmp_path) in loaded_settings["source"]


def test_editorconfig_without_sections(tmp_path: Path) -> None:
    test_config = tmp_path / "test_config.editorconfig"
    test_config.write_text("\nroot = true\n", "utf8")
    loaded_settings = settings._get_config_data(str(test_config), sections=("*.py",))
    assert not loaded_settings


def test_get_config_data_with_toml_and_utf8(tmp_path: Path) -> None:
    test_config = tmp_path / "pyproject.toml"
    # Exception: UnicodeDecodeError: 'gbk' codec can't decode byte 0x84 in position 57
    test_config.write_text(
        """
[project]
description = "基于FastAPI + Mysql的 TodoList"  # Exception: UnicodeDecodeError
name = "TodoList"
version = "0.1.0"

[tool.isort]
multi_line_output = 3

""",
        "utf8",
    )
    loaded_settings = settings._get_config_data(
        str(test_config), sections=settings.CONFIG_SECTIONS["pyproject.toml"]
    )
    assert loaded_settings
    assert isinstance(loaded_settings["source"], str)
    assert str(tmp_path) in loaded_settings["source"]


def test_as_bool() -> None:
    assert settings._as_bool("TrUe") is True
    assert settings._as_bool("true") is True
    assert settings._as_bool("t") is True
    assert settings._as_bool("FALSE") is False
    assert settings._as_bool("faLSE") is False
    assert settings._as_bool("f") is False
    with pytest.raises(ValueError, match="invalid truth value"):
        settings._as_bool("")
    with pytest.raises(ValueError, match="invalid truth value falsey"):
        settings._as_bool("falsey")
    with pytest.raises(ValueError, match="invalid truth value truthy"):
        settings._as_bool("truthy")


def test_find_all_configs(tmp_path: Path) -> None:
    setup_cfg = """
[isort]
profile=django
"""

    pyproject_toml = """
[tool.isort]
profile = "hug"
"""

    isort_cfg = """
[settings]
profile=black
"""

    pyproject_toml_broken = """
[tool.isorts]
something = nothing
"""

    dir1 = tmp_path / "subdir1"
    dir2 = tmp_path / "subdir2"
    dir3 = tmp_path / "subdir3"
    dir4 = tmp_path / "subdir4"

    dir1.mkdir()
    dir2.mkdir()
    dir3.mkdir()
    dir4.mkdir()

    setup_cfg_file = dir1 / "setup.cfg"
    setup_cfg_file.write_text(setup_cfg, "utf-8")

    pyproject_toml_file = dir2 / "pyproject.toml"
    pyproject_toml_file.write_text(pyproject_toml, "utf-8")

    isort_cfg_file = dir3 / ".isort.cfg"
    isort_cfg_file.write_text(isort_cfg, "utf-8")

    pyproject_toml_file_broken = dir4 / "pyproject.toml"
    pyproject_toml_file_broken.write_text(pyproject_toml_broken, "utf-8")

    config_trie = settings.find_all_configs(str(tmp_path))

    config_info_1 = config_trie.search(str(dir1 / "test1.py"))
    assert config_info_1[0] == str(setup_cfg_file)
    assert config_info_1[0] == str(setup_cfg_file)
    assert config_info_1[1]["profile"] == "django"

    config_info_2 = config_trie.search(str(dir2 / "test2.py"))
    assert config_info_2[0] == str(pyproject_toml_file)
    assert config_info_2[0] == str(pyproject_toml_file)
    assert config_info_2[1]["profile"] == "hug"

    config_info_3 = config_trie.search(str(dir3 / "test3.py"))
    assert config_info_3[0] == str(isort_cfg_file)
    assert config_info_3[0] == str(isort_cfg_file)
    assert config_info_3[1]["profile"] == "black"

    config_info_4 = config_trie.search(str(tmp_path / "file4.py"))
    assert config_info_4[0] == "default"
