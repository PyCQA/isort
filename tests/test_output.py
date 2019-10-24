import sys

from isort import output

if sys.version_info[1] > 5:
    from hypothesis_auto import auto_pytest_magic

    auto_pytest_magic(output.with_comments, auto_allow_exceptions_=(ValueError,))
