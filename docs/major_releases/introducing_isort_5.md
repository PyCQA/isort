# Introducing isort 5

[![isort 5 - the best version of isort yet](https://raw.githubusercontent.com/pycqa/isort/develop/art/logo_5.png)](https://pycqa.github.io/isort/)

isort 5.0.0 is the first major release of isort in over five years and the first significant refactoring of isort since it was conceived more than ten years ago.
It's also the first version to require Python 3 (Python 3.6+ at that!) to run - though it can still be run on source files from any version of Python.
This does mean that there may be some pain with the upgrade process, but we believe the improvements will be well worth it.

[Click here for an attempt at full changelog with a list of breaking changes.](https://pycqa.github.io/isort/CHANGELOG/)

[Using isort 4.x.x? Click here for the isort 5.0.0 upgrade guide.](https://pycqa.github.io/isort/docs/upgrade_guides/5.0.0/)

[Try isort 5 right now from your browser!](https://pycqa.github.io/isort/docs/quick_start/0.-try/)

So why the massive change?

# Profile support
```
isort --profile black .
isort --profile django .
isort --profile pycharm .
isort --profile google .
isort --profile open_stack .
isort --profile plone .
isort --profile attrs .
isort --profile hug .
```

isort is very configurable. That's great, but it can be overwhelming, both for users and for the isort project. isort now comes with profiles for the most common isort configurations,
so you likely will not need to configure anything at all. This also means that as a project, isort can run extensive tests against these specific profiles to ensure nothing breaks over time.

# Sort imports **anywhere**

```python3
import a  # <- These are sorted
import b

b.install(a)

import os  # <- And these are sorted
import sys


def my_function():
    import x  # <- Even these are sorted!
    import z
```

isort 5 will find and sort contiguous section of imports no matter where they are.
It also allows you to place code in-between imports without any hacks required.

# Streaming architecture

```python3
import a
import b
...
∞
```
isort has been refactored to use a streaming architecture. This means it can sort files of *any* size (even larger than the Python interpreter supports!) without breaking a sweat.
It also means that even when sorting imports in smaller files, it is faster and more resource-efficient.

# Consistent behavior across **all** environments

Sorting the same file with the same configuration should give you the same output no matter what computer or OS you are running. Extensive effort has been placed around refactoring
how modules are placed and how configuration files are loaded to ensure this is the case.


# Cython support

```python3
cimport ctime
from cpython cimport PyLong_FromVoidPtr
from cpython cimport bool as py_bool
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from libc.stdint cimport uint64_t, uintptr_t
from libc.stdlib cimport atoi, calloc, free, malloc
from libc.string cimport memcpy, strlen
from libcpp cimport bool as cpp_bool
from libcpp.map cimport map as cpp_map
from libcpp.pair cimport pair as cpp_pair
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from multimap cimport multimap as cpp_multimap
from wstring cimport wstring as cpp_wstring
```

isort 5 adds seamless support for Cython (`.pyx`) files.

# Action Comments

```python3
import e
import f

# isort: off  <- Turns isort parsing off

import b
import a

# isort: on  <- Turns isort parsing back on

import c
import d
```

isort 5 adds support for [Action Comments](https://pycqa.github.io/isort/docs/configuration/action_comments/) which provide a quick and convient way to control the flow of parsing within single source files.


# First class Python API

```python3
import isort

isort.code("""
import b
import a
""") == """
import a
import b
"""
```

isort now exposes its programmatic API as a first-class citizen. This API makes it easy to extend or use isort in your own Python project. You can see the full documentation for this new API [here](https://pycqa.github.io/isort/reference/isort/api/).

# Solid base for the future

A major focus for the release was to give isort a solid foundation for the next 5-10 years of the project's life.
isort has been refactored into functional components that are easily testable. The project now has 100% code coverage.
It utilizes tools like [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) to reduce the number of unexpected errors.
It went from fully dynamic to fully static typing using mypy. Finally, it utilizes the latest linters both on (like [DeepSource](https://deepsource.io/gh/pycqa/isort/)) and offline (like [Flake8](https://flake8.pycqa.org/en/latest/)) to help ensure a higher bar for all code contributions into the future.

# Give 5.0.0 a try!

[Try isort 5 right now from your browser!](https://pycqa.github.io/isort/docs/quick_start/0.-try/)

OR

Install isort locally using `pip3 install isort`.

[Click here for full installation instructions.](https://pycqa.github.io/isort/docs/quick_start/1.-install/)
