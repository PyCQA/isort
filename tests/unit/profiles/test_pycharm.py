from functools import partial

from ..utils import isort_test

pycharm_isort_test = partial(isort_test, profile="pycharm")


def test_pycharm_snippet_one():
    pycharm_isort_test(
        """import shutil
import sys
from io import StringIO
from pathlib import Path
from typing import (
    Optional,
    TextIO,
    Union,
    cast
)
from warnings import warn

from isort import core

from . import io
from .exceptions import (
    ExistingSyntaxErrors,
    FileSkipComment,
    FileSkipSetting,
    IntroducedSyntaxErrors
)
from .format import (
    ask_whether_to_apply_changes_to_file,
    create_terminal_printer,
    show_unified_diff
)
from .io import Empty
from .place import module as place_module  # noqa: F401
from .place import module_with_reason as place_module_with_reason  # noqa: F401
from .settings import (
    DEFAULT_CONFIG,
    Config
)


def sort_code_string(
    code: str,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    show_diff: Union[bool, TextIO] = False,
    **config_kwargs,
):
"""
    )
