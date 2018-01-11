# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from haystack.views import SearchView

from marine_parts.apps.search.views import FacetedSearchView
from marine_parts.apps.search.forms import SearchForm

from haystack.query import SearchQuerySet

urlpatterns = [
    url(r'^$', FacetedSearchView(form_class=SearchForm), name='haystack_search'),

]

