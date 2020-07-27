from hypothesis_auto import auto_pytest_magic

from isort import comments

auto_pytest_magic(comments.parse)
auto_pytest_magic(comments.add_to_line)


def test_add_to_line():
    assert comments.add_to_line([], "import os  # comment", removed=True).strip() == "import os"
