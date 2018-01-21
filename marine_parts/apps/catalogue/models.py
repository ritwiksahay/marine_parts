"""
Vanilla product models
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue import abstract_models
from marine_parts.apps.catalogue.abstract_models import  AbstractReplacementProduct


#@python_2_unicode_compatible
class Product(abstract_models.AbstractProduct):
    replacement_products = models.ManyToManyField(
        'Product', through='ReplacementProduct', blank=True,
        related_name='replacements',
        verbose_name=_("Replacement products"),
        through_fields=('primary', 'replacement'),
        help_text=_("These are products that are designated to replace "
                    "main product."))


    recommended_products = models.ManyToManyField(
        'Product', through='ProductRecommendation', blank=True,
        related_name='recommendations',
        verbose_name=_("Recommended products"),
        through_fields=('primary', 'recommendation'),
        help_text=_("These are products that are recommended to accompany the "
                    "main product."))


#if not is_model_registered('catalogue.', 'ReplacementProduct'):
class ReplacementProduct(AbstractReplacementProduct):
    pass

from oscar.apps.catalogue.models import *