import importlib.machinery
import os
import posixpath
from pathlib import Path
from unittest.mock import patch

from isort import sections, settings
from isort.deprecated import finders
from isort.deprecated.finders import FindersManager
from isort.settings import Config

PIPFILE = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[requires]
python_version = "3.5"

[packages]
Django = "~=1.11"
deal = {editable = true, git = "https://github.com/orsinium/deal.git"}

[dev-packages]
"""


class TestFindersManager:
    def test_init(self):
        assert FindersManager(settings.DEFAULT_CONFIG)

        class ExceptionOnInit(finders.BaseFinder):
            def __init__(*args, **kwargs):
                super().__init__(*args, **kwargs)
                raise ValueError("test")

        with patch(
            "isort.deprecated.finders.FindersManager._default_finders_classes",
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
            == settings.DEFAULT_CONFIG.default_section
        )


class TestPipfileFinder(AbstractTestFinder):
    kind = finders.PipfileFinder


class TestRequirementsFinder(AbstractTestFinder):
    kind = finders.RequirementsFinder

    def test_no_pipreqs(self):
        with patch("isort.deprecated.finders.pipreqs", None):
            assert not self.kind(settings.DEFAULT_CONFIG).find("isort")

    def test_not_enabled(self):
        test_finder = self.kind(settings.DEFAULT_CONFIG)
        test_finder.enabled = False
        assert not test_finder.find("isort")

    def test_requirements_dir(self, tmpdir):
        tmpdir.mkdir("requirements").join("development.txt").write("x==1.00")
        test_finder = self.kind(settings.DEFAULT_CONFIG, str(tmpdir))
        assert test_finder.find("x")


def test_requirements_finder(tmpdir) -> None:
    subdir = tmpdir.mkdir("subdir").join("lol.txt")
    subdir.write("flask")
    req_file = tmpdir.join("requirements.txt")
    req_file.write("Django==1.11\n-e git+https://github.com/orsinium/deal.git#egg=deal\n")
    for path in (str(tmpdir), str(subdir)):

        finder = finders.RequirementsFinder(config=Config(), path=path)

        files = list(finder._get_files())
        assert len(files) == 1  # file finding
        assert files[0].endswith("requirements.txt")  # file finding
        assert set(finder._get_names(str(req_file))) == {"Django", "deal"}  # file parsing

        assert finder.find("django") == sections.THIRDPARTY  # package in reqs
        assert finder.find("flask") is None  # package not in reqs
        assert finder.find("deal") == sections.THIRDPARTY  # vcs

        assert len(finder.mapping) > 100
        assert finder._normalize_name("deal") == "deal"
        assert finder._normalize_name("Django") == "django"  # lowercase
        assert finder._normalize_name("django_haystack") == "haystack"  # mapping
        assert finder._normalize_name("Flask-RESTful") == "flask_restful"  # conver `-`to `_`

    req_file.remove()


def test_pipfile_finder(tmpdir) -> None:
    pipfile = tmpdir.join("Pipfile")
    pipfile.write(PIPFILE)
    finder = finders.PipfileFinder(config=Config(), path=str(tmpdir))

    assert set(finder._get_names(str(tmpdir))) == {"Django", "deal"}  # file parsing

    assert finder.find("django") == sections.THIRDPARTY  # package in reqs
    assert finder.find("flask") is None  # package not in reqs
    assert finder.find("deal") == sections.THIRDPARTY  # vcs

    assert len(finder.mapping) > 100
    assert finder._normalize_name("deal") == "deal"
    assert finder._normalize_name("Django") == "django"  # lowercase
    assert finder._normalize_name("django_haystack") == "haystack"  # mapping
    assert finder._normalize_name("Flask-RESTful") == "flask_restful"  # conver `-`to `_`

    pipfile.remove()


def test_path_finder(monkeypatch) -> None:
    config = config = Config()
    finder = finders.PathFinder(config=config)
    third_party_prefix = next(path for path in finder.paths if "site-packages" in path)
    ext_suffixes = importlib.machinery.EXTENSION_SUFFIXES
    imaginary_paths = {
        posixpath.join(finder.stdlib_lib_prefix, "example_1.py"),
        posixpath.join(third_party_prefix, "example_2.py"),
        posixpath.join(os.getcwd(), "example_3.py"),
    }
    imaginary_paths.update(
        {
            posixpath.join(third_party_prefix, "example_" + str(i) + ext_suffix)
            for i, ext_suffix in enumerate(ext_suffixes, 4)
        }
    )

    monkeypatch.setattr(
        "isort.deprecated.finders.exists_case_sensitive", lambda p: p in imaginary_paths
    )
    assert finder.find("example_1") == sections.STDLIB
    assert finder.find("example_2") == sections.THIRDPARTY
    assert finder.find("example_3") == settings.DEFAULT_CONFIG.default_section
    for i, _ in enumerate(ext_suffixes, 4):
        assert finder.find("example_" + str(i)) == sections.THIRDPARTY
