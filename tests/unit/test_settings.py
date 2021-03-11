import os
import sys
from pathlib import Path

import pytest

from isort import exceptions, settings
from isort.settings import Config
from isort.wrap_modes import WrapModes


class TestConfig:
    instance = Config()

    def test_init(self):
        assert Config()

    def test_init_unsupported_settings_fails_gracefully(self):
        with pytest.raises(exceptions.UnsupportedSettings):
            Config(apply=True)
        try:
            Config(apply=True)
        except exceptions.UnsupportedSettings as error:
            assert error.unsupported_settings == {"apply": {"value": True, "source": "runtime"}}

    def test_known_settings(self):
        assert Config(known_third_party=["one"]).known_third_party == frozenset({"one"})
        assert Config(known_thirdparty=["two"]).known_third_party == frozenset({"two"})
        assert Config(
            known_third_party=["one"], known_thirdparty=["two"]
        ).known_third_party == frozenset({"one"})

    def test_invalid_settings_path(self):
        with pytest.raises(exceptions.InvalidSettingsPath):
            Config(settings_path="this_couldnt_possibly_actually_exists/could_it")

    def test_invalid_pyversion(self):
        with pytest.raises(ValueError):
            Config(py_version=10)

    def test_invalid_profile(self):
        with pytest.raises(exceptions.ProfileDoesNotExist):
            Config(profile="blackandwhitestylemixedwithpep8")

    def test_is_skipped(self):
        assert Config().is_skipped(Path("C:\\path\\isort.py"))
        assert Config(skip=["/path/isort.py"]).is_skipped(Path("C:\\path\\isort.py"))

    def test_is_supported_filetype(self):
        assert self.instance.is_supported_filetype("file.py")
        assert self.instance.is_supported_filetype("file.pyi")
        assert self.instance.is_supported_filetype("file.pyx")
        assert self.instance.is_supported_filetype("file.pxd")
        assert not self.instance.is_supported_filetype("file.pyc")
        assert not self.instance.is_supported_filetype("file.txt")
        assert not self.instance.is_supported_filetype("file.pex")

    def test_is_supported_filetype_ioerror(self, tmpdir):
        does_not_exist = tmpdir.join("fake.txt")
        assert not self.instance.is_supported_filetype(str(does_not_exist))

    def test_is_supported_filetype_shebang(self, tmpdir):
        path = tmpdir.join("myscript")
        path.write("#!/usr/bin/env python\n")
        assert self.instance.is_supported_filetype(str(path))

    def test_is_supported_filetype_editor_backup(self, tmpdir):
        path = tmpdir.join("myscript~")
        path.write("#!/usr/bin/env python\n")
        assert not self.instance.is_supported_filetype(str(path))

    def test_is_supported_filetype_defaults(self, tmpdir):
        assert self.instance.is_supported_filetype(str(tmpdir.join("stub.pyi")))
        assert self.instance.is_supported_filetype(str(tmpdir.join("source.py")))
        assert self.instance.is_supported_filetype(str(tmpdir.join("source.pyx")))

    def test_is_supported_filetype_configuration(self, tmpdir):
        config = Config(supported_extensions=("pyx",), blocked_extensions=("py",))
        assert config.is_supported_filetype(str(tmpdir.join("stub.pyx")))
        assert not config.is_supported_filetype(str(tmpdir.join("stub.py")))

    @pytest.mark.skipif(
        sys.platform == "win32", reason="cannot create fifo file on Windows platform"
    )
    def test_is_supported_filetype_fifo(self, tmpdir):
        fifo_file = os.path.join(tmpdir, "fifo_file")
        os.mkfifo(fifo_file)
        assert not self.instance.is_supported_filetype(fifo_file)

    def test_src_paths_are_combined_and_deduplicated(self):
        src_paths = ["src", "tests"]
        src_full_paths = (Path(os.getcwd()) / f for f in src_paths)
        assert Config(src_paths=src_paths * 2).src_paths == tuple(src_full_paths)

    def test_deprecated_multi_line_output(self):
        assert Config(multi_line_output=6).multi_line_output == WrapModes.VERTICAL_GRID_GROUPED


def test_as_list():
    assert settings._as_list([" one "]) == ["one"]
    assert settings._as_list("one,two") == ["one", "two"]


def _write_simple_settings(tmp_file):
    tmp_file.write_text(
        """
[isort]
force_grid_wrap=true
""",
        "utf8",
    )


def test_find_config(tmpdir):
    tmp_config = tmpdir.join(".isort.cfg")

    # can't find config if it has no relevant section
    settings._find_config.cache_clear()
    settings._get_config_data.cache_clear()
    tmp_config.write_text(
        """
[section]
force_grid_wrap=true
""",
        "utf8",
    )
    assert not settings._find_config(str(tmpdir))[1]

    # or if it is malformed
    settings._find_config.cache_clear()
    settings._get_config_data.cache_clear()
    tmp_config.write_text("""arstoyrsyan arienrsaeinrastyngpuywnlguyn354q^%$)(%_)@$""", "utf8")
    assert not settings._find_config(str(tmpdir))[1]

    # can when it has either a file format, or generic relevant section
    settings._find_config.cache_clear()
    settings._get_config_data.cache_clear()
    _write_simple_settings(tmp_config)
    assert settings._find_config(str(tmpdir))[1]


def test_find_config_deep(tmpdir):
    # can't find config if it is further up than MAX_CONFIG_SEARCH_DEPTH
    dirs = [f"dir{i}" for i in range(settings.MAX_CONFIG_SEARCH_DEPTH + 1)]
    tmp_dirs = tmpdir.ensure(*dirs, dirs=True)
    tmp_config = tmpdir.join("dir0", ".isort.cfg")
    settings._find_config.cache_clear()
    settings._get_config_data.cache_clear()
    _write_simple_settings(tmp_config)
    assert not settings._find_config(str(tmp_dirs))[1]
    # but can find config if it is MAX_CONFIG_SEARCH_DEPTH up
    one_parent_up = os.path.split(str(tmp_dirs))[0]
    assert settings._find_config(one_parent_up)[1]


def test_get_config_data(tmpdir):
    test_config = tmpdir.join("test_config.editorconfig")
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
    assert str(tmpdir) in loaded_settings["source"]


def test_editorconfig_without_sections(tmpdir):
    test_config = tmpdir.join("test_config.editorconfig")
    test_config.write_text("\nroot = true\n", "utf8")
    loaded_settings = settings._get_config_data(str(test_config), sections=("*.py",))
    assert not loaded_settings


def test_get_config_data_with_toml_and_utf8(tmpdir):
    test_config = tmpdir.join("pyproject.toml")
    # Exception: UnicodeDecodeError: 'gbk' codec can't decode byte 0x84 in position 57
    test_config.write_text(
        """
[tool.poetry]

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
    assert str(tmpdir) in loaded_settings["source"]


def test_as_bool():
    assert settings._as_bool("TrUe") is True
    assert settings._as_bool("true") is True
    assert settings._as_bool("t") is True
    assert settings._as_bool("FALSE") is False
    assert settings._as_bool("faLSE") is False
    assert settings._as_bool("f") is False
    with pytest.raises(ValueError):
        settings._as_bool("")
    with pytest.raises(ValueError):
        settings._as_bool("falsey")
    with pytest.raises(ValueError):
        settings._as_bool("truthy")
