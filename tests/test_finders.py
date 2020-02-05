from isort import finders, settings


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
