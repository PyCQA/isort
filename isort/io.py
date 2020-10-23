"""Defines any IO utilities used by isort"""
import io
import re
import tokenize
from contextlib import contextmanager
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
from typing import BinaryIO
from typing import Iterator, NamedTuple, TextIO, Union
from typing import Tuple

from isort.exceptions import UnsupportedEncoding

_ENCODING_PATTERN = re.compile(br"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")


class File(NamedTuple):
    stream: TextIO
    path: Path
    encoding: str
    newline: str

    @staticmethod
    def decode_bytes(filename: str, buffer: BinaryIO) -> Tuple[TextIO, str, str]:
        try:
            encoding, lines = tokenize.detect_encoding(buffer.readline)
        except Exception:
            raise UnsupportedEncoding(filename)

        if not lines:
            newline = "\n"
        elif b"\r\n" == lines[0][-2:]:
            newline = "\r\n"
        elif b"\r" == lines[0][-1:]:
            newline = "\r"
        else:
            newline = "\n"

        buffer.seek(0)
        text = io.TextIOWrapper(buffer, encoding, line_buffering=True)
        return text, encoding, newline

    @staticmethod
    def from_contents(contents: str, filename: str) -> "File":
        text, encoding, newline = File.decode_bytes(filename, BytesIO(contents.encode("utf-8")))
        return File(StringIO(contents), path=Path(filename).resolve(), encoding=encoding, newline=newline)

    @property
    def extension(self):
        return self.path.suffix.lstrip(".")

    @staticmethod
    @contextmanager
    def read(filename: Union[str, Path]) -> Iterator["File"]:
        file_path = Path(filename).resolve()
        buffer = None
        try:
            buffer = open(filename, "rb")
            stream, encoding, newline = File.decode_bytes(filename, buffer)
            yield File(stream=stream, path=file_path, encoding=encoding, newline=newline)
        finally:
            if buffer is not None:
                buffer.close()


class _EmptyIO(StringIO):
    def write(self, *args, **kwargs):
        pass


Empty = _EmptyIO()
