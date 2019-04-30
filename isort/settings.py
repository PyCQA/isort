"""isort/settings.py.

Defines how the default settings for isort should be loaded

(First from the default setting dictionary at the top of the file, then overridden by any settings
 in ~/.isort.cfg or $XDG_CONFIG_HOME/isort.cfg if there are any)

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
import configparser
import enum
import fnmatch
import os
import posixpath
import re
import warnings
from distutils.util import strtobool
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Union

from .utils import difference, union

try:
    import toml
except ImportError:
    toml = None  # type: ignore

try:
    import appdirs
    if appdirs.system == 'darwin':
        appdirs.system = 'linux2'
except ImportError:
    appdirs = None

MAX_CONFIG_SEARCH_DEPTH = 25  # The number of parent directories isort will look for a config file within
DEFAULT_SECTIONS = ('FUTURE', 'STDLIB', 'THIRDPARTY', 'FIRSTPARTY', 'LOCALFOLDER')

safety_exclude_re = re.compile(
    r"/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|\.pants\.d"
    r"|lib/python[0-9].[0-9]+)/"
)


class WrapModes(enum.Enum):
    GRID = 0  # 0
    VERTICAL = 1
    HANGING_INDENT = 2
    VERTICAL_HANGING_INDENT = 3
    VERTICAL_GRID = 4
    VERTICAL_GRID_GROUPED = 5
    VERTICAL_GRID_GROUPED_NO_COMMA = 6
    NOQA = 7

    @staticmethod
    def from_string(value: str) -> 'WrapModes':
        return getattr(WrapModes, str(value), None) or WrapModes(int(value))


# Note that none of these lists must be complete as they are simply fallbacks for when included auto-detection fails.
default = {'force_to_top': [],
           'skip': [],
           'skip_glob': [],
           'line_length': 79,
           'wrap_length': 0,
           'line_ending': None,
           'sections': DEFAULT_SECTIONS,
           'no_sections': False,
           'known_future_library': ['__future__'],
           'known_standard_library': ['AL', 'BaseHTTPServer', 'Bastion', 'CGIHTTPServer', 'Carbon', 'ColorPicker',
                                      'ConfigParser', 'Cookie', 'DEVICE', 'DocXMLRPCServer', 'EasyDialogs', 'FL',
                                      'FrameWork', 'GL', 'HTMLParser', 'MacOS', 'MimeWriter', 'MiniAEFrame', 'Nav',
                                      'PixMapWrapper', 'Queue', 'SUNAUDIODEV', 'ScrolledText', 'SimpleHTTPServer',
                                      'SimpleXMLRPCServer', 'SocketServer', 'StringIO', 'Tix', 'Tkinter', 'UserDict',
                                      'UserList', 'UserString', 'W', '__builtin__', 'abc', 'aepack', 'aetools',
                                      'aetypes', 'aifc', 'al', 'anydbm', 'applesingle', 'argparse', 'array', 'ast',
                                      'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop', 'autoGIL', 'base64',
                                      'bdb', 'binascii', 'binhex', 'bisect', 'bsddb', 'buildtools', 'builtins',
                                      'bz2', 'cPickle', 'cProfile', 'cStringIO', 'calendar', 'cd', 'cfmfile', 'cgi',
                                      'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop', 'collections',
                                      'colorsys', 'commands', 'compileall', 'compiler', 'concurrent', 'configparser',
                                      'contextlib', 'contextvars', 'cookielib', 'copy', 'copy_reg', 'copyreg', 'crypt', 'csv',
                                      'ctypes', 'curses', 'dataclasses', 'datetime', 'dbhash', 'dbm', 'decimal', 'difflib',
                                      'dircache', 'dis', 'distutils', 'dl', 'doctest', 'dumbdbm', 'dummy_thread',
                                      'dummy_threading', 'email', 'encodings', 'ensurepip', 'enum', 'errno',
                                      'exceptions', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'findertools',
                                      'fl', 'flp', 'fm', 'fnmatch', 'formatter', 'fpectl', 'fpformat', 'fractions',
                                      'ftplib', 'functools', 'future_builtins', 'gc', 'gdbm', 'gensuitemodule',
                                      'getopt', 'getpass', 'gettext', 'gl', 'glob', 'grp', 'gzip', 'hashlib',
                                      'heapq', 'hmac', 'hotshot', 'html', 'htmlentitydefs', 'htmllib', 'http',
                                      'httplib', 'ic', 'icopen', 'imageop', 'imaplib', 'imgfile', 'imghdr', 'imp',
                                      'importlib', 'imputil', 'inspect', 'io', 'ipaddress', 'itertools', 'jpeg',
                                      'json', 'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma',
                                      'macerrors', 'macostools', 'macpath', 'macresource', 'mailbox', 'mailcap',
                                      'marshal', 'math', 'md5', 'mhlib', 'mimetools', 'mimetypes', 'mimify', 'mmap',
                                      'modulefinder', 'msilib', 'msvcrt', 'multifile', 'multiprocessing', 'mutex',
                                      'netrc', 'new', 'nis', 'nntplib', 'numbers', 'operator', 'optparse', 'os',
                                      'ossaudiodev', 'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes',
                                      'pkgutil', 'platform', 'plistlib', 'popen2', 'poplib', 'posix', 'posixfile',
                                      'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc',
                                      'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource', 'rexec',
                                      'rfc822', 'rlcompleter', 'robotparser', 'runpy', 'sched', 'secrets', 'select',
                                      'selectors', 'sets', 'sgmllib', 'sha', 'shelve', 'shlex', 'shutil', 'signal',
                                      'site', 'sitecustomize', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver',
                                      'spwd', 'sqlite3', 'ssl', 'stat', 'statistics', 'statvfs', 'string', 'stringprep',
                                      'struct', 'subprocess', 'sunau', 'sunaudiodev', 'symbol', 'symtable', 'sys',
                                      'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios',
                                      'test', 'textwrap', 'this', 'thread', 'threading', 'time', 'timeit', 'tkinter',
                                      'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'ttk', 'tty', 'turtle',
                                      'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'urllib2',
                                      'urlparse', 'usercustomize', 'uu', 'uuid', 'venv', 'videoreader',
                                      'warnings', 'wave', 'weakref', 'webbrowser', 'whichdb', 'winreg', 'winsound',
                                      'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'xmlrpclib', 'zipapp', 'zipfile',
                                      'zipimport', 'zlib'],
           'known_third_party': ['google.appengine.api'],
           'known_first_party': [],
           'multi_line_output': WrapModes.GRID,
           'forced_separate': [],
           'indent': ' ' * 4,
           'comment_prefix': '  #',
           'length_sort': False,
           'add_imports': [],
           'remove_imports': [],
           'reverse_relative': False,
           'force_single_line': False,
           'default_section': 'FIRSTPARTY',
           'import_heading_future': '',
           'import_heading_stdlib': '',
           'import_heading_thirdparty': '',
           'import_heading_firstparty': '',
           'import_heading_localfolder': '',
           'balanced_wrapping': False,
           'use_parentheses': False,
           'order_by_type': True,
           'atomic': False,
           'lines_after_imports': -1,
           'lines_between_sections': 1,
           'lines_between_types': 0,
           'combine_as_imports': False,
           'combine_star': False,
           'keep_direct_and_as_imports': False,
           'include_trailing_comma': False,
           'from_first': False,
           'verbose': False,
           'quiet': False,
           'force_adds': False,
           'force_alphabetical_sort_within_sections': False,
           'force_alphabetical_sort': False,
           'force_grid_wrap': 0,
           'force_sort_within_sections': False,
           'show_diff': False,
           'ignore_whitespace': False,
           'no_lines_before': [],
           'no_inline_sort': False,
           'ignore_comments': False,
           'safety_excludes': True,
           'case_sensitive': False}


@lru_cache()
def from_path(path: Union[str, Path]) -> Dict[str, Any]:
    computed_settings = default.copy()
    isort_defaults = ['~/.isort.cfg']
    if appdirs:
        isort_defaults = [appdirs.user_config_dir('isort.cfg')] + isort_defaults

    if isinstance(path, Path):
        path = str(path)

    _update_settings_with_config(path, '.editorconfig', ['~/.editorconfig'], ('*', '*.py', '**.py'), computed_settings)
    _update_settings_with_config(path, 'pyproject.toml', [], ('tool.isort', ), computed_settings)
    _update_settings_with_config(path, '.isort.cfg', isort_defaults, ('settings', 'isort'), computed_settings)
    _update_settings_with_config(path, 'setup.cfg', [], ('isort', 'tool:isort'), computed_settings)
    _update_settings_with_config(path, 'tox.ini', [], ('isort', 'tool:isort'), computed_settings)
    return computed_settings


def prepare_config(settings_path: Path, **setting_overrides: Any) -> Dict[str, Any]:
    config = from_path(settings_path).copy()
    for key, value in setting_overrides.items():
        access_key = key.replace('not_', '').lower()
        # The sections config needs to retain order and can't be converted to a set.
        if access_key != 'sections' and type(config.get(access_key)) in (list, tuple):
            if key.startswith('not_'):
                config[access_key] = list(set(config[access_key]).difference(value))
            else:
                config[access_key] = list(set(config[access_key]).union(value))
        else:
            config[key] = value

    if config['force_alphabetical_sort']:
        config.update({'force_alphabetical_sort_within_sections': True,
                       'no_sections': True,
                       'lines_between_types': 1,
                       'from_first': True})

    indent = str(config['indent'])
    if indent.isdigit():
        indent = " " * int(indent)
    else:
        indent = indent.strip("'").strip('"')
        if indent.lower() == "tab":
            indent = "\t"
    config['indent'] = indent

    config['comment_prefix'] = config['comment_prefix'].strip("'").strip('"')
    return config


def _update_settings_with_config(
    path: str,
    name: str,
    default: Iterable[str],
    sections: Iterable[str],
    computed_settings: MutableMapping[str, Any]
) -> None:
    editor_config_file = None
    for potential_settings_path in default:
        expanded = os.path.expanduser(potential_settings_path)
        if os.path.exists(expanded):
            editor_config_file = expanded
            break

    tries = 0
    current_directory = path
    while current_directory and tries < MAX_CONFIG_SEARCH_DEPTH:
        potential_path = os.path.join(current_directory, name)
        if os.path.exists(potential_path):
            editor_config_file = potential_path
            break

        new_directory = os.path.split(current_directory)[0]
        if current_directory == new_directory:
            break
        current_directory = new_directory
        tries += 1

    if editor_config_file and os.path.exists(editor_config_file):
        _update_with_config_file(editor_config_file, sections, computed_settings)


def _get_str_to_type_converter(setting_name: str) -> Callable[[str], Any]:
    type_converter = type(default.get(setting_name, ''))  # type: Callable[[str], Any]
    if type_converter == WrapModes:
        type_converter = WrapModes.from_string
    return type_converter


def _update_with_config_file(
    file_path: str,
    sections: Iterable[str],
    computed_settings: MutableMapping[str, Any]
) -> None:
    cwd = os.path.dirname(file_path)
    settings = _get_config_data(file_path, sections).copy()
    if not settings:
        return

    if file_path.endswith('.editorconfig'):
        indent_style = settings.pop('indent_style', '').strip()
        indent_size = settings.pop('indent_size', '').strip()
        if indent_size == "tab":
            indent_size = settings.pop('tab_width', '').strip()

        if indent_style == 'space':
            computed_settings['indent'] = ' ' * (indent_size and int(indent_size) or 4)
        elif indent_style == 'tab':
            computed_settings['indent'] = '\t' * (indent_size and int(indent_size) or 1)

        max_line_length = settings.pop('max_line_length', '').strip()
        if max_line_length:
            computed_settings['line_length'] = float('inf') if max_line_length == 'off' else int(max_line_length)

    for key, value in settings.items():
        access_key = key.replace('not_', '').lower()
        existing_value_type = _get_str_to_type_converter(access_key)
        if existing_value_type in (list, tuple):
            # sections has fixed order values; no adding or substraction from any set
            if access_key == 'sections':
                computed_settings[access_key] = tuple(_as_list(value))
            else:
                existing_data = set(computed_settings.get(access_key, default.get(access_key)))
                if key.startswith('not_'):
                    computed_settings[access_key] = difference(existing_data, _as_list(value))
                elif key.startswith('known_'):
                    computed_settings[access_key] = union(existing_data, _abspaths(cwd, _as_list(value)))
                else:
                    computed_settings[access_key] = union(existing_data, _as_list(value))
        elif existing_value_type == bool:
            # Only some configuration formats support native boolean values.
            if not isinstance(value, bool):
                value = bool(strtobool(value))
            computed_settings[access_key] = value
        elif key.startswith('known_'):
            computed_settings[access_key] = list(_abspaths(cwd, _as_list(value)))
        elif key == 'force_grid_wrap':
            try:
                result = existing_value_type(value)
            except ValueError:
                # backwards compat
                result = default.get(access_key) if value.lower().strip() == 'false' else 2
            computed_settings[access_key] = result
        else:
            computed_settings[access_key] = getattr(existing_value_type, str(value), None) or existing_value_type(value)


def _as_list(value: str) -> List[str]:
    if isinstance(value, list):
        return [item.strip() for item in value]
    filtered = [
        item.strip()
        for item in value.replace('\n', ',').split(',')
        if item.strip()
    ]
    return filtered


def _abspaths(cwd: str, values: Iterable[str]) -> List[str]:
    paths = [
        os.path.join(cwd, value)
        if not value.startswith(os.path.sep) and value.endswith(os.path.sep)
        else value
        for value in values
    ]
    return paths


@lru_cache()
def _get_config_data(file_path: str, sections: Iterable[str]) -> Dict[str, Any]:
    settings = {}  # type: Dict[str, Any]

    with open(file_path) as config_file:
        if file_path.endswith('.toml'):
            if toml:
                config = toml.load(config_file)
                for section in sections:
                    config_section = config
                    for key in section.split('.'):
                        config_section = config_section.get(key, {})
                    settings.update(config_section)
            else:
                if '[tool.isort]' in config_file.read():
                    warnings.warn("Found {} with [tool.isort] section, but toml package is not installed. "
                                  "To configure isort with {}, install with 'isort[pyproject]'.".format(file_path,
                                                                                                        file_path))
        else:
            if file_path.endswith('.editorconfig'):
                line = '\n'
                last_position = config_file.tell()
                while line:
                    line = config_file.readline()
                    if '[' in line:
                        config_file.seek(last_position)
                        break
                    last_position = config_file.tell()

            config = configparser.ConfigParser(strict=False)
            config.read_file(config_file)
            for section in sections:
                if config.has_section(section):
                    settings.update(config.items(section))

    return settings


def file_should_be_skipped(
    filename: str,
    config: Mapping[str, Any],
    path: str = ''
) -> bool:
    """Returns True if the file and/or folder should be skipped based on the passed in settings."""
    os_path = os.path.join(path, filename)

    normalized_path = os_path.replace('\\', '/')
    if normalized_path[1:2] == ':':
        normalized_path = normalized_path[2:]

    if path and config['safety_excludes']:
        check_exclude = '/' + filename.replace('\\', '/') + '/'
        if path and os.path.basename(path) in ('lib', ):
            check_exclude = '/' + os.path.basename(path) + check_exclude
        if safety_exclude_re.search(check_exclude):
            return True

    for skip_path in config['skip']:
        if posixpath.abspath(normalized_path) == posixpath.abspath(skip_path.replace('\\', '/')):
            return True

    position = os.path.split(filename)
    while position[1]:
        if position[1] in config['skip']:
            return True
        position = os.path.split(position[0])

    for glob in config['skip_glob']:
        if fnmatch.fnmatch(filename, glob) or fnmatch.fnmatch('/' + filename, glob):
            return True

    if not (os.path.isfile(os_path) or os.path.isdir(os_path) or os.path.islink(os_path)):
        return True

    return False
