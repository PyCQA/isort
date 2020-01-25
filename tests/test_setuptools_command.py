from distutils.dist import Distribution
from unittest.mock import MagicMock

from isort import setuptools_commands


def test_run():
    command = setuptools_commands.ISortCommand(Distribution())
    command.initialize_options()
    command.finalize_options()
    command.run()
