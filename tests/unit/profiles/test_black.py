import black

import isort


def black_format(code: str, is_pyi: bool = False, line_length: int = 88) -> str:
    """Formats the provided code snippet using black"""
    try:
        return black.format_file_contents(
            code,
            fast=True,
            mode=black.FileMode(
                is_pyi=is_pyi,
                line_length=line_length,
            ),
        )
    except black.NothingChanged:
        return code


def black_test(code: str, expected_output: str = ""):
    """Tests that the given code:
    - Behaves the same when formatted multiple times with isort.
    - Agrees with black formatting.
    - Matches the desired output or itself if none is provided.
    """
    expected_output = expected_output or code

    # output should stay consistent over multiple runs
    output = isort.code(code, profile="black")
    assert output == isort.code(code, profile="black")

    # output should agree with black
    black_output = black_format(output)
    assert output == black_output

    # output should match expected output
    assert output == expected_output


def test_black_snippet_one():
    """Test consistent code formatting between isort and black for code snippet from black repository.
    See: https://github.com/psf/black/blob/master/tests/test_black.py
    """
    black_test(
        """#!/usr/bin/env python3
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from functools import partial
import inspect
from io import BytesIO, TextIOWrapper
import os
from pathlib import Path
from platform import system
import regex as re
import sys
from tempfile import TemporaryDirectory
import types
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    Generator,
    List,
    Tuple,
    Iterator,
    TypeVar,
)
import unittest
from unittest.mock import patch, MagicMock

import click
from click import unstyle
from click.testing import CliRunner

import black
from black import Feature, TargetVersion

try:
    import blackd
    from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
    from aiohttp import web
except ImportError:
    has_blackd_deps = False
else:
    has_blackd_deps = True

from pathspec import PathSpec

# Import other test classes
from .test_primer import PrimerCLITests  # noqa: F401


DEFAULT_MODE = black.FileMode(experimental_string_processing=True)
""",
        """#!/usr/bin/env python3
import asyncio
import inspect
import logging
import os
import sys
import types
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from functools import partial
from io import BytesIO, TextIOWrapper
from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Tuple,
    TypeVar,
)
from unittest.mock import MagicMock, patch

import black
import click
import regex as re
from black import Feature, TargetVersion
from click import unstyle
from click.testing import CliRunner

try:
    import blackd
    from aiohttp import web
    from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
except ImportError:
    has_blackd_deps = False
else:
    has_blackd_deps = True

from pathspec import PathSpec

# Import other test classes
from .test_primer import PrimerCLITests  # noqa: F401

DEFAULT_MODE = black.FileMode(experimental_string_processing=True)
""",
    )


def test_black_snippet_two():
    """Test consistent code formatting between isort and black for code snippet from black repository.
    See: https://github.com/psf/black/blob/master/tests/test_primer.py
    """
    black_test(
        '''#!/usr/bin/env python3

import asyncio
import sys
import unittest
from contextlib import contextmanager
from copy import deepcopy
from io import StringIO
from os import getpid
from pathlib import Path
from platform import system
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory, gettempdir
from typing import Any, Callable, Generator, Iterator, Tuple
from unittest.mock import Mock, patch

from click.testing import CliRunner

from black_primer import cli, lib


EXPECTED_ANALYSIS_OUTPUT = """\
-- primer results 📊 --
68 / 69 succeeded (98.55%) ✅
1 / 69 FAILED (1.45%) 💩
 - 0 projects disabled by config
 - 0 projects skipped due to Python version
 - 0 skipped due to long checkout
Failed projects:
## black:
 - Returned 69
 - stdout:
Black didn't work
"""
''',
        '''#!/usr/bin/env python3

import asyncio
import sys
import unittest
from contextlib import contextmanager
from copy import deepcopy
from io import StringIO
from os import getpid
from pathlib import Path
from platform import system
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory, gettempdir
from typing import Any, Callable, Generator, Iterator, Tuple
from unittest.mock import Mock, patch

from black_primer import cli, lib
from click.testing import CliRunner

EXPECTED_ANALYSIS_OUTPUT = """-- primer results 📊 --
68 / 69 succeeded (98.55%) ✅
1 / 69 FAILED (1.45%) 💩
 - 0 projects disabled by config
 - 0 projects skipped due to Python version
 - 0 skipped due to long checkout
Failed projects:
## black:
 - Returned 69
 - stdout:
Black didn't work
"""
''',
    )


def test_black_snippet_three():
    """Test consistent code formatting between isort and black for code snippet from black repository.
    See: https://github.com/psf/black/blob/master/src/black/__init__.py
    """
    black_test(
        """import ast
import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from functools import lru_cache, partial, wraps
import io
import itertools
import logging
from multiprocessing import Manager, freeze_support
import os
from pathlib import Path
import pickle
import regex as re
import signal
import sys
import tempfile
import tokenize
import traceback
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Sized,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    TYPE_CHECKING,
)
from typing_extensions import Final
from mypy_extensions import mypyc_attr

from appdirs import user_cache_dir
from dataclasses import dataclass, field, replace
import click
import toml
from typed_ast import ast3, ast27
from pathspec import PathSpec

# lib2to3 fork
from blib2to3.pytree import Node, Leaf, type_repr
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.parse import ParseError

from _black_version import version as __version__

if TYPE_CHECKING:
    import colorama  # noqa: F401

DEFAULT_LINE_LENGTH = 88
""",
        """import ast
import asyncio
import io
import itertools
import logging
import os
import pickle
import signal
import sys
import tempfile
import tokenize
import traceback
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from functools import lru_cache, partial, wraps
from multiprocessing import Manager, freeze_support
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Sized,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import click
import regex as re
import toml
from _black_version import version as __version__
from appdirs import user_cache_dir
from blib2to3 import pygram, pytree
from blib2to3.pgen2 import driver, token
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.parse import ParseError

# lib2to3 fork
from blib2to3.pytree import Leaf, Node, type_repr
from mypy_extensions import mypyc_attr
from pathspec import PathSpec
from typed_ast import ast3, ast27
from typing_extensions import Final

if TYPE_CHECKING:
    import colorama  # noqa: F401

DEFAULT_LINE_LENGTH = 88
""",
    )
