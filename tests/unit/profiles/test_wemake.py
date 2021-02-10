"""A set of test cases for the wemake isort profile.

Snippets are taken directly from the wemake-python-styleguide project here:
https://github.com/wemake-services/wemake-python-styleguide
"""
from functools import partial

from ..utils import isort_test

wemake_isort_test = partial(
    isort_test, profile="wemake", known_first_party=["wemake_python_styleguide"]
)


def test_wemake_snippet_one():
    wemake_isort_test(
        """
import ast
import tokenize
import traceback
from typing import ClassVar, Iterator, Sequence, Type

from flake8.options.manager import OptionManager
from typing_extensions import final

from wemake_python_styleguide import constants, types
from wemake_python_styleguide import version as pkg_version
from wemake_python_styleguide.options.config import Configuration
from wemake_python_styleguide.options.validation import validate_options
from wemake_python_styleguide.presets.types import file_tokens as tokens_preset
from wemake_python_styleguide.presets.types import filename as filename_preset
from wemake_python_styleguide.presets.types import tree as tree_preset
from wemake_python_styleguide.transformations.ast_tree import transform
from wemake_python_styleguide.violations import system
from wemake_python_styleguide.visitors import base

VisitorClass = Type[base.BaseVisitor]
"""
    )


def test_wemake_snippet_two():
    wemake_isort_test(
        """
from collections import defaultdict
from typing import ClassVar, DefaultDict, List

from flake8.formatting.base import BaseFormatter
from flake8.statistics import Statistics
from flake8.style_guide import Violation
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
from typing_extensions import Final

from wemake_python_styleguide.version import pkg_version

#: That url is generated and hosted by Sphinx.
DOCS_URL_TEMPLATE: Final = (
    'https://wemake-python-stylegui.de/en/{0}/pages/usage/violations/'
)
"""
    )


def test_wemake_snippet_three():
    wemake_isort_test(
        """
import ast

from pep8ext_naming import NamingChecker
from typing_extensions import final

from wemake_python_styleguide.transformations.ast.bugfixes import (
    fix_async_offset,
    fix_line_number,
)
from wemake_python_styleguide.transformations.ast.enhancements import (
    set_if_chain,
    set_node_context,
)


@final
class _ClassVisitor(ast.NodeVisitor): ...
"""
    )
