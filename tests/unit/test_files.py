import os
from pathlib import Path

import pytest

from isort import files
from isort.main import main
from isort.settings import DEFAULT_CONFIG, Config


def test_find(tmp_path: Path) -> None:
    tmp_file = tmp_path / "file.py"
    tmp_file.write_text("import os, sys\n")
    assert tuple(files.find((tmp_file,), DEFAULT_CONFIG, [], [])) == (tmp_file,)


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_skips_symlinks_outside_git_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    scan = project / "scan"
    scan.mkdir()

    internal_file = project / "internal.py"
    internal_file.write_text("import os\n")
    internal_file_link = scan / "internal_file.py"
    internal_file_link.symlink_to(internal_file)
    internal_directory = project / "internal"
    internal_directory.mkdir()
    nested_repository = internal_directory / "nested_repository"
    nested_repository.mkdir()
    (nested_repository / ".git").mkdir()
    (nested_repository / "module.py").write_text("import os\n")
    internal_directory_link = scan / "internal_directory"
    internal_directory_link.symlink_to(internal_directory, target_is_directory=True)

    external_directory = tmp_path / "external"
    external_directory.mkdir()
    (external_directory / ".git").mkdir()
    external_file = external_directory / "external.py"
    external_file.write_text("import os\n")
    external_file_link = scan / "external_file.py"
    external_file_link.symlink_to(external_file)
    external_directory_link = scan / "external_directory"
    external_directory_link.symlink_to(external_directory, target_is_directory=True)

    skipped: list[str] = []
    found = set(files.find([scan], Config(directory=str(project)), skipped, []))

    assert found == {
        str(internal_file_link),
        str(internal_directory_link / "nested_repository" / "module.py"),
    }
    assert set(skipped) == {
        str(external_file_link),
        str(external_directory_link),
        str(internal_directory_link / "nested_repository" / ".git"),
    }


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
@pytest.mark.parametrize("direct_file", [False, True])
def test_find_git_repository_below_symlinked_parent(tmp_path: Path, direct_file: bool) -> None:
    physical = tmp_path / "physical"
    project = physical / "project"
    project.mkdir(parents=True)
    (project / ".git").mkdir()
    (project / "internal.py").write_text("import os\n")
    alias = tmp_path / "alias"
    alias.symlink_to(physical, target_is_directory=True)

    external = tmp_path / "external"
    external.mkdir()
    (external / ".git").mkdir()
    external_file = external / "module.py"
    external_file.write_text("import os\n")
    (project / "external.py").symlink_to(external_file)
    (project / "external").symlink_to(external, target_is_directory=True)

    aliased_project = alias / "project"
    target = aliased_project / "external" / "module.py" if direct_file else aliased_project
    skipped: list[str] = []
    found = set(files.find([target], Config(directory=str(project)), skipped, []))

    if direct_file:
        assert found == set()
        assert skipped == [str(target)]
    else:
        assert found == {str(aliased_project / "internal.py")}
        assert set(skipped) == {
            str(aliased_project / ".git"),
            str(aliased_project / "external.py"),
            str(aliased_project / "external"),
        }


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_direct_symlinks_respect_git_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").write_text("gitdir: elsewhere\n")
    internal_file = project / "internal.py"
    internal_file.write_text("import os\n")
    internal_link = project / "internal_link.py"
    internal_link.symlink_to(internal_file)
    external_file = tmp_path / "external.py"
    external_file.write_text("import os\n")
    external_link = project / "external_link.py"
    external_link.symlink_to(external_file)

    skipped: list[str] = []
    found = tuple(
        files.find([internal_link, external_link], Config(directory=str(project)), skipped, [])
    )

    assert found == (internal_link,)
    assert skipped == [str(external_link)]


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
@pytest.mark.parametrize("git_marker", ["directory", "file"])
def test_find_direct_file_below_external_directory_symlink(tmp_path: Path, git_marker: str) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    external_directory = tmp_path / "external"
    external_directory.mkdir()
    if git_marker == "directory":
        (external_directory / ".git").mkdir()
    else:
        (external_directory / ".git").write_text("gitdir: elsewhere\n")
    external_file = external_directory / "module.py"
    external_file.write_text("import sys\nimport os\n")
    external_link = project / "external"
    external_link.symlink_to(external_directory, target_is_directory=True)
    linked_file = external_link / "module.py"

    skipped: list[str] = []
    found = tuple(files.find([linked_file], Config(directory=str(project)), skipped, []))

    assert found == ()
    assert skipped == [str(linked_file)]


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_cli_does_not_modify_files_below_external_symlink(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    external_directory = tmp_path / "external"
    external_directory.mkdir()
    external_file = external_directory / "module.py"
    unsorted = "import sys\nimport os\n"
    external_file.write_text(unsorted)
    external_link = project / "external"
    external_link.symlink_to(external_directory, target_is_directory=True)

    main([str(external_link / "module.py")])

    assert external_file.read_text() == unsorted


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_reports_broken_and_cyclic_links(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    broken_link = project / "broken.py"
    broken_link.symlink_to(project / "missing.py")
    cyclic_link = project / "cycle"
    cyclic_link.symlink_to(cyclic_link, target_is_directory=True)
    broken: list[str] = []

    found = tuple(
        files.find(
            [broken_link, cyclic_link],
            Config(directory=str(project)),
            [],
            broken,
        )
    )

    assert found == ()
    assert broken == [str(broken_link), str(cyclic_link)]


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_preserves_symlinks_without_git_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    external_file = tmp_path / "external.py"
    external_file.write_text("import os\n")
    external_link = project / "external_link.py"
    external_link.symlink_to(external_file)

    assert tuple(files.find([external_link], Config(directory=str(project)), [], [])) == (
        external_link,
    )
