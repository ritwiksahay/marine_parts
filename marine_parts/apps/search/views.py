"""."""

import itertools
import sys

from django.core.paginator import Paginator
from django.http import Http404

from haystack import views
from oscar.core.loading import get_class, get_model, get_classes

from . import signals
from .forms import SearchBySerialForm

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
        self.component = None
        self.is_category = None
        self.is_brand_child = None

    def __call__(self, request):
        """Override of parent call method."""
        self.category = self._get_category(request)
        self.is_component = self._is_component(request)
        self.is_brand_child = self._is_brand_child_category(request)
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

        # pass the current selected category
        extra['category'] = self.category

        # pass 'is component' flag to the template
        extra['is_component'] = self.is_component

        # pass whether is a direct child of the Brands Category
        extra['is_brand_child'] = self.is_brand_child

        # Pass the form for the search by serial number
        serial_search_form = SearchBySerialForm(self.request.GET)
        extra['serial_form'] = serial_search_form

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
            path = self.request.GET.get('var', None)[9:].split('/')
        except (AttributeError, TypeError):
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

    def _is_component(self, request):
        """Check if the category is a leaf (Component) and returns it."""
        return bool(self.category) and self.category.is_leaf()

    def _is_brand_child_category(self, request):
        """Check if the current category is a direct child."""
        """ of the category 'Brands'. e.g. Mercury, Mercruiser."""
        if self.category:
            parent = self.category.get_parent()
            if parent and parent.slug == 'brands':
                return True

        return False

    def _get_category(self, request):
        """Return the current searched category."""
        var = request.GET.get("var")
        if var and var != '0':
            category_full_slug = var[9:].strip()
            cat_slug = category_full_slug.split('/')[-1]
            matches = Category.objects.filter(slug=cat_slug)

            if matches:
                for cat in matches:
                    if cat.full_slug == category_full_slug:
                        return cat
            else:
                raise Http404("Category doesn't exist.")

        return None

    def build_page(self):
        """Override to add component behaviour."""
        # Check if the category is a leaf (Component)
        if self.component:
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


class SerialSearchView(FacetedSearchView):
    """View for the search by serial number requirement."""

    template = "search/results.html"
    search_signal = signals.user_search

    def __init__(self, *args, **kwargs):
        """Override to add the component attribute."""
        super(SerialSearchView, self).__init__(*args, **kwargs)

    def __get_categories(self, serial_number):
        """Search for categories whose serial number match with the specified."""
        # Get all grand-grand-child (serial number categories) of the current cat
        children = self.category.get_children()
        g_children = map(lambda a: a.get_children(), children)
        g_children = reduce(lambda a, b: a.union(b), g_children)
        gg_children = map(lambda a: a.get_children(), g_children)
        gg_children = reduce(lambda a, b: a.union(b), gg_children)

        result = gg_children.filter(name__icontains=serial_number)

    def extra_context(self):
        extra = super(SerialSearchView, self).extra_context()
        q = self.request.GET.get('q_serial', 0)
        extra['serial_results'] = self.__get_categories(q)
        return extra

    def build_page(self):
        """We're not displaying any result pages in serial search view."""
        return (None, None)

    def get_results(self):
        """We're not displaying any part results in serial search view."""
        return []
