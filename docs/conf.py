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
    "sphinx.ext.napoleon",
]

html_theme = "sphinx_immaterial"
html_title = "isort"
html_static_path = ["../art"]
html_logo = "../art/logo.png"
html_favicon = "../art/logo.png"

myst_heading_anchors = 2

suppress_warnings = ["docutils"]

html_theme_options = {
    "site_url": "https://isort.readthedocs.io/",
    "repo_url": "https://github.com/PyCQA/isort/",
    "palette": {"primary": "deep-orange", "accent": "deep-orange"},
}
