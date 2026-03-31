import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "isort"
copyright = "2013-2026, Timothy Crosley"
author = "Timothy Crosley"

extensions = [
    "myst_parser",
    "sphinx_immaterial",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

html_theme = "sphinx_immaterial"
html_title = "isort"
html_static_path = ["../art"]
html_logo = "../art/logo.png"
html_favicon = "../art/logo.png"

myst_heading_anchors = 2

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
# To avoid a lot of errors about problems generating autodoc for the defaults, we ignore them.
autodoc_preserve_defaults = True
autodoc_default_options = {"members": True, "show-inheritance": True, "undoc-members": True}

html_theme_options = {
    "site_url": "https://isort.readthedocs.io/",
    "repo_url": "https://github.com/PyCQA/isort/",
    "repo_name": "isort",
    "palette": {"primary": "deep-orange", "accent": "deep-orange"},
}
