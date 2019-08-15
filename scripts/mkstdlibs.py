#!/usr/bin/env python3

from sphinx.ext.intersphinx import fetch_inventory


URL = "https://docs.python.org/{}/objects.inv"
PATH = "isort/stdlibs/py{}.py"
VERSIONS = [("2", "7"), ("3",)]

DOCSTRING = """
File contains the standard library of Python {}.

DO NOT EDIT. If the standard library changes, a new list should be created
using the mkstdlibs.py script.
"""


class FakeConfig:
    intersphinx_timeout = None
    tls_verify = True


class FakeApp:
    srcdir = ""
    config = FakeConfig()


for version_info in VERSIONS:
    version = ".".join(version_info)
    url = URL.format(version)
    invdata = fetch_inventory(FakeApp(), "", url)

    modules = set()
    for module in invdata["py:module"]:
        root, *_ = module.split(".")
        if root not in ["__future__", "__main__"]:
            modules.add(root)

    path = PATH.format("".join(version_info))
    with open(path, "w") as fp:
        docstring = DOCSTRING.format(version)
        fp.write('"""{}"""\n\n'.format(docstring))
        fp.write("stdlib = [\n")
        for module in sorted(modules):
            fp.write('    "{}",\n'.format(module))
        fp.write("]\n")
