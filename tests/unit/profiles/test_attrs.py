from functools import partial

from ..utils import isort_test

attrs_isort_test = partial(isort_test, profile="attrs")


def test_attrs_code_snippet_one():
    attrs_isort_test(
        """from __future__ import absolute_import, division, print_function

import sys

from functools import partial

from . import converters, exceptions, filters, setters, validators
from ._config import get_run_validators, set_run_validators
from ._funcs import asdict, assoc, astuple, evolve, has, resolve_types
from ._make import (
    NOTHING,
    Attribute,
    Factory,
    attrib,
    attrs,
    fields,
    fields_dict,
    make_class,
    validate,
)
from ._version_info import VersionInfo


__version__ = "20.2.0.dev0"
"""
    )


def test_attrs_code_snippet_two():
    attrs_isort_test(
        """from __future__ import absolute_import, division, print_function

import copy
import linecache
import sys
import threading
import uuid
import warnings

from operator import itemgetter

from . import _config, setters
from ._compat import (
    PY2,
    isclass,
    iteritems,
    metadata_proxy,
    ordered_dict,
    set_closure_cell,
)
from .exceptions import (
    DefaultAlreadySetError,
    FrozenInstanceError,
    NotAnAttrsClassError,
    PythonTooOldError,
    UnannotatedAttributeError,
)


# This is used at least twice, so cache it here.
_obj_setattr = object.__setattr__
"""
    )


def test_attrs_code_snippet_three():
    attrs_isort_test(
        '''
"""
Commonly useful validators.
"""

from __future__ import absolute_import, division, print_function

import re

from ._make import _AndValidator, and_, attrib, attrs
from .exceptions import NotCallableError


__all__ = [
    "and_",
    "deep_iterable",
    "deep_mapping",
    "in_",
    "instance_of",
    "is_callable",
    "matches_re",
    "optional",
    "provides",
]
'''
    )
