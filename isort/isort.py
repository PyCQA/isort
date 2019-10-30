"""Exposes a simple library to sort through imports within Python code

usage:
    SortImports(file_name)
or:
    sorted = SortImports(file_contents=file_contents).output
"""
import copy
import itertools
import re
from collections import OrderedDict, defaultdict, namedtuple
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from isort import utils

from . import output, parse, settings, sorting, wrap
from .finders import FindersManager


class _SortImports:
    def __init__(self, file_contents: str, config: Dict[str, Any], extension: str = "py") -> None:
        self.config = config

        self.parsed = parse.file_contents(file_contents, config=self.config)
        if self.parsed.import_index != -1:
            self.out_lines = output.sorted_imports(self.parsed, self.config, extension)
        else:
            self.out_lines = self.parsed.lines_without_imports

        while self.out_lines and self.out_lines[-1].strip() == "":
            self.out_lines.pop(-1)

        self.out_lines.append("")
        self.output = self.parsed.line_separator.join(self.out_lines)

    def remove_whitespaces(self, contents: str) -> str:
        contents = (
            contents.replace(self.parsed.line_separator, "").replace(" ", "").replace("\x0c", "")
        )
        return contents

    def get_out_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.out_lines, self.parsed.line_separator)

    def get_in_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.parsed.in_lines, self.parsed.line_separator)

    def check_if_input_already_sorted(
        self, output: str, check_against: str, *, logging_file_path: str
    ) -> bool:
        if output.strip() == check_against.strip():
            if self.config["verbose"]:
                print(f"SUCCESS: {logging_file_path} Everything Looks Good!")
            return True

        print(f"ERROR: {logging_file_path} Imports are incorrectly sorted.")
        return False

    @staticmethod
    def _strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
        """Strips # comments that exist at the top of the given lines"""
        lines = copy.copy(lines)
        while lines and lines[0].startswith("#"):
            lines = lines[1:]
        return line_separator.join(lines)
