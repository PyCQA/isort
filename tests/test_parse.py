import sys

from isort import parse

if sys.version_info[1] > 5:
    from hypothesis_auto import auto_pytest_magic

    auto_pytest_magic(parse.import_comment)
