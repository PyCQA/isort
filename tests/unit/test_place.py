"""Tests for the isort import placement module"""
from functools import partial

from isort import place, sections
from isort.settings import Config


def test_module(src_path):
    place_tester = partial(place.module, config=Config(src_paths=[src_path]))
    assert place_tester("isort") == sections.FIRSTPARTY
    assert place_tester("os") == sections.STDLIB
    assert place_tester(".deprecated") == sections.LOCALFOLDER
    assert place_tester("__future__") == sections.FUTURE
    assert place_tester("hug") == sections.THIRDPARTY


def test_extra_standard_library(src_path):
    place_tester = partial(
        place.module, config=Config(src_paths=[src_path], extra_standard_library=["hug"])
    )
    assert place_tester("os") == sections.STDLIB
    assert place_tester("hug") == sections.STDLIB


def test_no_standard_library_placement():
    assert place.module_with_reason(
        "pathlib", config=Config(sections=["THIRDPARTY"], default_section="THIRDPARTY")
    ) == ("THIRDPARTY", "Default option in Config or universal default.")
    assert place.module("pathlib") == "STDLIB"


def test_namespace_package_placement(examples_path):
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
    for lacks_namespace in (no_namespace, almost_implicit):
        config = Config(settings_path=lacks_namespace)
        manual_namespace = Config(settings_path=lacks_namespace, namespace_packages=["root"])
        assert place.module("root.name", config=config) == "FIRSTPARTY"
        assert place.module("root.nested", config=config) == "FIRSTPARTY"
        assert place.module("root.name", config=manual_namespace) == "THIRDPARTY"
        assert place.module("root.nested", config=config) == "FIRSTPARTY"
