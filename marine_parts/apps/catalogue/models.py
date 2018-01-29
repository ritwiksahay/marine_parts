"""Override of Oscar's Catalogue app Models."""

from urllib import pathname2url as to_url

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from oscar.apps.catalogue import abstract_models
from oscar.apps.catalogue.abstract_models import AbstractCategory

from marine_parts.apps.catalogue.abstract_models import  AbstractReplacementProduct


class Category(AbstractCategory):
    """Override of Category Model."""

    diagram_image = models.ImageField(
        _('Diagram'),
        upload_to='categories',
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Parts Diagram. Only upload a diagram image if "
                    "you are creating a Leaf Category (Component).")
    )

    def get_absolute_url(self):
        """Building the url that points to the search of the category."""
        url = reverse('search:search') + '?var=category:'
        url += '&var=category:' \
            .join([to_url(c.full_name) for c in self.get_ancestors_and_self()])

        return url

    # def clean(self):
    #    """Override Category Validation Method."""
    # When adding a new category, the parent cannot have a diagram image
    #    super(Category, self).clean()
    #    if self.get_parent().diagram_image:
    #        raise ValidationError(
    #            _("Cannot add a child to a leaf category."
    #              "Delete diagram image in the parent first.")
    #        )


# @python_2_unicode_compatible
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


# if not is_model_registered('catalogue.', 'ReplacementProduct'):
class ReplacementProduct(AbstractReplacementProduct):
    pass

from oscar.apps.catalogue.models import *  # noqa isort:skip
