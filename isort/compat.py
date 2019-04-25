import locale
import os
import sys
from typing import Any, Optional

from isort import settings
from isort.format import ask_whether_to_apply_changes_to_file, show_unified_diff
from isort.isort import _SortImports, determine_file_encoding, read_file_contents


class SortImports(object):
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
        _settings_path = settings_path
        if _settings_path is None:
            if file_path:
                _settings_path = os.path.dirname(os.path.abspath(file_path))
            else:
                _settings_path = os.getcwd()

        self.config = settings.prepare_config(_settings_path, **setting_overrides)
        self.output = None

        file_encoding = 'utf-8'
        file_name = file_path

        self.skipped = False

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
            # self.output = None
            if write_to_stdout and file_contents:
                sys.stdout.write(file_contents)
            return

        self.sorted_imports = _SortImports(file_path=self.file_path,
                                           file_contents=file_contents,
                                           check=check,
                                           config=self.config)
        self.output = self.sorted_imports.output

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
    def incorrectly_sorted(self):
        return self.sorted_imports.incorrectly_sorted

    @property
    def length_change(self) -> int:
        return self.sorted_imports.length_change
