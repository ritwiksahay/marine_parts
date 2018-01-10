from oscar.apps.catalogue.models import Category
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, TemplateView


class HomeView(TemplateView):
    """
    This is the home page and will typically live at /
    """
    template_name = 'promotions/home.html'

    def get_context_data(self, **kwargs):
        if 'best_sellers' not in kwargs:
            best_sellers = Category.objects.get(slug='best-sellers')
            kwargs['best_sellers'] = best_sellers.get_children()

        if 'categories' not in kwargs:
            categories = Category.objects.get(slug='categories')
            kwargs['categories'] = categories.get_children()
        return kwargs


class RecordClickView(RedirectView):
    """
    Simple RedirectView that helps recording clicks made on promotions
    """
    permanent = False
    model = None

    def get_redirect_url(self, **kwargs):
        try:
            prom = self.model.objects.get(pk=kwargs['pk'])
        except self.model.DoesNotExist:
            return reverse('promotions:home')

        if prom.promotion.has_link:
            prom.record_click()
            return prom.link_url
        return reverse('promotions:home')
