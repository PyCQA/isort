from hypothesis_auto import auto_pytest_magic

import sys
from isort import output

auto_pytest_magic(output.with_comments, auto_allow_exceptions_=(ValueError,))
