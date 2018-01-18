from haystack import views

from oscar.core.loading import get_class, get_model

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
        component = None
        vars_list = self.request.GET.getlist("var")

        vars_list = [var for var in vars_list if var != '0']
        if len(vars_list) > 0:
            category_name = vars_list[-1][9:].split(' > ')[-1]
            category = Category.objects.get(name=category_name)
            # Check if the category is a leaf (Component)
            if not category.has_children():
                component = category
        extra['component'] = component

        return extra

    def get_results(self):
        # We're only interested in products (there might be other content types
        # in the Solr index).
        return super(FacetedSearchView, self).get_results().models(Product)
