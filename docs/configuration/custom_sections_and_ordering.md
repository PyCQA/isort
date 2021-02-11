# Custom Sections and Ordering

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

However, if you prefer to keep strict alphabetical sorting you can set [force sort within sections](https://pycqa.github.io/isort/docs/configuration/options/#force-sort-within-sections) to true. Resulting in:


```python
from a import a  # This will now appear at top because a appears in the alphabet before b
import b
```

You can even tell isort to always place from imports on top, instead of the default of placing them on bottom, using [from first](https://pycqa.github.io/isort/docs/configuration/options/#from-first).

```python
from b import b # If from first is set to True, all from imports will be placed before non-from imports.
import a
```
