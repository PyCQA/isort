import os
import re
import sys
from pathlib import Path

from sphinx.application import Sphinx

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

def _generate_includes(app: Sphinx) -> None:
    """Create Sphinx-friendly copies of some files at build time."""
    # Use absolute paths based on this file's location
    root_dir = Path(__file__).parent.absolute().parent
    gen_dir = Path(__file__).parent.absolute() / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)

    for file in ("CHANGELOG.md", "README.md"):
        content = (root_dir / file).read_text(encoding="utf-8")
        content = re.sub(r"\]\(docs/(.*?)\.md\)", r"](../\1)", content)
        (gen_dir / file).write_text(content, encoding="utf-8")


def setup(app: Sphinx) -> None:
    """Register build hooks."""
    app.connect("builder-inited", _generate_includes)
