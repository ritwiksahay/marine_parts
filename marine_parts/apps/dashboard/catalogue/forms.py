"""Override of Oscar's Dashboard Catalogue Forms."""

from django import forms

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from oscar.apps.dashboard.catalogue import forms as base_form
from marine_parts.apps.dashboard.catalogue.widgets import ProductSelect, CategorySelect

from marine_parts.apps.catalogue.models import Category, ReplacementProduct, ProductCategory


class CategoryForm(base_form.CategoryForm):
    """Override Dashboard's Category Form."""

    def __init__(self, *args, **kwargs):
        """Category Form constructor method."""
        super(CategoryForm, self).__init__(*args, **kwargs)

        # If it's not a Category Leaf, hide diagram field
        self.fields['_ref_node_id'].widget = CategorySelect()
        self.fields['_ref_node_id'].widget.attrs['class'] = 'select2'
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

    def __init__(self, *args, **kwargs):
        super(ProductReplacementForm, self).__init__(*args, **kwargs)
        self.fields['replacement'].widget.attrs['class'] = 'select2'


class ProductCategoryForm(forms.ModelForm):

    class Meta:
        model = ProductCategory
        fields = ('category', )
        widgets = {
            'category': CategorySelect,
        }

    def __init__(self, *args, **kwargs):
        super(ProductCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'select2'
