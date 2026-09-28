"""isort test wide fixtures and configuration"""

import os
from pathlib import Path

import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "../../isort/"))


@pytest.fixture
def test_dir() -> str:
    return TEST_DIR


@pytest.fixture
def src_dir() -> str:
    return SRC_DIR


@pytest.fixture
def test_path() -> Path:
    return Path(TEST_DIR).resolve()


@pytest.fixture
def src_path() -> Path:
    return Path(SRC_DIR).resolve()


@pytest.fixture
def examples_path() -> Path:
    return Path(TEST_DIR).resolve() / "example_projects"
