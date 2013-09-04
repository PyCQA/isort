"""
    isort/settings.py

    Defines how the default settings for isort should be loaded

    (First from the default setting dictionary at the top of the file, then overridden by any settings
     in ~/.isort.conf if there are any)

    Copyright (C) 2013  Timothy Edmund Crosley

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from configparser import SafeConfigParser
from pies import *

default = {'force_to_top': [],
           'skip': ['__init__.py', ],
           'line_length': 80,
           'known_standard_library': ['os', 'sys', 'time', 'copy', 're', '__builtin__', 'thread', 'signal', 'gc',
                                      'exceptions', 'email'],
           'known_third_party': ['google.appengine.api'],
           'known_first_party': []}

try:
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
except EnvironmentError:
    pass
