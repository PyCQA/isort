from ._version import _VERSION_STRING

ASCII_ART = rf"""
                 _                 _
                (_) ___  ___  _ __| |_
                | |/ _/ / _ \/ '__  _/
                | |\__ \/\_\/| |  | |_
                |_|\___/\___/\_/   \_/

      isort your imports, so you don't have to.

                    VERSION {_VERSION_STRING}
"""

__doc__ = f"""
```python
{ASCII_ART}
```
"""
