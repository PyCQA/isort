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

from . import output, parse, settings, wrap, sorting, output
from .finders import FindersManager
from .natural import nsorted


class _SortImports:

    def __init__(self, file_contents: str, config: Dict[str, Any], extension: str = "py") -> None:
        self.config = config
        self.extension = extension

        parsed = parse.file_contents(file_contents, config=self.config)
        (
            self.in_lines,
            self.out_lines,
            self.import_index,
            self.place_imports,
            self.import_placements,
            self.as_map,
            self.imports,
            self.comments,
            self._first_comment_index_start,
            self._first_comment_index_end,
            self.length_change,
            self.original_num_of_lines,
            self.line_separator,
            self.sections,
            self._section_comments,
        ) = parsed

        if self.import_index != -1:
            self.out_lines = output.with_formatted_imports(parsed, self.config, self.extension)
        while self.out_lines and self.out_lines[-1].strip() == "":
            self.out_lines.pop(-1)
        self.out_lines.append("")
        self.output = self.line_separator.join(self.out_lines)

    def remove_whitespaces(self, contents: str) -> str:
        contents = contents.replace(self.line_separator, "").replace(" ", "").replace("\x0c", "")
        return contents

    def get_out_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.out_lines, self.line_separator)

    def get_in_lines_without_top_comment(self) -> str:
        return self._strip_top_comments(self.in_lines, self.line_separator)

    def check_if_input_already_sorted(
        self, output: str, check_against: str, *, logging_file_path: str
    ) -> bool:
        if output.strip() == check_against.strip():
            if self.config["verbose"]:
                print("SUCCESS: {} Everything Looks Good!".format(logging_file_path))
            return True

        print("ERROR: {} Imports are incorrectly sorted.".format(logging_file_path))
        return False

    @staticmethod
    def _strip_top_comments(lines: Sequence[str], line_separator: str) -> str:
        """Strips # comments that exist at the top of the given lines"""
        lines = copy.copy(lines)
        while lines and lines[0].startswith("#"):
            lines = lines[1:]
        return line_separator.join(lines)
