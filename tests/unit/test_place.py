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


def test_src_path_name_matching_thirdparty_not_firstparty(tmp_path: Path) -> None:
    # A root directory whose name matches a module name must not cause that module
    # to be identified as FIRSTPARTY unless the directory itself is a Python module/package.
    root = tmp_path / "some_name"
    root.mkdir()
    (root / "pyproject.toml").write_text('[project]\nname = "package_name"\n', "utf-8")
    pkg = root / "package_name"
    pkg.mkdir()
    (pkg / "__init__.py").touch()
    (pkg / "file1.py").touch()

    config = Config(src_paths=[root / "src", root])
    assert place.module("package_name", config=config) == sections.FIRSTPARTY
    assert place.module("some_name", config=config) == sections.THIRDPARTY

    # Subdirectory with same name as third-party import but no __init__.py (issue #2247)
    app_fastapi = tmp_path / "app" / "fastapi"
    app_fastapi.mkdir(parents=True)
    (app_fastapi / "same_dir_module.py").touch()
    (app_fastapi / "main.py").touch()

    config_2247 = Config(src_paths=[app_fastapi, tmp_path])
    assert place.module("same_dir_module", config=config_2247) == sections.FIRSTPARTY
    assert place.module("fastapi", config=config_2247) == sections.THIRDPARTY


def test_src_path_namespace_package_root_placement(tmp_path: Path) -> None:
    # When src_paths points directly at an implicit namespace package root,
    # both the bare namespace package name and its submodules should resolve as FIRSTPARTY.
    nspkg = tmp_path / "nspkg"
    sub = nspkg / "sub"
    sub.mkdir(parents=True)
    (sub / "__init__.py").touch()

    config = Config(src_paths=[nspkg], auto_identify_namespace_packages=True)
    assert place.module("nspkg.sub", config=config) == sections.FIRSTPARTY
    assert place.module("nspkg", config=config) == sections.FIRSTPARTY

    config_explicit = Config(src_paths=[nspkg], namespace_packages=["nspkg"])
    assert place.module("nspkg.sub", config=config_explicit) == sections.FIRSTPARTY
    assert place.module("nspkg", config=config_explicit) == sections.FIRSTPARTY

