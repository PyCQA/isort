import os
from pathlib import Path

import pytest

from isort import files
from isort.main import main
from isort.settings import DEFAULT_CONFIG, Config


@pytest.fixture(autouse=True)
def isolate_git_markers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep enclosing checkout markers out of temporary repository scenarios."""
    original_exists = Path.exists

    def exists(path: Path) -> bool:
        if path.name == ".git" and not path.is_relative_to(tmp_path):
            return False
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)


@pytest.fixture(params=["directory", "file"])
def git_marker(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture(
    params=[
        "subdirectory_alias",
        "external_alias_chain",
        "nested_repository_alias",
        "nested_subdirectory_alias",
    ]
)
def repository_alias_case(
    tmp_path: Path, request: pytest.FixtureRequest, git_marker: str
) -> tuple[Path, Path]:
    """Return an aliased input and the outside file it must not select."""

    def repository(path: Path) -> Path:
        path.mkdir(parents=True)
        if git_marker == "directory":
            (path / ".git").mkdir()
        else:
            (path / ".git").write_text("gitdir: elsewhere\n")
        return path

    if request.param == "subdirectory_alias":
        project = repository(tmp_path / "project")
        package = project / "package"
        package.mkdir()
        outside = tmp_path / "outside.py"
        (package / "escape.py").symlink_to(outside)
        alias = tmp_path / "alias"
        alias.symlink_to(package, target_is_directory=True)
        source = alias / "escape.py"
    elif request.param == "external_alias_chain":
        project = repository(tmp_path / "project")
        external = repository(tmp_path / "external")
        package = external / "package"
        package.mkdir()
        outside = package / "module.py"
        (external / "alias").symlink_to(package, target_is_directory=True)
        (project / "link").symlink_to(external, target_is_directory=True)
        source = project / "link" / "alias" / "module.py"
    else:
        project = repository(tmp_path / "project")
        package = repository(project / "physical" / "inner")
        outside = project / "shared.py"
        alias = project / "alias"
        if request.param == "nested_subdirectory_alias":
            package = package / "package"
            package.mkdir()
            alias.symlink_to(package, target_is_directory=True)
            source = alias / "escape.py"
        else:
            alias.symlink_to(package.parent, target_is_directory=True)
            source = alias / "inner" / "escape.py"
        (package / "escape.py").symlink_to(outside)

    outside.write_text("import sys\nimport os\n")
    return source, outside


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
@pytest.mark.parametrize("direct_file", [False, True])
@pytest.mark.parametrize("follow_links", [False, True])
def test_find_preserves_repository_boundary_through_aliases(
    tmp_path: Path,
    repository_alias_case: tuple[Path, Path],
    direct_file: bool,
    follow_links: bool,
) -> None:
    source, _ = repository_alias_case
    target = source if direct_file else source.parent
    skipped: list[str] = []
    broken: list[str] = []

    found = tuple(
        files.find(
            [target],
            Config(directory=str(tmp_path), follow_links=follow_links),
            skipped,
            broken,
        )
    )

    assert found == ()
    assert str(source) in skipped or str(target) in skipped
    assert set(skipped) <= {str(source), str(target), str(target / ".git")}
    assert broken == []


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
@pytest.mark.parametrize("direct_file", [False, True])
def test_cli_preserves_outside_file_through_repository_aliases(
    repository_alias_case: tuple[Path, Path], direct_file: bool
) -> None:
    source, outside = repository_alias_case
    before = outside.read_bytes()

    main([str(source if direct_file else source.parent)])

    assert outside.read_bytes() == before


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_allows_explicit_physical_inputs(
    tmp_path: Path, repository_alias_case: tuple[Path, Path]
) -> None:
    _, physical_file = repository_alias_case

    assert tuple(files.find([physical_file], Config(directory=str(tmp_path)), [], [])) == (
        physical_file,
    )


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_preserves_internal_files_below_subdirectory_alias(tmp_path: Path) -> None:
    package = tmp_path / "project" / "package"
    package.mkdir(parents=True)
    (package.parent / ".git").mkdir()
    (package / "module.py").write_text("import os\n")
    alias = tmp_path / "alias"
    alias.symlink_to(package, target_is_directory=True)

    assert tuple(files.find([alias], Config(directory=str(tmp_path)), [], [])) == (
        str(alias / "module.py"),
    )


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
@pytest.mark.parametrize("aliased", [False, True])
def test_find_preserves_physical_and_aliased_nested_repository_boundary(
    tmp_path: Path, aliased: bool
) -> None:
    project = tmp_path / "project"
    inner = project / "physical" / "inner"
    inner.mkdir(parents=True)
    (project / ".git").mkdir()
    (inner / ".git").mkdir()
    outside = project / "shared.py"
    outside.write_text("import os\n")
    (inner / "escape.py").symlink_to(outside)
    alias = project / "alias"
    alias.symlink_to(inner.parent, target_is_directory=True)
    source = (alias / "inner" if aliased else inner) / "escape.py"
    skipped: list[str] = []

    assert tuple(files.find([source], Config(directory=str(project)), skipped, [])) == ()
    assert skipped == [str(source)]


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks requires extra privileges")
def test_find_git_root_prefers_nearest_repository_below_alias(tmp_path: Path) -> None:
    physical = tmp_path / "physical"
    outer = physical / "outer"
    inner = outer / "inner"
    inner.mkdir(parents=True)
    (outer / ".git").mkdir()
    (inner / ".git").mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(physical, target_is_directory=True)

    assert files._find_git_root(alias / "outer" / "inner") == alias / "outer" / "inner"


def test_external_symlink_check_ignores_unrelated_git_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "module.py"
    source.write_text("import os\n")
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    monkeypatch.setattr(files, "_find_git_root", lambda path: unrelated)

    assert not files._is_external_git_symlink(source)


@pytest.mark.parametrize("error", [OSError, RuntimeError])
def test_prune_directories_records_resolution_errors_and_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: type[Exception]
) -> None:
    broken_directory = tmp_path / "broken"
    healthy_directory = tmp_path / "healthy"
    broken_directory.mkdir()
    healthy_directory.mkdir()
    original_resolve = Path.resolve

    def resolve(path: Path, strict: bool = False) -> Path:
        if path == broken_directory:
            raise error("Cannot resolve directory")
        return original_resolve(path, strict=strict)

    # Exercise pruning after the independent skip-policy check has accepted the directory.
    monkeypatch.setattr(Config, "is_skipped", lambda self, path: False)
    monkeypatch.setattr(Path, "resolve", resolve)
    dirnames = ["broken", "healthy"]
    skipped: list[str] = []
    broken: list[str] = []
    visited: set[Path] = set()

    files._prune_directories(tmp_path, dirnames, DEFAULT_CONFIG, skipped, broken, visited)

    assert dirnames == ["healthy"]
    assert skipped == []
    assert broken == [str(broken_directory)]
    assert visited == {healthy_directory.resolve()}


def test_find(tmp_path: Path) -> None:
    tmp_file = tmp_path / "file.py"
    tmp_file.write_text("import os, sys\n")
    assert tuple(files.find((tmp_file,), DEFAULT_CONFIG, [], [])) == (tmp_file,)


def test_find_ignores_unsupported_files(tmp_path: Path) -> None:
    source = tmp_path / "module.py"
    source.write_text("import os\n")
    (tmp_path / "notes.txt").write_text("Not Python source\n")

    assert tuple(files.find([tmp_path], Config(directory=str(tmp_path)), [], [])) == (str(source),)


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
