"""Contains all logic related to placing an import within a certain section."""
import importlib
from fnmatch import fnmatch
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

from isort import sections
from isort.settings import DEFAULT_CONFIG, Config
from isort.utils import exists_case_sensitive

LOCAL = "LOCALFOLDER"


def module(name: str, config: Config = DEFAULT_CONFIG) -> str:
    """Returns the section placement for the given module name."""
    return module_with_reason(name, config)[0]


@lru_cache(maxsize=1000)
def module_with_reason(name: str, config: Config = DEFAULT_CONFIG) -> Tuple[str, str]:
    """Returns the section placement for the given module name alongside the reasoning."""
    return (
        _forced_separate(name, config)
        or _local(name, config)
        or _known_pattern(name, config)
        or _src_path(name, config)
        or (config.default_section, "Default option in Config or universal default.")
    )


def _forced_separate(name: str, config: Config) -> Optional[Tuple[str, str]]:
    for forced_separate in config.forced_separate:
        # Ensure all forced_separate patterns will match to end of string
        path_glob = forced_separate
        if not forced_separate.endswith("*"):
            path_glob = "%s*" % forced_separate

        if fnmatch(name, path_glob) or fnmatch(name, "." + path_glob):
            return (forced_separate, f"Matched forced_separate ({forced_separate}) config value.")

    return None


def _local(name: str, config: Config) -> Optional[Tuple[str, str]]:
    if name.startswith("."):
        return (LOCAL, "Module name started with a dot.")

    return None


def _known_pattern(name: str, config: Config) -> Optional[Tuple[str, str]]:
    parts = name.split(".")
    module_names_to_check = (".".join(parts[:first_k]) for first_k in range(len(parts), 0, -1))
    for module_name_to_check in module_names_to_check:
        for pattern, placement in config.known_patterns:
            if pattern.match(module_name_to_check):
                return (placement, f"Matched configured known pattern {pattern}")

    return None


def _src_path(name: str, config: Config) -> Optional[Tuple[str, str]]:
    search_paths = zip(config.src_paths, config.src_paths)
    for index, module_part in enumerate(name.split(".")):
        if index == len(module_parts):
            for search_path, src_path in search_paths:
                module_path = (search_path / module_part).resolve()
                if (
                    _is_module(module_path)
                    or _is_package(module_path)
                    or _src_path_is_module(search_path, module_part)
                ):
                    return (sections.FIRSTPARTY, f"Found in one of the configured src_paths: {src_path}.")
        else:
            new_search_paths = []
            for search_path, src_path in search_paths:
                if

            search_paths = [search_path for search_path in search_paths if
                            _is_package((src_path / root_module_name).resolve()) or
                            index == 0 and _src_path_is_module

            for src_path in config.src_paths:
                root_module_name = name.split(".")[0]
                module_path =
                if (
                    or
                    or _src_path_is_module(src_path, root_module_name)
                ):
                    return (sections.FIRSTPARTY, f"Found in one of the configured src_paths: {src_path}.")


    for src_path in config.src_paths:

        for part in
        root_module_name = name.split(".")[0]
        module_path = (src_path / root_module_name).resolve()
        if (
            _is_module(module_path)
            or _is_package(module_path)
            or _src_path_is_module(src_path, root_module_name)
        ):
            return (sections.FIRSTPARTY, f"Found in one of the configured src_paths: {src_path}.")

    return None


def _is_module(path: Path) -> bool:
    return (
        exists_case_sensitive(str(path.with_suffix(".py")))
        or any(
            exists_case_sensitive(str(path.with_suffix(ext_suffix)))
            for ext_suffix in importlib.machinery.EXTENSION_SUFFIXES
        )
        or exists_case_sensitive(str(path / "__init__.py"))
    )


def _is_package(path: Path) -> bool:
    return exists_case_sensitive(str(path)) and path.is_dir()


def _src_path_is_module(src_path: Path, module_name: str) -> bool:
    return (
        module_name == src_path.name and src_path.is_dir() and exists_case_sensitive(str(src_path))
    )
