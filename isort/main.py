"""Tool for sorting imports alphabetically, and automatically separated into sections."""
import argparse
import functools
import glob
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, MutableMapping, Optional, Sequence
from warnings import warn

import setuptools

from isort import SortImports, __version__
from isort.logo import ASCII_ART
from isort.settings import (
    VALID_PY_TARGETS,
    WrapModes,
    Config
    # default,
    # file_should_be_skipped,
    # from_path,
    # wrap_mode_from_string,
)
from . import sections

shebang_re = re.compile(br"^#!.*\bpython[23w]?\b")


def is_python_file(path: str) -> bool:
    _root, ext = os.path.splitext(path)
    if ext in (".py", ".pyi"):
        return True
    if ext in (".pex",):
        return False

    # Skip editor backup files.
    if path.endswith("~"):
        return False

    try:
        with open(path, "rb") as fp:
            line = fp.readline(100)
    except OSError:
        return False
    else:
        return bool(shebang_re.match(line))


class SortAttempt:
    def __init__(self, incorrectly_sorted: bool, skipped: bool) -> None:
        self.incorrectly_sorted = incorrectly_sorted
        self.skipped = skipped


def sort_imports(file_name: str, **arguments: Any) -> Optional[SortAttempt]:
    try:
        result = SortImports(file_name, **arguments)
        return SortAttempt(result.incorrectly_sorted, result.skipped)
    except OSError as error:
        warn(f"Unable to parse file {file_name} due to {error}")
        return None


def iter_source_code(
    paths: Iterable[str], config: Config, skipped: List[str]
) -> Iterator[str]:
    """Iterate over all Python source files defined in paths."""
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, topdown=True, followlinks=True):
                base_path = Path(dirpath)
                for dirname in list(dirnames):
                    if config.is_skipped(base_path / dirname):
                        skipped.append(dirname)
                        dirnames.remove(dirname)
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if is_python_file(filepath):
                        if config.is_skipped(Path(filepath)):
                            skipped.append(filename)
                        else:
                            yield filepath
        else:
            yield path


class ISortCommand(setuptools.Command):
    """The :class:`ISortCommand` class is used by setuptools to perform
    imports checks on registered modules.
    """

    description = "Run isort on modules registered in setuptools"
    user_options: List[Any] = []

    def initialize_options(self) -> None:
        default_settings = default.copy()
        for key, value in default_settings.items():
            setattr(self, key, value)

    def finalize_options(self) -> None:
        "Get options from config files."
        self.arguments: Dict[str, Any] = {}
        computed_settings = from_path(os.getcwd())
        for key, value in computed_settings.items():
            self.arguments[key] = value

    def distribution_files(self) -> Iterator[str]:
        """Find distribution packages."""
        # This is verbatim from flake8
        if self.distribution.packages:
            package_dirs = self.distribution.package_dir or {}
            for package in self.distribution.packages:
                pkg_dir = package
                if package in package_dirs:
                    pkg_dir = package_dirs[package]
                elif "" in package_dirs:
                    pkg_dir = package_dirs[""] + os.path.sep + pkg_dir
                yield pkg_dir.replace(".", os.path.sep)

        if self.distribution.py_modules:
            for filename in self.distribution.py_modules:
                yield "%s.py" % filename
        # Don't miss the setup.py file itself
        yield "setup.py"

    def run(self) -> None:
        arguments = self.arguments
        wrong_sorted_files = False
        arguments["check"] = True
        for path in self.distribution_files():
            for python_file in glob.iglob(os.path.join(path, "*.py")):
                try:
                    incorrectly_sorted = SortImports(python_file, **arguments).incorrectly_sorted
                    if incorrectly_sorted:
                        wrong_sorted_files = True
                except OSError as error:
                    warn(f"Unable to parse file {python_file} due to {error}")
        if wrong_sorted_files:
            sys.exit(1)


def parse_args(argv: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    parser = argparse.ArgumentParser(
        description="Sort Python import definitions alphabetically "
        "within logical sections. Run with no arguments to run "
        "interactively. Run with `-` as the first argument to read from "
        "stdin. Otherwise provide a list of files to sort."
    )
    inline_args_group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-a",
        "--add-import",
        dest="add_imports",
        action="append",
        help="Adds the specified import line to all files, "
        "automatically determining correct placement.",
    )
    parser.add_argument(
        "--ac",
        "--atomic",
        dest="atomic",
        action="store_true",
        help="Ensures the output doesn't save if the resulting file contains syntax errors.",
    )
    parser.add_argument(
        "--af",
        "--force-adds",
        dest="force_adds",
        action="store_true",
        help="Forces import adds even if the original file is empty.",
    )
    parser.add_argument(
        "-b",
        "--builtin",
        dest="known_standard_library",
        action="append",
        help="Force sortImports to recognize a module as part of the python standard library.",
    )
    parser.add_argument(
        "-c",
        "--check-only",
        action="store_true",
        dest="check",
        help="Checks the file for unsorted / unformatted imports and prints them to the "
        "command line without modifying the file.",
    )
    parser.add_argument(
        "--ca",
        "--combine-as",
        dest="combine_as_imports",
        action="store_true",
        help="Combines as imports on the same line.",
    )
    parser.add_argument(
        "--cs",
        "--combine-star",
        dest="combine_star",
        action="store_true",
        help="Ensures that if a star import is present, "
        "nothing else is imported from that namespace.",
    )
    parser.add_argument(
        "-d",
        "--stdout",
        help="Force resulting output to stdout, instead of in-place.",
        dest="write_to_stdout",
        action="store_true",
    )
    parser.add_argument(
        "--df",
        "--diff",
        dest="show_diff",
        action="store_true",
        help="Prints a diff of all the changes isort would make to a file, instead of "
        "changing it in place",
    )
    parser.add_argument(
        "--ds",
        "--no-sections",
        help="Put all imports into the same section bucket",
        dest="no_sections",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--balanced",
        dest="balanced_wrapping",
        action="store_true",
        help="Balances wrapping to produce the most consistent line length possible",
    )
    parser.add_argument(
        "-f",
        "--future",
        dest="known_future_library",
        action="append",
        help="Force sortImports to recognize a module as part "
        "of the future compatibility libraries.",
    )
    parser.add_argument(
        "--fas",
        "--force-alphabetical-sort",
        action="store_true",
        dest="force_alphabetical_sort",
        help="Force all imports to be sorted as a single section",
    )
    parser.add_argument(
        "--fass",
        "--force-alphabetical-sort-within-sections",
        action="store_true",
        dest="force_alphabetical_sort",
        help="Force all imports to be sorted alphabetically within a section",
    )
    parser.add_argument(
        "--ff",
        "--from-first",
        dest="from_first",
        help="Switches the typical ordering preference, "
        "showing from imports first then straight ones.",
    )
    parser.add_argument(
        "--fgw",
        "--force-grid-wrap",
        nargs="?",
        const=2,
        type=int,
        dest="force_grid_wrap",
        help="Force number of from imports (defaults to 2) to be grid wrapped regardless of line "
        "length",
    )
    parser.add_argument(
        "--fss",
        "--force-sort-within-sections",
        action="store_true",
        dest="force_sort_within_sections",
        help="Force imports to be sorted by module, independent of import_type",
    )
    parser.add_argument(
        "-i",
        "--indent",
        help='String to place for indents defaults to "    " (4 spaces).',
        dest="indent",
        type=str,
    )
    parser.add_argument(
        "-j", "--jobs", help="Number of files to process in parallel.", dest="jobs", type=int
    )
    parser.add_argument(
        "-k",
        "--keep-direct-and-as",
        dest="keep_direct_and_as_imports",
        action="store_true",
        help="Turns off default behavior that removes direct imports when as imports exist.",
    )
    parser.add_argument(
        "-l",
        "--lines",
        help="[Deprecated] The max length of an import line (used for wrapping " "long imports).",
        dest="line_length",
        type=int,
    )
    parser.add_argument("-lai", "--lines-after-imports", dest="lines_after_imports", type=int)
    parser.add_argument("-lbt", "--lines-between-types", dest="lines_between_types", type=int)
    parser.add_argument(
        "--le",
        "--line-ending",
        dest="line_ending",
        help="Forces line endings to the specified value. "
        "If not set, values will be guessed per-file.",
    )
    parser.add_argument(
        "--ls",
        "--length-sort",
        help="Sort imports by their string length.",
        dest="length_sort",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--multi-line",
        dest="multi_line_output",
        choices=WrapModes.__members__,
        type=WrapModes.__getitem__,
        help="Multi line output (0-grid, 1-vertical, 2-hanging, 3-vert-hanging, 4-vert-grid, "
        "5-vert-grid-grouped, 6-vert-grid-grouped-no-comma).",
    )
    inline_args_group.add_argument(
        "--nis",
        "--no-inline-sort",
        dest="no_inline_sort",
        action="store_true",
        help="Leaves `from` imports with multiple imports 'as-is' "
        "(e.g. `from foo import a, c ,b`).",
    )
    parser.add_argument(
        "--nlb",
        "--no-lines-before",
        help="Sections which should not be split with previous by empty lines",
        dest="no_lines_before",
        action="append",
    )
    parser.add_argument(
        "-o",
        "--thirdparty",
        dest="known_third_party",
        action="append",
        help="Force sortImports to recognize a module as being part of a third party library.",
    )
    parser.add_argument(
        "--ot",
        "--order-by-type",
        dest="order_by_type",
        action="store_true",
        help="Order imports by type in addition to alphabetically",
    )
    parser.add_argument(
        "--dt",
        "--dont-order-by-type",
        dest="dont_order_by_type",
        action="store_true",
        help="Don't order imports by type in addition to alphabetically",
    )
    parser.add_argument(
        "-p",
        "--project",
        dest="known_first_party",
        action="append",
        help="Force sortImports to recognize a module as being part of the current python project.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        dest="quiet",
        help="Shows extra quiet output, only errors are outputted.",
    )
    parser.add_argument(
        "--rm",
        "--remove-import",
        dest="remove_imports",
        action="append",
        help="Removes the specified import from all files.",
    )
    parser.add_argument(
        "--rr",
        "--reverse-relative",
        dest="reverse_relative",
        action="store_true",
        help="Reverse order of relative imports.",
    )
    parser.add_argument(
        "--rc",
        "--recursive",
        dest="recursive",
        action="store_true",
        help="Recursively look for Python files of which to sort imports",
    )
    parser.add_argument(
        "-s",
        "--skip",
        help="Files that sort imports should skip over. If you want to skip multiple "
        "files you should specify twice: --skip file1 --skip file2.",
        dest="skip",
        action="append",
    )
    parser.add_argument(
        "--sd",
        "--section-default",
        dest="default_section",
        help="Sets the default section for imports (by default FIRSTPARTY) options: "
        + str(sections.DEFAULT),
    )
    parser.add_argument(
        "--sg",
        "--skip-glob",
        help="Files that sort imports should skip over.",
        dest="skip_glob",
        action="append",
    )
    inline_args_group.add_argument(
        "--sl",
        "--force-single-line-imports",
        dest="force_single_line",
        action="store_true",
        help="Forces all from imports to appear on their own line",
    )
    parser.add_argument(
        "--sp",
        "--settings-path",
        dest="settings_path",
        help="Explicitly set the settings path instead of auto determining based on file location.",
    )
    parser.add_argument(
        "-t",
        "--top",
        help="Force specific imports to the top of their appropriate section.",
        dest="force_to_top",
        action="append",
    )
    parser.add_argument(
        "--tc",
        "--trailing-comma",
        dest="include_trailing_comma",
        action="store_true",
        help="Includes a trailing comma on multi line imports that include parentheses.",
    )
    parser.add_argument(
        "--up",
        "--use-parentheses",
        dest="use_parentheses",
        action="store_true",
        help="Use parenthesis for line continuation on length limit instead of slashes.",
    )
    parser.add_argument("-v", "--version", action="store_true", dest="show_version")
    parser.add_argument(
        "--vb",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Shows verbose output, such as when files are skipped or when a check is successful.",
    )
    parser.add_argument(
        "--virtual-env",
        dest="virtual_env",
        help="Virtual environment to use for determining whether a package is third-party",
    )
    parser.add_argument(
        "--conda-env",
        dest="conda_env",
        help="Conda environment to use for determining whether a package is third-party",
    )
    parser.add_argument(
        "--vn",
        "--version-number",
        action="version",
        version=__version__,
        help="Returns just the current version number without the logo",
    )
    parser.add_argument(
        "-w",
        "--line-width",
        help="The max length of an import line (used for wrapping long imports).",
        dest="line_length",
        type=int,
    )
    parser.add_argument(
        "--wl",
        "--wrap-length",
        dest="wrap_length",
        type=int,
        help="Specifies how long lines that are wrapped should be, if not set line_length is used.",
    )
    parser.add_argument(
        "--ws",
        "--ignore-whitespace",
        action="store_true",
        dest="ignore_whitespace",
        help="Tells isort to ignore whitespace differences when --check-only is being used.",
    )
    parser.add_argument(
        "-y",
        "--apply",
        dest="apply",
        action="store_true",
        help="Tells isort to apply changes recursively without asking",
    )
    parser.add_argument(
        "--unsafe",
        dest="unsafe",
        action="store_true",
        help="Tells isort to look for files in standard library directories, etc. "
        "where it may not be safe to operate in",
    )
    parser.add_argument(
        "--case-sensitive",
        dest="case_sensitive",
        action="store_true",
        help="Tells isort to include casing when sorting module names",
    )
    parser.add_argument(
        "--filter-files",
        dest="filter_files",
        action="store_true",
        help="Tells isort to filter files even when they are explicitly passed in as "
        "part of the command",
    )
    parser.add_argument(
        "files", nargs="*", help="One or more Python source files that need their imports sorted."
    )
    parser.add_argument(
        "--py",
        "--python-version",
        action="store",
        dest="py_version",
        choices=tuple(VALID_PY_TARGETS) + ("auto",),
        help="Tells isort to set the known standard library based on the the specified Python "
        "version. Default is to assume any Python 3 version could be the target, and use a union "
        "off all stdlib modules across versions. If auto is specified, the version of the "
        "interpreter used to run isort "
        f"(currently: {sys.version_info.major}{sys.version_info.minor}) will be used.",
    )

    values = vars(parser.parse_args(argv))
    arguments = {key: value for key, value in vars(parser.parse_args(argv)).items() if value}
    if "dont_order_by_type" in arguments:
        arguments["order_by_type"] = False
    if arguments.pop("unsafe", False):
        arguments["safety_excludes"] = False
    return arguments


def main(argv: Optional[Sequence[str]] = None) -> None:
    arguments = parse_args(argv)
    if arguments.get("show_version"):
        print(ASCII_ART)
        return

    if "settings_path" in arguments:
        sp = arguments["settings_path"]
        arguments["settings_path"] = (
            os.path.abspath(sp) if os.path.isdir(sp) else os.path.dirname(os.path.abspath(sp))
        )
        if not os.path.isdir(arguments["settings_path"]):
            warn(f"settings_path dir does not exist: {arguments['settings_path']}")

    if "virtual_env" in arguments:
        venv = arguments["virtual_env"]
        arguments["virtual_env"] = os.path.abspath(venv)
        if not os.path.isdir(arguments["virtual_env"]):
            warn(f"virtual_env dir does not exist: {arguments['virtual_env']}")

    file_names = arguments.pop("files", [])
    if file_names == ["-"]:
        SortImports(file_contents=sys.stdin.read(), write_to_stdout=True, **arguments)
    else:
        if not file_names:
            file_names = ["."]
            arguments["recursive"] = True
            if not arguments.get("apply", False):
                arguments["ask_to_apply"] = True

        if not "settings_path" in arguments:
            arguments["settings_path"] = os.path.abspath(file_names[0]) or os.getcwd()

        config_dict = arguments.copy()
        config_dict.pop("recursive", False)
        config_dict.pop("ask_to_apply", False)
        jobs = config_dict.pop("jobs", ())
        show_logo = config_dict.pop("show_logo", False)
        filter_files = config_dict.pop("filter_files", False)
        check = config_dict.pop("check", False)
        config = Config(**config_dict)

        wrong_sorted_files = False
        skipped: List[str] = []

        if filter_files:
            filtered_files = []
            for file_name in file_names:
                if config.is_skipped(Path(file_name)):
                    skipped.append(file_name)
                else:
                    filtered_files.append(file_name)
            file_names = filtered_files

        if arguments.get("recursive", False):
            file_names = iter_source_code(file_names, config, skipped)
        num_skipped = 0
        if config.verbose or show_logo:
            print(ASCII_ART)

        if jobs:
            import multiprocessing

            executor = multiprocessing.Pool(jobs)
            attempt_iterator = executor.imap(
                functools.partial(sort_imports, check=check, **config_dict), file_names
            )
        else:
            # https://github.com/python/typeshed/pull/2814
            attempt_iterator = (  # type: ignore
                sort_imports(file_name, check=check, **config_dict) for file_name in file_names
            )

        for sort_attempt in attempt_iterator:
            if not sort_attempt:
                continue
            incorrectly_sorted = sort_attempt.incorrectly_sorted
            if arguments.get("check", False) and incorrectly_sorted:
                wrong_sorted_files = True
            if sort_attempt.skipped:
                num_skipped += 1

        if wrong_sorted_files:
            sys.exit(1)

        num_skipped += len(skipped)
        if num_skipped and not arguments.get("quiet", False):
            if config.verbose:
                for was_skipped in skipped:
                    warn(
                        f"{was_skipped} was skipped as it's listed in 'skip' setting"
                        " or matches a glob in 'skip_glob' setting"
                    )
            print(f"Skipped {num_skipped} files")


if __name__ == "__main__":
    main()
