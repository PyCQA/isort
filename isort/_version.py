from importlib import metadata

try:
    __version__ = metadata.version("isort")
except metadata.PackageNotFoundError:
    # Case where isort package metadata is not available.
    __version__ = ""
