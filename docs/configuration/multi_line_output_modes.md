# Multi Line Output Modes

This [config option](https://pycqa.github.io/isort/docs/configuration/options/#multi-line-output) defines how from imports wrap when they extend past the line\_length
limit and has 12 possible settings:

## 0 - Grid

```python
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

## 1 - Vertical

```python
from third_party import (lib1,
                         lib2,
                         lib3
                         lib4,
                         lib5,
                         ...)
```

## 2 - Hanging Indent

```python
from third_party import \
    lib1, lib2, lib3, \
    lib4, lib5, lib6
```

## 3 - Vertical Hanging Indent

```python
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
)
```

## 4 - Hanging Grid

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...)
```

## 5 - Hanging Grid Grouped

```python
from third_party import (
    lib1, lib2, lib3, lib4,
    lib5, ...
)
```

## 6 - Hanging Grid Grouped

Same as Mode 5. Deprecated.

## 7 - NOQA

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

## 8 - Vertical Hanging Indent Bracket

Same as Mode 3 - _Vertical Hanging Indent_ but the closing parentheses
on the last line is indented.

```python
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
    )
```

## 9 - Vertical Prefix From Module Import

Starts a new line with the same `from MODULE import ` prefix when lines are longer than the line length limit.

```python
from third_party import lib1, lib2, lib3
from third_party import lib4, lib5, lib6
```

## 10 - Hanging Indent With Parentheses

Same as Mode 2 - _Hanging Indent_ but uses parentheses instead of backslash
for wrapping long lines.

```python
from third_party import (
    lib1, lib2, lib3,
    lib4, lib5, lib6)
```

## 11 - Backslash Grid

Same as Mode 0 - _Grid_ but uses backslashes instead of parentheses to group imports.

```python
from third_party import lib1, lib2, lib3, \
                        lib4, lib5
```
