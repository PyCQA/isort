"""isort/settings.py.

Defines how the default settings for isort should be loaded

(First from the default setting dictionary at the top of the file, then overridden by any settings
 in ~/.isort.cfg or $XDG_CONFIG_HOME/isort.cfg if there are any)
"""
import configparser
import enum
import fnmatch
import os
import posixpath
import re
import sys
import warnings
from distutils.util import strtobool
from functools import lru_cache
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)
from warnings import warn

from . import stdlibs
from ._future import dataclass, field
from .utils import difference, union
from .wrap_modes import WrapModes
from .wrap_modes import from_string as wrap_mode_from_string

try:
    import toml
except ImportError:
    toml = None  # type: ignore

try:
    import appdirs

    if appdirs.system == "darwin":
        appdirs.system = "linux2"
except ImportError:
    appdirs = None

MAX_CONFIG_SEARCH_DEPTH: int = (
    25
)  # The number of parent directories isort will look for a config file within
DEFAULT_SECTIONS: Iterable[str] = ("FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER")

safety_exclude_re = re.compile(
    r"/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|\.pants\.d"
    r"|lib/python[0-9].[0-9]+|node_modules)/"
)
VALID_PY_TARGETS: Iterable[str] = tuple(
    target.replace("py", "") for target in dir(stdlibs) if not target.startswith("_")
)
CONFIG_SOURCES = (".isort.cfg", "pyproject.toml", "setup.cfg", "tox.ini", ".editorconfig")
CONFIG_SECTIONS = {
    ".isort.cfg": ("settings", "isort"),
    "pyproject.toml": ("tool.isort",),
    "setup.cfg": ("isort", "tool:isort"),
    "tox.ini": ("isort", "tool:isort"),
    ".editorconfig": ("*", "*.py", "**.py"),
}
FALLBACK_CONFIG_SECTIONS = ("isort", "tool:isort", "tool.isort")

if appdirs:
    FALLBACK_CONFIGS = [
        appdirs.user_config_dir(".isort.cfg"),
        appdirs.user_config_dir(".editorconfig"),
    ]
else:
    FALLBACK_CONFIGS = ["~/.isort.cfg", "~/.editorconfig"]


@dataclass(frozen=True)
class _Config:
    """Defines the data schema and defaults used for isort configuration.

    NOTE: known lists, such as known_standard_library, are intentionally not complete as they are
    dynamically determined later on.
    """
    py_version: str = "3"
    force_to_top: List[str] = field(default_factory=list)
    skip: List[str] = field(default_factory=list)
    skip_glob: List[str] = field(default_factory=list)
    line_length: int = 79
    wrap_length: int = 0
    line_ending: str = ""
    sections: Iterable[str] = DEFAULT_SECTIONS
    no_sections: bool = False
    known_future_library: List[str] = field(default_factory=lambda: ["__future__"])
    known_third_party: List[str] = field(default_factory=lambda: ["google.appengine.api"])
    known_first_party: List[str] = field(default_factory=list)
    known_standard_library: List[str] = field(default_factory=list)
    multi_line_output = WrapModes.GRID  # type: ignore
    forced_separate: List[str] = field(default_factory=list)
    indent: str = " " * 4
    comment_prefix: str = "  #"
    length_sort: bool = False
    add_imports: List[str] = field(default_factory=list)
    remove_imports: List[str] = field(default_factory=list)
    reverse_relative: bool = False
    force_single_line: bool = False
    default_section: str = "FIRSTPARTY"
    import_heading_future: str = ""
    import_heading_stdlib: str = ""
    import_heading_thirdparty: str = ""
    import_heading_firstparty: str = ""
    import_heading_localfolder: str = ""
    balanced_wrapping: bool = False
    use_parentheses: bool = False
    order_by_type: bool = True
    atomic: bool = False
    lines_after_imports: int = -1
    lines_between_sections: int = 1
    lines_between_types: int = 0
    combine_as_imports: bool = False
    combine_star: bool = False
    keep_direct_and_as_imports: bool = False
    include_trailing_comma: bool = False
    from_first: bool = False
    verbose: bool = False
    quiet: bool = False
    force_adds: bool = False
    force_alphabetical_sort_within_sections: bool = False
    force_alphabetical_sort: bool = False
    force_grid_wrap: int = 0
    force_sort_within_sections: bool = False
    show_diff: bool = False
    ignore_whitespace: bool = False
    no_lines_before: List[str] = field(default_factory=list)
    no_inline_sort: bool = False
    ignore_comments: bool = False
    safety_excludes: bool = True
    case_sensitive: bool = False
    sources: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        py_version = self.py_version
        if py_version == "auto":
            py_version = f"{sys.version_info.major}{sys.version_info.minor}"

        if py_version not in VALID_PY_TARGETS:
            raise ValueError(
                f"The python version {py_version} is not supported. "
                "You can set a python version with the -py or --python-version flag. "
                f"The following versions are supported: {VALID_PY_TARGETS}"
            )

        if py_version != "all":
            object.__setattr__(self, "py_version", f"py{py_version}")

        object.__setattr__(
            self,
            "known_standard_library",
            list(getattr(stdlibs, self.py_version).stdlib | set(self.known_standard_library)),
        )

        if self.force_alphabetical_sort:
            object.__setattr__(self, "force_alphabetical_sort_within_sections", True)
            object.__setattr__(self, "no_sections", True)
            object.__setattr__(self, "lines_between_types", 1)
            object.__setattr__(self, "from_first", True)

_DEFAULT_SETTINGS = {**vars(_Config()), "source": "defaults"}


class Config(_Config):
    def __init__(self, settings_file:str="", settings_path:str="", **config_overrides):
        sources: List[Dict[str, Any]] = [_DEFAULT_SETTINGS]

        config_settings: Dict[str, Any]
        if settings_file:
            config_settings = config_data = get_config_data(settings_file, CONFIG_SECTIONS.get(os.path.basename(settings_file), FALLBACK_CONFIG_SECTIONS))
        elif settings_path:
            config_settings = _find_config(settings_path)
        else:
            config_settings = {}

        if config_settings:



            sources.append(config_settings)
        if config_overrides:
            config_overrides["source"] = "runtime"
            sources.append(config_overrides)

    def file_should_be_skipped(self, filename: str, path: str = "") -> bool:
        """Returns True if the file and/or folder should be skipped based on current settings."""
        os_path = os.path.join(path, filename)

        normalized_path = os_path.replace("\\", "/")
        if normalized_path[1:2] == ":":
            normalized_path = normalized_path[2:]

        if path and self.safety_excludes:
            check_exclude = "/" + filename.replace("\\", "/") + "/"
            if path and os.path.basename(path) in ("lib",):
                check_exclude = "/" + os.path.basename(path) + check_exclude
            if safety_exclude_re.search(check_exclude):
                return True

        for skip_path in self.skip:
            if posixpath.abspath(normalized_path) == posixpath.abspath(skip_path.replace("\\", "/")):
                return True

        position = os.path.split(filename)
        while position[1]:
            if position[1] in self.skip:
                return True
            position = os.path.split(position[0])

        for glob in self.skip_glob:
            if fnmatch.fnmatch(filename, glob) or fnmatch.fnmatch("/" + filename, glob):
                return True

        if not (os.path.isfile(os_path) or os.path.isdir(os_path) or os.path.islink(os_path)):
            return True

        return False


def prepare_config(settings_path: Path, **setting_overrides: Any) -> Dict[str, Any]:
    py_version = setting_overrides.pop("py_version", None)
    config = from_path(settings_path, py_version).copy()
    for key, value in setting_overrides.items():
        access_key = key.replace("not_", "").lower()
        # The sections config needs to retain order and can't be converted to a set.
        if access_key != "sections" and type(config.get(access_key)) in (list, tuple, set):
            if key.startswith("not_"):
                config[access_key] = list(set(config[access_key]).difference(value))
            else:
                config[access_key] = list(set(config[access_key]).union(value))
        else:
            config[key] = value

    indent = str(config["indent"])
    if indent.isdigit():
        indent = " " * int(indent)
    else:
        indent = indent.strip("'").strip('"')
        if indent.lower() == "tab":
            indent = "\t"
    config["indent"] = indent

    config["comment_prefix"] = config["comment_prefix"].strip("'").strip('"')
    return config


def _get_str_to_type_converter(setting_name: str) -> Callable[[str], Any]:
    type_converter: Callable[[str], Any] = type(_DEFAULT_SETTINGS.get(setting_name, ""))
    if type_converter == WrapModes:
        type_converter = wrap_mode_from_string
    return type_converter


def _update_with_config_file(
    file_path: str, sections: Iterable[str], computed_settings: MutableMapping[str, Any]
) -> None:
    cwd = os.path.dirname(file_path)
    settings = _get_config_data(file_path, sections).copy()
    if not settings:
        return

def _as_list(value: str) -> List[str]:
    if isinstance(value, list):
        return [item.strip() for item in value]
    filtered = [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]
    return filtered


def _abspaths(cwd: str, values: Iterable[str]) -> List[str]:
    paths = set([
        os.path.join(cwd, value)
        if not value.startswith(os.path.sep) and value.endswith(os.path.sep)
        else value
        for value in values
    ])
    return paths


@lru_cache()
def _find_config(path: str) -> Dict[str, Any]:
    current_directory = path
    tries = 0
    while current_directory and tries < MAX_CONFIG_SEARCH_DEPTH:
        for config_file_name in CONFIG_SOURCES:
            potential_config_file = os.path.join(current_directory, config_file_name)
            if os.path.isfile(potential_config_file):
                config_data: Dict[str, Any]
                try:
                    config_data = _get_config_data(
                        potential_config_file, CONFIG_SECTIONS[config_file_name]
                    )
                except Exception:
                    warn(f"Failed to pull configuration information from {potential_config_file}")
                    config_data = {}
                if config_data:
                    return config_data

        new_directory = os.path.split(current_directory)[0]
        if new_directory == current_directory:
            break

        current_directory = new_directory
        tries += 1

    return {}


@lru_cache()
def _get_config_data(file_path: str, sections: Iterable[str]) -> Dict[str, Any]:
    settings: Dict[str, Any] = {}

    with open(file_path) as config_file:
        if file_path.endswith(".toml"):
            if toml:
                config = toml.load(config_file)
                for section in sections:
                    config_section = config
                    for key in section.split("."):
                        config_section = config_section.get(key, {})
                    settings.update(config_section)
            else:
                if "[tool.isort]" in config_file.read():
                    warnings.warn(
                        f"Found {file_path} with [tool.isort] section, but toml package is not "
                        f"installed. To configure isort with {file_path}, install with "
                        "'isort[pyproject]'."
                    )
        else:
            if file_path.endswith(".editorconfig"):
                line = "\n"
                last_position = config_file.tell()
                while line:
                    line = config_file.readline()
                    if "[" in line:
                        config_file.seek(last_position)
                        break
                    last_position = config_file.tell()

            config = configparser.ConfigParser(strict=False)
            config.read_file(config_file)
            for section in sections:
                if config.has_section(section):
                    settings.update(config.items(section))

    if settings:
        settings["source"] = file_path

        if file_path.endswith(".editorconfig"):
            indent_style = settings.pop("indent_style", "").strip()
            indent_size = settings.pop("indent_size", "").strip()
            if indent_size == "tab":
                indent_size = settings.pop("tab_width", "").strip()

            if indent_style == "space":
                settings["indent"] = " " * (indent_size and int(indent_size) or 4)

            elif indent_style == "tab":
                settings["indent"] = "\t" * (indent_size and int(indent_size) or 1)

            max_line_length = settings.pop("max_line_length", "").strip()
            if max_line_length:
                settings["line_length"] = (
                    float("inf") if max_line_length == "off" else int(max_line_length)
                )

        for key, value in settings.items():
            existing_value_type = _get_str_to_type_converter(key)
            if existing_value_type in (list, tuple):
                if key == "sections":  # sections need to maintain order
                    settings[key] = tuple(_as_list(value))
                else: # other list options do not and can be uniquified using set.
                    settings[key] = set(settings.get(key))
            elif existing_value_type == bool:
                # Only some configuration formats support native boolean values.
                if not isinstance(value, bool):
                    value = bool(_as_bool(value))
                settings[key] = value
            elif key.startswith("known_"):
                settings[key] = _abspaths(os.path.dirname(file_path), _as_list(value))
            elif key == "force_grid_wrap":
                try:
                    result = existing_value_type(value)
                except ValueError:
                    # backwards compat
                    result = default.get(access_key) if value.lower().strip() == "false" else 2
                computed_settings[access_key] = result
            else:
                existing_value_type(value)

    return settings



