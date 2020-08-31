from typing import get_type_hints

import hypothesis
from hypothesis import strategies as st

import isort


def _as_config(kw) -> isort.Config:
    kw["atomic"] = False
    if "wrap_length" in kw and "line_length" in kw:
        kw["wrap_length"], kw["line_length"] = sorted([kw["wrap_length"], kw["line_length"]])
    try:
        return isort.Config(**kw)
    except ValueError:
        kw["wrap_length"] = 0
        return isort.Config(**kw)


def configs() -> st.SearchStrategy[isort.Config]:
    """Generate arbitrary Config objects."""
    skip = {
        "line_ending",
        "sections",
        "known_standard_library",
        "known_future_library",
        "known_third_party",
        "known_first_party",
        "known_local_folder",
        "extra_standard_library",
        "forced_separate",
        "lines_after_imports",
        "add_imports",
        "lines_between_sections",
        "lines_between_types",
        "sources",
        "virtual_env",
        "conda_env",
        "directory",
        "formatter",
        "formatting_function",
        "comment_prefix",
        "atomic",
        "skip",
        "src_paths",
    }
    inferred_kwargs = {
        k: st.from_type(v)
        for k, v in get_type_hints(isort.settings._Config).items()
        if k not in skip
    }
    specific = {
        "line_length": st.integers(0, 200),
        "wrap_length": st.integers(0, 200),
        "indent": st.integers(0, 20).map(lambda n: n * " "),
        "default_section": st.sampled_from(sorted(isort.settings.KNOWN_SECTION_MAPPING)),
        "force_grid_wrap": st.integers(0, 20),
        "profile": st.sampled_from(sorted(isort.settings.profiles)),
        "py_version": st.sampled_from(("auto",) + isort.settings.VALID_PY_TARGETS),
    }
    kwargs = {**inferred_kwargs, **specific}
    return st.fixed_dictionaries({}, optional=kwargs).map(_as_config)


st.register_type_strategy(isort.Config, configs())

CODE_SNIPPET = """
'''Taken from bottle.py

Copyright (c) 2009-2018, Marcel Hellkamp.
License: MIT (see LICENSE for details)
'''
# Lots of stdlib and builtin differences.
if py3k:
    import http.client as httplib
    import _thread as thread
    from urllib.parse import urljoin, SplitResult as UrlSplitResult
    from urllib.parse import urlencode, quote as urlquote, unquote as urlunquote
    urlunquote = functools.partial(urlunquote, encoding='latin1')
    from http.cookies import SimpleCookie, Morsel, CookieError
    from collections.abc import MutableMapping as DictMixin
    import pickle # comment number 2
    from io import BytesIO
    import configparser

    basestring = str
    unicode = str
    json_loads = lambda s: json_lds(touni(s))
    callable = lambda x: hasattr(x, '__call__')
    imap = map

    def _raise(*a):
        raise a[0](a[1]).with_traceback(a[2])
else:  # 2.x
    import httplib
    import thread
    from urlparse import urljoin, SplitResult as UrlSplitResult
    from urllib import urlencode, quote as urlquote, unquote as urlunquote
    from Cookie import SimpleCookie, Morsel, CookieError
    from itertools import imap
    import cPickle as pickle
    from StringIO import StringIO as BytesIO
    import ConfigParser as configparser  # commentnumberone
    from collections import MutableMapping as DictMixin
    unicode = unicode
    json_loads = json_lds
    exec(compile('def _raise(*a): raise a[0], a[1], a[2]', '<py3fix>', 'exec'))
"""
SHOULD_RETAIN = [
    """'''Taken from bottle.py

Copyright (c) 2009-2018, Marcel Hellkamp.
License: MIT (see LICENSE for details)
'''""",
    "# Lots of stdlib and builtin differences.",
    "if py3k:",
    "http.client",
    "_thread",
    "urllib.parse",
    "urlencode",
    "urlunquote = functools.partial(urlunquote, encoding='latin1')",
    "http.cookies",
    "SimpleCookie",
    "collections.abc",
    "pickle",
    "comment number 2",
    "io",
    "configparser",
    """basestring = str
    unicode = str
    json_loads = lambda s: json_lds(touni(s))
    callable = lambda x: hasattr(x, '__call__')
    imap = map

    def _raise(*a):
        raise a[0](a[1]).with_traceback(a[2])
else:  # 2.x
""",
    "httplib",
    "thread",
    "urlparse",
    "urllib",
    "Cookie",
    "itertools",
    "cPickle",
    "StringIO",
    "ConfigParser",
    "commentnumberone",
    "collections",
    """unicode = unicode
    json_loads = json_lds
    exec(compile('def _raise(*a): raise a[0], a[1], a[2]', '<py3fix>', 'exec'))""",
]


@hypothesis.given(
    config=st.from_type(isort.Config),
    disregard_skip=st.booleans(),
)
def test_isort_is_idempotent(config: isort.Config, disregard_skip: bool) -> None:
    try:
        result = isort.code(CODE_SNIPPET, config=config, disregard_skip=disregard_skip)
        result = isort.code(result, config=config, disregard_skip=disregard_skip)
        assert result == isort.code(result, config=config, disregard_skip=disregard_skip)
    except ValueError:
        pass


@hypothesis.given(
    config=st.from_type(isort.Config),
    disregard_skip=st.booleans(),
)
def test_isort_doesnt_lose_imports_or_comments(config: isort.Config, disregard_skip: bool) -> None:
    result = isort.code(CODE_SNIPPET, config=config, disregard_skip=disregard_skip)
    for should_be_retained in SHOULD_RETAIN:
        if should_be_retained not in result:
            if config.ignore_comments and should_be_retained.startswith("comment"):
                continue

            assert should_be_retained in result
