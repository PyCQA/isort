"""isort/natural.py.

Enables sorting strings that contain numbers naturally

usage:
    natural.nsorted(list)

Copyright (C) 2013  Timothy Edmund Crosley

Implementation originally from @HappyLeapSecond stack overflow user in response to:
   https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
import re
from typing import Any, Callable, Iterable, List, Mapping, Optional


def _atoi(text: str) -> Any:
    return int(text) if text.isdigit() else text


def _natural_keys(text: str) -> List[Any]:
    return [_atoi(c) for c in re.split(r'(\d+)', text)]


def get_naturally_sortable_module_name(
    module_name: str,
    config: Mapping[str, Any],
    sub_imports: bool = False,
    ignore_case: bool = False,
    section_name: Optional[Any] = None
) -> str:
    dots = 0
    while module_name.startswith('.'):
        dots += 1
        module_name = module_name[1:]

    if dots:
        module_name = '{} {}'.format(('.' * dots), module_name)

    prefix = ""
    if ignore_case:
        module_name = str(module_name).lower()
    else:
        module_name = str(module_name)

    if sub_imports and config['order_by_type']:
        if module_name.isupper() and len(module_name) > 1:
            prefix = "A"
        elif module_name[0:1].isupper():
            prefix = "B"
        else:
            prefix = "C"
    module_name = module_name.lower()
    if section_name is None or 'length_sort_' + str(section_name).lower() not in config:
        length_sort = config['length_sort']
    else:
        length_sort = config['length_sort_' + str(section_name).lower()]
    return "{0}{1}{2}".format(module_name in config['force_to_top'] and "A" or "B", prefix,
                              length_sort and (str(len(module_name)) + ":" + module_name) or module_name)


def nsorted(
    to_sort: Iterable[str],
    key: Optional[Callable[[str], str]] = None
) -> List[str]:
    """Returns a naturally sorted list"""
    if key is None:
        key_callback = _natural_keys
    else:
        def key_callback(text: str) -> List[Any]:
            return _natural_keys(key(text))

    return sorted(to_sort, key=key_callback)
