import locale
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional, Tuple
from warnings import warn

from isort import settings, api
from isort.format import ask_whether_to_apply_changes_to_file, show_unified_diff
from isort.isort import _SortImports
from .io import File
from .exceptions import FileSkipped



def get_settings_path(settings_path: Optional[Path], current_file_path: Optional[Path]) -> Path:
    if settings_path:
        return settings_path

    if current_file_path:
        return current_file_path.resolve().parent
    else:
        return Path.cwd()


class SortImports:
    incorrectly_sorted = False
    skipped = False

    def __init__(
        self,
        file_path: Optional[str] = None,
        file_contents: Optional[str] = None,
        write_to_stdout: bool = False,
        check: bool = False,
        show_diff: bool = False,
        settings_path: Optional[str] = None,
        ask_to_apply: bool = False,
        run_path: str = "",
        check_skip: bool = True,
        extension: Optional[str] = None,
        **setting_overrides: Any,
    ):
        file_encoding = "utf-8"

        self.file_path = None
        try:
            if file_path:
                file_contents, file_path, file_encoding = File.read(file_path)
                extension = file_path.suffix

            self.output = api.sorted_imports(file_contents, extension=extension, **setting_overrides)
        except FileSkipped as error:
            if self.config["verbose"]:
                warn(error.message)

        if check:
            check_output = self.output
            check_against = file_contents
            if self.config["ignore_whitespace"]:
                check_output = self.sorted_imports.remove_whitespaces(check_output)
                check_against = self.sorted_imports.remove_whitespaces(check_against)

            current_input_sorted_correctly = self.sorted_imports.check_if_input_already_sorted(
                check_output, check_against, logging_file_path=str(self.file_path or "")
            )
            if current_input_sorted_correctly:
                return
            else:
                self.incorrectly_sorted = True

        if show_diff or self.config["show_diff"]:
            show_unified_diff(
                file_input=file_contents, file_output=self.output, file_path=self.file_path
            )

        elif write_to_stdout:
            sys.stdout.write(self.output)

        elif self.file_path and not check:
            # if file_name resolves to True, file_path never None or ''
            if self.output == file_contents:
                return

            if ask_to_apply:
                show_unified_diff(
                    file_input=file_contents, file_output=self.output, file_path=self.file_path
                )
                apply_changes = ask_whether_to_apply_changes_to_file(str(self.file_path))
                if not apply_changes:
                    return

            with self.file_path.open("w", encoding=file_encoding, newline="") as output_file:
                if not self.config["quiet"]:
                    print(f"Fixing {self.file_path}")

                output_file.write(self.output)

    @property
    def sections(self):
        return self.sorted_imports.parsed.sections

    @property
    def length_change(self) -> int:
        return self.sorted_imports.parsed.change_count
