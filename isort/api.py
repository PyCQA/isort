from .settings import Config, DEFAULT_CONFIG
from . import parse, output
from .exceptions import UnableToDetermineEncoding
import re
from pathlib import Path
from typing import Any, Optional, Tuple

_ENCODING_PATTERN = re.compile(br"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")


def sorted_contents(file_contents: str, extension: str = "py", config: Config=DEFAULT_CONFIG, **config_kwargs) -> str:
    if config_kwargs and config is not DEFAULT_CONFIG:
        raise ValueError("You can either specify custom configuration options using kwargs or "
                         "passing in a Config object. Not Both!")
    elif config_kwargs:
        config = Config(**config_kwargs)

    return output.sorted_imports(parse.file_contents(file_contents, config=config), config, extension)


def sorted_file(filename: str, config: Config=DEFAULT_CONFIG, **config_kwargs) -> str:
    file_path = Path(filename).resolve()
    if config_kwargs or config is DEFAULT_CONFIG:
        if not "settings_path" in config_kwargs and not "settings_file" in config_kwargs:
            config_kwargs["settings_path"] = file_path.parent

    contents, used_encoding = _read_file_contents(file_path)
    return sorted_contents(file_contents=contents, extension=file_path.suffix, config=config, **config_kwargs)


def _determine_file_encoding(file_path: Path, default: str = "utf-8") -> str:
    # see https://www.python.org/dev/peps/pep-0263/
    coding = default
    with file_path.open("rb") as f:
        for line_number, line in enumerate(f, 1):
            if line_number > 2:
                break
            groups = re.findall(_ENCODING_PATTERN, line)
            if groups:
                coding = groups[0].decode("ascii")
                break

    return coding


def _read_file_contents(
    file_path: Path
) -> Tuple[Optional[str], Optional[str]]:
    encoding = _determine_file_encoding(file_path)
    with file_path.open(encoding=encoding, newline="") as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, encoding
        except UnicodeDecodeError:
            pass

    # Try default encoding for open(mode='r') on the system
    fallback_encoding = _locale.getpreferredencoding(False)
    with file_path.open(encoding=fallback_encoding, newline="") as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, fallback_encoding
        except UnicodeDecodeError:
            pass

    raise UnableToDetermineEncoding(file_path, encoding, fallback_encoding)
