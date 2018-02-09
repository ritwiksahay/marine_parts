from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from forms import UploadFileForm


# class BulkUpdaterView(TemplateView):
#     """
#     An overview view which displays several reports about the shop.
#     Supports the permission-based dashboard. It is recommended to add a
#     index_nonstaff.html template because Oscar's default template will
#     display potentially sensitive store information.
#     """
#
#     def get_template_names(self):
#
#
#     def get_context_data(self, **kwargs):
#         ctx = super(BulkUpdaterView, self).get_context_data(**kwargs)
#         return ctx

class UploadFileView(FormView):
    form_class = UploadFileForm
    success_url = 'review/'

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['dashboard/bulk_price_updater/update-price-index.html', ]
        else:
            return ['dashboard/index_nonstaff.html', 'dashboard/index.html']



class ReviewUpdater(TemplateView):
    template_name = 'dashboard/bulk_price_updater/update-price-review.html'

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        import pdb; pdb.set_trace()
        if form.is_valid():
            process_file(request.FILES['file'])
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # def get_template_names(self):
    #     if self.request.user.is_staff:
    #         return [
    #     else:
    #         return ['dashboard/index_nonstaff.html', 'dashboard/index.html']

    # def form_valid(self, form):
    #     process_file()
    #     return super(ReviewUpdater, self).form_valid(form)


def process_file(f):
    print(f)
