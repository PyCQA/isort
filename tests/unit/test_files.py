from isort import files
from isort.settings import DEFAULT_CONFIG


def test_find(tmpdir):
    tmp_file = tmpdir.join("file.py")
    tmp_file.write("import os, sys\n")
    assert tuple(files.find((tmp_file,), DEFAULT_CONFIG, [], [])) == (tmp_file,)
