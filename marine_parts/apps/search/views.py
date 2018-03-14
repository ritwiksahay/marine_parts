"""."""

import sys

from django.core.paginator import Paginator
from django.http import Http404

from haystack import views
from oscar.core.loading import get_class, get_model, get_classes
from oscar.core.compat import user_is_authenticated

from . import signals

from marine_parts.apps.catalogue.models import Cat, Category
BasketLineFormSet, SavedLineFormSet = get_classes(
    'basket.formsets', ('BasketLineFormSet', 'SavedLineFormSet'))

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
        """Override to add the component attribute."""
        super(FacetedSearchView, self).__init__(*args, **kwargs)
        self.is_component = None

    def __call__(self, request):
        self._is_component_(request)
        return super(FacetedSearchView, self).__call__(request)

    # Override this method to add the spelling suggestion to the context and to
    # convert Haystack's default facet data into a more useful structure so we
    # have to do less work in the template.
    def extra_context(self):
        """Override to add the component to the context."""
        extra = super(FacetedSearchView, self).extra_context()

        # Pass list of selected facets so they can be included in the sorting
        # form.
        extra['selected_facets'] = self.request.GET.getlist('var')

        # Obtain the Component name and, retrieve it
        # check if it is a compoenent and pass it to context

        extra['component'] = self.is_component

        # pass Basket formset to handle the basket element
        formset = BasketLineFormSet(
            strategy=self.request.basket.strategy,
            queryset=self.request.basket.all_lines()
        )
        extra['formset'] = formset

        # pass the user basket
        extra['basket'] = self.request.basket

        # get var element (contains the complete category path)
        try:
            path = self.request.GET.get('var')[9:].split('/')
        except:
            path = []

        # get categories to show in refined search form
        extra['category_tree'] = self.categories_json(path)

        return extra

    def categories_json(self, path):
        """Json with all the categories to show in the refined search form."""
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

    def _is_component_(self, request):
        """Set is_component attribute."""
        # Get the selected category
        var = request.GET.get("var")
        if var and var != '0':
            category_full_slug = var[9:].strip()
            cat_slug = category_full_slug.split('/')[-1]
            category = None
            matches = Category.objects.filter(slug=cat_slug)

            if matches:
                for cat in matches:
                    if cat.full_slug == category_full_slug:
                        category = cat

            else:
                raise Http404("Category doesn't exist.")

            # Check if the category is a leaf (Component)
            if category.is_leaf():
                self.is_component = category

    def build_page(self):
        """Override to add component behaviour."""
        # Check if the category is a leaf (Component)
        if self.is_component:
            # if it's component then there's not pagination
            paginator = Paginator(self.results, sys.maxsize)
            page = paginator.page(1)
            return (paginator, page)
        return super(FacetedSearchView, self).build_page()

    def get_results(self):
        """."""
        # We're only interested in products (there might be other content types
        # in the Solr index).
        if self.is_component or self.request.GET.get("q"):
            return super(FacetedSearchView, self).get_results()
        else:
            return []
