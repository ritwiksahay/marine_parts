"""Override of Oscar's Dashboard Catalogue Forms."""

from django import forms

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from oscar.apps.dashboard.catalogue import forms as base_form
from oscar.apps.dashboard.catalogue.widgets import ProductSelect

from marine_parts.apps.catalogue.models import Category
from marine_parts.apps.catalogue.models import ReplacementProduct


class CategoryForm(base_form.CategoryForm):
    """Override Dashboard's Category Form."""

    def __init__(self, *args, **kwargs):
        """Category Form constructor method."""
        super(CategoryForm, self).__init__(*args, **kwargs)

        # If it's not a Category Leaf, hide diagram field
        if self.instance.has_children():
            del self.fields['diagram_image']

    class Meta:
        """Meta Class of Category Form. Fields Overriden."""

        model = Category
        fields = [
            'name',
            'description',
            'image',
            'diagram_image',
        ]

    def clean(self, *args, **kwargs):
        """Category Form Validation."""
        super(CategoryForm, self).clean(*args, **kwargs)
        diagram = self.instance.diagram_image
        # Only Category Leafs can have a diagram image
        if self.instance.has_children() and diagram:
            raise ValidationError(
                _("A non leaf category cannot have a diagram image")
            )

    def save(self, commit=True):
        """Override Category Form Save Method."""
        instance = super(CategoryForm, self).save(commit=False)

        # When adding a new category, the parent cannot have a diagram image
        # If it is root, it doesn't make sense to check for parent
        if not instance.is_root():
            parent = instance.get_parent()
            if parent.diagram_image:
                parent.diagram_image = None
            parent.save()
        instance.save()
        return instance


class ProductReplacementForm(forms.ModelForm):

    class Meta:
        model = ReplacementProduct
        fields = ['primary', 'replacement', 'order']
        widgets = {
            'replacement': ProductSelect,
        }
