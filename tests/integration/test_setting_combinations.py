import isort
import hypothesis
from hypothesis import find, settings, Verbosity
from hypothesis import strategies as st

CODE_SNIPPET = """
''' Taken from bottle.py

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
SHOULD_RETAIN = ["""''' Taken from bottle.py

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
    exec(compile('def _raise(*a): raise a[0], a[1], a[2]', '<py3fix>', 'exec'))"""
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
