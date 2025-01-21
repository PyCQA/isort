#!/usr/bin/env python3
import re

from stdlibs import py38, py39, py310, py311, py312, py313

URL = "https://docs.python.org/{}/objects.inv"
PATH = "isort/stdlibs/py{}.py"
VERSIONS = [
    py38,
    py39,
    py310,
    py311,
    py312,
    py313,
]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""


class FakeConfig:
    intersphinx_timeout = None
    tls_verify = True
    user_agent = ""
    tls_cacerts = None


class FakeApp:
    srcdir = ""
    config = FakeConfig()


for version_module in VERSIONS:
    version_match = re.match(
        r"^stdlibs\.py(?P<major>\d)(?P<minor>\d+)$",
        version_module.__name__,
    )
    version_info = (version_match.groupdict()["major"], version_match.groupdict()["minor"])

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {"_ast", "posixpath", "ntpath", "sre_constants", "sre_parse", "sre_compile", "sre"}
    modules.update(
        {
            module_name
            for module_name in version_module.module_names
            if not module_name.startswith("_")
        }
    )

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(".".join(version_info))
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(modules):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
