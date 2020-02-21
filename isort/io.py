"""Defines any IO utilities used by isort"""
import locale
import re
import tokenize
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from typing import List, NamedTuple, Optional, TextIO, Tuple

from .exceptions import UnableToDetermineEncoding

_ENCODING_PATTERN = re.compile(br"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")


class File(NamedTuple):
    contents: TextIO
    path: Path
    encoding: str

    @staticmethod
    def read(filename: str) -> "File":
        file_path = Path(filename).resolve()
        stream = File._open(file_path)
        return File(contents=stream, path=file_path, encoding=stream.encoding)

    @staticmethod
    def from_contents(contents: str, filename: str) -> "File":
        encoding, lines = tokenize.detect_encoding(BytesIO(contents.encode("utf-8")).readline)
        return File(StringIO(contents), path=Path(filename).resolve(), encoding=encoding)

    @property
    def extension(self):
        return self.path.suffix.lstrip(".")

    @staticmethod
    def _open(filename):
        """Open a file in read only mode using the encoding detected by
        detect_encoding().
        """
        buffer = open(filename, "rb")
        try:
            encoding, lines = tokenize.detect_encoding(buffer.readline)
            buffer.seek(0)
            text = TextIOWrapper(buffer, encoding, line_buffering=True, newline="")
            return text
        except Exception:
            buffer.close()
            raise


class _EmptyIO(StringIO):
    def write(self, *args, **kwargs):
        pass


Empty = _EmptyIO()
