from functools import partial

from ..utils import isort_test

plone_isort_test = partial(isort_test, profile="plone")


def test_plone_code_snippet_one():
    plone_isort_test(
        """# -*- coding: utf-8 -*-
from plone.app.multilingual.testing import PLONE_APP_MULTILINGUAL_PRESET_FIXTURE  # noqa
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import plone.app.multilingualindexes


PAMI_FIXTURE = PloneWithPackageLayer(
    bases=(PLONE_APP_MULTILINGUAL_PRESET_FIXTURE,),
    name="PAMILayer:Fixture",
    gs_profile_id="plone.app.multilingualindexes:default",
    zcml_package=plone.app.multilingualindexes,
    zcml_filename="configure.zcml",
    additional_z2_products=["plone.app.multilingualindexes"],
)
"""
    )


def test_plone_code_snippet_two():
    plone_isort_test(
        """# -*- coding: utf-8 -*-
from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOTreeSet
from logging import getLogger
from plone import api
from plone.app.multilingual.events import ITranslationRegisteredEvent
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingualindexes.utils import get_configuration
from plone.indexer.interfaces import IIndexableObject
from Products.CMFPlone.utils import safe_hasattr
from Products.DateRecurringIndex.index import DateRecurringIndex
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.ZCatalog.Catalog import Catalog
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.component import queryAdapter
from zope.globalrequest import getRequest


logger = getLogger(__name__)
"""
    )


def test_plone_code_snippet_three():
    plone_isort_test(
        """# -*- coding: utf-8 -*-
from plone.app.querystring.interfaces import IQueryModifier
from zope.interface import provider

import logging


logger = logging.getLogger(__name__)

"""
    )
