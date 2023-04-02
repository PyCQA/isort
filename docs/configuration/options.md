# Configuration options for isort

As a code formatter isort has opinions. However, it also allows you to have your own. If your opinions disagree with those of isort,
isort will disagree but commit to your way of formatting. To enable this, isort exposes a plethora of options to specify
how you want your imports sorted, organized, and formatted.

Too busy to build your perfect isort configuration? For curated common configurations, see isort's [built-in
profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html).

## Python Version

Tells isort to set the known standard library based on the specified Python version. Default is to assume any Python 3 version could be the target, and use a union of all stdlib modules across versions. If auto is specified, the version of the interpreter used to run isort (currently: 39) will be used.

**Type:** String  
**Default:** `py3`  
**Config default:** `3`  
**Python & Config File Name:** py_version  
**CLI Flags:**

- --py
- --python-version

**Examples:**

### Example `.isort.cfg`

```
[settings]
py_version=39

```

### Example `pyproject.toml`

```
[tool.isort]
py_version=39

```

### Example cli usage

`isort --py 39`

## Force To Top

Force specific imports to the top of their appropriate section.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** force_to_top  
**CLI Flags:**

- -t
- --top

## Skip

Files that isort should skip over. If you want to skip multiple files you should specify twice: `--skip file1 --skip file2`. Values can be file names, directory names or file paths. To skip all files in a nested path, use [`--skip-glob`](#skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `('.bzr', '.direnv', '.eggs', '.git', '.hg', '.mypy_cache', '.nox', '.pants.d', '.pytype' '.svn', '.tox', '.venv', '__pypackages__', '_build', 'buck-out', 'build', 'dist', 'node_modules', 'venv')`  
**Config default:** `['.bzr', '.direnv', '.eggs', '.git', '.hg', '.mypy_cache', '.nox', '.pants.d', '.svn', '.tox', '.venv', '__pypackages__', '_build', 'buck-out', 'build', 'dist', 'node_modules', 'venv']`  
**Python & Config File Name:** skip  
**CLI Flags:**

- -s
- --skip

**Examples:**

### Example `.isort.cfg`

```
[settings]
skip=.gitignore,.dockerignore
```

### Example `pyproject.toml`

```
[tool.isort]
skip = [".gitignore", ".dockerignore"]

```

## Extend Skip

Extends --skip to add additional files that isort should skip over. If you want to skip multiple files you should specify twice: --skip file1 --skip file2. Values can be file names, directory names or file paths. To skip all files in a nested path, use [`--skip-glob`](#skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extend_skip  
**CLI Flags:**

- --extend-skip

**Examples:**

### Example `.isort.cfg`

```
[settings]
extend_skip=.md,.json
```

### Example `pyproject.toml`

```
[tool.isort]
extend_skip = [".md", ".json"]

```

## Skip Glob

Files that isort should skip over. To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** skip_glob  
**CLI Flags:**

- --sg
- --skip-glob

**Examples:**

### Example `.isort.cfg`

```
[settings]
skip_glob=docs/*

```

### Example `pyproject.toml`

```
[tool.isort]
skip_glob = ["docs/*"]

```

## Extend Skip Glob

Additional files that isort should skip over (extending --skip-glob). To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extend_skip_glob  
**CLI Flags:**

- --extend-skip-glob

**Examples:**

### Example `.isort.cfg`

```
[settings]
extend_skip_glob=my_*_module.py,test/*

```

### Example `pyproject.toml`

```
[tool.isort]
extend_skip_glob = ["my_*_module.py", "test/*"]

```

## Skip Gitignore

Treat project as a git repository and ignore files listed in .gitignore. To even skip matching files that have been specified on the command line, use [`--filter-files`](#filter-files).

NOTE: This requires git to be installed and accessible from the same shell as isort.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** skip_gitignore  
**CLI Flags:**

- --gitignore
- --skip-gitignore

## Line Length

The max length of an import line (used for wrapping long imports).

**Type:** Int  
**Default:** `79`  
**Config default:** `79`  
**Python & Config File Name:** line_length  
**CLI Flags:**

- -l
- -w
- --line-length
- --line-width

## Wrap Length

Specifies how long lines that are wrapped should be, if not set line_length is used.
NOTE: wrap_length must be LOWER than or equal to line_length.

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** wrap_length  
**CLI Flags:**

- --wl
- --wrap-length

## Line Ending

Forces line endings to the specified value. If not set, values will be guessed per-file.

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** line_ending  
**CLI Flags:**

- --le
- --line-ending

## Sort Re-exports

Specifies whether to sort re-exports (`__all__` collections) automatically.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** sort_reexports  
**CLI Flags:**

- --srx
- --sort-reexports

## Sections

What sections isort should display imports for and in what order

**Type:** List of Strings  
**Default:** `('FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER')`  
**Config default:** `['FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER']`  
**Python & Config File Name:** sections  
**CLI Flags:** **Not Supported**

## No Sections

Put all imports into the same section bucket

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** no_sections  
**CLI Flags:**

- --ds
- --no-sections

## Known Future Library

Force isort to recognize a module as part of Python's internal future compatibility libraries. WARNING: this overrides the behavior of __future__ handling and therefore can result in code that can't execute. If you're looking to add dependencies such as six, a better option is to create another section below --future using custom sections. See: https://github.com/PyCQA/isort#custom-sections-and-ordering and the discussion here: https://github.com/PyCQA/isort/issues/1463.

**Type:** List of Strings  
**Default:** `('__future__',)`  
**Config default:** `['__future__']`  
**Python & Config File Name:** known_future_library  
**CLI Flags:**

- -f
- --future

## Known Third Party

Force isort to recognize a module as being part of a third party library.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_third_party  
**CLI Flags:**

- -o
- --thirdparty

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_third_party=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_third_party = ["my_module1", "my_module2"]

```

## Known First Party

Force isort to recognize a module as being part of the current python project.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_first_party  
**CLI Flags:**

- -p
- --project

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_first_party=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_first_party = ["my_module1", "my_module2"]

```

## Known Local Folder

Force isort to recognize a module as being a local folder. Generally, this is reserved for relative imports (from . import module).

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** known_local_folder  
**CLI Flags:**

- --known-local-folder

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_local_folder=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_local_folder = ["my_module1", "my_module2"]

```

## Known Standard Library

Force isort to recognize a module as part of Python's standard library.

**Type:** List of Strings  
**Default:** `('_ast', '_dummy_thread', '_thread', 'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'dummy_threading', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fpectl', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'ntpath', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo')`  
**Config default:** `['_ast', '_dummy_thread', '_thread', 'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'dummy_threading', 'email', 'encodings', 'ensurepip', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fpectl', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'macpath', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis', 'nntplib', 'ntpath', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'sre', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', 'zoneinfo']`  
**Python & Config File Name:** known_standard_library  
**CLI Flags:**

- -b
- --builtin

**Examples:**

### Example `.isort.cfg`

```
[settings]
known_standard_library=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
known_standard_library = ["my_module1", "my_module2"]

```

## Extra Standard Library

Extra modules to be included in the list of ones in Python's standard library.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** extra_standard_library  
**CLI Flags:**

- --extra-builtin

**Examples:**

### Example `.isort.cfg`

```
[settings]
extra_standard_library=my_module1,my_module2

```

### Example `pyproject.toml`

```
[tool.isort]
extra_standard_library = ["my_module1", "my_module2"]

```

## Known Other

known_OTHER is how imports of custom sections are defined. OTHER is a placeholder for the custom section name.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** known_other  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
sections=FUTURE,STDLIB,THIRDPARTY,AIRFLOW,FIRSTPARTY,LOCALFOLDER
known_airflow=airflow
```

### Example `pyproject.toml`

```
[tool.isort]
sections = ['FUTURE', 'STDLIB', 'THIRDPARTY', 'AIRFLOW', 'FIRSTPARTY', 'LOCALFOLDER']
known_airflow = ['airflow']
```

## Multi Line Output

Multi line output (0-grid, 1-vertical, 2-hanging, 3-vert-hanging, 4-vert-grid, 5-vert-grid-grouped, 6-deprecated-alias-for-5, 7-noqa, 8-vertical-hanging-indent-bracket, 9-vertical-prefix-from-module-import, 10-hanging-indent-with-parentheses).

**Type:** Wrapmodes  
**Default:** `WrapModes.GRID`  
**Config default:** `WrapModes.GRID`  
**Python & Config File Name:** multi_line_output  
**CLI Flags:**

- -m
- --multi-line

**Examples:**

### Example `.isort.cfg`

```
[settings]
multi_line_output=3
```

### Example `pyproject.toml`

```
[tool.isort]
multi_line_output = 3
```

## Forced Separate

Force certain sub modules to show separately

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** forced_separate  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
forced_separate=glob_exp1,glob_exp2

```

### Example `pyproject.toml`

```
[tool.isort]
forced_separate = ["glob_exp1", "glob_exp2"]

```

## Indent

String to place for indents defaults to "    " (4 spaces).

**Type:** String  
**Default:** `    `  
**Config default:** `    `  
**Python & Config File Name:** indent  
**CLI Flags:**

- -i
- --indent

## Comment Prefix

Allows customizing how isort prefixes comments that it adds or modifies on import linesGenerally `  #` (two spaces before a pound symbol) is use, though one space is also common.

**Type:** String  
**Default:** `  #`  
**Config default:** `  #`  
**Python & Config File Name:** comment_prefix  
**CLI Flags:** **Not Supported**

## Length Sort

Sort imports by their string length.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** length_sort  
**CLI Flags:**

- --ls
- --length-sort

## Length Sort Straight

Sort straight imports by their string length. Similar to `length_sort` but applies only to straight imports and doesn't affect from imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** length_sort_straight  
**CLI Flags:**

- --lss
- --length-sort-straight

## Length Sort Sections

Sort the given sections by length

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** length_sort_sections  
**CLI Flags:** **Not Supported**

**Examples:**

### Example `.isort.cfg`

```
[settings]
length_sort_sections=future,stdlib

```

### Example `pyproject.toml`

```
[tool.isort]
length_sort_sections = ["future", "stdlib"]

```

## Add Imports

Adds the specified import line to all files, automatically determining correct placement.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** add_imports  
**CLI Flags:**

- -a
- --add-import

**Examples:**

### Example `.isort.cfg`

```
[settings]
add_imports=import os,import json

```

### Example `pyproject.toml`

```
[tool.isort]
add_imports = ["import os", "import json"]

```

## Remove Imports

Removes the specified import from all files.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** remove_imports  
**CLI Flags:**

- --rm
- --remove-import

**Examples:**

### Example `.isort.cfg`

```
[settings]
remove_imports=os,json

```

### Example `pyproject.toml`

```
[tool.isort]
remove_imports = ["os", "json"]

```

## Append Only

Only adds the imports specified in --add-import if the file contains existing imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** append_only  
**CLI Flags:**

- --append
- --append-only

## Reverse Relative

Reverse order of relative imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** reverse_relative  
**CLI Flags:**

- --rr
- --reverse-relative

## Force Single Line

Forces all from imports to appear on their own line

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_single_line  
**CLI Flags:**

- --sl
- --force-single-line-imports

## Single Line Exclusions

One or more modules to exclude from the single line rule.

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** single_line_exclusions  
**CLI Flags:**

- --nsl
- --single-line-exclusions

**Examples:**

### Example `.isort.cfg`

```
[settings]
single_line_exclusions=os,json

```

### Example `pyproject.toml`

```
[tool.isort]
single_line_exclusions = ["os", "json"]

```

## Default Section

Sets the default section for import options: ('FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER')

**Type:** String  
**Default:** `THIRDPARTY`  
**Config default:** `THIRDPARTY`  
**Python & Config File Name:** default_section  
**CLI Flags:**

- --sd
- --section-default

## Import Headings

A mapping of import sections to import heading comments that should show above them.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** import_headings  
**CLI Flags:** **Not Supported**

## Import Footers

A mapping of import sections to import footer comments that should show below them.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** import_footers  
**CLI Flags:** **Not Supported**

## Balanced Wrapping

Balances wrapping to produce the most consistent line length possible

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** balanced_wrapping  
**CLI Flags:**

- -e
- --balanced

## Use Parentheses

Use parentheses for line continuation on length limit instead of backslashes. **NOTE**: This is separate from wrap modes, and only affects how individual lines that  are too long get continued, not sections of multiple imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** use_parentheses  
**CLI Flags:**

- --up
- --use-parentheses

## Order By Type

Order imports by type, which is determined by case, in addition to alphabetically.

**NOTE**: type here refers to the implied type from the import name capitalization.
 isort does not do type introspection for the imports. These "types" are simply: CONSTANT_VARIABLE, CamelCaseClass, variable_or_function. If your project follows PEP8 or a related coding standard and has many imports this is a good default, otherwise you likely will want to turn it off. From the CLI the `--dont-order-by-type` option will turn this off.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** order_by_type  
**CLI Flags:**

- --ot
- --order-by-type

## Atomic

Ensures the output doesn't save if the resulting file contains syntax errors.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** atomic  
**CLI Flags:**

- --ac
- --atomic

## Lines Before Imports

The number of blank lines to place before imports. -1 for automatic determination

**Type:** Int  
**Default:** `-1`  
**Config default:** `-1`  
**Python & Config File Name:** lines_before_imports  
**CLI Flags:**

- --lbi
- --lines-before-imports

## Lines After Imports

The number of blank lines to place after imports. -1 for automatic determination

**Type:** Int  
**Default:** `-1`  
**Config default:** `-1`  
**Python & Config File Name:** lines_after_imports  
**CLI Flags:**

- --lai
- --lines-after-imports

## Lines Between Sections

The number of lines to place between sections

**Type:** Int  
**Default:** `1`  
**Config default:** `1`  
**Python & Config File Name:** lines_between_sections  
**CLI Flags:** **Not Supported**

## Lines Between Types

The number of lines to place between direct and from imports

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** lines_between_types  
**CLI Flags:**

- --lbt
- --lines-between-types

## Combine As Imports

Combines as imports on the same line.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_as_imports  
**CLI Flags:**

- --ca
- --combine-as

## Combine Star

Ensures that if a star import is present, nothing else is imported from that namespace.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_star  
**CLI Flags:**

- --cs
- --combine-star

## Include Trailing Comma

Includes a trailing comma on multi line imports that include parentheses.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** include_trailing_comma  
**CLI Flags:**

- --tc
- --trailing-comma
## Split on Trailing Comma

Split imports list followed by a trailing comma into VERTICAL_HANGING_INDENT mode. This follows Black style magic comma.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** split_on_trailing_comma
**CLI Flags:**

- --split-on-trailing-comma

## From First

Switches the typical ordering preference, showing from imports first then straight ones.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** from_first  
**CLI Flags:**

- --ff
- --from-first

## Verbose

Shows verbose output, such as when files are skipped or when a check is successful.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** verbose  
**CLI Flags:**

- -v
- --verbose

## Quiet

Shows extra quiet output, only errors are outputted.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** quiet  
**CLI Flags:**

- -q
- --quiet

## Force Adds

Forces import adds even if the original file is empty.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_adds  
**CLI Flags:**

- --af
- --force-adds

## Force Alphabetical Sort Within Sections

Force all imports to be sorted alphabetically within a section

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_alphabetical_sort_within_sections  
**CLI Flags:**

- --fass
- --force-alphabetical-sort-within-sections

## Force Alphabetical Sort

Force all imports to be sorted as a single section

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_alphabetical_sort  
**CLI Flags:**

- --fas
- --force-alphabetical-sort

## Force Grid Wrap

Force number of from imports (defaults to 2 when passed as CLI flag without value) to be grid wrapped regardless of line length. If 0 is passed in (the global default) only line length is considered.

**Type:** Int  
**Default:** `0`  
**Config default:** `0`  
**Python & Config File Name:** force_grid_wrap  
**CLI Flags:**

- --fgw
- --force-grid-wrap

## Force Sort Within Sections

Don't sort straight-style imports (like import sys) before from-style imports (like from itertools import groupby). Instead, sort the imports by module, independent of import style.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** force_sort_within_sections  
**CLI Flags:**

- --fss
- --force-sort-within-sections

## Lexicographical

Lexicographical order is strictly alphabetical order. For example by default isort will sort `1, 10, 2` into `1, 2, 10` - but with lexicographical sorting enabled it will remain `1, 10, 2`.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** lexicographical  
**CLI Flags:** **Not Supported**

## Group By Package

If `True` isort will automatically create section groups by the top-level package they come from.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** group_by_package  
**CLI Flags:** **Not Supported**

## Ignore Whitespace

Tells isort to ignore whitespace differences when --check-only is being used.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ignore_whitespace  
**CLI Flags:**

- --ws
- --ignore-whitespace

## No Lines Before

Sections which should not be split with previous by empty lines

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** no_lines_before  
**CLI Flags:**

- --nlb
- --no-lines-before

**Examples:**

### Example `.isort.cfg`

```
[settings]
no_lines_before=future,stdlib

```

### Example `pyproject.toml`

```
[tool.isort]
no_lines_before = ["future", "stdlib"]

```

## No Inline Sort

Leaves `from` imports with multiple imports 'as-is' (e.g. `from foo import a, c ,b`).

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** no_inline_sort  
**CLI Flags:**

- --nis
- --no-inline-sort

## Ignore Comments

If enabled, isort will strip comments that exist within import lines.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ignore_comments  
**CLI Flags:** **Not Supported**

## Case Sensitive

Tells isort to include casing when sorting module names

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** case_sensitive  
**CLI Flags:**

- --case-sensitive

## Virtual Env

Virtual environment to use for determining whether a package is third-party

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** virtual_env  
**CLI Flags:**

- --virtual-env

## Conda Env

Conda environment to use for determining whether a package is third-party

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** conda_env  
**CLI Flags:**

- --conda-env

## Ensure Newline Before Comments

Inserts a blank line before a comment following an import.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** ensure_newline_before_comments  
**CLI Flags:**

- -n
- --ensure-newline-before-comments

## Profile

Base profile type to use for configuration. Profiles include: black, django,
pycharm, google, open\_stack, plone, attrs, hug, wemake, appnexus. As well as
any [shared
profiles](https://pycqa.github.io/isort/docs/howto/shared_profiles.html).

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** profile  
**CLI Flags:**

- --profile

## Honor Noqa

Tells isort to honor noqa comments to enforce skipping those comments.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** honor_noqa  
**CLI Flags:**

- --honor-noqa

## Src Paths

Add an explicitly defined source path (modules within src paths have their imports automatically categorized as first_party). Glob expansion (`*` and `**`) is supported for this option.

**Type:** List of Strings  
**Default:** `()`  
**Config default:** `[]`  
**Python & Config File Name:** src_paths  
**CLI Flags:**

- --src
- --src-path

**Examples:**

### Example `.isort.cfg`

```
[settings]
src_paths = src,tests

```

### Example `pyproject.toml`

```
[tool.isort]
src_paths = ["src", "tests"]

```

## Old Finders

Use the old deprecated finder logic that relies on environment introspection magic.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** old_finders  
**CLI Flags:**

- --old-finders
- --magic-placement

## Remove Redundant Aliases

Tells isort to remove redundant aliases from imports, such as `import os as os`. This defaults to `False` simply because some projects use these seemingly useless  aliases to signify intent and change behaviour.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** remove_redundant_aliases  
**CLI Flags:**

- --remove-redundant-aliases

## Float To Top

Causes all non-indented imports to float to the top of the file having its imports sorted (immediately below the top of file comment).
This can be an excellent shortcut for collecting imports every once in a while when you place them in the middle of a file to avoid context switching.

*NOTE*: It currently doesn't work with cimports and introduces some extra over-head and a performance penalty.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** float_to_top  
**CLI Flags:**

- --float-to-top

## Filter Files

Tells isort to filter files even when they are explicitly passed in as part of the CLI command.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** filter_files  
**CLI Flags:**

- --filter-files

## Formatter

Specifies the name of a formatting plugin to use when producing output.

**Type:** String  
**Default:** ` `  
**Config default:** ` `  
**Python & Config File Name:** formatter  
**CLI Flags:**

- --formatter

## Formatting Function

The fully qualified Python path of a function to apply to format code sorted by isort.

**Type:** Nonetype  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** formatting_function  
**CLI Flags:** **Not Supported**

## Color Output

Tells isort to use color in terminal output.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** color_output  
**CLI Flags:**

- --color

## Treat Comments As Code

Tells isort to treat the specified single line comment(s) as if they are code.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** treat_comments_as_code  
**CLI Flags:**

- --treat-comment-as-code

**Examples:**

### Example `.isort.cfg`

```
[settings]
treat_comments_as_code = # my comment 1, # my other comment

```

### Example `pyproject.toml`

```
[tool.isort]
treat_comments_as_code = ["# my comment 1", "# my other comment"]

```

## Treat All Comments As Code

Tells isort to treat all single line comments as if they are code.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** treat_all_comments_as_code  
**CLI Flags:**

- --treat-all-comment-as-code

## Supported Extensions

Specifies what extensions isort can be run against.

**Type:** List of Strings  
**Default:** `('pxd', 'py', 'pyi', 'pyx')`  
**Config default:** `['pxd', 'py', 'pyi', 'pyx']`  
**Python & Config File Name:** supported_extensions  
**CLI Flags:**

- --ext
- --extension
- --supported-extension

**Examples:**

### Example `.isort.cfg`

```
[settings]
supported_extensions=pyw,ext

```

### Example `pyproject.toml`

```
[tool.isort]
supported_extensions = ["pyw", "ext"]

```

## Blocked Extensions

Specifies what extensions isort can never be run against.

**Type:** List of Strings  
**Default:** `('pex',)`  
**Config default:** `['pex']`  
**Python & Config File Name:** blocked_extensions  
**CLI Flags:**

- --blocked-extension

**Examples:**

### Example `.isort.cfg`

```
[settings]
blocked_extensions=pyw,pyc

```

### Example `pyproject.toml`

```
[tool.isort]
blocked_extensions = ["pyw", "pyc"]

```

## Constants

An override list of tokens to always recognize as a CONSTANT for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** constants  
**CLI Flags:** **Not Supported**

## Classes

An override list of tokens to always recognize as a Class for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** classes  
**CLI Flags:** **Not Supported**

## Variables

An override list of tokens to always recognize as a var for order_by_type regardless of casing.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** variables  
**CLI Flags:** **Not Supported**

## Dedup Headings

Tells isort to only show an identical custom import heading comment once, even if there are multiple sections with the comment set.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** dedup_headings  
**CLI Flags:**

- --dedup-headings

## Only Sections

Causes imports to be sorted based on their sections like STDLIB, THIRDPARTY, etc. Within sections, the imports are ordered by their import style and the imports with the same style maintain their relative positions.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** only_sections  
**CLI Flags:**

- --only-sections
- --os

## Only Modified

Suppresses verbose output for non-modified files.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** only_modified  
**CLI Flags:**

- --only-modified
- --om

## Combine Straight Imports

Combines all the bare straight imports of the same section in a single line. Won't work with sections which have 'as' imports

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** combine_straight_imports  
**CLI Flags:**

- --combine-straight-imports
- --csi

## Auto Identify Namespace Packages

Automatically determine local namespace packages, generally by lack of any src files before a src containing directory.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** auto_identify_namespace_packages  
**CLI Flags:** **Not Supported**

## Namespace Packages

Manually specify one or more namespace packages.

**Type:** List of Strings  
**Default:** `frozenset()`  
**Config default:** `[]`  
**Python & Config File Name:** namespace_packages  
**CLI Flags:** **Not Supported**

## Follow Links

If `True` isort will follow symbolic links when doing recursive sorting.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** follow_links  
**CLI Flags:** **Not Supported**

## Indented Import Headings

If `True` isort will apply import headings to indended imports the same way it does unindented ones.

**Type:** Bool  
**Default:** `True`  
**Config default:** `true`  
**Python & Config File Name:** indented_import_headings  
**CLI Flags:** **Not Supported**

## Honor Case In Force Sorted Sections

Honor `--case-sensitive` when `--force-sort-within-sections` is being used. Without this option set, `--order-by-type` decides module name ordering too.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** honor_case_in_force_sorted_sections  
**CLI Flags:**

- --hcss
- --honor-case-in-force-sorted-sections

## Sort Relative In Force Sorted Sections

When using `--force-sort-within-sections`, sort relative imports the same way as they are sorted when not using that setting.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** sort_relative_in_force_sorted_sections  
**CLI Flags:**

- --srss
- --sort-relative-in-force-sorted-sections

## Overwrite In Place

Tells isort to overwrite in place using the same file handle. Comes at a performance and memory usage penalty over its standard approach but ensures all file flags and modes stay unchanged.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** overwrite_in_place  
**CLI Flags:**

- --overwrite-in-place

## Reverse Sort

Reverses the ordering of imports.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** reverse_sort  
**CLI Flags:**

- --reverse-sort

## Star First

Forces star imports above others to avoid overriding directly imported variables.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** star_first  
**CLI Flags:**

- --star-first

## Git Ignore

If `True` isort will honor ignores within locally defined .git_ignore files.

**Type:** Dict  
**Default:** `{}`  
**Config default:** `{}`  
**Python & Config File Name:** git_ignore  
**CLI Flags:** **Not Supported**

## Format Error

Override the format used to print errors.

**Type:** String  
**Default:** `{error}: {message}`  
**Config default:** `{error}: {message}`  
**Python & Config File Name:** format_error  
**CLI Flags:**

- --format-error

## Format Success

Override the format used to print success.

**Type:** String  
**Default:** `{success}: {message}`  
**Config default:** `{success}: {message}`  
**Python & Config File Name:** format_success  
**CLI Flags:**

- --format-success

## Sort Order

Specify sorting function. Can be built in (natural[default] = force numbers to be sequential, native = Python's built-in sorted function) or an installable plugin.

**Type:** String  
**Default:** `natural`  
**Config default:** `natural`  
**Python & Config File Name:** sort_order  
**CLI Flags:**

- --sort-order

## Show Version

Displays the currently installed version of isort.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -V
- --version

**Examples:**

### Example cli usage

`isort --version`

## Version Number

Returns just the current version number without the logo

**Type:** String  
**Default:** `==SUPPRESS==`  
**Config default:** `==SUPPRESS==`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --vn
- --version-number

## Write To Stdout

Force resulting output to stdout, instead of in-place.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -d
- --stdout

## Show Config

See isort's determined config, as well as sources of config options.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --show-config

## Show Files

See the files isort will be run against with the current config options.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --show-files

## Show Diff

Prints a diff of all the changes isort would make to a file, instead of changing it in place

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --df
- --diff

## Check

Checks the file for unsorted / unformatted imports and prints them to the command line without modifying the file. Returns 0 when nothing would change and returns 1 when the file would be reformatted.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -c
- --check-only
- --check

## Settings Path

Explicitly set the settings path or file instead of auto determining based on file location.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --sp
- --settings-path
- --settings-file
- --settings

## Config Root

Explicitly set the config root for resolving all configs. When used with the --resolve-all-configs flag, isort will look at all sub-folders in this config root to resolve config files and sort files based on the closest available config(if any)

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --cr
- --config-root

## Resolve All Configs

Tells isort to resolve the configs for all sub-directories and sort files in terms of its closest config files.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --resolve-all-configs

## Jobs

Number of files to process in parallel. Negative value means use number of CPUs.

**Type:** Int  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -j
- --jobs

## Ask To Apply

Tells isort to apply changes interactively.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --interactive

## Files

One or more Python source files that need their imports sorted.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- 

## Dont Follow Links

Tells isort not to follow symlinks that are encountered when running recursively.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dont-follow-links

## Filename

Provide the filename associated with a stream.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --filename

## Allow Root

Tells isort not to treat / specially, allowing it to be run against the root dir.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --allow-root

## Dont Float To Top

Forces --float-to-top setting off. See --float-to-top for more information.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dont-float-to-top

## Dont Order By Type

Don't order imports by type, which is determined by case, in addition to alphabetically.

**NOTE**: type here refers to the implied type from the import name capitalization.
 isort does not do type introspection for the imports. These "types" are simply: CONSTANT_VARIABLE, CamelCaseClass, variable_or_function. If your project follows PEP8 or a related coding standard and has many imports this is a good default. You can turn this on from the CLI using `--order-by-type`.

**Type:** Bool  
**Default:** `False`  
**Config default:** `false`  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --dt
- --dont-order-by-type

## Ext Format

Tells isort to format the given files according to an extensions formatting rules.

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- --ext-format

## Deprecated Flags

==SUPPRESS==

**Type:** String  
**Default:** `None`  
**Config default:** ` `  
**Python & Config File Name:** **Not Supported**  
**CLI Flags:**

- -k
- --keep-direct-and-as
