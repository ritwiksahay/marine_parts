"""Override of Oscar's Promotions context processors."""
from marine_parts.apps.catalogue.models import Category

from oscar.apps.promotions.context_processors import (get_request_promotions,
                                                      split_by_position)


def promotions(request):
    """For adding bindings for banners and pods to the template context."""
    promotions = get_request_promotions(request)

    # Split the promotions into separate lists for each position, and add them
    # to the template bindings
    context = {
        'url_path': request.path
    }
    split_by_position(promotions, context)

    # Get the available brands to show in the main navbar
    brands = Category.objects.get(slug='brands')
    context['brands'] = brands.get_children()

    # Get the available categories to show in the main navbar
    categories = Category.objects.get(slug='categories')
    context['categories'] = categories.get_children()

    return context
