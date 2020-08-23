"""Basic set of tests to ensure entire code base is importable"""
import pytest


def test_importable():
    """Simple smoketest to ensure all isort modules are importable"""

    import isort
    import isort._future
    import isort._future._dataclasses
    import isort._version
    import isort.api
    import isort.comments
    import isort.deprecated.finders
    import isort.exceptions
    import isort.format
    import isort.hooks
    import isort.logo
    import isort.main
    import isort.output
    import isort.parse
    import isort.place
    import isort.profiles
    import isort.pylama_isort
    import isort.sections
    import isort.settings
    import isort.setuptools_commands
    import isort.sorting
    import isort.stdlibs
    import isort.stdlibs.all
    import isort.stdlibs.py2
    import isort.stdlibs.py3
    import isort.stdlibs.py27
    import isort.stdlibs.py35
    import isort.stdlibs.py36
    import isort.stdlibs.py37
    import isort.utils
    import isort.wrap
    import isort.wrap_modes

    with pytest.raises(SystemExit):
        import isort.__main__  # noqa: F401
