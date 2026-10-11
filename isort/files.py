import os
from collections.abc import Iterable, Iterator
from pathlib import Path

from isort.settings import Config


def _find_git_root(path: Path) -> Path | None:
    """Find the source Git repository, allowing a symlinked repository alias."""
    absolute_path = path.absolute()
    start = absolute_path.parent if path.is_symlink() or not path.is_dir() else absolute_path
    directories = (start, *start.parents)
    symlink_index = next(
        (i for i, directory in enumerate(directories) if directory.is_symlink()), -1
    )
    root_below_link = None
    # Prefer the source repository above the closest directory symlink: a
    # .git entry below it may belong to an external target. If there is no
    # source repository, the link may simply alias the repository itself.
    for i, directory in enumerate(directories):
        if (directory / ".git").exists():
            if i > symlink_index:
                return directory
            if root_below_link is None:
                root_below_link = directory

    return root_below_link


def _is_external_git_symlink(path: Path) -> bool:
    """Detect links that resolve outside the containing source Git repository."""
    # Broken links are reported through ``broken`` by ``find``. Resolving a
    # symlink cycle can also raise, so leave both cases to the caller.
    if not path.exists():
        return False

    git_root = _find_git_root(path)
    if git_root is None:
        return False

    absolute_path = path.absolute()
    absolute_root = git_root.absolute()
    try:
        relative_path = absolute_path.relative_to(absolute_root)
    except ValueError:
        return False

    current_path = absolute_root
    contains_symlink = False
    for part in relative_path.parts:
        current_path /= part
        if current_path.is_symlink():
            contains_symlink = True
            break

    if not contains_symlink:
        return False

    try:
        path.resolve().relative_to(git_root.resolve())
    except (OSError, RuntimeError, ValueError):
        return True

    return False


def _prune_directories(
    base_path: Path,
    dirnames: list[str],
    config: Config,
    skipped: list[str],
    broken: list[str],
    visited_dirs: set[Path],
) -> None:
    """Prune an os.walk step and record skipped, broken and visited directories."""
    for dirname in list(dirnames):
        full_path = base_path / dirname
        if (full_path.is_symlink() and _is_external_git_symlink(full_path)) or config.is_skipped(
            full_path
        ):
            skipped.append(str(full_path))
            dirnames.remove(dirname)
            continue

        try:
            resolved_path = full_path.resolve()
        except (OSError, RuntimeError):
            broken.append(str(full_path))
            dirnames.remove(dirname)
            continue

        if resolved_path in visited_dirs:  # pragma: no cover
            dirnames.remove(dirname)
        visited_dirs.add(resolved_path)


def find(
    paths: Iterable[str | Path], config: Config, skipped: list[str], broken: list[str]
) -> Iterator[str | Path]:
    """Finds and provides an iterator for all Python source files defined in paths."""
    visited_dirs: set[Path] = set()

    for path in paths:
        path_object = Path(path)
        if _is_external_git_symlink(path_object):
            skipped.append(str(path))
            continue

        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(
                path, topdown=True, followlinks=config.follow_links
            ):
                _prune_directories(Path(dirpath), dirnames, config, skipped, broken, visited_dirs)

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if config.is_supported_filetype(filepath):
                        absolute_path = Path(os.path.abspath(filepath))
                        if (
                            absolute_path.is_symlink() and _is_external_git_symlink(absolute_path)
                        ) or config.is_skipped(absolute_path):
                            skipped.append(os.path.abspath(filepath))
                        else:
                            yield filepath
        elif not os.path.exists(path):
            broken.append(str(path))
        else:
            yield path
