"""Auxiliar functions and structures for serial search functionality."""

from marine_parts.apps.catalogue.models import Category


def get_category_brand(category):
    """Given a category, returns its category brand."""
    current = category
    while current:
        parent = current.get_parent()
        if parent.full_slug == 'brands':
            return current
        current = parent
    return None


def get_serial_queryset(brand):
    """Get queryset containing the serial cats corresp to the brand."""
    initial = Category.objects.none()

    if not brand:
        return initial

    def f_chi(a):
        return a.get_children()

    def f_uni(a, b):
        return a | b

    result = brand.get_children()

    depth = META_BRAND_SEARCH_BY_SERIAL[brand.slug][0]

    for _ in range(depth):
        result = reduce(f_uni, map(f_chi, result), initial)

    return result


def exact_search(qs, q_serial):
    """Perform a exact match search over the given serial number."""
    return qs.filter(name__iexact=q_serial)


def contains_search(qs, q_serial):
    """Perform a 'LIKE '%%'' match search over the given serial number."""
    return qs.filter(name__icontains=q_serial)


def range_search(qs, q_serial):
    """Perform range search by serial number."""
    return


def get_serial_search_results(category, q_serial):
    """Return the results of search by serial for a given category brand."""
    try:
        brand = get_category_brand(category)
        qs = get_serial_queryset(brand)
        type_of_search_func = META_BRAND_SEARCH_BY_SERIAL[brand.slug][1]
        result = type_of_search_func(qs, q_serial)
        return result
    except KeyError:  # if brand is not recognized, return empty
        return Category.objects.none()


def get_serial_or_model(category):
    """Return string containing the domain of the field to search."""
    """Engine Model Number or Serial Number"""
    brand = get_category_brand(category)
    brand_slug = brand.slug
    aux = META_BRAND_SEARCH_BY_SERIAL.get(brand_slug, None)
    if aux:
        return aux[2]
    return "Serial/Model"

# Structure that holds information about the serial search by brand
# For each category brand, we store the depth of the serial categories in the
# category tree corresponding to that brand. We also store the type of the
# search to be perfomed. Finally we store the domain of the field we'll be
# searching in
META_BRAND_SEARCH_BY_SERIAL = {
    'evinrude-johnson': (3, contains_search, 'Engine Model'),
    'mercury': (2, contains_search, 'Serial'),
    'volvo-penta': (1, contains_search, 'Engine Model'),
    'mercruiser': (2, contains_search, 'Serial'),
}
