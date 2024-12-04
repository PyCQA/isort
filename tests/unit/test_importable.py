"""Basic set of tests to ensure entire code base is importable"""

import pytest


def test_importable():
    """Simple smoketest to ensure all isort modules are importable"""

    import isort
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
    import isort.stdlibs.py36
    import isort.stdlibs.py37
    import isort.stdlibs.py38
    import isort.stdlibs.py39
    import isort.stdlibs.py310
    import isort.stdlibs.py311
    import isort.stdlibs.py312
    import isort.utils
    import isort.wrap
    import isort.wrap_modes

    with pytest.raises(SystemExit):
        import isort.__main__  # noqa: F401
