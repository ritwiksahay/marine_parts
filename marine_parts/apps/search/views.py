"""."""

import sys

from django.core.paginator import Paginator

from haystack import views
from oscar.core.loading import get_class, get_model
from oscar.apps.basket.formsets import BasketLineFormSet

from . import signals

from marine_parts.apps.catalogue.models import Category

Product = get_model('catalogue', 'Product')
FacetMunger = get_class('search.facets', 'FacetMunger')


class FacetedSearchView(views.FacetedSearchView):
    """
    A modified version of Haystack's FacetedSearchView.

    Note that facets are configured when the ``SearchQuerySet`` is initialised.
    This takes place in the search application class.

    See https://django-haystack.readthedocs.io/en/v2.1.0/views_and_forms.html#facetedsearchform # noqa
    """

    # Haystack uses a different class attribute to CBVs
    template = "search/results.html"
    search_signal = signals.user_search

    def __init__(self, *args, **kwargs):
        super(FacetedSearchView, self).__init__(*args, **kwargs)
        self.is_component = None

    def __call__(self, request):
        response = super(FacetedSearchView, self).__call__(request)

        # Raise a signal for other apps to hook into for analytics
        self.search_signal.send(
            sender=self, session=self.request.session,
            user=self.request.user, query=self.query)

        return response

    # Override this method to add the spelling suggestion to the context and to
    # convert Haystack's default facet data into a more useful structure so we
    # have to do less work in the template.
    def extra_context(self):
        """Override to add the component to the context."""
        extra = super(FacetedSearchView, self).extra_context()

        # Show suggestion no matter what.  Haystack 2.1 only shows a suggestion
        # if there are some results, which seems a bit weird to me.
        if self.results.query.backend.include_spelling:
            # Note, this triggers an extra call to the search backend
            suggestion = self.form.get_suggestion()
            if suggestion != self.query:
                extra['suggestion'] = suggestion

        # Convert facet data into a more useful data structure
        if 'fields' in extra['facets']:
            munger = FacetMunger(
                self.request.get_full_path(),
                self.form.selected_multi_facets,
                self.results.facet_counts())
            extra['facet_data'] = munger.facet_data()
            has_facets = any([len(data['results']) for
                              data in extra['facet_data'].values()])
            extra['has_facets'] = has_facets

        # Pass list of selected facets so they can be included in the sorting
        # form.

        extra['selected_facets'] = self.request.GET.getlist('var')

        # Obtain the Component name and, retrieve it
        # check if it is a compoenent and pass it to context

        extra['component'] = self.is_component

        # pass Basket formset to handle the basket element
        formset = BasketLineFormSet(self.request.strategy)

        extra['formset'] = formset
        # pass the user basket
        extra['basket'] = self.request.basket

        return extra

    def build_page(self):
        """Override to add component behaviour."""
        vars_list = self.request.GET.getlist("var")
        vars_list = [var for var in vars_list if var != '0']
        if len(vars_list) > 0:
            category_full_name = vars_list[-1][9:]
            category = None
            for cat in Category.objects.all():
                if cat.full_name == category_full_name:
                    category = cat
                    break

            # Check if the category is a leaf (Component)
            if not category.has_children():
                self.is_component = category

        if self.is_component:
            # if it's component then there's not pagination
            paginator = Paginator(self.results, sys.maxsize)
            page = paginator.page(1)
            return (paginator, page)
        return super(FacetedSearchView, self).build_page()
