#!/usr/bin/env python3
import re

from stdlibs import py38, py39, py310, py311, py312, py313, py314

PATH = "isort/stdlibs/py{}.py"
VERSIONS = [
    py38,
    py39,
    py310,
    py311,
    py312,
    py313,
    py314,
]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""


for version_module in VERSIONS:
    version_match = re.match(
        r"^stdlibs\.py(?P<major>\d)(?P<minor>\d+)$",
        version_module.__name__,
    )
    version_info = (version_match.groupdict()["major"], version_match.groupdict()["minor"])

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(".".join(version_info))
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(version_module.module_names):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
