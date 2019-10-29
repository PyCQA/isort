import sys

if sys.version_info.major <= 3 and sys.version_info.minor <= 6:
    from . import _dataclasses as dataclasses
else:
    import dataclasses

dataclass = dataclasses.dataclass

__all__ = ["dataclasses", "dataclass"]
