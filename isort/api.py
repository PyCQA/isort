from .settings import Config, DEFAULT_CONFIG, FILE_SKIP_COMMENT
from . import parse, output
from .exceptions import UnableToDetermineEncoding, FileSkipComment, IntroducedSyntaxErrors
import re
from pathlib import Path
from typing import Any, Optional, Tuple, NamedTuple
from .io import File


def sorted_contents(file_contents: str, extension: str = "py", config: Config=DEFAULT_CONFIG, file_path: Optional[Path]=None, disregard_skip: bool=False, **config_kwargs) -> str:
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

    if settings.atomic:
        compile(file_contents, content_source, "exec", 0, 1)

    parsed_output = output.sorted_imports(parse.file_contents(file_contents, config=config), config, extension)
    if settings.atomic:
        try:
            compile(file_contents, content_source, "exec", 0, 1)
        except SyntaxError:
            raise IntroducedSyntaxErrors(content_source)
    return parsed_output


def sorted_file(filename: str, config: Config=DEFAULT_CONFIG, **config_kwargs) -> str:
    file_data = File.read(filename)
    if config_kwargs or config is DEFAULT_CONFIG:
        if not "settings_path" in config_kwargs and not "settings_file" in config_kwargs:
            config_kwargs["settings_path"] = file_data.path.parent

    return sorted_contents(file_contents=file_data.contents, extension=file_data.path.suffix, config=config, file_path=file_data.path, **config_kwargs)
