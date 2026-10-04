# Comment handling

isort keeps the comments that belong to your imports, but it attaches them to
*import statements* rather than to positions in the file. Because sorting moves
imports around, this means a comment can end up somewhere other than where you
typed it.

This page describes where comments end up, so you can predict the output and
choose the settings that give you the result you want.

## Comments above an import travel with it

A comment that sits directly above an import is treated as part of that import
and is re-sorted along with it. A blank line *above* the comment does not change
this: what matters is that the comment touches the import below it.

```python
import zebra
# why aardvark comes first
import aardvark
```

becomes:

```python
# why aardvark comes first
import aardvark
import zebra
```

The comment moved up because `aardvark` sorts before `zebra`.

To keep a comment out of the sort, separate it from the imports with blank lines
on both sides. A comment that is detached this way is a *floating* comment: it is
not attached to any import and stays where you put it.

```python
import zebra

# general note about the import order

import aardvark
```

becomes:

```python
import aardvark
import zebra

# general note about the import order
```

## Comments inside a `from ... import` block

### Own-line comments move to the opening line

A comment on its own line inside a multiline import is moved onto the line that
opens the import:

```python
from a_rather_long_module_name_xx import (
    # this option is deprecated
    aaaaaa_long_name_one,
    bbbbbb_long_name_two,
)
```

becomes:

```python
from a_rather_long_module_name_xx import (  # this option is deprecated
    aaaaaa_long_name_one,
    bbbbbb_long_name_two
)
```

### Trailing comments are attached to that name

A comment at the end of an imported name is attached to *that name*. isort cannot
leave it inside a wrapped group, because the comment would then appear to belong
to the line below it. Instead, the name that has the comment is put on its own
`from` import:

```python
from a_rather_long_module_name_xx import (
    aaaaaa_long_name_one,  # noqa
    bbbbbb_long_name_two,
)
```

becomes:

```python
from a_rather_long_module_name_xx import aaaaaa_long_name_one  # noqa
from a_rather_long_module_name_xx import bbbbbb_long_name_two
```

This is not specific to a particular [multi line output mode](./multi_line_output_modes.md):
the same input produces the same output for modes 0 through 5.

If the comment is long enough that the resulting single-line `from ... import
name  # comment` would not fit within `line_length`, isort keeps the name inside
the wrapped group and puts the comment on the opening line instead:

```python
from a_rather_long_module_name_xx import (
    aaaaaa_long_name_one,  # this comment is deliberately very long indeed
    bbbbbb_long_name_two,
)
```

becomes:

```python
from a_rather_long_module_name_xx import (  # this comment is deliberately very long indeed
    aaaaaa_long_name_one
)
from a_rather_long_module_name_xx import bbbbbb_long_name_two
```

### Comments float to the first import of a module

When the same module is imported in more than one statement, a comment attached
to a later statement is moved above the *first* statement for that module:

```python
from module import aaa  # trailing comment on aaa
# note about bbb
from module import bbb
```

becomes:

```python
# note about bbb
from module import aaa  # trailing comment on aaa
from module import bbb
```

## Options that affect comment placement

### ensure_newline_before_comments

Inserts a blank line before a comment that follows an import, so the comment is
not visually glued to the import above it:

```python
import os
import sys
# a note
```

with `ensure_newline_before_comments` (CLI flag `-n`) becomes:

```python
import os
import sys

# a note
```

See [ensure newline before comments](./options.md#ensure-newline-before-comments)
for details.

### comment_prefix

Controls the prefix (spacing and `#`) that isort uses when it writes a comment
onto an import line. The default is two spaces followed by `#`. See
[comment prefix](./options.md#comment-prefix) for details.

### Related options

- [multi line output mode](./options.md#multi-line-output) — decides how long
  `from` imports wrap, which determines whether a comment lands on the opening
  line or on its own line.
- [action comments](./action_comments.md) — comments such as `# isort: skip` and
  `# isort: off` that control isort directly.
