import os
import sys

import pytest

from isort import main


def test_is_python_file():
    assert main.is_python_file("file.py")
    assert main.is_python_file("file.pyi")
    assert main.is_python_file("file.pyx")
    assert not main.is_python_file("file.pyc")
    assert not main.is_python_file("file.txt")


@pytest.mark.skipif(sys.platform == "win32", reason="cannot create fifo file on Windows platform")
def test_is_python_file_fifo(tmpdir):
    fifo_file = os.path.join(tmpdir, "fifo_file")
    os.mkfifo(fifo_file)
    assert not main.is_python_file(fifo_file)


def test_isort_command():
    """Ensure ISortCommand got registered, otherwise setuptools error must have occured"""
    assert main.ISortCommand
