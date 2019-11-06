import re
from pathlib import Path
from typing import Any, NamedTuple, Optional, Tuple

from . import output, parse
from .exceptions import FileSkipComment, IntroducedSyntaxErrors, UnableToDetermineEncoding
from .io import File
from .settings import DEFAULT_CONFIG, FILE_SKIP_COMMENT, Config


def sorted_imports(file_contents: str, extension: str = "py", config: Config=DEFAULT_CONFIG, file_path: Optional[Path]=None, disregard_skip: bool=False, **config_kwargs) -> str:
    content_source = str(file_path or "Passed in content")
    if not disregard_skip:
        if FILE_SKIP_COMMENT in file_contents:
            raise FileSkipComment(content_source)

        elif file_path and config.is_skipped(file_path):
            raise FileSkipSetting(file_path)

    if config_kwargs and config is not DEFAULT_CONFIG:
        raise ValueError("You can either specify custom configuration options using kwargs or "
                         "passing in a Config object. Not Both!")
    elif config_kwargs:
        config = Config(**config_kwargs)

    if config.atomic:
        compile(file_contents, content_source, "exec", 0, 1)

    parsed_output = output.sorted_imports(parse.file_contents(file_contents, config=config), config, extension)
    if config.atomic:
        try:
            compile(file_contents, content_source, "exec", 0, 1)
        except SyntaxError:
            raise IntroducedSyntaxErrors(content_source)
    return parsed_output


def sorted_file(filename: str, config: Config=DEFAULT_CONFIG, **config_kwargs) -> str:
    file_data = File.read(filename)
    if config is DEFAULT_CONFIG and not "settings_path" in config_kwargs and not "settings_file" in config_kwargs:
        config_kwargs["settings_path"] = file_data.path.parent

    return sorted_contents(file_contents=file_data.contents, extension=file_data.path.suffix, config=config, file_path=file_data.path, **config_kwargs)
