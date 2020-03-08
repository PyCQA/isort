import os
import sys

import pytest
from hypothesis_auto import auto_pytest_magic

from isort import main
from isort._version import __version__
from isort.settings import DEFAULT_CONFIG

auto_pytest_magic(main.sort_imports)


def test_iter_source_code(tmpdir):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    assert tuple(main.iter_source_code((tmp_file,), DEFAULT_CONFIG, [])) == (tmp_file,)


def test_is_python_file():
    assert main.is_python_file("file.py")
    assert main.is_python_file("file.pyi")
    assert main.is_python_file("file.pyx")
    assert not main.is_python_file("file.pyc")
    assert not main.is_python_file("file.txt")
    assert not main.is_python_file("file.pex")


def test_ascii_art(capsys):
    main.main(["--version"])
    out, error = capsys.readouterr()
    assert (
        out
        == f"""
                 _                 _
                (_) ___  ___  _ __| |_
                | |/ _/ / _ \\/ '__  _/
                | |\\__ \\/\\_\\/| |  | |_
                |_|\\___/\\___/\\_/   \\_/

      isort your imports, so you don't have to.

                    VERSION {__version__}

"""
    )
    assert error == ""


@pytest.mark.skipif(sys.platform == "win32", reason="cannot create fifo file on Windows platform")
def test_is_python_file_fifo(tmpdir):
    fifo_file = os.path.join(tmpdir, "fifo_file")
    os.mkfifo(fifo_file)
    assert not main.is_python_file(fifo_file)


def test_isort_command():
    """Ensure ISortCommand got registered, otherwise setuptools error must have occured"""
    assert main.ISortCommand
