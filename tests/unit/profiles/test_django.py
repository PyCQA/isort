from functools import partial

from ..utils import isort_test

django_isort_test = partial(isort_test, profile="django", known_first_party=["django"])


def test_django_snippet_one():
    django_isort_test(
        """import copy
import inspect
import warnings
from functools import partialmethod
from itertools import chain

from django.apps import apps
from django.conf import settings
from django.core import checks
from django.core.exceptions import (
    NON_FIELD_ERRORS, FieldDoesNotExist, FieldError, MultipleObjectsReturned,
    ObjectDoesNotExist, ValidationError,
)
from django.db import (
    DEFAULT_DB_ALIAS, DJANGO_VERSION_PICKLE_KEY, DatabaseError, connection,
    connections, router, transaction,
)
from django.db.models import (
    NOT_PROVIDED, ExpressionWrapper, IntegerField, Max, Value,
)
from django.db.models.constants import LOOKUP_SEP
from django.db.models.constraints import CheckConstraint
from django.db.models.deletion import CASCADE, Collector
from django.db.models.fields.related import (
    ForeignObjectRel, OneToOneField, lazy_related_operation, resolve_relation,
)
from django.db.models.functions import Coalesce
from django.db.models.manager import Manager
from django.db.models.options import Options
from django.db.models.query import Q
from django.db.models.signals import (
    class_prepared, post_init, post_save, pre_init, pre_save,
)
from django.db.models.utils import make_model_tuple
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable
from django.utils.text import capfirst, get_text_list
from django.utils.translation import gettext_lazy as _
from django.utils.version import get_version


class Deferred:
    def __repr__(self):
        return '<Deferred field>'

    def __str__(self):
        return '<Deferred field>'"""
    )


def test_django_snippet_two():
    django_isort_test(
        '''from django.utils.version import get_version

VERSION = (3, 2, 0, 'alpha', 0)

__version__ = get_version(VERSION)


def setup(set_prefix=True):
    """
    Configure the settings (this happens as a side effect of accessing the
    first setting), configure logging and populate the app registry.
    Set the thread-local urlresolvers script prefix if `set_prefix` is True.
    """
    from django.apps import apps
    from django.conf import settings
    from django.urls import set_script_prefix
    from django.utils.log import configure_logging

    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
    if set_prefix:
        set_script_prefix(
            '/' if settings.FORCE_SCRIPT_NAME is None else settings.FORCE_SCRIPT_NAME
        )
    apps.populate(settings.INSTALLED_APPS)'''
    )


def test_django_snippet_three():
    django_isort_test(
        """import cgi
import codecs
import copy
import warnings
from io import BytesIO
from itertools import chain
from urllib.parse import quote, urlencode, urljoin, urlsplit

from django.conf import settings
from django.core import signing
from django.core.exceptions import (
    DisallowedHost, ImproperlyConfigured, RequestDataTooBig,
)
from django.core.files import uploadhandler
from django.http.multipartparser import MultiPartParser, MultiPartParserError
from django.utils.datastructures import (
    CaseInsensitiveMapping, ImmutableList, MultiValueDict,
)
from django.utils.deprecation import RemovedInDjango40Warning
from django.utils.encoding import escape_uri_path, iri_to_uri
from django.utils.functional import cached_property
from django.utils.http import is_same_domain, limited_parse_qsl
from django.utils.regex_helper import _lazy_re_compile

from .multipartparser import parse_header

RAISE_ERROR = object()


class UnreadablePostError(OSError):
    pass"""
    )
