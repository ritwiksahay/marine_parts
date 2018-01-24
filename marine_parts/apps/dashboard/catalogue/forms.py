from django import forms
from oscar.apps.dashboard.catalogue.widgets import ProductSelect
from marine_parts.apps.catalogue.models import ReplacementProduct

class ProductReplacementForm(forms.ModelForm):

    class Meta:
        model = ReplacementProduct
        fields = ['primary', 'replacement', 'order']
        widgets = {
            'replacement': ProductSelect,
        }


