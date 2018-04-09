"""."""

import sys

from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from haystack import views
from oscar.core import ajax
from oscar.core.loading import get_class, get_model, get_classes

from . import signals
from .forms import SearchByModelSerialForm
from .serial_search import (get_model_search_results,
                            get_serial_search_results,
                            get_serial_or_model,
                            get_list_horses_power)

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
        self.is_component = False

    def __call__(self, request):
        """Override of parent call method."""
        self.category = self._get_category(request)
        self.is_brand_descendant, self.brand_slug = \
            self._is_brand_descendant_category()
        self.is_component = self._is_component()
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

        # pass whether is a descendant of one of the Brands Category
        extra['is_brand_descendant'] = self.is_brand_descendant

        # Check if the search by model/serial must be shown
        if self.is_brand_descendant:
            is_serial_or_model = get_serial_or_model(self.category)
            if is_serial_or_model == 'Engine Model' or \
                    self.category.get_depth() >= 3:
                # if it's mercury or mercruiser (range search)
                # the widget must appear when are in the hp
                # level of the main search
                extra['can_search_by_model_serial'] = True
                # Pass the form for the search by serial number
                serial_search_form = SearchByModelSerialForm(self.request.GET)
                extra['model_serial_form'] = serial_search_form

                """Pass if it's serial or model number we're searching"""
                extra['is_model_or_serial'] = is_serial_or_model

                if is_serial_or_model == 'Serial':
                    extra['list_hps'] = get_list_horses_power()

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

    def _is_component(self):
        """Check if category is a leaf (Component) from a brand category."""
        return bool(self.category) and \
            self.is_brand_descendant and \
            self.category.is_leaf()

    def _is_brand_descendant_category(self):
        """Check if the current category is a descendant ."""
        """of the category 'Brands'. e.g. Mercury, Mercruiser."""
        """If it's true, return also the slug of the brand caregory"""
        if self.category:
            category_path = self.category.full_slug.split('/')
            if len(category_path) > 1:  # if it's not a root, continue
                # get the slug of the root category
                root_slug = category_path[0]
                if root_slug == 'brands':
                    return True, category_path[1]
        return False, None

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


class ModelSearchView(FacetedSearchView):
    """View for the search by serial number requirement."""

    template = "search/results.html"
    search_signal = signals.user_search

    def __init__(self, *args, **kwargs):
        """Override to add the component attribute."""
        super(SerialSearchView, self).__init__(*args, **kwargs)

    def extra_context(self):
        """Add the serial search results to the context."""
        extra = super(SerialSearchView, self).extra_context()
        q = self.request.GET.get('q_serial', None)
        extra['serial_results'] = get_model_search_results(self.category, q)
        return extra

    def create_response(self):
        """Generate the actual HttpResponse to send back to the user."""
        # if only one result is returned then automatically redirect
        # to that serial category page
        context = self.get_context()
        results = context['serial_results']
        if results.count() == 1:
            cat = results[0]
            return redirect(cat)
        else:
            # if not serials were found, show message to user
            if not results:
                flash_messages = ajax.FlashMessages()
                flash_messages.error(_("No categories were found."))
                flash_messages.apply_to_request(self.request)
            return super(SerialSearchView, self).create_response()


class SerialSearchView(FacetedSearchView):
    """View for the search by engine model number requirement."""

    def extra_context(self):
        """Add the serial search results to the context."""
        extra = super(SerialSearchView, self).extra_context()
        q = self.request.GET.get('q_serial', None)
        hp = self.request.GET.get('hp', None)
        extra['selected_hp'] = hp
        extra['serial_results'] = \
            get_serial_search_results(self.category, q, hp)
        return extra

    def create_response(self):
        """Generate the actual HttpResponse to send back to the user."""
        # if only one result is returned then automatically redirect
        # to that serial category page
        context = self.get_context()
        results = context['serial_results']
        if results.count() == 1:
            cat = results[0]
            return redirect(cat)
        else:
            # if not serials were found, show message to user
            if not results:
                flash_messages = ajax.FlashMessages()
                flash_messages.error(_("No categories were found."))
                flash_messages.apply_to_request(self.request)
            return super(SerialSearchView, self).create_response()
