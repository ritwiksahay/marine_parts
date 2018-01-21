from django import forms
from django.core import exceptions
from django.forms.models import inlineformset_factory
from marine_parts.apps.catalogue.models  import Product, ReplacementProduct
from django.utils.translation import ugettext_lazy as _
from marine_parts.apps.dashboard.catalogue.forms import ProductReplacementForm
#from oscar.core.loading import get_classes, get_model


BaseProductRecommendationFormSet = inlineformset_factory(
    Product, ReplacementProduct, form=ProductReplacementForm,
    extra=5, fk_name="replacement")


class ProductReplacementFormSet(BaseProductRecommendationFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(ProductReplacementFormSet, self).__init__(*args, **kwargs)

