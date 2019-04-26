import locale
import os
import re
import sys
from typing import Any, Optional, Tuple

from isort import settings
from isort.format import ask_whether_to_apply_changes_to_file, show_unified_diff
from isort.isort import _SortImports


def determine_file_encoding(fname: str, default: str = 'utf-8') -> str:
    # see https://www.python.org/dev/peps/pep-0263/
    pattern = re.compile(br'coding[:=]\s*([-\w.]+)')

    coding = default
    with open(fname, 'rb') as f:
        for line_number, line in enumerate(f, 1):
            groups = re.findall(pattern, line)
            if groups:
                coding = groups[0].decode('ascii')
                break
            if line_number > 2:
                break

    return coding


def read_file_contents(file_path: str, encoding: str, fallback_encoding: str) -> Tuple[Optional[str], Optional[str]]:
    with open(file_path, encoding=encoding, newline='') as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, encoding
        except UnicodeDecodeError:
            pass

    with open(file_path, encoding=fallback_encoding, newline='') as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, fallback_encoding
        except UnicodeDecodeError:
            return None, None


def get_settings_path(settings_path: Optional[str], current_file_path: Optional[str]) -> str:
    if settings_path:
        return settings_path

    if current_file_path:
        return os.path.dirname(os.path.abspath(current_file_path))
    else:
        return os.getcwd()


class SortImports(object):
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
            run_path: str = '',
            check_skip: bool = True,
            **setting_overrides: Any
    ):
        self.config = settings.prepare_config(get_settings_path(settings_path, file_path),
                                              **setting_overrides)
        self.output = None

        file_encoding = 'utf-8'
        file_name = file_path

        self.file_path = file_path or ""
        if file_path:
            file_path = os.path.abspath(file_path)
            if check_skip:
                if run_path and file_path.startswith(run_path):
                    file_name = os.path.relpath(file_path, run_path)
                else:
                    file_name = file_path
                    run_path = ''

                if settings.file_should_be_skipped(file_name, self.config, run_path):
                    self.skipped = True
                    if self.config['verbose']:
                        print("WARNING: {0} was skipped as it's listed in 'skip' setting"
                              " or matches a glob in 'skip_glob' setting".format(file_path))
                    file_contents = None

            if not self.skipped and not file_contents:
                preferred_encoding = determine_file_encoding(file_path)

                # default encoding for open(mode='r') on the system
                fallback_encoding = locale.getpreferredencoding(False)

                file_contents, used_encoding = read_file_contents(file_path,
                                                                  encoding=preferred_encoding,
                                                                  fallback_encoding=fallback_encoding)
                if used_encoding is None:
                    self.skipped = True
                    if self.config['verbose']:
                        print("WARNING: {} was skipped as it couldn't be opened with the given "
                              "{} encoding or {} fallback encoding".format(file_path,
                                                                           file_encoding,
                                                                           fallback_encoding))
                else:
                    file_encoding = used_encoding

        if file_contents is None or ("isort:" + "skip_file") in file_contents:
            self.skipped = True
            if write_to_stdout and file_contents:
                sys.stdout.write(file_contents)
            return

        self.sorted_imports = _SortImports(file_contents=file_contents,
                                           config=self.config)
        self.output = self.sorted_imports.output

        if self.config['atomic']:
            try:
                out_lines_without_top_comment = self.sorted_imports.get_out_lines_without_top_comment()
                compile(out_lines_without_top_comment, self.file_path, 'exec', 0, 1)
            except SyntaxError:
                self.output = file_contents
                self.incorrectly_sorted = True
                try:
                    in_lines_without_top_comment = self.sorted_imports.get_in_lines_without_top_comment()
                    compile(in_lines_without_top_comment, self.file_path, 'exec', 0, 1)
                    print("ERROR: {0} isort would have introduced syntax errors, please report to the project!".
                          format(self.file_path))
                except SyntaxError:
                    print("ERROR: {0} File contains syntax errors.".format(self.file_path))

                return

        if check:
            check_output = self.output
            check_against = file_contents
            if self.config['ignore_whitespace']:
                check_output = check_output.replace(self.sorted_imports.line_separator, "").replace(" ", "").replace("\x0c", "")
                check_against = check_against.replace(self.sorted_imports.line_separator, "").replace(" ", "").replace("\x0c", "")

            current_input_sorted_correctly = self.sorted_imports.check_if_input_already_sorted(check_output, check_against,
                                                                                               current_file_path=self.file_path)
            if current_input_sorted_correctly:
                return
            else:
                self.incorrectly_sorted = True

        if show_diff or self.config['show_diff']:
            show_unified_diff(file_input=file_contents, file_output=self.output,
                              file_path=self.file_path)

        elif write_to_stdout:
            sys.stdout.write(self.output)

        elif file_name and not check:
            if self.output == file_contents:
                return

            if ask_to_apply:
                show_unified_diff(file_input=file_contents, file_output=self.output,
                                  file_path=self.file_path)
                apply_changes = ask_whether_to_apply_changes_to_file(self.file_path)
                if not apply_changes:
                    return

            with open(self.file_path, 'w', encoding=file_encoding, newline='') as output_file:
                if not self.config['quiet']:
                    print("Fixing {0}".format(self.file_path))

                output_file.write(self.output)

    @property
    def sections(self):
        return self.sorted_imports.sections

    @property
    def length_change(self) -> int:
        return self.sorted_imports.length_change
