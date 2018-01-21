from django.db import models
#from oscar.apps.catalogue import abstract_models
from django.utils.translation import ugettext_lazy as _


#class AbstractProduct(abstract_models.AbstractProduct):


class AbstractReplacementProduct(models.Model):
    """
    'Through' model for product replacement
    """
    primary = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='primary_replacement',
        verbose_name=_("Primary product"))
    replacement = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name=_("Replacement product"))

    order = models.PositiveSmallIntegerField(
        _('order'), default=0,
        help_text=_('Determines order of the products. A product with a higher'
                    ' value will appear before one with a lower ranking.'))

    class Meta:
        abstract = True
        app_label = 'catalogue'
        ordering = ['primary', '-order']
        unique_together = ('primary', 'replacement')
        verbose_name = _('Replacement Product')
        verbose_name_plural = _('Replacement products')

