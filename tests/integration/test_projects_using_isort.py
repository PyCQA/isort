"""Tests projects that use isort to see if any differences are found between
their current imports and what isort suggest on the develop branch.
This is an important early warning signal of regressions.

NOTE: If you use isort within a public repository, please feel empowered to add your project here!
It is important to isort that as few regressions as possible are experienced by our users.
Having your project tested here is the most sure way to keep those regressions form ever happening.
"""

from __future__ import annotations

from collections.abc import Generator, Sequence
from pathlib import Path
from subprocess import check_call

import pytest

from isort.main import main


def git_clone(repository_url: str, directory: Path) -> None:
    """Clones the given repository into the given directory path"""
    check_call(["git", "clone", "--depth", "1", repository_url, str(directory)])


def run_isort(arguments: Generator[str, None, None] | Sequence[str]) -> None:
    """Runs isort in diff and check mode with the given arguments"""
    main(["--check-only", "--diff", *arguments])


def test_django(tmp_path: Path) -> None:
    git_clone("https://github.com/django/django.git", tmp_path)
    run_isort(
        str(target_dir)
        for target_dir in (tmp_path / "django", tmp_path / "tests", tmp_path / "scripts")
    )


def test_plone(tmp_path: Path) -> None:
    git_clone("https://github.com/plone/plone.app.multilingualindexes.git", tmp_path)
    run_isort([str(tmp_path / "src"), "--skip", "languagefallback.py"])


@pytest.mark.skip(
    "Skip for now as #2295 introduce a breaking change. Can be re-enabled after pandas has updated."
)
def test_pandas(tmp_path: Path) -> None:
    git_clone("https://github.com/pandas-dev/pandas.git", tmp_path)
    run_isort((str(tmp_path / "pandas"), "--skip", "__init__.py"))


def test_habitat_lab(tmp_path: Path) -> None:
    git_clone("https://github.com/facebookresearch/habitat-lab.git", tmp_path)
    run_isort([str(tmp_path)])


def test_pylint(tmp_path: Path) -> None:
    git_clone("https://github.com/PyCQA/pylint.git", tmp_path)
    run_isort([str(tmp_path), "--skip", "bad.py"])


def test_hypothesis(tmp_path: Path) -> None:
    git_clone("https://github.com/HypothesisWorks/hypothesis.git", tmp_path)
    run_isort(
        (
            str(tmp_path),
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


def test_pyramid(tmp_path: Path) -> None:
    git_clone("https://github.com/Pylons/pyramid.git", tmp_path)
    run_isort(
        str(target_dir)
        for target_dir in (tmp_path / "src" / "pyramid", tmp_path / "tests", tmp_path / "setup.py")
    )


def test_products_zopetree(tmp_path: Path) -> None:
    git_clone("https://github.com/jugmac00/Products.ZopeTree.git", tmp_path)
    run_isort([str(tmp_path)])


def test_dobby(tmp_path: Path) -> None:
    git_clone("https://github.com/rocketDuck/dobby.git", tmp_path)
    run_isort([str(tmp_path / "tests"), str(tmp_path / "src")])


def test_zope(tmp_path: Path) -> None:
    git_clone("https://github.com/zopefoundation/Zope.git", tmp_path)
    run_isort([str(tmp_path), "--skip", "util.py"])
