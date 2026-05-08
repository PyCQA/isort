import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
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

_GENERATED_INCLUDES = ("_readme_include.md", "_changelog_include.md")


def _generate_includes(app: "Sphinx") -> None:
    """Create Sphinx-friendly copies of README and CHANGELOG at build time."""
    src = Path(app.srcdir)
    build_dir = src / "_build"
    build_dir.mkdir(parents=True, exist_ok=True)

    pairs = [
        (src.parent / "README.md", build_dir / "_readme_include.md"),
        (src.parent / "CHANGELOG.md", build_dir / "_changelog_include.md"),
    ]
    for source, dest in pairs:
        if not source.exists():
            continue
        content = source.read_text(encoding="utf-8")
        # Rewrite relative links: (docs/X) -> (X)
        content = re.sub(r"\]\(docs/", "](", content)
        dest.write_text(content, encoding="utf-8")


def _cleanup_includes(app: "Sphinx", _exception: Optional[Exception]) -> None:
    """Remove generated include files after the build."""
    src = Path(app.srcdir)
    build_dir = src / "_build"
    for name in _GENERATED_INCLUDES:
        path = build_dir / name
        if path.exists():
            path.unlink()


def setup(app: "Sphinx") -> Dict[str, Any]:
    """Register build hooks."""
    app.connect("builder-inited", _generate_includes)
    app.connect("build-finished", _cleanup_includes)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
