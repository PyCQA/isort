import pytest

from isort import api

imperfect_content = "import b\nimport a\n"
fixed_content = "import a\nimport b\n"


@pytest.fixture
def imperfect(tmpdir) -> None:
    imperfect_file = tmpdir.join("test_needs_changes.py")
    imperfect_file.write_text(imperfect_content, "utf8")
    return imperfect_file


def test_sort_file(benchmark, imperfect) -> None:
    def sort_file():
        api.sort_file(imperfect)

    benchmark.pedantic(sort_file, iterations=10, rounds=100)
    assert imperfect.read() == fixed_content


def test_sort_file_in_place(benchmark, imperfect) -> None:
    def sort_file():
        api.sort_file(imperfect, overwrite_in_place=True)

    benchmark.pedantic(sort_file, iterations=10, rounds=100)
    assert imperfect.read() == fixed_content
