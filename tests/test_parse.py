from hypothesis_auto import auto_pytest_magic

from isort import parse

auto_pytest_magic(parse.import_comment)
