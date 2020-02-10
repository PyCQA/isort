from hypothesis_auto import auto_pytest_magic

from isort import comments

auto_pytest_magic(comments.parse)
auto_pytest_magic(comments.add_to_line)
