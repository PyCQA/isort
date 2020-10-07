from functools import partial

from ..utils import isort_test

google_isort_test = partial(isort_test, profile="google")


def test_google_code_snippet_shared_example():
    """Tests snippet examples directly shared with the isort project.
    See: https://github.com/PyCQA/isort/issues/1486.
    """
    google_isort_test(
        """import collections
import cProfile
"""
    )
    google_isort_test(
        """from a import z
from a.b import c
"""
    )


def test_google_code_snippet_one():
    google_isort_test(
        '''# coding=utf-8
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""JAX user-facing transformations and utilities.
The transformations here mostly wrap internal transformations, providing
convenience flags to control behavior and handling Python containers of
arguments and outputs. The Python containers handled are pytrees (see
tree_util.py), which include nested tuples/lists/dicts, where the leaves are
arrays.
"""

# flake8: noqa: F401
import collections
import functools
import inspect
import itertools as it
import threading
import weakref
from typing import Any, Callable, Iterable, List, NamedTuple, Optional, Sequence, Tuple, TypeVar, Union
from warnings import warn

import numpy as np
from contextlib import contextmanager, ExitStack

from . import core
from . import linear_util as lu
from . import ad_util
from . import dtypes
from .core import eval_jaxpr
from .api_util import (wraps, flatten_fun, apply_flat_fun, flatten_fun_nokwargs,
                       flatten_fun_nokwargs2, argnums_partial, flatten_axes,
                       donation_vector, rebase_donate_argnums)
from .traceback_util import api_boundary
from .tree_util import (tree_map, tree_flatten, tree_unflatten, tree_structure,
                        tree_transpose, tree_leaves, tree_multimap,
                        treedef_is_leaf, Partial)
from .util import (unzip2, curry, partial, safe_map, safe_zip, prod, split_list,
                   extend_name_stack, wrap_name, cache)
from .lib import xla_bridge as xb
from .lib import xla_client as xc
# Unused imports to be exported
from .lib.xla_bridge import (device_count, local_device_count, devices,
                             local_devices, host_id, host_ids, host_count)
from .abstract_arrays import ConcreteArray, ShapedArray, raise_to_shaped
from .interpreters import partial_eval as pe
from .interpreters import xla
from .interpreters import pxla
from .interpreters import ad
from .interpreters import batching
from .interpreters import masking
from .interpreters import invertible_ad as iad
from .interpreters.invertible_ad import custom_ivjp
from .custom_derivatives import custom_jvp, custom_vjp
from .config import flags, config, bool_env

AxisName = Any

# This TypeVar is used below to express the fact that function call signatures
# are invariant under the jit, vmap, and pmap transformations.
# Specifically, we statically assert that the return type is invariant.
# Until PEP-612 is implemented, we cannot express the same invariance for
# function arguments.
# Note that the return type annotations will generally not strictly hold
# in JIT internals, as Tracer values are passed through the function.
# Should this raise any type errors for the tracing code in future, we can disable
# type checking in parts of the tracing code, or remove these annotations.
T = TypeVar("T")

map = safe_map
zip = safe_zip

FLAGS = flags.FLAGS
flags.DEFINE_bool("jax_disable_jit", bool_env("JAX_DISABLE_JIT", False),
                  "Disable JIT compilation and just call original Python.")

''',
        '''# coding=utf-8
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""JAX user-facing transformations and utilities.
The transformations here mostly wrap internal transformations, providing
convenience flags to control behavior and handling Python containers of
arguments and outputs. The Python containers handled are pytrees (see
tree_util.py), which include nested tuples/lists/dicts, where the leaves are
arrays.
"""

# flake8: noqa: F401
import collections
from contextlib import contextmanager
from contextlib import ExitStack
import functools
import inspect
import itertools as it
import threading
from typing import (Any, Callable, Iterable, List, NamedTuple, Optional,
                    Sequence, Tuple, TypeVar, Union)
from warnings import warn
import weakref

import numpy as np

from . import ad_util
from . import core
from . import dtypes
from . import linear_util as lu
from .abstract_arrays import ConcreteArray
from .abstract_arrays import raise_to_shaped
from .abstract_arrays import ShapedArray
from .api_util import apply_flat_fun
from .api_util import argnums_partial
from .api_util import donation_vector
from .api_util import flatten_axes
from .api_util import flatten_fun
from .api_util import flatten_fun_nokwargs
from .api_util import flatten_fun_nokwargs2
from .api_util import rebase_donate_argnums
from .api_util import wraps
from .config import bool_env
from .config import config
from .config import flags
from .core import eval_jaxpr
from .custom_derivatives import custom_jvp
from .custom_derivatives import custom_vjp
from .interpreters import ad
from .interpreters import batching
from .interpreters import invertible_ad as iad
from .interpreters import masking
from .interpreters import partial_eval as pe
from .interpreters import pxla
from .interpreters import xla
from .interpreters.invertible_ad import custom_ivjp
from .lib import xla_bridge as xb
from .lib import xla_client as xc
# Unused imports to be exported
from .lib.xla_bridge import device_count
from .lib.xla_bridge import devices
from .lib.xla_bridge import host_count
from .lib.xla_bridge import host_id
from .lib.xla_bridge import host_ids
from .lib.xla_bridge import local_device_count
from .lib.xla_bridge import local_devices
from .traceback_util import api_boundary
from .tree_util import Partial
from .tree_util import tree_flatten
from .tree_util import tree_leaves
from .tree_util import tree_map
from .tree_util import tree_multimap
from .tree_util import tree_structure
from .tree_util import tree_transpose
from .tree_util import tree_unflatten
from .tree_util import treedef_is_leaf
from .util import cache
from .util import curry
from .util import extend_name_stack
from .util import partial
from .util import prod
from .util import safe_map
from .util import safe_zip
from .util import split_list
from .util import unzip2
from .util import wrap_name

AxisName = Any

# This TypeVar is used below to express the fact that function call signatures
# are invariant under the jit, vmap, and pmap transformations.
# Specifically, we statically assert that the return type is invariant.
# Until PEP-612 is implemented, we cannot express the same invariance for
# function arguments.
# Note that the return type annotations will generally not strictly hold
# in JIT internals, as Tracer values are passed through the function.
# Should this raise any type errors for the tracing code in future, we can disable
# type checking in parts of the tracing code, or remove these annotations.
T = TypeVar("T")

map = safe_map
zip = safe_zip

FLAGS = flags.FLAGS
flags.DEFINE_bool("jax_disable_jit", bool_env("JAX_DISABLE_JIT", False),
                  "Disable JIT compilation and just call original Python.")

''',
    )


def test_google_code_snippet_two():
    google_isort_test(
        """#!/usr/bin/env python
# In[ ]:
#  coding: utf-8

###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import sys
version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    from http.client import IncompleteRead, BadStatusLine
    http.client._MAXHEADERS = 1000
else:  # If the Current Version of Python is 2.x
    import urllib2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import quote
    import httplib
    from httplib import IncompleteRead, BadStatusLine
    httplib._MAXHEADERS = 1000
import time  # Importing the time library to check the time of code execution
import os
import argparse
import ssl
import datetime
import json
import re
import codecs
import socket""",
        """#!/usr/bin/env python
# In[ ]:
#  coding: utf-8

###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import sys

version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import http.client
    from http.client import BadStatusLine
    from http.client import IncompleteRead
    from urllib.parse import quote
    import urllib.request
    from urllib.request import HTTPError
    from urllib.request import Request
    from urllib.request import URLError
    from urllib.request import urlopen
    http.client._MAXHEADERS = 1000
else:  # If the Current Version of Python is 2.x
    from urllib import quote

    import httplib
    from httplib import BadStatusLine
    from httplib import IncompleteRead
    import urllib2
    from urllib2 import HTTPError
    from urllib2 import Request
    from urllib2 import URLError
    from urllib2 import urlopen
    httplib._MAXHEADERS = 1000
import argparse
import codecs
import datetime
import json
import os
import re
import socket
import ssl
import time  # Importing the time library to check the time of code execution
""",
    )


def test_code_snippet_three():
    google_isort_test(
        '''# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Monitoring."""
# pylint: disable=invalid-name
# TODO(ochang): Remove V3 from names once all metrics are migrated to
# stackdriver.

from builtins import object
from builtins import range
from builtins import str

import bisect
import collections
import functools
import itertools
import re
import six
import threading
import time

try:
  from google.cloud import monitoring_v3
except (ImportError, RuntimeError):
  monitoring_v3 = None

from google.api_core import exceptions
from google.api_core import retry

from base import errors
from base import utils
from config import local_config
from google_cloud_utils import compute_metadata
from google_cloud_utils import credentials
from metrics import logs
from system import environment''',
        '''# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Monitoring."""
# pylint: disable=invalid-name
# TODO(ochang): Remove V3 from names once all metrics are migrated to
# stackdriver.

import bisect
from builtins import object
from builtins import range
from builtins import str
import collections
import functools
import itertools
import re
import threading
import time

import six

try:
  from google.cloud import monitoring_v3
except (ImportError, RuntimeError):
  monitoring_v3 = None

from base import errors
from base import utils
from config import local_config
from google.api_core import exceptions
from google.api_core import retry
from google_cloud_utils import compute_metadata
from google_cloud_utils import credentials
from metrics import logs
from system import environment
''',
    )
