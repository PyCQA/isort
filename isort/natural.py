"""isort/natural.py.

Enables sorting strings that contain numbers naturally

usage:
    natural.nsorted(list)

Copyright (C) 2013  Timothy Edmund Crosley

Implementation originally from @HappyLeapSecond stack overflow user in response to:
   https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
"""
import re
from typing import Any, Callable, Iterable, List, Optional


def _atoi(text: str) -> Any:
    return int(text) if text.isdigit() else text


def _natural_keys(text: str) -> List[Any]:
    return [_atoi(c) for c in re.split(r"(\d+)", text)]


def nsorted(to_sort: Iterable[str], key: Optional[Callable[[str], Any]] = None) -> List[str]:
    """Returns a naturally sorted list"""
    if key is None:
        key_callback = _natural_keys
    else:

        def key_callback(text: str) -> List[Any]:
            return _natural_keys(key(text))  # type: ignore

    return sorted(to_sort, key=key_callback)
