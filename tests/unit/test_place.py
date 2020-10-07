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
