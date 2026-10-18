import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from isort import io
from isort.exceptions import UnsupportedEncoding


class TestFile:
    @pytest.mark.skipif(sys.platform == "win32", reason="Can't run file encoding test in AppVeyor")
    def test_read(self, tmp_path: Path) -> None:
        test_file_content = """# -*- encoding: ascii -*-

import Ὡ
"""
        test_file = tmp_path / "file.py"
        test_file.write_text(test_file_content)
        with pytest.raises(UnicodeDecodeError):
            with io.File.read(str(test_file)) as file_handler:
                file_handler.stream.read()

    def test_from_content(self, tmp_path: Path) -> None:
        test_file = tmp_path / "file.py"
        test_file.write_text("import os", "utf8")
        file_obj = io.File.from_contents("import os", filename=str(test_file))
        assert file_obj
        assert file_obj.extension == "py"

    def test_open(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            io.File._open("THISCANTBEAREALFILEὩὩὩὩὩὩὩὩὩὩὩὩ.ὩὩὩὩὩ")

        def raise_arbitrary_exception(*args: object, **kwargs: object) -> None:
            raise RuntimeError("test")

        test_file = tmp_path / "file.py"
        test_file.write_text("import os")
        assert io.File._open(str(test_file))

        # correctly responds to error determining encoding
        with patch("tokenize.detect_encoding", raise_arbitrary_exception):
            with pytest.raises(UnsupportedEncoding):
                io.File._open(str(test_file))
