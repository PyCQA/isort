"""pie_slice/overrides.py.

Overrides Python syntax to conform to the Python3 version as much as possible using a '*' import

Copyright (C) 2013  Timothy Edmund Crosley

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
from __future__ import absolute_import

import collections
import sys

__version__ = "1.1.0"

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
VERSION = sys.version_info

native_dict = dict
native_round = round
native_filter = filter
native_map = map
native_zip = zip
native_range = range
native_str = str
native_chr = chr
native_input = input
native_next = next
native_object = object

common = ['native_dict', 'native_round', 'native_filter', 'native_map', 'native_range', 'native_str', 'native_chr',
          'native_input', 'PY2', 'PY3', 'u', 'itemsview', 'valuesview', 'keysview', 'execute', 'integer_types',
          'native_next', 'native_object', 'with_metaclass', 'lru_cache']


def with_metaclass(meta, *bases):
    """Enables use of meta classes across Python Versions. taken from jinja2/_compat.py.

    Use it like this::

        class BaseForm(object):
            pass

        class FormType(type):
            pass

        class Form(with_metaclass(FormType, BaseForm)):
            pass

    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


def unmodified_isinstance(*bases):
    """When called in the form

    MyOverrideClass(unmodified_isinstance(BuiltInClass))

    it allows calls against passed in built in instances to pass even if there not a subclass

    """
    class UnmodifiedIsInstance(type):
        @classmethod
        def __instancecheck__(cls, instance):
            if cls.__name__ in (str(base.__name__) for base in bases):
                return isinstance(instance, bases)

            return type.__instancecheck__(cls, instance)

    return with_metaclass(UnmodifiedIsInstance, *bases)


if PY3:
    import urllib
    import builtins
    from urllib import parse

    input = input
    integer_types = (int, )

    def u(string):
        return string

    def itemsview(collection):
        return collection.items()

    def valuesview(collection):
        return collection.values()

    def keysview(collection):
        return collection.keys()

    urllib.quote = parse.quote
    urllib.quote_plus = parse.quote_plus
    urllib.unquote = parse.unquote
    urllib.unquote_plus = parse.unquote_plus
    urllib.urlencode = parse.urlencode
    execute = getattr(builtins, 'exec')
    if VERSION[1] < 2:
        def callable(entity):
            return hasattr(entity, '__call__')
        common.append('callable')

    def apply_changes_to_python_environment():
        pass

    __all__ = common + ['urllib', 'apply_changes_to_python_environment']
else:
    from itertools import ifilter as filter  # noqa: F401
    from itertools import imap as map  # noqa: F401
    from itertools import izip as zip  # noqa: F401
    from decimal import Decimal, ROUND_HALF_EVEN

    try:
        str = unicode
        chr = unichr
        input = raw_input
        range = xrange
        integer_types = (int, long)
    except NameError:  # Python 3
        sys.exit('This should not happen!')

    import sys
    stdout = sys.stdout
    stderr = sys.stderr

    def _create_not_allowed(name):
        def _not_allow(*args, **kwargs):
            raise NameError("name '{0}' is not defined".format(name))
        _not_allow.__name__ = name
        return _not_allow

    python_environment_changes_applied = False

    def apply_changes_to_python_environment():
        global python_environment_changes_applied
        if python_environment_changes_applied:
            return

        try:
            reload(sys)
            sys.stdout = stdout
            sys.stderr = stderr
            sys.setdefaultencoding('utf-8')
        except NameError:  # Python 3
            sys.exit('This should not happen!')

        for removed in ('apply', 'cmp', 'coerce', 'execfile', 'raw_input', 'unpacks'):
            globals()[removed] = _create_not_allowed(removed)

        python_environment_changes_applied = True

    def u(s):
        try:
            if isinstance(s, unicode):
                return s
            else:
                return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
        except NameError:  # Python 3
            return str(s)

    def execute(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    class _dict_view_base(object):
        __slots__ = ('_dictionary', )

        def __init__(self, dictionary):
            self._dictionary = dictionary

        def __repr__(self):
            return "{0}({1})".format(self.__class__.__name__, str(list(self.__iter__())))

        def __unicode__(self):
            return str(self.__repr__())

        def __str__(self):
            return str(self.__unicode__())

    class dict_keys(_dict_view_base):
        __slots__ = ()

        def __iter__(self):
            return self._dictionary.iterkeys()

    class dict_values(_dict_view_base):
        __slots__ = ()

        def __iter__(self):
            return self._dictionary.itervalues()

    class dict_items(_dict_view_base):
        __slots__ = ()

        def __iter__(self):
            return self._dictionary.iteritems()

    def itemsview(collection):
        return dict_items(collection)

    def valuesview(collection):
        return dict_values(collection)

    def keysview(collection):
        return dict_keys(collection)

    class dict(unmodified_isinstance(native_dict)):
        def has_key(self, *args, **kwargs):
            return AttributeError("'dict' object has no attribute 'has_key'")

        def items(self):
            return dict_items(self)

        def keys(self):
            return dict_keys(self)

        def values(self):
            return dict_values(self)

    def round(number, ndigits=None):
        return_int = False
        if ndigits is None:
            return_int = True
            ndigits = 0
        if hasattr(number, '__round__'):
            return number.__round__(ndigits)

        if ndigits < 0:
            raise NotImplementedError('negative ndigits not supported yet')
        exponent = Decimal('10') ** (-ndigits)
        d = Decimal.from_float(number).quantize(exponent,
                                                rounding=ROUND_HALF_EVEN)
        if return_int:
            return int(d)
        else:
            return float(d)

    def next(iterator):
        try:
            iterator.__next__()
        except Exception:
            native_next(iterator)

    class FixStr(type):
        def __new__(cls, name, bases, dct):
            if '__str__' in dct:
                dct['__unicode__'] = dct['__str__']
            dct['__str__'] = lambda self: self.__unicode__().encode('utf-8')
            return type.__new__(cls, name, bases, dct)

        def __instancecheck__(cls, instance):
            if cls.__name__ == "object":
                return isinstance(instance, native_object)
            return type.__instancecheck__(cls, instance)

    class object(with_metaclass(FixStr, object)):
        pass

    __all__ = common + ['round', 'dict', 'apply', 'cmp', 'coerce', 'execfile', 'raw_input', 'unpacks', 'str', 'chr',
                        'input', 'range', 'filter', 'map', 'zip', 'object']


if sys.version_info < (3, 2):
    try:
        from threading import Lock
    except ImportError:
        from dummy_threading import Lock

    from functools import wraps

    _CacheInfo = collections.namedtuple("CacheInfo", "hits misses maxsize currsize")

    def lru_cache(maxsize=100):
        """Least-recently-used cache decorator.
        Taking from: https://github.com/MiCHiLU/python-functools32/blob/master/functools32/functools32.py
        with slight modifications.
        If *maxsize* is set to None, the LRU features are disabled and the cache
        can grow without bound.
        Arguments to the cached function must be hashable.
        View the cache statistics named tuple (hits, misses, maxsize, currsize) with
        f.cache_info().  Clear the cache and statistics with f.cache_clear().
        Access the underlying function with f.__wrapped__.
        See: https://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used

        """
        def decorating_function(user_function, tuple=tuple, sorted=sorted, len=len, KeyError=KeyError):
            hits, misses = [0], [0]
            kwd_mark = (object(),)          # separates positional and keyword args
            lock = Lock()

            if maxsize is None:
                CACHE = {}

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    try:
                        result = CACHE[key]
                        hits[0] += 1
                        return result
                    except KeyError:
                        pass
                    result = user_function(*args, **kwds)
                    CACHE[key] = result
                    misses[0] += 1
                    return result
            else:
                CACHE = collections.OrderedDict()

                @wraps(user_function)
                def wrapper(*args, **kwds):
                    key = args
                    if kwds:
                        key += kwd_mark + tuple(sorted(kwds.items()))
                    with lock:
                        cached = CACHE.get(key, None)
                        if cached:
                            del CACHE[key]
                            CACHE[key] = cached
                            hits[0] += 1
                            return cached
                    result = user_function(*args, **kwds)
                    with lock:
                        CACHE[key] = result     # record recent use of this key
                        misses[0] += 1
                        while len(CACHE) > maxsize:
                            CACHE.popitem(last=False)
                    return result

            def cache_info():
                """Report CACHE statistics."""
                with lock:
                    return _CacheInfo(hits[0], misses[0], maxsize, len(CACHE))

            def cache_clear():
                """Clear the CACHE and CACHE statistics."""
                with lock:
                    CACHE.clear()
                    hits[0] = misses[0] = 0

            wrapper.cache_info = cache_info
            wrapper.cache_clear = cache_clear
            return wrapper

        return decorating_function

else:
    from functools import lru_cache  # noqa: F401
