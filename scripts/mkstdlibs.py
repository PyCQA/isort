#!/usr/bin/env python3
import sys

from stdlibs import py39

PATH = "isort/stdlibs/py{}.py"
VERSIONS = [
    ("3", "9"),
    ("3", "10"),
    ("3", "11"),
    ("3", "12"),
    ("3", "13"),
]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""

for version_info in VERSIONS:
    version = ".".join(version_info)

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {"_ast", "posixpath", "ntpath", "sre_constants", "sre_parse", "sre_compile", "sre"}

    if version_info == ("3", "9"):
        modules |= py39.module_names
    else:
        modules |= sys.stdlib_module_names
    modules -= {"__future__", "__main__", "antigravity", "this"}

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(version)
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(modules):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
