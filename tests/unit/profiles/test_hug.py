from functools import partial

from ..utils import isort_test

hug_isort_test = partial(isort_test, profile="hug", known_first_party=["hug"])


def test_hug_code_snippet_one():
    hug_isort_test(
        '''
from __future__ import absolute_import

import asyncio
import sys
from collections import OrderedDict, namedtuple
from distutils.util import strtobool
from functools import partial
from itertools import chain
from types import ModuleType
from wsgiref.simple_server import make_server

import falcon
from falcon import HTTP_METHODS

import hug.defaults
import hug.output_format
from hug import introspect
from hug._version import current

INTRO = """
/#######################################################################\\
          `.----``..-------..``.----.
         :/:::::--:---------:--::::://.
        .+::::----##/-/oo+:-##----:::://
        `//::-------/oosoo-------::://.       ##    ##  ##    ##    #####
          .-:------./++o/o-.------::-`   ```  ##    ##  ##    ##  ##
             `----.-./+o+:..----.     `.:///. ########  ##    ## ##
   ```        `----.-::::::------  `.-:::://. ##    ##  ##    ## ##   ####
  ://::--.``` -:``...-----...` `:--::::::-.`  ##    ##  ##   ##   ##    ##
  :/:::::::::-:-     `````      .:::::-.`     ##    ##    ####     ######
   ``.--:::::::.                .:::.`
         ``..::.                .::         EMBRACE THE APIs OF THE FUTURE
             ::-                .:-
             -::`               ::-                   VERSION {0}
             `::-              -::`
              -::-`           -::-
\\########################################################################/
 Copyright (C) 2016 Timothy Edmund Crosley
 Under the MIT License
""".format(
    current
)'''
    )


def test_hug_code_snippet_two():
    hug_isort_test(
        """from __future__ import absolute_import

import functools
from collections import namedtuple

from falcon import HTTP_METHODS

import hug.api
import hug.defaults
import hug.output_format
from hug import introspect
from hug.format import underscore


def default_output_format(
    content_type="application/json", apply_globally=False, api=None, cli=False, http=True
):
"""
    )


def test_hug_code_snippet_three():
    hug_isort_test(
        """from __future__ import absolute_import

import argparse
import asyncio
import os
import sys
from collections import OrderedDict
from functools import lru_cache, partial, wraps

import falcon
from falcon import HTTP_BAD_REQUEST

import hug._empty as empty
import hug.api
import hug.output_format
import hug.types as types
from hug import introspect
from hug.exceptions import InvalidTypeData
from hug.format import parse_content_type
from hug.types import (
    MarshmallowInputSchema,
    MarshmallowReturnSchema,
    Multiple,
    OneOf,
    SmartBoolean,
    Text,
    text,
)

DOC_TYPE_MAP = {str: "String", bool: "Boolean", list: "Multiple", int: "Integer", float: "Float"}
"""
    )
