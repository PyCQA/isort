"""Tests projects that use isort to see if any differences are found between
their current imports and what isort suggest on the develop branch.
This is an important early warning signal of regressions.

NOTE: If you use isort within a public repository, please feel empowered to add your project here!
It is important to isort that as few regressions as possible are experienced by our users.
Having your project tested here is the most sure way to keep those regressions form ever happening.
"""
from subprocess import check_call

from isort.main import main


def test_django(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/django/django.git", str(tmpdir)]
    )
    isort_target_dirs = [
        str(target_dir) for target_dir in (tmpdir / "django", tmpdir / "tests", tmpdir / "scripts")
    ]
    main(["--check-only", "--diff", *isort_target_dirs])


def test_plone(tmpdir):
    check_call(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/plone/plone.app.multilingualindexes.git",
            str(tmpdir),
        ]
    )
    main(["--check-only", "--diff", str(tmpdir / "src")])


def test_pandas(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/pandas-dev/pandas.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir / "pandas"), "--skip", "__init__.py"])


def test_fastapi(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/tiangolo/fastapi.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir / "fastapi")])


def test_zulip(tmpdir):
    check_call(["git", "clone", "--depth", "1", "https://github.com/zulip/zulip.git", str(tmpdir)])
    main(["--check-only", "--diff", str(tmpdir), "--skip", "__init__.pyi"])


def test_habitat_lab(tmpdir):
    check_call(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/facebookresearch/habitat-lab.git",
            str(tmpdir),
        ]
    )
    main(["--check-only", "--diff", str(tmpdir)])


def test_tmuxp(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/tmux-python/tmuxp.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir)])


def test_websockets(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/aaugustin/websockets.git", str(tmpdir)]
    )
    main(
        [
            "--check-only",
            "--diff",
            str(tmpdir),
            "--skip",
            "example",
            "--skip",
            "docs",
            "--skip",
            "compliance",
        ]
    )


def test_airflow(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/apache/airflow.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir)])


def test_typeshed(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/python/typeshed.git", str(tmpdir)]
    )
    main(
        [
            "--check-only",
            "--diff",
            str(tmpdir),
            "--skip",
            "tests",
            "--skip",
            "scripts",
            "--skip",
            f"{tmpdir}/third_party/2and3/yaml/__init__.pyi",
        ]
    )


def test_pylint(tmpdir):
    check_call(["git", "clone", "--depth", "1", "https://github.com/PyCQA/pylint.git", str(tmpdir)])
    main(["--check-only", "--diff", str(tmpdir)])


def test_poetry(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/python-poetry/poetry.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir), "--skip", "tests"])


def test_hypothesis(tmpdir):
    check_call(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/HypothesisWorks/hypothesis.git",
            str(tmpdir),
        ]
    )
    main(["--check-only", "--diff", str(tmpdir), "--skip", "tests"])


def test_pillow(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/python-pillow/Pillow.git", str(tmpdir)]
    )
    main(["--check-only", "--diff", str(tmpdir), "--skip", "tests"])


def test_attrs(tmpdir):
    check_call(
        ["git", "clone", "--depth", "1", "https://github.com/python-attrs/attrs.git", str(tmpdir)]
    )
    main(
        [
            "--check-only",
            "--diff",
            str(tmpdir),
            "--skip",
            "tests",
            "--ext",
            "py",
            "--skip",
            "_compat.py",
        ]
    )
