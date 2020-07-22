#!/usr/bin/env python3

from sphinx.ext.intersphinx import fetch_inventory

URL = "https://docs.python.org/{}/objects.inv"
PATH = "isort/stdlibs/py{}.py"
VERSIONS = [("2", "7"), ("3", "5"), ("3", "6"), ("3", "7"), ("3", "8"), ("3", "9")]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""


class FakeConfig:
    intersphinx_timeout = None
    tls_verify = True
    user_agent = ""


class FakeApp:
    srcdir = ""
    config = FakeConfig()


for version_info in VERSIONS:
    version = ".".join(version_info)
    url = URL.format(version)
    invdata = fetch_inventory(FakeApp(), "", url)

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {"posixpath", "ntpath", "sre_constants", "sre_parse", "sre_compile", "sre"}
    for module in invdata["py:module"]:
        root, *_ = module.split(".")
        if root not in ["__future__", "__main__"]:
            modules.add(root)

    path = PATH.format("".join(version_info))
    with open(path, "w") as stdlib_file:
        docstring = DOCSTRING.format(version)
        stdlib_file.write(f'"""{docstring}"""\n\n')
        stdlib_file.write("stdlib = {\n")
        for module in sorted(modules):
            stdlib_file.write(f'    "{module}",\n')
        stdlib_file.write("}\n")
