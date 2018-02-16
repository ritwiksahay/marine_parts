from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from forms import UploadFileForm
from price_updater import execUpdater


class UploadFileView(FormView):
    form_class = UploadFileForm
    success_url = 'review/'

    def get_template_names(self):
        if self.request.user.is_staff:
            return ['dashboard/bulk_price_updater/update-price-index.html', ]
        else:
            return ['dashboard/index_nonstaff.html', 'dashboard/index.html']

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['stats'], \
                request.session['log'] = execUpdater(request.FILES['file'].get_records())
            return super(UploadFileView, self).form_valid(form)
        else:
            return super(UploadFileView, self).form_invalid(form)


class ReviewUpdater(TemplateView):
    template_name = 'dashboard/bulk_price_updater/update-price-review.html'

    def get_context_data(self, **kwargs):
        context_data = super(ReviewUpdater, self).get_context_data(**kwargs)
        context_data['stats'] = self.request.session['stats']
        context_data['log'] = self.request.session['log'].strip().split('\n')
        return context_data
