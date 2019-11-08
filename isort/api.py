import re
from pathlib import Path
from typing import Any, NamedTuple, Optional, Tuple

from . import output, parse
from .exceptions import FileSkipComment, IntroducedSyntaxErrors, UnableToDetermineEncoding, ExistingSyntaxErrors, FileSkipSetting
from .io import File
from .format import remove_whitespace
from .settings import DEFAULT_CONFIG, FILE_SKIP_COMMENT, Config


def _config(path: Optional[Path]=None, config: Config=DEFAULT_CONFIG, **config_kwargs) -> Config:
    if path:
        if config is DEFAULT_CONFIG and not "settings_path" in config_kwargs and not "settings_file" in config_kwargs:
            config_kwargs["settings_path"] = path

    if config_kwargs and config is not DEFAULT_CONFIG:
        raise ValueError("You can either specify custom configuration options using kwargs or "
                         "passing in a Config object. Not Both!")
    elif config_kwargs:
        config = Config(**config_kwargs)

    return config


def sorted_imports(file_contents: str, extension: str = "py", config: Config=DEFAULT_CONFIG, file_path: Optional[Path]=None, disregard_skip: bool=False, **config_kwargs) -> str:
    config = _config(config=config, **config_kwargs)
    content_source = str(file_path or "Passed in content")
    if not disregard_skip:
        if FILE_SKIP_COMMENT in file_contents:
            raise FileSkipComment(content_source)

        elif file_path and config.is_skipped(file_path):
            raise FileSkipSetting(file_path)

    if config.atomic:
        try:
            compile(file_contents, content_source, "exec", 0, 1)
        except SyntaxError:
            raise ExistingSyntaxErrors(content_source)

    parsed_output = output.sorted_imports(parse.file_contents(file_contents, config=config), config, extension)
    if config.atomic:
        try:
            compile(file_contents, content_source, "exec", 0, 1)
        except SyntaxError:
            raise IntroducedSyntaxErrors(content_source)
    return parsed_output


def check_imports(file_contents: str, show_diff: bool=False, extension: str = "py", config: Config=DEFAULT_CONFIG, file_path: Optional[Path]=None, disregard_skip: bool=False, **config_kwargs) -> str:
    config = _config(config=config, **config_kwargs)

    sorted_output = sorted_imports(file_contents=file_contents, extension=extension, config=config, file_path=file_path, disregard_skip=disregard_skip, **config_kwargs)
    if config.ignore_whitespace:
        line_separator = config.line_ending or parse._infer_line_separator(file_contents)
        compare_in = remove_whitespace(file_contents, line_separator=line_separator).strip()
        compare_out = remove_whitespace(sorted_output, line_separator=line_separator).strip()
    else:
        compare_in = file_contents.strip()
        compare_out = sorted_output.strip()

    if compare_out == compare_in:
        if config.verbose:
            print(f"SUCCESS: {file_path or ''} Everything Looks Good!")
        return True
    else:
        print(f"ERROR: {file_path or ''} Imports are incorrectly sorted.")
        if show_diff:
            show_unified_diff(
                file_input=file_contents, file_output=sorted_output, file_path=file_path
            )
        return False


def sorted_file(filename: str, config: Config=DEFAULT_CONFIG, **config_kwargs) -> str:
    file_data = File.read(filename)
    config = _config(path=file_data.path.parent, config=config)
    return sorted_contents(file_contents=file_data.contents, extension=file_data.extension, config=config, file_path=file_data.path, **config_kwargs)
