[![isort - isort your imports for you, so you don't have to](https://raw.githubusercontent.com/timothycrosley/isort/develop/art/logo_large.png)](https://timothycrosley.github.io/isort/)

------------------------------------------------------------------------

[![PyPI version](https://badge.fury.io/py/isort.svg)](https://badge.fury.io/py/isort)
[![Build Status](https://travis-ci.org/timothycrosley/isort.svg?branch=master)](https://travis-ci.org/timothycrosley/isort)
[![Code coverage Status](https://codecov.io/gh/timothycrosley/isort/branch/develop/graph/badge.svg)](https://codecov.io/gh/timothycrosley/isort)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.org/project/hug/)
[![Join the chat at https://gitter.im/timothycrosley/isort](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/timothycrosley/isort?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Downloads](https://pepy.tech/badge/isort)](https://pepy.tech/project/isort)
_________________

[Read Latest Documentation](https://timothycrosley.github.io/isort/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/isort/)
_________________

isort your imports for you, so you don't have to.

isort is a Python utility / library to sort imports alphabetically, and
automatically separated into sections. It provides a command line
utility, Python library and [plugins for various
editors](https://github.com/timothycrosley/isort/wiki/isort-Plugins) to
quickly sort all your imports. It requires Python 3.6+ to run but
supports formatting Python 2 code too.

------------------------------------------------------------------------

[Get professionally supported isort with the Tidelift
Subscription](https://tidelift.com/subscription/pkg/pypi-isort?utm_source=pypi-isort&utm_medium=referral&utm_campaign=readme)

Professional support for isort is available as part of the [Tidelift
Subscription](https://tidelift.com/subscription/pkg/pypi-isort?utm_source=pypi-isort&utm_medium=referral&utm_campaign=readme).
Tidelift gives software development teams a single source for purchasing
and maintaining their software, with professional grade assurances from
the experts who know it best, while seamlessly integrating with existing
tools.

------------------------------------------------------------------------

![Example Usage](https://raw.github.com/timothycrosley/isort/develop/example.gif)

Before isort:

```python
from my_lib import Object

import os

from my_lib import Object3

from my_lib import Object2

import sys

from third_party import lib15, lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8, lib9, lib10, lib11, lib12, lib13, lib14

import sys

from __future__ import absolute_import

from third_party import lib3

print("Hey")
print("yo")
```

After isort:

```python
from __future__ import absolute_import

import os
import sys

from third_party import (lib1, lib2, lib3, lib4, lib5, lib6, lib7, lib8,
                         lib9, lib10, lib11, lib12, lib13, lib14, lib15)

from my_lib import Object, Object2, Object3

print("Hey")
print("yo")
```

Installing isort
================

Installing isort is as simple as:

```bash
pip install isort
```

Install isort with requirements.txt support:

```bash
pip install isort[requirements]
```

Install isort with Pipfile support:

```bash
pip install isort[pipfile]
```

Install isort with both formats support:

```bash
pip install isort[requirements,pipfile]
```

Using isort
===========

**From the command line**:

```bash
isort mypythonfile.py mypythonfile2.py
```

or recursively:

```bash
isort -rc .
```

*which is equivalent to:*

```bash
isort **/*.py
```

or to see the proposed changes without applying them:

```bash
isort mypythonfile.py --diff
```

Finally, to atomically run isort against a project, only applying
changes if they don't introduce syntax errors do:

```bash
isort -rc --atomic .
```

(Note: this is disabled by default as it keeps isort from being able to
run against code written using a different version of Python)

**From within Python**:

```bash
from isort import SortImports

SortImports("pythonfile.py")
```

or:

```bash
from isort import SortImports

new_contents = SortImports(file_contents=old_contents).output
```

**From within Kate:**

```bash
ctrl+[
```

or:

```bash
menu > Python > Sort Imports
```

Installing isort's Kate plugin
===============================

For KDE 4.13+ / Pate 2.0+:

```bash
wget https://raw.github.com/timothycrosley/isort/master/kate_plugin/isort_plugin.py --output-document ~/.kde/share/apps/kate/pate/isort_plugin.py
wget https://raw.github.com/timothycrosley/isort/master/kate_plugin/isort_plugin_ui.rc --output-document ~/.kde/share/apps/kate/pate/isort_plugin_ui.rc
wget https://raw.github.com/timothycrosley/isort/master/kate_plugin/katepart_isort.desktop --output-document ~/.kde/share/kde4/services/katepart_isort.desktop
```

For all older versions:

```bash
wget https://raw.github.com/timothycrosley/isort/master/kate_plugin/isort_plugin_old.py --output-document ~/.kde/share/apps/kate/pate/isort_plugin.py
```

You will then need to restart kate and enable Python Plugins as well as
the isort plugin itself.

Installing isort's for your preferred text editor
==================================================

Several plugins have been written that enable to use isort from within a
variety of text-editors. You can find a full list of them [on the isort
wiki](https://github.com/timothycrosley/isort/wiki/isort-Plugins).
Additionally, I will enthusiastically accept pull requests that include
plugins for other text editors and add documentation for them as I am
notified.

How does isort work?
====================

isort parses specified files for global level import lines (imports
outside of try / except blocks, functions, etc..) and puts them all at
the top of the file grouped together by the type of import:

-   Future
-   Python Standard Library
-   Third Party
-   Current Python Project
-   Explicitly Local (. before import, as in: `from . import x`)
-   Custom Separate Sections (Defined by forced\_separate list in
    configuration file)
-   Custom Sections (Defined by sections list in configuration file)

Inside of each section the imports are sorted alphabetically. isort
automatically removes duplicate python imports, and wraps long from
imports to the specified line length (defaults to 79).

When will isort not work?
=========================

If you ever have the situation where you need to have a try / except
block in the middle of top-level imports or if your import order is
directly linked to precedence.

For example: a common practice in Django settings files is importing \*
from various settings files to form a new settings file. In this case if
any of the imports change order you are changing the settings definition
itself.

However, you can configure isort to skip over just these files - or even
to force certain imports to the top.

Configuring isort
=================

If you find the default isort settings do not work well for your
project, isort provides several ways to adjust the behavior.

To configure isort for a single user create a `~/.isort.cfg` or
`$XDG_CONFIG_HOME/isort.cfg` file:

```ini
[settings]
line_length=120
force_to_top=file1.py,file2.py
skip=file3.py,file4.py
known_future_library=future,pies
known_standard_library=std,std2
known_third_party=randomthirdparty
known_first_party=mylib1,mylib2
indent='    '
multi_line_output=3
length_sort=1
forced_separate=django.contrib,django.utils
default_section=FIRSTPARTY
no_lines_before=LOCALFOLDER
```

Additionally, you can specify project level configuration simply by
placing a `.isort.cfg` file at the root of your project. isort will look
up to 25 directories up, from the file it is ran against, to find a
project specific configuration.

Or, if you prefer, you can add an `isort` or `tool:isort` section to
your project's `setup.cfg` or `tox.ini` file with any desired settings.

You can also add your desired settings under a `[tool.isort]` section in
your `pyproject.toml` file.

You can then override any of these settings by using command line
arguments, or by passing in override values to the SortImports class.

Finally, as of version 3.0 isort supports editorconfig files using the
standard syntax defined here: <https://editorconfig.org/>

Meaning you place any standard isort configuration parameters within a
.editorconfig file under the `*.py` section and they will be honored.

For a full list of isort settings and their meanings [take a look at the
isort
wiki](https://github.com/timothycrosley/isort/wiki/isort-Settings).

Multi line output modes
=======================

You will notice above the \"multi\_line\_output\" setting. This setting
defines how from imports wrap when they extend past the line\_length
limit and has 6 possible settings:

**0 - Grid**

```python
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

**1 - Vertical**

```python
from third_party import (lib1,
                         lib2,
                         lib3
                         lib4,
                         lib5,
                         ...)
```

**2 - Hanging Indent**

```python
from third_party import \
    lib1, lib2, lib3, \
    lib4, lib5, lib6
```

**3 - Vertical Hanging Indent**

```python
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
)
```

**4 - Hanging Grid**

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...)
```

**5 - Hanging Grid Grouped**

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...
)
```

**6 - Hanging Grid Grouped, No Trailing Comma**

In Mode 5 isort leaves a single extra space to maintain consistency of
output when a comma is added at the end. Mode 6 is the same - except
that no extra space is maintained leading to the possibility of lines
one character longer. You can enforce a trailing comma by using this in
conjunction with `-tc` or `include_trailing_comma: True`.

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5
)
```

**7 - NOQA**

```python
from third_party import lib1, lib2, lib3, ...  # NOQA
```

Alternatively, you can set `force_single_line` to `True` (`-sl` on the
command line) and every import will appear on its own line:

```python
from third_party import lib1
from third_party import lib2
from third_party import lib3
...
```

Note: to change the how constant indents appear - simply change the
indent property with the following accepted formats:

-   Number of spaces you would like. For example: 4 would cause standard
    4 space indentation.
-   Tab
-   A verbatim string with quotes around it.

For example:

```python
"    "
```

is equivalent to 4.

For the import styles that use parentheses, you can control whether or
not to include a trailing comma after the last import with the
`include_trailing_comma` option (defaults to `False`).

Intelligently Balanced Multi-line Imports
=========================================

As of isort 3.1.0 support for balanced multi-line imports has been
added. With this enabled isort will dynamically change the import length
to the one that produces the most balanced grid, while staying below the
maximum import length defined.

Example:

```python
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
```

Will be produced instead of:

```python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
```

To enable this set `balanced_wrapping` to `True` in your config or pass
the `-e` option into the command line utility.

Custom Sections and Ordering
============================

You can change the section order with `sections` option from the default
of:

```ini
FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
```

to your preference:

```ini
sections=FUTURE,STDLIB,FIRSTPARTY,THIRDPARTY,LOCALFOLDER
```

You also can define your own sections and their order.

Example:

```ini
known_django=django
known_pandas=pandas,numpy
sections=FUTURE,STDLIB,DJANGO,THIRDPARTY,PANDAS,FIRSTPARTY,LOCALFOLDER
```

would create two new sections with the specified known modules.

The `no_lines_before` option will prevent the listed sections from being
split from the previous section by an empty line.

Example:

```ini
sections=FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
no_lines_before=LOCALFOLDER
```

would produce a section with both FIRSTPARTY and LOCALFOLDER modules
combined.

Auto-comment import sections
============================

Some projects prefer to have import sections uniquely titled to aid in
identifying the sections quickly when visually scanning. isort can
automate this as well. To do this simply set the
`import_heading_{section_name}` setting for each section you wish to
have auto commented - to the desired comment.

For Example:

```ini
import_heading_stdlib=Standard Library
import_heading_firstparty=My Stuff
```

Would lead to output looking like the following:

```python
# Standard Library
import os
import sys

import django.settings

# My Stuff
import myproject.test
```

Ordering by import length
=========================

isort also makes it easy to sort your imports by length, simply by
setting the `length_sort` option to `True`. This will result in the
following output style:

```python
from evn.util import (
    Pool,
    Dict,
    Options,
    Constant,
    DecayDict,
    UnexpectedCodePath,
)
```

It is also possible to opt-in to sorting imports by length for only
specific sections by using `length_sort_` followed by the section name
as a configuration item, e.g.:

    length_sort_stdlib=1

Skip processing of imports (outside of configuration)
=====================================================

To make isort ignore a single import simply add a comment at the end of
the import line containing the text `isort:skip`:

```python
import module  # isort:skip
```

or:

```python
from xyz import (abc,  # isort:skip
                 yo,
                 hey)
```

To make isort skip an entire file simply add `isort:skip_file` to the
module's doc string:

```python
""" my_module.py
    Best module ever

   isort:skip_file
"""

import b
import a
```

Adding an import to multiple files
==================================

isort makes it easy to add an import statement across multiple files,
while being assured it's correctly placed.

From the command line:

```bash
isort -a "from __future__ import print_function" *.py
```

from within Kate:

```
ctrl+]
```

or:

```
menu > Python > Add Import
```

Removing an import from multiple files
======================================

isort also makes it easy to remove an import from multiple files,
without having to be concerned with how it was originally formatted.

From the command line:

```bash
isort -rm "os.system" *.py
```

from within Kate:

```
ctrl+shift+]
```

or:

```
menu > Python > Remove Import
```

Using isort to verify code
==========================

The `--check-only` option
-------------------------

isort can also be used to used to verify that code is correctly
formatted by running it with `-c`. Any files that contain incorrectly
sorted and/or formatted imports will be outputted to `stderr`.

```bash
isort **/*.py -c -vb

SUCCESS: /home/timothy/Projects/Open_Source/isort/isort_kate_plugin.py Everything Looks Good!
ERROR: /home/timothy/Projects/Open_Source/isort/isort/isort.py Imports are incorrectly sorted.
```

One great place this can be used is with a pre-commit git hook, such as
this one by \@acdha:

<https://gist.github.com/acdha/8717683>

This can help to ensure a certain level of code quality throughout a
project.

Git hook
--------

isort provides [pre-commit](https://pre-commit.com/) hook definition
so you easily set up a hook to ensure that your imports remain
sorted. To use it, add something like this to your
`.pre-commit-config.yaml`.

```yaml
- repo: https://github.com/timothycrosley/isort
  rev: 4.3.21-2
  hooks:
    - id: isort
```

isort also ships with a hook function that can be integrated into your Git
pre-commit script to check Python code before committing.

To cause the commit to fail if there are isort errors (strict mode),
include the following in `.git/hooks/pre-commit`:

```python
#!/usr/bin/env python
import sys
from isort.hooks import git_hook

sys.exit(git_hook(strict=True, modify=True))
```

If you just want to display warnings, but allow the commit to happen
anyway, call `git_hook` without the strict parameter. If you want to
display warnings, but not also fix the code, call `git_hook` without the
modify parameter.

Setuptools integration
----------------------

Upon installation, isort enables a `setuptools` command that checks
Python files declared by your project.

Running `python setup.py isort` on the command line will check the files
listed in your `py_modules` and `packages`. If any warning is found, the
command will exit with an error code:

```bash
$ python setup.py isort
```

Also, to allow users to be able to use the command without having to
install isort themselves, add isort to the setup\_requires of your
`setup()` like so:

```python
setup(
    name="project",
    packages=["project"],

    setup_requires=[
        "isort"
    ]
)
```

Security contact information
==========

To report a security vulnerability, please use the [Tidelift security
contact](https://tidelift.com/security). Tidelift will coordinate the
fix and disclosure.

Why isort?
==========

isort simply stands for import sort. It was originally called
"sortImports" however I got tired of typing the extra characters and
came to the realization camelCase is not pythonic.

I wrote isort because in an organization I used to work in the manager
came in one day and decided all code must have alphabetically sorted
imports. The code base was huge - and he meant for us to do it by hand.
However, being a programmer - I\'m too lazy to spend 8 hours mindlessly
performing a function, but not too lazy to spend 16 hours automating it.
I was given permission to open source sortImports and here we are :)

------------------------------------------------------------------------

Thanks and I hope you find isort useful!

~Timothy Crosley
