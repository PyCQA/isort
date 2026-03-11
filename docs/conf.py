"""Sphinx configuration for isort documentation."""

project = "isort"
copyright = "2013-2024, Timothy Crosley"  # noqa: A001
author = "Timothy Crosley"

extensions = [
    "myst_parser",
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "quick_start/0.-try.md",
    "quick_start/interactive.css",
    "quick_start/interactive.js",
    "quick_start/isort-*.whl",
]

html_theme = "furo"
html_title = "isort"
html_static_path = ["../art"]
html_logo = "../art/logo.png"
html_favicon = "../art/logo.png"

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
]

suppress_warnings = [
    "myst.header",
    "myst.xref_missing",
    "misc.highlighting_failure",
]
