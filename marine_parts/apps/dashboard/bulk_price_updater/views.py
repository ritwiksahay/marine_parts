from django.views.generic.base import TemplateView


class BulkUpdaterView(TemplateView):
    """
    An overview view which displays several reports about the shop.
    Supports the permission-based dashboard. It is recommended to add a
    index_nonstaff.html template because Oscar's default template will
    display potentially sensitive store information.
    """

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['dashboard/bulk_price_updater/update-price-index.html', ]
        else:
            return ['dashboard/index_nonstaff.html', 'dashboard/index.html']

    def get_context_data(self, **kwargs):
        ctx = super(BulkUpdaterView, self).get_context_data(**kwargs)
        return ctx