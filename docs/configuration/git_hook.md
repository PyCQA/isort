# Git Hook

isort provides a hook function that can be integrated into your Git
pre-commit script to check Python code before committing.

To cause the commit to fail if there are isort errors (strict mode),
include the following in `.git/hooks/pre-commit`:

```python
#!/usr/bin/env python
import sys
from isort.hooks import git_hook

sys.exit(git_hook(strict=True, modify=True, lazy=True, settings_file=""))
```

If you just want to display warnings, but allow the commit to happen
anyway, call `git_hook` without the strict parameter. If you want to
display warnings, but not also fix the code, call `git_hook` without the
modify parameter.
The `lazy` argument is to support users who are "lazy" to add files
individually to the index and tend to use `git commit -a` instead.
Set it to `True` to ensure all tracked files are properly isorted,
leave it out or set it to `False` to check only files added to your
index.

If you want to use a specific configuration file for the hook, you can pass its
path to settings_file. If no path is specifically requested, `git_hook` will
search for the configuration file starting at the directory containing the first
staged file, as per `git diff-index` ordering, and going upward in the directory
structure until a valid configuration file is found or
[`MAX_CONFIG_SEARCH_DEPTH`](src/config.py:35) directories are checked.
The settings_file parameter is used to support users who keep their configuration
file in a directory that might not be a parent of all the other files.
