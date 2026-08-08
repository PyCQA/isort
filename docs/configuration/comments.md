# Comments on imports

isort preserves comments on imports, but their position can change when the
associated import is sorted or reformatted. This is because comments are
associated with import statements and imported names while parsing, then
rendered with the sorted imports.

## Comments before imports

A comment immediately before an import, with no blank line between them, moves
with that import:

```python
import zlib
# Used to inspect the current process state.
import os
```

becomes:

```python
# Used to inspect the current process state.
import os
import zlib
```

When imports from the same module are combined, comments attached to those
imports are emitted before the combined statement:

```python
# Used by feature B.
from package import b
# Used by feature A.
from package import a
```

becomes:

```python
# Used by feature B.
# Used by feature A.
from package import a, b
```

## Comments in multiline imports

A comment on its own line inside a multiline import is associated with the
whole statement. With vertical hanging indent (multi-line output mode 3) and a
line length of 40, it is moved to the opening line:

```python
from package import (
    a_very_long_import_name_b,
    # Used by feature A.
    a_very_long_import_name_a,
)
```

can become:

```python
from package import (  # Used by feature A.
    a_very_long_import_name_a,
    a_very_long_import_name_b
)
```

See the [multi-line output modes](multi_line_output_modes.md) for the available
layouts.

An inline comment remains associated with its imported name. When combining
that name into a multiline statement would make the association ambiguous,
isort can keep it in a separate import:

```python
from package import (
    b,  # Used by feature B.
    a,
)
```

becomes:

```python
from package import b  # Used by feature B.
from package import a
```

## Controlling comment handling

Use [action comments](action_comments.md) such as `# isort: off` and
`# isort: on` when exact import and comment placement must remain unchanged.
The following options also affect comment handling:

- [`no_inline_sort`](options.md#no-inline-sort) leaves names within `from`
  imports in their existing order.
- [`ignore_comments`](options.md#ignore-comments) removes comments within
  import statements.
- [`ensure_newline_before_comments`](options.md#ensure-newline-before-comments)
  inserts a blank line before a comment following an import.
- [`treat_comments_as_code`](options.md#treat-comments-as-code) and
  [`treat_all_comments_as_code`](options.md#treat-all-comments-as-code) keep
  selected standalone comments outside the import section.
