"""Tests for the isort import placement module"""

from functools import partial
from pathlib import Path

from isort import place, sections
from isort.settings import Config


def test_module(src_path: Path) -> None:
    place_tester = partial(place.module, config=Config(src_paths=[src_path]))
    assert place_tester("isort") == sections.FIRSTPARTY
    assert place_tester("os") == sections.STDLIB
    assert place_tester(".deprecated") == sections.LOCALFOLDER
    assert place_tester("__future__") == sections.FUTURE
    assert place_tester("hug") == sections.THIRDPARTY


def test_extra_standard_library(src_path: Path) -> None:
    place_tester = partial(
        place.module, config=Config(src_paths=[src_path], extra_standard_library=["hug"])
    )
    assert place_tester("os") == sections.STDLIB
    assert place_tester("hug") == sections.STDLIB


def test_no_standard_library_placement() -> None:
    assert place.module_with_reason(
        "pathlib", config=Config(sections=["THIRDPARTY"], default_section="THIRDPARTY")
    ) == ("THIRDPARTY", "Default option in Config or universal default.")
    assert place.module("pathlib") == "STDLIB"


def test_namespace_package_placement(examples_path: Path) -> None:
    namespace_examples = examples_path / "namespaces"

    implicit = namespace_examples / "implicit"
    pkg_resource = namespace_examples / "pkg_resource"
    pkgutil = namespace_examples / "pkgutil"
    for namespace_test in (implicit, pkg_resource, pkgutil):
        print(namespace_test)
        config = Config(settings_path=namespace_test)
        no_namespaces = Config(settings_path=namespace_test, auto_identify_namespace_packages=False)
        namespace_override = Config(settings_path=namespace_test, known_firstparty=["root.name"])
        assert place.module("root.name", config=config) == "THIRDPARTY"
        assert place.module("root.nested", config=config) == "FIRSTPARTY"
        assert place.module("root.name", config=no_namespaces) == "FIRSTPARTY"
        assert place.module("root.name", config=namespace_override) == "FIRSTPARTY"

    no_namespace = namespace_examples / "none"
    almost_implicit = namespace_examples / "almost-implicit"
    weird_encoding = namespace_examples / "weird_encoding"
    for lacks_namespace in (no_namespace, almost_implicit, weird_encoding):
        config = Config(settings_path=lacks_namespace)
        manual_namespace = Config(settings_path=lacks_namespace, namespace_packages=["root"])
        assert place.module("root.name", config=config) == "FIRSTPARTY"
        assert place.module("root.nested", config=config) == "FIRSTPARTY"
        assert place.module("root.name", config=manual_namespace) == "THIRDPARTY"
        assert place.module("root.nested", config=config) == "FIRSTPARTY"


def test_root_directory_name_is_not_first_party(tmp_path: Path) -> None:
    """A module that only shares its name with the project root directory
    must not be classified as first-party (issue #2240).

    The default src_paths include the project root; the root is a
    container for the project's packages, not a package itself.
    """
    root = tmp_path / "some_name"
    package = root / "package_name"
    package.mkdir(parents=True)
    (package / "__init__.py").touch()
    (root / "pyproject.toml").touch()
    config = Config(directory=str(root))
    assert place.module("package_name", config=config) == sections.FIRSTPARTY
    assert place.module("some_name", config=config) == sections.THIRDPARTY
    assert place.module("third_party", config=config) == sections.THIRDPARTY


def test_src_path_pointing_at_package_directory(tmp_path: Path) -> None:
    """A src_path that points directly at a package directory still
    identifies that package as first-party."""
    package = tmp_path / "mypackage"
    package.mkdir()
    (package / "__init__.py").touch()
    (package / "module.py").touch()
    config = Config(src_paths=[package])
    assert place.module("mypackage", config=config) == sections.FIRSTPARTY


def test_src_path_pointing_at_namespace_package_directory(tmp_path: Path) -> None:
    """Same as above for a namespace package directory (no __init__.py,
    but with module files in it)."""
    package = tmp_path / "mynamespace"
    package.mkdir()
    (package / "module.py").touch()
    config = Config(src_paths=[package])
    assert place.module("mynamespace", config=config) == sections.FIRSTPARTY


def test_package_directory_that_is_also_the_project_root(tmp_path: Path) -> None:
    """A regular package directory still identifies its package as
    first-party when it is also config.directory (its own project root)."""
    package = tmp_path / "mypackage"
    package.mkdir()
    (package / "__init__.py").touch()
    (package / "module.py").touch()
    config = Config(directory=str(package), src_paths=[package])
    assert place.module("mypackage", config=config) == sections.FIRSTPARTY


def test_namespace_package_directory_that_is_also_the_project_root(tmp_path: Path) -> None:
    """Same as above for a namespace package directory (no __init__.py,
    but with module files in it) that is also config.directory."""
    package = tmp_path / "mynamespace"
    package.mkdir()
    (package / "module.py").touch()
    config = Config(directory=str(package), src_paths=[package])
    assert place.module("mynamespace", config=config) == sections.FIRSTPARTY


def test_directory_named_like_module_without_python_source(tmp_path: Path) -> None:
    """The project root does not make a like-named module first-party,
    even if the root is also listed in src_paths explicitly."""
    container = tmp_path / "some_name"
    (container / "docs").mkdir(parents=True)
    (container / "pyproject.toml").touch()
    config = Config(directory=str(container), src_paths=[container])
    assert place.module("some_name", config=config) == sections.THIRDPARTY


def test_directory_named_like_module_with_sibling_module_file(tmp_path: Path) -> None:
    """A module file next to the project root (a sibling sharing the
    root directory's name) is outside the configured src_paths and does
    not make the like-named module first-party."""
    container = tmp_path / "some_name"
    (container / "docs").mkdir(parents=True)
    (container / "pyproject.toml").touch()
    (tmp_path / "some_name.py").touch()
    config = Config(directory=str(container), src_paths=[container])
    assert place.module("some_name", config=config) == sections.THIRDPARTY


def test_namespace_root_with_only_subpackages_that_is_also_the_project_root(
    tmp_path: Path,
) -> None:
    """A namespace package directory containing only subpackages still
    identifies its package as first-party when it is also
    config.directory."""
    package = tmp_path / "mynamespace"
    nested = package / "nested"
    nested.mkdir(parents=True)
    (nested / "__init__.py").touch()
    config = Config(directory=str(package), src_paths=[package])
    assert place.module("mynamespace", config=config) == sections.FIRSTPARTY
    assert place.module("mynamespace.nested", config=config) == sections.FIRSTPARTY
