import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

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


def _generate_includes(app: Any) -> None:
    """Create Sphinx-friendly copies of README and CHANGELOG at build time."""
    import re
    from pathlib import Path

    try:
        src = Path(app.srcdir)
        gen_dir = src / "generated"
        gen_dir.mkdir(parents=True, exist_ok=True)

        pairs = [
            (src.parent / "README.md", gen_dir / "_readme_include.md"),
            (src.parent / "CHANGELOG.md", gen_dir / "_changelog_include.md"),
        ]
        for source, dest in pairs:
            if source.exists():
                content = source.read_text(encoding="utf-8")
                # Rewrite relative links: (docs/X) -> (X)
                content = re.sub(r"\]\(docs/", "](", content)
                dest.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"Warning: Failed to generate docs includes: {e}")


def _cleanup_includes(app: Any, _exception: Optional[Exception]) -> None:
    """Remove generated include files after the build."""
    from pathlib import Path

    try:
        src = Path(app.srcdir)
        gen_dir = src / "generated"
        for name in _GENERATED_INCLUDES:
            path = gen_dir / name
            if path.exists():
                path.unlink()
    except Exception:
        pass


def setup(app: Any) -> Dict[str, Any]:
    """Register build hooks."""
    app.connect("builder-inited", _generate_includes)
    app.connect("build-finished", _cleanup_includes)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
