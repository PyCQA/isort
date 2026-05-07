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

_GENERATED_INCLUDES = ("_readme_include.md", "_changelog_include.md")


def _generate_includes(app):
    """Create Sphinx-friendly copies of README and CHANGELOG at build time."""
    import re

    src = app.srcdir
    pairs = [
        (os.path.join(src, "..", "README.md"), os.path.join(src, "_readme_include.md")),
        (os.path.join(src, "..", "CHANGELOG.md"), os.path.join(src, "_changelog_include.md")),
    ]
    for source, dest in pairs:
        with open(source, encoding="utf-8") as f:
            content = f.read()
        # Rewrite relative links: (docs/X) -> (X)
        content = re.sub(r"\]\(docs/", "](", content)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)


def _cleanup_includes(app, exception):
    """Remove generated include files after the build."""
    for name in _GENERATED_INCLUDES:
        path = os.path.join(app.srcdir, name)
        if os.path.exists(path):
            os.remove(path)


def setup(app):
    app.connect("builder-inited", _generate_includes)
    app.connect("build-finished", _cleanup_includes)

