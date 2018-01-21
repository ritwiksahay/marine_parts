from oscar.apps.dashboard.catalogue import views
from marine_parts.apps.dashboard.catalogue.formsets import ProductReplacementFormSet


class ProductCreateUpdateView(views.ProductCreateUpdateView):
    replacement_formset = ProductReplacementFormSet

    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'recommended_formset': self.recommendations_formset,
                         'replacement_formset': self.replacement_formset,
                         'stockrecord_formset': self.stockrecord_formset}

