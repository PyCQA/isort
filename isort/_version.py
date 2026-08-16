from importlib import metadata

__version__ = metadata.version("isort")
_IS_COMPILED = __file__.endswith((".so", ".pyd"))
_VERSION_STRING = f"{__version__} (compiled {'yes' if _IS_COMPILED else 'no'})"
