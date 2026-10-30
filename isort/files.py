import os
from collections.abc import Iterable, Iterator
from pathlib import Path

from isort.settings import Config


def _find_git_root(path: Path) -> Path | None:
    """Find the source Git repository, allowing a symlinked repository alias."""
    absolute_path = path.absolute()
    start = absolute_path if absolute_path.is_dir() else absolute_path.parent
    directories = (start, *start.parents)
    git_root = None
    # Check links from the source side before accepting a target-side .git.
    # Internal aliases may still lead to a nearer, nested repository.
    for directory in reversed(directories):
        if directory.is_symlink():
            resolved = directory.resolve()
            if git_root is not None and not resolved.is_relative_to(git_root.resolve()):
                return git_root
            # An alias can skip a physical repository marker, including a
            # nested repository inside the current boundary.
            git_root = next(
                (parent for parent in (resolved, *resolved.parents) if (parent / ".git").exists()),
                git_root,
            )
        if (directory / ".git").exists():
            git_root = directory

    return git_root


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
    # The root may be physical rather than a lexical parent of an alias.
    if not any(directory.is_symlink() for directory in (absolute_path, *absolute_path.parents)):
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
