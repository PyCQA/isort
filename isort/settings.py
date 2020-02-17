"""isort/settings.py.

Defines how the default settings for isort should be loaded

(First from the default setting dictionary at the top of the file, then overridden by any settings
 in ~/.isort.cfg or $XDG_CONFIG_HOME/.isort.cfg if there are any)
"""
import configparser
import fnmatch
import os
import posixpath
import sys
import warnings
from distutils.util import strtobool as _as_bool
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple
from warnings import warn

from . import stdlibs
from ._future import dataclass, field
from .exceptions import ProfileDoesNotExist
from .profiles import profiles
from .sections import DEFAULT as SECTION_DEFAULTS
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

SUPPORTED_EXTENSIONS = (".py", ".pyi", ".pyx")
FILE_SKIP_COMMENTS: Tuple[str, ...] = (
    "isort:" + "skip_file",
    "isort: " + "skip_file",
)  # Concatenated to avoid this file being skipped
MAX_CONFIG_SEARCH_DEPTH: int = 25  # The number of parent directories to for a config file within
STOP_CONFIG_SEARCH_ON_DIRS: Tuple[str, ...] = (".git", ".hg")
VALID_PY_TARGETS: Tuple[str, ...] = tuple(
    target.replace("py", "") for target in dir(stdlibs) if not target.startswith("_")
)
CONFIG_SOURCES: Tuple[str, ...] = (
    ".isort.cfg",
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    ".editorconfig",
)

CONFIG_SECTIONS: Dict[str, Tuple[str, ...]] = {
    ".isort.cfg": ("settings", "isort"),
    "pyproject.toml": ("tool.isort",),
    "setup.cfg": ("isort", "tool:isort"),
    "tox.ini": ("isort", "tool:isort"),
    ".editorconfig": ("*", "*.py", "**.py", "*.{py}"),
}
FALLBACK_CONFIG_SECTIONS: Tuple[str, ...] = ("isort", "tool:isort", "tool.isort")
FALLBACK_CONFIGS: Tuple[str, ...]
if appdirs:
    FALLBACK_CONFIGS = (
        appdirs.user_config_dir(".isort.cfg"),
        appdirs.user_config_dir(".editorconfig"),
    )
else:
    FALLBACK_CONFIGS = ("~/.isort.cfg", "~/.editorconfig")

IMPORT_HEADING_PREFIX = "import_heading_"
KNOWN_PREFIX = "known_"


@dataclass(frozen=True)
class _Config:
    """Defines the data schema and defaults used for isort configuration.

    NOTE: known lists, such as known_standard_library, are intentionally not complete as they are
    dynamically determined later on.
    """

    py_version: str = "3"
    force_to_top: FrozenSet[str] = frozenset()
    skip: FrozenSet[str] = frozenset(
        {
            ".venv",
            "venv",
            ".tox",
            ".eggs",
            ".git",
            ".hg",
            ".mypy_cache",
            ".nox",
            "_build",
            "buck-out",
            "build",
            "dist",
            ".pants.d",
            "node_modules",
        }
    )
    skip_glob: FrozenSet[str] = frozenset()
    line_length: int = 79
    wrap_length: int = 0
    line_ending: str = ""
    sections: Tuple[str, ...] = SECTION_DEFAULTS
    no_sections: bool = False
    known_future_library: FrozenSet[str] = frozenset(("__future__",))
    known_third_party: FrozenSet[str] = frozenset(("google.appengine.api",))
    known_first_party: FrozenSet[str] = frozenset()
    known_standard_library: FrozenSet[str] = frozenset()
    known_other: Dict[str, FrozenSet[str]] = field(default_factory=dict)
    multi_line_output: WrapModes = WrapModes.GRID  # type: ignore
    forced_separate: Tuple[str, ...] = ()
    indent: str = " " * 4
    comment_prefix: str = "  #"
    length_sort: bool = False
    length_sort_sections: FrozenSet[str] = frozenset()
    add_imports: FrozenSet[str] = frozenset()
    remove_imports: FrozenSet[str] = frozenset()
    reverse_relative: bool = False
    force_single_line: bool = False
    single_line_exclusions: Tuple[str, ...] = ()
    default_section: str = "FIRSTPARTY"
    import_headings: Dict[str, str] = field(default_factory=dict)
    balanced_wrapping: bool = False
    use_parentheses: bool = False
    order_by_type: bool = True
    atomic: bool = False
    lines_after_imports: int = -1
    lines_between_sections: int = 1
    lines_between_types: int = 0
    combine_as_imports: bool = False
    combine_star: bool = False
    keep_direct_and_as_imports: bool = True
    include_trailing_comma: bool = False
    from_first: bool = False
    verbose: bool = False
    quiet: bool = False
    force_adds: bool = False
    force_alphabetical_sort_within_sections: bool = False
    force_alphabetical_sort: bool = False
    force_grid_wrap: int = 0
    force_sort_within_sections: bool = False
    lexicographical: bool = False
    ignore_whitespace: bool = False
    no_lines_before: FrozenSet[str] = frozenset()
    no_inline_sort: bool = False
    ignore_comments: bool = False
    case_sensitive: bool = False
    sources: Tuple[Dict[str, Any], ...] = ()
    virtual_env: str = ""
    conda_env: str = ""
    ensure_newline_before_comments: bool = False
    directory: str = ""
    profile: str = ""

    def __post_init__(self):
        py_version = self.py_version
        if py_version == "auto":
            if sys.version_info.major == 2 and sys.version_info.minor <= 6:
                py_version = "2"
            elif sys.version_info.major == 3 and (
                sys.version_info.minor <= 5 or sys.version_info.minor >= 8
            ):
                py_version = "3"
            else:
                py_version = f"{sys.version_info.major}{sys.version_info.minor}"

        if py_version not in VALID_PY_TARGETS:
            raise ValueError(
                f"The python version {py_version} is not supported. "
                "You can set a python version with the -py or --python-version flag. "
                f"The following versions are supported: {VALID_PY_TARGETS}"
            )

        if py_version != "all":
            object.__setattr__(self, "py_version", f"py{py_version}")

        if not self.known_standard_library:
            object.__setattr__(
                self, "known_standard_library", frozenset(getattr(stdlibs, self.py_version).stdlib)
            )

        if self.force_alphabetical_sort:
            object.__setattr__(self, "force_alphabetical_sort_within_sections", True)
            object.__setattr__(self, "no_sections", True)
            object.__setattr__(self, "lines_between_types", 1)
            object.__setattr__(self, "from_first", True)
        if self.wrap_length > self.line_length:
            raise ValueError(
                "wrap_length must be set lower than or equal to line_length: "
                f"{self.wrap_length} > {self.line_length}."
            )


_DEFAULT_SETTINGS = {**vars(_Config()), "source": "defaults"}


class Config(_Config):
    def __init__(
        self,
        settings_file: str = "",
        settings_path: str = "",
        config: Optional[_Config] = None,
        **config_overrides,
    ):
        if config:
            config_vars = vars(config).copy()
            config_vars.update(config_overrides)
            config_vars["py_version"] = config_vars["py_version"].replace("py", "")
            return super().__init__(**config_vars)  # type: ignore

        sources: List[Dict[str, Any]] = [_DEFAULT_SETTINGS]

        config_settings: Dict[str, Any]
        if settings_file:
            config_settings = _get_config_data(
                settings_file,
                CONFIG_SECTIONS.get(os.path.basename(settings_file), FALLBACK_CONFIG_SECTIONS),
            )
        elif settings_path:
            config_settings = _find_config(settings_path)
        else:
            config_settings = {}

        profile_name = config_overrides.get("profile", config_settings.get("profile", ""))
        profile: Dict[str, Any] = {}
        if profile_name:
            if profile_name not in profiles:
                raise ProfileDoesNotExist(profile_name)

            profile = profiles[profile_name].copy()
            profile["source"] = f"{profile_name} profile"
            sources.append(profile)

        if config_settings:
            sources.append(config_settings)
        if config_overrides:
            config_overrides["source"] = "runtime"
            sources.append(config_overrides)

        combined_config = {**profile, **config_settings, **config_overrides}
        if "indent" in combined_config:
            indent = str(combined_config["indent"])
            if indent.isdigit():
                indent = " " * int(indent)
            else:
                indent = indent.strip("'").strip('"')
                if indent.lower() == "tab":
                    indent = "\t"
            combined_config["indent"] = indent

        known_other = {}
        import_headings = {}
        for key, value in combined_config.items():
            # Collect all known sections beyond those that have direct entries
            if key.startswith(KNOWN_PREFIX) and key not in (
                "known_standard_library",
                "known_future_library",
                "known_third_party",
                "known_first_party",
            ):
                known_other[key[len(KNOWN_PREFIX) :].lower()] = frozenset(value)
            if key.startswith(IMPORT_HEADING_PREFIX):
                import_headings[key[len(IMPORT_HEADING_PREFIX) :].lower()] = str(value)

            # Coerce all provided config values into their correct type
            default_value = _DEFAULT_SETTINGS.get(key, None)
            if default_value is None:
                continue

            combined_config[key] = type(default_value)(value)

        if "directory" not in combined_config:
            combined_config["directory"] = os.path.basename(
                config_settings.get("source", None) or os.getcwd()
            )

        # Remove any config values that are used for creating config object but
        # aren't defined in dataclass
        combined_config.pop("source", None)
        combined_config.pop("sources", None)
        if known_other:
            for known_key in known_other.keys():
                combined_config.pop(f"{KNOWN_PREFIX}{known_key}", None)
            combined_config["known_other"] = known_other
        if import_headings:
            for import_heading_key in import_headings.keys():
                combined_config.pop(f"{IMPORT_HEADING_PREFIX}{import_heading_key}")
            combined_config["import_headings"] = import_headings

        super().__init__(sources=tuple(sources), **combined_config)  # type: ignore

    def is_skipped(self, file_path: Path) -> bool:
        """Returns True if the file and/or folder should be skipped based on current settings."""
        if self.directory and Path(self.directory) in file_path.parents:
            file_name = os.path.relpath(file_path, self.directory)
        else:
            file_name = str(file_path)

        os_path = str(file_path)

        normalized_path = os_path.replace("\\", "/")
        if normalized_path[1:2] == ":":
            normalized_path = normalized_path[2:]

        for skip_path in self.skip:
            if posixpath.abspath(normalized_path) == posixpath.abspath(
                skip_path.replace("\\", "/")
            ):
                return True

        position = os.path.split(file_name)
        while position[1]:
            if position[1] in self.skip:
                return True
            position = os.path.split(position[0])

        for glob in self.skip_glob:
            if fnmatch.fnmatch(file_name, glob) or fnmatch.fnmatch("/" + file_name, glob):
                return True

        if not (os.path.isfile(os_path) or os.path.isdir(os_path) or os.path.islink(os_path)):
            return True

        return False


def _get_str_to_type_converter(setting_name: str) -> Callable[[str], Any]:
    type_converter: Callable[[str], Any] = type(_DEFAULT_SETTINGS.get(setting_name, ""))
    if type_converter == WrapModes:
        type_converter = wrap_mode_from_string
    return type_converter


def _as_list(value: str) -> List[str]:
    if isinstance(value, list):
        return [item.strip() for item in value]
    filtered = [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]
    return filtered


def _abspaths(cwd: str, values: Iterable[str]) -> Set[str]:
    paths = set(
        [
            os.path.join(cwd, value)
            if not value.startswith(os.path.sep) and value.endswith(os.path.sep)
            else value
            for value in values
        ]
    )
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

        for stop_dir in STOP_CONFIG_SEARCH_ON_DIRS:
            if os.path.isdir(stop_dir):
                break

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
                if section.startswith("*.{") and section.endswith("}"):
                    extension = section[len("*.{") : -1]
                    for config_key in config.keys():
                        if config_key.startswith("*.{") and config_key.endswith("}"):
                            if extension in map(
                                lambda text: text.strip(), config_key[len("*.{") : -1].split(",")
                            ):
                                settings.update(config.items(config_key))

                elif config.has_section(section):
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
            settings = {
                key: value for key, value in settings.items() if key in _DEFAULT_SETTINGS.keys()
            }

        for key, value in settings.items():
            existing_value_type = _get_str_to_type_converter(key)
            if existing_value_type == tuple:
                settings[key] = tuple(_as_list(value))
            elif existing_value_type == frozenset:
                settings[key] = frozenset(_as_list(settings.get(key)))  # type: ignore
            elif existing_value_type == bool:
                # Only some configuration formats support native boolean values.
                if not isinstance(value, bool):
                    value = bool(_as_bool(value))
                settings[key] = value
            elif key.startswith(KNOWN_PREFIX):
                settings[key] = _abspaths(os.path.dirname(file_path), _as_list(value))
            elif key == "force_grid_wrap":
                try:
                    result = existing_value_type(value)
                except ValueError:  # backwards compatibility for true / false force grid wrap
                    result = 0 if value.lower().strip() == "false" else 2
                settings[key] = result
            elif key == "comment_prefix":
                settings[key] = str(value).strip("'").strip('"')
            else:
                settings[key] = existing_value_type(value)

    return settings


DEFAULT_CONFIG = Config()
