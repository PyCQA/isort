"""Tests projects that use isort to see if any differences are found between
their current imports and what isort suggest on the develop branch.
This is an important early warning signal of regressions.

NOTE: If you use isort within a public repository, please feel empowered to add your project here!
It is important to isort that as few regressions as possible are experienced by our users.
Having your project tested here is the most sure way to keep those regressions form ever happening.
"""

from __future__ import annotations

from pathlib import Path
from subprocess import check_call
from typing import Generator, Sequence

from isort.main import main


def git_clone(repository_url: str, directory: Path):
    """Clones the given repository into the given directory path"""
    check_call(["git", "clone", "--depth", "1", repository_url, str(directory)])


def run_isort(arguments: Generator[str, None, None] | Sequence[str]):
    """Runs isort in diff and check mode with the given arguments"""
    main(["--check-only", "--diff", *arguments])


def test_django(tmpdir):
    git_clone("https://github.com/django/django.git", tmpdir)
    run_isort(
        str(target_dir) for target_dir in (tmpdir / "django", tmpdir / "tests", tmpdir / "scripts")
    )


def test_plone(tmpdir):
    git_clone("https://github.com/plone/plone.app.multilingualindexes.git", tmpdir)
    run_isort([str(tmpdir / "src"), "--skip", "languagefallback.py"])


def test_pandas(tmpdir):
    git_clone("https://github.com/pandas-dev/pandas.git", tmpdir)
    run_isort((str(tmpdir / "pandas"), "--skip", "__init__.py"))


def test_habitat_lab(tmpdir):
    git_clone("https://github.com/facebookresearch/habitat-lab.git", tmpdir)
    run_isort([str(tmpdir)])


def test_pylint(tmpdir):
    git_clone("https://github.com/PyCQA/pylint.git", tmpdir)
    run_isort([str(tmpdir), "--skip", "bad.py"])


def test_hypothesis(tmpdir):
    git_clone("https://github.com/HypothesisWorks/hypothesis.git", tmpdir)
    run_isort(
        (
            str(tmpdir),
            "--skip",
            "tests",
            "--profile",
            "black",
            "--ca",
            "--project",
            "hypothesis",
            "--project",
            "hypothesistooling",
        )
    )


def test_pyramid(tmpdir):
    git_clone("https://github.com/Pylons/pyramid.git", tmpdir)
    run_isort(
        str(target_dir)
        for target_dir in (tmpdir / "src" / "pyramid", tmpdir / "tests", tmpdir / "setup.py")
    )


def test_products_zopetree(tmpdir):
    git_clone("https://github.com/jugmac00/Products.ZopeTree.git", tmpdir)
    run_isort([str(tmpdir)])


def test_dobby(tmpdir):
    git_clone("https://github.com/rocketDuck/dobby.git", tmpdir)
    run_isort([str(tmpdir / "tests"), str(tmpdir / "src")])


def test_zope(tmpdir):
    git_clone("https://github.com/zopefoundation/Zope.git", tmpdir)
    run_isort([str(tmpdir), "--skip", "util.py"])
