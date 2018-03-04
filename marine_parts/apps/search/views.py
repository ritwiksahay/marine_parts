"""."""

import json
import sys

from django.core.paginator import Paginator
from django.http import Http404

from haystack import views
from oscar.core.loading import get_class, get_model
from oscar.apps.basket.formsets import BasketLineFormSet

from . import signals

from marine_parts.apps.catalogue.models import Cat, Category

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

        args = "".join(extra['selected_facets'])

        # get last var element (contains the complete category path)

        try:
            path = self.request.GET.getlist('var')[-1][9:].split('/')
        except IndexError:
            path = []

        # get categories to show in refined search form
        extra['category_tree'] = self.categories_json(path)
        extra['url_args'] = args[9:]

        return extra

    def categories_json(self, path):
        """Json with all the categories to show to the user for selection."""
        roots = Category.get_root_nodes()

        def get_tree(parents, path):
            result = []
            selected = None
            for parent in parents:
                # build category dict
                cat = Cat()
                cat.id = parent.id
                cat.name = parent.name
                cat.full_slug = parent.full_slug
                cat.url = parent.get_search_url()
                cat.is_selected = False
                cat.children = []

                if len(path) != 0 and parent.slug == path[0]:
                    cat.is_selected = True
                    selected = cat
                    if parent.has_children():
                        path = path[1:]
                        cat.children = get_tree(parent.get_children(), path)

                result.append(cat)

            return {"categories": result, "selected": selected}

        return get_tree(roots, path)

    def build_page(self):
        """Override to add component behaviour."""
        vars_list = self.request.GET.getlist("var")
        vars_list = [var for var in vars_list if var != '0']
        if len(vars_list) > 0:
            category_full_slug = vars_list[-1][9:]
            category = None
            for cat in Category.objects.all():
                if cat.full_slug == category_full_slug:
                    category = cat
                    break

            if category is None:
                raise Http404("Category doesn't exist.")

            # Check if the category is a leaf (Component)
            if not category.has_children():
                self.is_component = category

        if self.is_component:
            # if it's component then there's not pagination
            paginator = Paginator(self.results, sys.maxsize)
            page = paginator.page(1)
            return (paginator, page)
        return super(FacetedSearchView, self).build_page()
