"""isort test wide fixtures and configuration"""
import os
from pathlib import Path

import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "../../isort/"))


@pytest.fixture
def test_dir():
    return TEST_DIR


@pytest.fixture
def src_dir():
    return SRC_DIR


@pytest.fixture
def test_path():
    return Path(TEST_DIR).resolve()


@pytest.fixture
def src_path():
    return Path(SRC_DIR).resolve()


@pytest.fixture
def examples_path():
    return Path(TEST_DIR).resolve() / "example_projects"
