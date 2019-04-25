from typing import Optional, Any

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
        self.sorted_imports = _SortImports(file_path, file_contents, write_to_stdout, check, show_diff, settings_path,
                                           ask_to_apply, run_path, check_skip, **setting_overrides)

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
