from collections.abc import Callable
from pathlib import Path
from typing import Protocol

import pytest

from isort import api


class BenchmarkFixture(Protocol):
    def pedantic(self, target: Callable[[], object], *, iterations: int, rounds: int) -> None: ...


imperfect_content = "import b\nimport a\n"
fixed_content = "import a\nimport b\n"


@pytest.fixture
def imperfect(tmp_path: Path) -> Path:
    imperfect_file = tmp_path / "test_needs_changes.py"
    imperfect_file.write_text(imperfect_content, "utf8")
    return imperfect_file


def test_sort_file(benchmark: BenchmarkFixture, imperfect: Path) -> None:
    def sort_file() -> None:
        api.sort_file(imperfect)

    benchmark.pedantic(sort_file, iterations=10, rounds=100)
    assert imperfect.read_text() == fixed_content


def test_sort_file_in_place(benchmark: BenchmarkFixture, imperfect: Path) -> None:
    def sort_file() -> None:
        api.sort_file(imperfect, overwrite_in_place=True)

    benchmark.pedantic(sort_file, iterations=10, rounds=100)
    assert imperfect.read_text() == fixed_content
