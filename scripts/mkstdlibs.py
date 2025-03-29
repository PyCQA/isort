#!/usr/bin/env python3
from stdlibs import py39, py310, py311, py312, py313

PATH = "isort/stdlibs/py{}.py"
VERSIONS = {
    ("3", "9"): py39,
    ("3", "10"): py310,
    ("3", "11"): py311,
    ("3", "12"): py312,
    ("3", "13"): py313,
}

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""

for version_info, version_module in VERSIONS.items():
    version = ".".join(version_info)

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {"_ast", "posixpath", "ntpath", "sre_parse", "sre_compile", "sre"}

    modules |= version_module.module_names
    modules -= {"__future__", "__main__"}

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(version)
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(modules):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
