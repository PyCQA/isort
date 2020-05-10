from unittest.mock import patch

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

    def __init__(self):
        self.instance = self.kind(settings.DEFAULT_CONFIG)

    def test_create(self):
        assert self.kind(settings.DEFAULT_CONFIG)

    def test_find(self):
        self.instance.find("isort")


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


class TestPipfileFinder(AbstractTestFinder):
    kind = finders.PipfileFinder


class TestRequirementsFinder(AbstractTestFinder):
    kind = finders.RequirementsFinder
