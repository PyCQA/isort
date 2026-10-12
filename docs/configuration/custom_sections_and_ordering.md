# Custom sections and ordering

isort provides lots of features to enable configuring how it sections imports
and how it sorts imports within those sections.
You can change the section order with `sections` option from the default
of:

```ini
FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
```

to your preference (if defined, omitting a default section may cause errors):

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

**IMPORTANT NOTE**: It is very important to know when setting `known` sections that the naming
does not directly map for historical reasons. For custom settings, the only difference is
capitalization (`known_custom=custom` VS `sections=CUSTOM,...`) for all others reference the
following mapping:

 - `known_standard_library` : `STANDARD_LIBRARY`
 - `extra_standard_library` : `STANDARD_LIBRARY` # Like known standard library but appends instead of replacing
 - `known_future_library` : `FUTURE`
 - `known_first_party`: `FIRSTPARTY`
 - `known_third_party`: `THIRDPARTY`
 - `known_local_folder`: `LOCALFOLDER`

This will likely be changed in isort 6.0.0+ in a backwards compatible way.


## How imports are classified

isort classifies each imported module before sorting it into a section. It uses
these checks in order, stopping at the first match:

1. A matching [forced separate](options.md#forced-separate) pattern puts the
   import in that separate section.
2. An import starting with a dot, such as `from .utils import helper`, goes in
   `LOCALFOLDER`.
3. A matching `known_*` setting selects its configured section. This includes
   the standard library list for the configured [Python version](options.md#python-version).
   isort checks the full module name before its parent names, so a setting for
   `mypackage.special` can override one for `mypackage`.
4. A module or package found under [source paths](options.md#src-paths) goes in
   `FIRSTPARTY`. This includes Python modules, extension modules, packages and
   directories. Namespace packages are checked for the imported submodule.
5. Otherwise, the import goes in the [default section](options.md#default-section),
   which is `THIRDPARTY` unless configured differently.

With the default configuration, this means:

| Import | Section | Reason |
| --- | --- | --- |
| `from __future__ import annotations` | `FUTURE` | Included in `known_future_library` |
| `import os` | `STDLIB` | Included in the standard library list |
| `import mypackage` | `FIRSTPARTY` | Found in the configured source paths |
| `import external_package` | `THIRDPARTY` | No earlier rule matches |
| `from . import utils` | `LOCALFOLDER` | Starts with a dot |

### First-party imports and the project layout

By default, isort searches the configuration directory and its `src`
subdirectory for first-party imports. Without a configuration file, this is
based on the directory used to resolve the configuration. Running isort from a
different directory, or selecting a different settings file, can therefore
change which imports are considered first-party.

For a project with its packages under `lib`, configure that directory explicitly:

```toml
[tool.isort]
src_paths = ["lib"]
```

Relative source paths are resolved from the configuration directory. A source
path may also name the package directory itself. In that case, both the package
and importable modules inside that directory can be classified as first-party.

To classify a package independently of where isort runs or whether its source
is present, use an explicit setting:

```toml
[tool.isort]
known_first_party = ["mypackage"]
known_third_party = ["external_package"]
```

These settings take precedence over source-path detection. isort does not need
to import a package or find it in an installed environment to classify it.
Use `isort --verbose path/to/file.py` to see each import's classification and
`isort --show-config path/to/file.py` to check the settings and their sources.


## Auto-comment import sections

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

## Ordering by import length

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

## Controlling how isort sections `from` imports

By default isort places straight (`import y`) imports above from imports (`from x import y`):

```python
import b
from a import a  # This will always appear below because it is a from import.
```

However, if you prefer to keep strict alphabetical sorting you can set [force sort within sections](./options.md#force-sort-within-sections) to true. Resulting in:


```python
from a import a  # This will now appear at top because a appears in the alphabet before b
import b
```

You can even tell isort to always place from imports on top, instead of the default of placing them on bottom, using [from first](./options.md#from-first).

```python
from b import b  # If from first turnrf on, all from imports are placed before non-from imports.
import a
```
