from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from forms import UploadFileForm
from price_updater import execUpdater
import os

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
            # Select file type reader
            ext = os.path.splitext(request.FILES['file'].name)[1].lower()
            if ext == '.xls':
                file = request.FILES['file'].get_records(library='pyexcel-xls')
            elif ext == '.xlsx':
                file = request.FILES['file'].get_records(library='pyexcel-xlsx')
            else:
                file = request.FILES['file'].get_records(library='pyexcel-io')

            # Execeute updater
            request.session['stats'], \
                request.session['log'] = execUpdater(file,
                                                     form.cleaned_data['partner'],
                                                     form.cleaned_data['percent'])
            return super(UploadFileView, self).form_valid(form)
        else:
            return super(UploadFileView, self).form_invalid(form)


class ReviewUpdater(TemplateView):
    template_name = 'dashboard/bulk_price_updater/update-price-review.html'

    def get_context_data(self, **kwargs):
        context_data = super(ReviewUpdater, self).get_context_data(**kwargs)
        context_data['stats'] = self.request.session['stats']
        log = self.request.session['log'].strip().split('\n')
        if '' in log:
            context_data['log'] = list()
        else:
            context_data['log'] = log

        return context_data
