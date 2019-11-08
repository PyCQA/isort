"""Defines any IO utilities used by isort"""
import locale
import re
from pathlib import Path
from typing import NamedTuple, Optional, Tuple

from .exceptions import UnableToDetermineEncoding

_ENCODING_PATTERN = re.compile(br"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")


class File(NamedTuple):
    contents: str
    path: Path
    encoding: str

    @staticmethod
    def read(filename: str) -> "File":
        file_path = Path(filename).resolve()
        contents, encoding = _read_file_contents(file_path)
        return File(contents=contents, path=file_path, encoding=encoding)

    @staticmethod
    def from_contents(contents: str, filename: str) -> "File":
        return File(
            contents, path=Path(filename).resolve(), encoding=_determine_content_encoding(contents)
        )

    @property
    def extension(self):
        return self.path.suffix.lstrip(".")


def _determine_stream_encoding(stream, default: str = "utf-8") -> str:
    for line_number, line in enumerate(stream, 1):
        if line_number > 2:
            break
        groups = re.findall(_ENCODING_PATTERN, line)
        if groups:
            return groups[0].decode("ascii")

    return default


def _determine_content_encoding(content: str, default: str = "utf-8"):
    return _determine_stream_encoding(content.encode(default).split(b"\n"), default=default)


def _determine_file_encoding(file_path: Path, default: str = "utf-8") -> str:
    # see https://www.python.org/dev/peps/pep-0263/
    with file_path.open("rb") as open_file:
        return _determine_stream_encoding(open_file, default=default)


def _read_file_contents(file_path: Path) -> Tuple[str, str]:
    encoding = _determine_file_encoding(file_path)
    with file_path.open(encoding=encoding, newline="") as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, encoding
        except UnicodeDecodeError:
            pass

    # Try default encoding for open(mode='r') on the system
    fallback_encoding = locale.getpreferredencoding(False)
    with file_path.open(encoding=fallback_encoding, newline="") as file_to_import_sort:
        try:
            file_contents = file_to_import_sort.read()
            return file_contents, fallback_encoding
        except UnicodeDecodeError:
            pass

    raise UnableToDetermineEncoding(file_path, encoding, fallback_encoding)
