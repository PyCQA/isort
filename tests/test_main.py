import os
from isort import main


def test_is_python_file(tmpdir):
    assert main.is_python_file("file.py")
    assert main.is_python_file("file.pyi")
    assert main.is_python_file("file.pyx")
    assert not main.is_python_file("file.pyc")
    assert not main.is_python_file("file.txt")

    fifo_file = os.path.join(tmpdir, "fifo_file")
    os.mkfifo(fifo_file)
    assert not main.is_python_file(fifo_file)



