import glob
import os
import sys
from typing import Any, Dict, Iterator, List
from warnings import warn

import setuptools

from . import SortImports
from .settings import DEFAULT_CONFIG, Config


class ISortCommand(setuptools.Command):
    """The :class:`ISortCommand` class is used by setuptools to perform
    imports checks on registered modules.
    """

    description = "Run isort on modules registered in setuptools"
    user_options: List[Any] = []

    def initialize_options(self) -> None:
        default_settings = vars(DEFAULT_CONFIG).copy()
        for key, value in default_settings.items():
            setattr(self, key, value)

    def finalize_options(self) -> None:
        "Get options from config files."
        self.arguments: Dict[str, Any] = {}
        computed_settings = vars(Config(directory=os.getcwd()))
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
