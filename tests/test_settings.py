import pytest

from isort import exceptions
from isort.settings import Config


class TestConfig:
    def test_init(self):
        assert Config()

    def test_invalid_pyversion(self):
        with pytest.raises(ValueError):
            Config(py_version=10)

    def test_invalid_profile(self):
        with pytest.raises(exceptions.ProfileDoesNotExist):
            Config(profile="blackandwhitestylemixedwithpep8")
