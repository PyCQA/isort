"""
    isort/settings.py

    Defines how the default settings for isort should be loaded

    (First from the default setting dictionary at the top of the file, then overridden by any settings
     in ~/.isort.conf if there are any)

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

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from pies import *


class MultiLineOutput(object):
    GRID = 0
    VERTICAL = 1
    HANGING_INDENT = 2
    VERTICAL_HANGING_INDENT = 3

# Note that none of these lists must be complete as they are simply fallbacks for when included auto-detection fails.
default = {'force_to_top': [],
           'skip': ['__init__.py', ],
           'line_length': 80,
           'known_standard_library': ["abc", "anydbm", "argparse", "array", "asynchat", "asyncore", "atexit", "base64",
                                      "BaseHTTPServer", "bisect", "bz2", "calendar", "cgitb", "cmd", "codecs",
                                      "collections", "commands", "compileall", "ConfigParser", "contextlib", "Cookie",
                                      "copy", "cPickle", "cProfile", "cStringIO", "csv", "datetime", "dbhash", "dbm",
                                      "decimal", "difflib", "dircache", "dis", "doctest", "dumbdbm", "EasyDialogs",
                                      "exceptions", "filecmp", "fileinput", "fnmatch", "fractions", "functools", "gc",
                                      "gdbm", "getopt", "getpass", "gettext", "glob", "grp", "gzip", "hashlib", "heapq",
                                      "hmac", "imaplib", "imp", "inspect", "itertools", "json", "linecache", "locale",
                                      "logging", "mailbox", "math", "mhlib", "mmap", "multiprocessing", "operator",
                                      "optparse", "os", "pdb", "pickle", "pipes", "pkgutil", "platform", "plistlib",
                                      "pprint", "profile", "pstats", "pwd", "pyclbr", "pydoc", "Queue", "random",
                                      "re", "readline", "resource", "rlcompleter", "robotparser", "sched", "select",
                                      "shelve", "shlex", "shutil", "signal", "SimpleXMLRPCServer", "site",
                                      "sitecustomize", "smtpd", "smtplib", "socket", "SocketServer", "sqlite3",
                                      "string", "StringIO", "struct", "subprocess", "sys", "sysconfig", "tabnanny",
                                      "tarfile", "tempfile", "textwrap", "threading", "time", "timeit", "trace",
                                      "traceback", "unittest", "urllib", "urllib2", "urlparse", "usercustomize", "uuid",
                                      "warnings", "weakref", "webbrowser", "whichdb", "xml", "xmlrpclib", "zipfile",
                                      "zipimport", "zlib"],
           'known_third_party': ['google.appengine.api'],
           'known_first_party': [],
           'multi_line_output': MultiLineOutput.GRID,
           'indent': ' ' * 4,
           'length_sort': False,
           'add_imports': [],
           'remove_imports': []}

try:
    from configparser import SafeConfigParser

    with open(os.path.expanduser('~/.isort.cfg')) as config_file:
        config = SafeConfigParser()
        config.readfp(config_file)
        settings = dict(config.items('settings'))
        for key, value in iteritems(settings):
            existing_value_type = type(default.get(key, ''))
            if existing_value_type in (list, tuple):
                default[key.lower()] = value.split(",")
            else:
                default[key.lower()] = existing_value_type(value)
except (ImportError, EnvironmentError):
    pass
