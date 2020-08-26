# Action Comments

The most basic way to configure the flow of isort within a single file is action comments. These comments are picked up and interpreted by the isort parser during parsing.


## isort: skip_file

Tells isort to skip the entire file.

Example:

```python
# !/bin/python3
# isort: skip_file
import os
import sys

...
```

!!! warning
    This should be placed as high in the file as reasonably possible.
    Since isort uses a streaming architecture, it may have already completed some work before it reaches the comment. Usually, this is okay - but can be confusing if --diff or any interactive options are used from the command line.


## isort: skip

If placed on the same line as (or within the continuation of a) an import statement, isort will not sort this import.
More specifically, it prevents the import statement from being recognized by isort as an import. In consequence, this line will be treated as code and be pushed down to below the import section of the file.

Example:

```python
import b
import a # isort: skip <- this will now stay below b
```
!!! note
    It is recommended to where possible use `# isort: off` and `# isort: on` or `# isort: split` instead as the behavior is more explicit and predictable.

## isort: off

Turns isort parsing off. Every line after an `# isort: off` statement will be passed along unchanged until an `# isort: on` comment or the end of the file.

Example:

```python
import e
import f

# isort: off

import b
import a
```

## isort: on

Turns isort parsing back on. This only makes sense if an `# isort: off` comment exists higher in the file! This allows you to have blocks of unsorted imports, around otherwise sorted ones.

Example:

```python

import e
import f

# isort: off

import b
import a

# isort: on

import c
import d

```

## isort: split

Tells isort the current sort section is finished, and all future imports belong to a new sort grouping.

Example:

```python

import e
import f

# isort: split

import a
import b
import c
import d

```

You can also use it inline to keep an import from having imports above or below it swap position:

```python
import c
import b  # isort: split
import a
```

!!! tip
    isort split is exactly the same as placing an `# isort: on` immediately below an `# isort: off`
