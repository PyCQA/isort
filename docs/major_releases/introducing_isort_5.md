isort 5.0.0 is the first significant release of isort in over five years and the first major refactoring of isort since it conceived more than ten years ago.
This does mean that there may be some pain with the upgrade process, but we believe the improvements will be well worth it.

[Click here for an attempt at full changelog with a list of breaking changes.](https://timothycrosley.github.io/isort/CHANGELOG/)
[Try isort 5 right now from your browser!](https://timothycrosley.github.io/isort/docs/interactive/try/)

So why the massive change? 

# Profile Support
```
isort --profile black
isort --profile django
isort --profile pycharm
isort --profile google
isort --profile open_stack
isort --profile plone
isort --profile attrs
isort --profile hug
```

isort is very configurable. That's great, but it can be overwhelming, both for users and for the isort project. isort now comes with profiles for the most common isort configurations,
so you likely will not need to configure anything at all.

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

# Consistent behavior across **all** environments.
Sorting the same file with the same configuration should give you the same output no matter what computer or OS you are running. Extensive effort has been placed around refactoring
how modules are placed and how configuration files are loaded to ensure this is the case.
