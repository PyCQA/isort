from functools import partial

from ..utils import isort_test

open_stack_isort_test = partial(isort_test, profile="open_stack")


def test_open_stack_code_snippet_one():
    open_stack_isort_test(
        """import httplib
import logging
import random
import StringIO
import time
import unittest

import eventlet
import webob.exc

import nova.api.ec2
from nova.api import manager
from nova.api import openstack
from nova.auth import users
from nova.endpoint import cloud
import nova.flags
from nova.i18n import _
from nova.i18n import _LC
from nova import test
""",
        known_first_party=["nova"],
        py_version="2",
        order_by_type=False,
    )


def test_open_stack_code_snippet_two():
    open_stack_isort_test(
        """# Copyright 2011 VMware, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import inspect
import os
import random

from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources
from neutron_lib import context
from neutron_lib.db import api as session
from neutron_lib.plugins import directory
from neutron_lib import rpc as n_rpc
from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
from oslo_messaging import server as rpc_server
from oslo_service import loopingcall
from oslo_service import service as common_service
from oslo_utils import excutils
from oslo_utils import importutils
import psutil

from neutron.common import config
from neutron.common import profiler
from neutron.conf import service
from neutron import worker as neutron_worker
from neutron import wsgi

service.register_service_opts(service.SERVICE_OPTS)
""",
        known_first_party=["neutron"],
    )


def test_open_stack_code_snippet_three():
    open_stack_isort_test(
        """
# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools

from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_messaging.rpc import dispatcher
from oslo_serialization import jsonutils
from oslo_service import periodic_task
from oslo_utils import importutils
import six

import nova.conf
import nova.context
import nova.exception
from nova.i18n import _

__all__ = [
    'init',
    'cleanup',
    'set_defaults',
    'add_extra_exmods',
    'clear_extra_exmods',
    'get_allowed_exmods',
    'RequestContextSerializer',
    'get_client',
    'get_server',
    'get_notifier',
]

profiler = importutils.try_import("osprofiler.profiler")
""",
        known_first_party=["nova"],
    )
