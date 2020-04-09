import sys
from unittest.mock import MagicMock, patch

import pytest

from isort import io


class TestFile:
    @pytest.mark.skipif(sys.platform == "win32", reason="Can't run file encoding test in AppVeyor")
    def test_read(self, tmpdir):
        test_file_content = """# -*- encoding: ascii -*-

import ☺
"""
        test_file = tmpdir.join("file.py")
        test_file.write(test_file_content)
