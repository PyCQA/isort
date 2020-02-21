import sys
from io import StringIO
from pathlib import Path
from typing import Any, Optional
from warnings import warn

from . import api
from .exceptions import ExistingSyntaxErrors, FileSkipped, IntroducedSyntaxErrors
from .format import ask_whether_to_apply_changes_to_file, show_unified_diff
from .io import File
from .settings import Config


class SortImports:
    incorrectly_sorted = False
    skipped = False

    def __init__(
        self,
        filename: Optional[str] = None,
        file_contents: str = "",
        write_to_stdout: bool = False,
        check: bool = False,
        show_diff: bool = False,
        settings_path: Optional[str] = None,
        ask_to_apply: bool = False,
        run_path: str = "",
        check_skip: bool = True,
        extension: str = "",
        **setting_overrides: Any,
    ):
        file_encoding = "utf-8"
        file_path: Optional[Path] = None
        if filename:
            if file_contents:
                file_data = File.from_contents(file_contents, filename=filename)
            else:
                file_data = File.read(filename)
            file_stream, file_path, file_encoding = file_data
            if not extension:
                extension = file_data.extension
        else:
            file_stream = StringIO(file_contents)

        if settings_path:
            setting_overrides["settings_path"] = settings_path
        elif file_path and "settings_file" not in setting_overrides:
            setting_overrides["settings_path"] = file_path.parent

        config = Config(**setting_overrides)

        try:
            if check:
                self.incorrectly_sorted = not api.check_imports(
                    file_stream,
                    extension=extension,
                    config=config,
                    file_path=file_path,
                    show_diff=show_diff,
                )
                self.output = ""
                return
            else:
                output_stream = StringIO()
                api.sorted_imports(
                    file_stream,
                    output_stream,
                    extension=extension,
                    config=config,
                    file_path=file_path,
                )
                output_stream.seek(0)
                self.output = output_stream.read()
        except FileSkipped as error:
            self.skipped = True
            self.output = ""
            if config.verbose:
                warn(str(error))
            return
        except ExistingSyntaxErrors:
            warn("{file_path} unable to sort due to existing syntax errors")
            self.output = file_contents
            return
        except IntroducedSyntaxErrors:
            warn("{file_path} unable to sort as isort introduces new syntax errors")
            self.output = file_contents
            return

        if show_diff:
            show_unified_diff(
                file_input=file_contents, file_output=self.output, file_path=file_path
            )

        elif write_to_stdout:
            sys.stdout.write(self.output)

        elif file_path and not check:
            # if file_name resolves to True, file_path never None or ''
            if self.output == file_contents:
                return

            if ask_to_apply:
                show_unified_diff(
                    file_input=file_contents, file_output=self.output, file_path=file_path
                )
                apply_changes = ask_whether_to_apply_changes_to_file(str(file_path))
                if not apply_changes:
                    return

            with file_path.open("w", encoding=file_encoding, newline="") as output_file:
                if not config.quiet:
                    print(f"Fixing {file_path}")

                output_file.write(self.output)
