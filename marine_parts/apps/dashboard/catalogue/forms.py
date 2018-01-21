from django import forms
from oscar.apps.dashboard.catalogue.widgets import ProductSelect

from marine_parts.apps.catalogue.models import ReplacementProduct


# def _attr_entity_field(attribute):
#     # Product entities don't have out-of-the-box supported in the ProductForm.
#     # There is no ModelChoiceField for generic foreign keys, and there's no
#     # good default behaviour anyway; offering a choice of *all* model instances
#     # is hardly useful.
#     return forms.ModelChoiceField(
#         label=attribute.name,
#         required=attribute.required,
#         queryset=Product.objects.all())
#
#
# class ProductForm(d.ProductForm):
#
#     FIELD_FACTORIES = {
#         "text": d._attr_text_field,
#         "richtext": d._attr_textarea_field,
#         "integer": d._attr_integer_field,
#         "boolean": d._attr_boolean_field,
#         "float": d._attr_float_field,
#         "date": d._attr_date_field,
#         "datetime": d._attr_datetime_field,
#         "option": d._attr_option_field,
#         "multi_option": d._attr_multi_option_field,
#         "entity": _attr_entity_field,
#         "numeric": d._attr_numeric_field,
#         "file": d._attr_file_field,
#         "image": d._attr_image_field,
#     }
#
#     def add_attribute_fields(self, product_class, is_parent=False):
#         """
#         For each attribute specified by the product class, this method
#         dynamically adds form fields to the product form.
#         """
#         import pdb; pdb.set_trace()
#
#         for attribute in product_class.attributes.all():
#             field = self.get_attribute_field(attribute)
#             if field:
#                 self.fields['attr_%s' % attribute.code] = field
#                 # Attributes are not required for a parent product
#                 if is_parent:
#                     self.fields['attr_%s' % attribute.code].required = False

class ProductReplacementForm(forms.ModelForm):

    class Meta:
        model = ReplacementProduct
        fields = ['primary', 'replacement', 'order']
        widgets = {
            'replacement': ProductSelect,
        }


