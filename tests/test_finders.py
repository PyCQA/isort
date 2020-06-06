from pathlib import Path
from unittest.mock import patch

import pytest

from isort import finders, settings
from isort.finders import FindersManager


class TestFindersManager:
    def test_init(self):
        assert FindersManager(settings.DEFAULT_CONFIG)

        class ExceptionOnInit(finders.BaseFinder):
            def __init__(*args, **kwargs):
                super().__init__(*args, **kwargs)
                raise ValueError("test")

        with patch(
            "isort.finders.FindersManager._default_finders_classes",
            FindersManager._default_finders_classes + (ExceptionOnInit,),
        ):
            assert FindersManager(settings.Config(verbose=True))

    def test_no_finders(self):
        assert FindersManager(settings.DEFAULT_CONFIG, []).find("isort") is None

    def test_find_broken_finder(self):
        class ExceptionOnFind(finders.BaseFinder):
            def find(*args, **kwargs):
                raise ValueError("test")

        assert (
            FindersManager(settings.Config(verbose=True), [ExceptionOnFind]).find("isort") is None
        )


class AbstractTestFinder:
    kind = finders.BaseFinder

    @classmethod
    def setup_class(cls):
        cls.instance = cls.kind(settings.DEFAULT_CONFIG)

    def test_create(self):
        assert self.kind(settings.DEFAULT_CONFIG)

    def test_find(self):
        self.instance.find("isort")
        self.instance.find("")


class TestForcedSeparateFinder(AbstractTestFinder):
    kind = finders.ForcedSeparateFinder


class TestDefaultFinder(AbstractTestFinder):
    kind = finders.DefaultFinder


class TestKnownPatternFinder(AbstractTestFinder):
    kind = finders.KnownPatternFinder


class TestLocalFinder(AbstractTestFinder):
    kind = finders.LocalFinder


class TestPathFinder(AbstractTestFinder):
    kind = finders.PathFinder

    def test_conda_and_virtual_env(self, tmpdir):
        python3lib = tmpdir.mkdir("lib").mkdir("python3")
        python3lib.mkdir("site-packages").mkdir("y")
        python3lib.mkdir("n").mkdir("site-packages").mkdir("x")
        tmpdir.mkdir("z").join("__init__.py").write("__version__ = '1.0.0'")
        tmpdir.chdir()

        conda = self.kind(settings.Config(conda_env=str(tmpdir)), str(tmpdir))
        venv = self.kind(settings.Config(virtual_env=str(tmpdir)), str(tmpdir))
        assert conda.find("y") == venv.find("y") == "THIRDPARTY"
        assert conda.find("x") == venv.find("x") == "THIRDPARTY"
        assert conda.find("z") == "THIRDPARTY"
        assert conda.find("os") == venv.find("os") == "STDLIB"

    def test_default_section(self, tmpdir):
        tmpdir.join("file.py").write("import b\nimport a\n")
        assert self.kind(settings.Config(default_section="CUSTOM"), tmpdir).find("file") == "CUSTOM"

    def test_src_paths(self, tmpdir):
        tmpdir.join("file.py").write("import b\nimport a\n")
        assert (
            self.kind(settings.Config(src_paths=[Path(str(tmpdir))]), tmpdir).find("file")
            == "FIRSTPARTY"
        )


class TestPipfileFinder(AbstractTestFinder):
    kind = finders.PipfileFinder


class TestRequirementsFinder(AbstractTestFinder):
    kind = finders.RequirementsFinder

    def test_no_pipreqs(self):
        with patch("isort.finders.pipreqs", None):
            assert not self.kind(settings.DEFAULT_CONFIG).find("isort")

    def test_not_enabled(self):
        test_finder = self.kind(settings.DEFAULT_CONFIG)
        test_finder.enabled = False
        assert not test_finder.find("isort")

    def test_requirements_dir(self, tmpdir):
        tmpdir.mkdir("requirements").join("development.txt").write("x==1.00")
        test_finder = self.kind(settings.DEFAULT_CONFIG, str(tmpdir))
        assert test_finder.find("x")
