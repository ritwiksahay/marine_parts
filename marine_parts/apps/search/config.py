from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SearchConfig(AppConfig):
    label = 'oscar.search'
    name = 'marine_parts.apps.search'
    verbose_name = _('Search')
