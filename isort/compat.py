import os
from typing import Any, Optional

from isort import settings
from isort.isort import _SortImports


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

        config = settings.prepare_config(_settings_path, **setting_overrides)

        self.sorted_imports = _SortImports(file_path=file_path,
                                           file_contents=file_contents,
                                           write_to_stdout=write_to_stdout,
                                           check=check,
                                           show_diff=show_diff,
                                           ask_to_apply=ask_to_apply,
                                           run_path=run_path,
                                           check_skip=check_skip,
                                           config=config)

    @property
    def config(self):
        return self.sorted_imports.config

    @property
    def sections(self):
        return self.sorted_imports.sections

    @property
    def incorrectly_sorted(self):
        return self.sorted_imports.incorrectly_sorted

    @property
    def skipped(self) -> bool:
        return self.sorted_imports.skipped

    @property
    def length_change(self) -> int:
        return self.sorted_imports.length_change

    @property
    def output(self):
        return self.sorted_imports.output
