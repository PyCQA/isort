import locale
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from isort import settings
from isort.format import ask_whether_to_apply_changes_to_file, show_unified_diff
from isort.isort import _SortImports


def determine_file_encoding(file_path: Path, default: str = 'utf-8') -> str:
    # see https://www.python.org/dev/peps/pep-0263/
    pattern = re.compile(br'coding[:=]\s*([-\w.]+)')

    coding = default
    with file_path.open('rb') as f:
        for line_number, line in enumerate(f, 1):
            groups = re.findall(pattern, line)
            if groups:
                coding = groups[0].decode('ascii')
                break
            if line_number > 2:
                break

    return coding


def read_file_contents(file_path: Path, encoding: str, fallback_encoding: str) -> Tuple[Optional[str], Optional[str]]:
    with file_path.open(encoding=encoding, newline='') as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, encoding
        except UnicodeDecodeError:
            pass

    with file_path.open(encoding=fallback_encoding, newline='') as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, fallback_encoding
        except UnicodeDecodeError:
            return None, None


def resolve(path: Path) -> Path:
    if sys.version_info[:2] >= (3, 6):
        return path.resolve()
    else:
        return Path(os.path.abspath(str(path)))


def get_settings_path(settings_path: Optional[Path], current_file_path: Optional[Path]) -> Path:
    if settings_path:
        return settings_path

    if current_file_path:
        return resolve(current_file_path).parent
    else:
        return Path.cwd()


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
            extension: Optional[str] = None,
            **setting_overrides: Any
    ):
        file_path = None if file_path is None else Path(file_path)
        file_name = None
        settings_path = None if settings_path is None else Path(settings_path)

        self.config = settings.prepare_config(get_settings_path(settings_path, file_path),
                                              **setting_overrides)
        self.output = None

        file_encoding = 'utf-8'

        self.file_path = None
        if file_path:
            self.file_path = file_path  # raw file path (unresolved) ?

            absolute_file_path = resolve(file_path)
            if check_skip:
                if run_path and run_path in absolute_file_path.parents:
                    # TODO: Drop str() when isort is Python 3.6+.
                    file_name = os.path.relpath(str(absolute_file_path), run_path)
                else:
                    file_name = str(absolute_file_path)
                    run_path = ''

                if settings.file_should_be_skipped(file_name, self.config, run_path):
                    self.skipped = True
                    if self.config['verbose']:
                        print("WARNING: {0} was skipped as it's listed in 'skip' setting"
                              " or matches a glob in 'skip_glob' setting".format(absolute_file_path))
                    file_contents = None

            if not self.skipped and not file_contents:
                preferred_encoding = determine_file_encoding(absolute_file_path)

                # default encoding for open(mode='r') on the system
                fallback_encoding = locale.getpreferredencoding(False)

                file_contents, used_encoding = read_file_contents(absolute_file_path,
                                                                  encoding=preferred_encoding,
                                                                  fallback_encoding=fallback_encoding)
                if used_encoding is None:
                    self.skipped = True
                    if self.config['verbose']:
                        print("WARNING: {} was skipped as it couldn't be opened with the given "
                              "{} encoding or {} fallback encoding".format(str(absolute_file_path),
                                                                           file_encoding,
                                                                           fallback_encoding))
                else:
                    file_encoding = used_encoding

        if file_contents is None or ("isort:" + "skip_file") in file_contents:
            self.skipped = True
            if write_to_stdout and file_contents:
                sys.stdout.write(file_contents)
            return

        if not extension:
            extension = file_name.split('.')[-1] if file_name else "py"

        self.sorted_imports = _SortImports(file_contents=file_contents,
                                           config=self.config,
                                           extension=extension)
        self.output = self.sorted_imports.output

        if self.config['atomic']:
            logging_file_path = str(self.file_path or '')
            try:
                out_lines_without_top_comment = self.sorted_imports.get_out_lines_without_top_comment()
                compile(out_lines_without_top_comment, logging_file_path, 'exec', 0, 1)
            except SyntaxError:
                self.output = file_contents
                self.incorrectly_sorted = True
                try:
                    in_lines_without_top_comment = self.sorted_imports.get_in_lines_without_top_comment()
                    compile(in_lines_without_top_comment, logging_file_path, 'exec', 0, 1)
                    print("ERROR: {0} isort would have introduced syntax errors, please report to the project!".
                          format(logging_file_path))
                except SyntaxError:
                    print("ERROR: {0} File contains syntax errors.".format(logging_file_path))

                return

        if check:
            check_output = self.output
            check_against = file_contents
            if self.config['ignore_whitespace']:
                check_output = self.sorted_imports.remove_whitespaces(check_output)
                check_against = self.sorted_imports.remove_whitespaces(check_against)

            current_input_sorted_correctly = (self.sorted_imports
                                              .check_if_input_already_sorted(check_output, check_against,
                                                                             logging_file_path=str(self.file_path or '')))
            if current_input_sorted_correctly:
                return
            else:
                self.incorrectly_sorted = True

        if show_diff or self.config['show_diff']:
            show_unified_diff(file_input=file_contents, file_output=self.output,
                              file_path=self.file_path)

        elif write_to_stdout:
            sys.stdout.write(self.output)

        elif self.file_path and not check:
            # if file_name resolves to True, file_path never None or ''
            if self.output == file_contents:
                return

            if ask_to_apply:
                show_unified_diff(file_input=file_contents, file_output=self.output,
                                  file_path=self.file_path)
                apply_changes = ask_whether_to_apply_changes_to_file(str(self.file_path))
                if not apply_changes:
                    return

            with self.file_path.open('w', encoding=file_encoding, newline='') as output_file:
                if not self.config['quiet']:
                    print("Fixing {0}".format(self.file_path))

                output_file.write(self.output)

    @property
    def sections(self):
        return self.sorted_imports.sections

    @property
    def length_change(self) -> int:
        return self.sorted_imports.length_change
