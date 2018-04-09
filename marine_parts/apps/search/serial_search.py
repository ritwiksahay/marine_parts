"""Auxiliar functions and structures for serial search functionality."""

import re

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


def get_queryset_filtered_by_hp(qs, hp):
    qs = qs.filter(name__icontains=hp)
    for q in qs:
        if (re.match('(V-)?' + hp + ' HP', q.name) or
                re.match('(V-)?' + hp + '(?:[A-Z]+|\s|$)', q.name) or
                re.search('(V-)?' + '\s' + hp + ' HP', q.name)):
                continue
        qs = qs.exclude(pk=q.pk)

    print(qs)
    return qs


def get_serial_queryset(brand, hp):
    """Get queryset containing the serial cats corresp to the brand."""
    initial = Category.objects.none()

    if not brand:
        return initial

    def f_chi(a):
        return a.get_children()

    def f_uni(a, b):
        return a | b

    qs = brand.get_children()

    depth = META_BRAND_SEARCH_BY_SERIAL[brand.slug][0]

    for _ in range(depth - 1):
        qs = reduce(f_uni, map(f_chi, qs), initial)

    if float(hp):
        qs = get_queryset_filtered_by_hp(qs, hp)
    result = reduce(f_uni, map(f_chi, qs), initial)
    return result


def get_model_queryset(brand):
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
    q = q_serial.lower()
    for cat in qs:
        range_split = cat.slug.split('-')
        if len(range_split) > 1:
            begin, end = range_split[0], range_split[1]
            if len(q) == len(begin) and \
               (len(begin) == len(end) or end == 'up'):
                if end == 'up':
                    end = begin[0:2] + '9' * (len(begin) - 2)
                if q >= begin and q <= end:
                    continue

        qs = qs.exclude(pk=cat.pk)
    return qs


def get_model_search_results(category, q_serial):
    """Return the results of search by serial for a given category brand."""
    try:
        brand = get_category_brand(category)
        qs = get_model_queryset(brand)
        type_of_search_func = META_BRAND_SEARCH_BY_SERIAL[brand.slug][1]
        result = type_of_search_func(qs, q_serial)
        return result
    except KeyError:  # if brand is not recognized, return empty
        return Category.objects.none()


def get_serial_search_results(category, q_serial, hp):
    """Return the results of search by serial for a given category brand."""
    try:
        brand = get_category_brand(category)
        qs = get_serial_queryset(brand, hp)
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
    return "Engine Model"


def get_list_horses_power():
    """Get the list of horses power available for a brand category."""
    return [
        '2', '2.2', '2.5', '3', '3.5', '3.6', '4', '4.5', '5', '6', '7.5', '8',
        '9.8', '9.9', '10', '13.5', '15', '18', '20', '25', '30', '35', '40',
        '50', '55', '60', '65', '70', '75', '80', '85', '90', '100', '105',
        '110', '115', '125', '135', '140', '150', '175', '200', '220', '225',
        '250', '275', '300', '350'
    ]


# Structure that holds information about the serial search by brand
# For each category brand, we store the depth of the serial categories in the
# category tree corresponding to that brand. We also store the type of the
# search to be perfomed. Finally we store the domain of the field we'll be
# searching in
META_BRAND_SEARCH_BY_SERIAL = {
    'evinrude-johnson': (4, contains_search, 'Engine Model'),
    'mercury': (2, range_search, 'Serial'),
    'volvo-penta': (1, contains_search, 'Engine Model'),
    'mercruiser': (2, range_search, 'Engine Model'),
}


hps = [
    '2 HP (Export)',
    '2 HP',
    '2 (4-Stroke) Carburetor',
    '2.2M HP',
    '2.5',
    '2.5 HP',
    '2.5 (4-Stroke) Carburetor',
    '3 HP',
    '3.3 HP',
    '3.5 HP',
    '3.5 (4-Stroke) Carburetor',
    '3.6 HP',
    '39 (1 Cylinder)',
    'Model 40 4 HP (1 Cylinder)',
    'Model 40, 4 HP (Gnat 2 Cylinder)',
    '4 HP (1 Cylinder Product of USA)',
    '4 HP (2-Stroke)',
    '4 HP (4-Stroke)',
    '4 / 5 HP (1 Cylinder Product of Japan)',
    '4 / 5 HP',
    'Model 45, 4.5 HP (1 Cylinder)',
    '4.5 HP (1 Cylinder)',
    '5 HP (2-Stroke)',
    '5 HP (4-Stroke)',
    '60',
    '60J',
    '6 HP',
    '6 HP (2 Cylinder) (2-Stroke) (International)',
    '6 HP (2 Cylinder) (International)',
    '6 HP (4-Stroke)',
    '7.5 HP',
    '75',
    'Model 75 7.5 HP',
    '8 HP',
    '8 HP (2 Cylinder) (International)',
    '8 SeaPro (2 Cylinder) (International)',
    '8 HP SeaPro (2 Cylinder) (International)',
    '8 HP (Bodensee) 4-Stroke (International)',
    '8 HP (4-Stroke) (209 cc)',
    '9.8 HP',
    '9.8 (2 Cylinder) (International)',
    '9.9 (2 Cylinder) (International)',
    '9.8 HP SeaPro (2 Cylinder) (International)',
    '9.9 HP',
    '9.9 HP (4-Stroke) (209 cc)',
    '9.9 HP (4-Stroke) (232 cc)',
    '9.9 HP (4-Stroke) (323 cc)',
    '100, 150, 200, 250',
    '10 HP SeaPro',
    '10 HP SeaPro',
    '10 HP Viking',
    'XR10',
    '110',
    'Model 110 9.8 HP',
    '13.5 HP (4-Stroke) (International)',
    '15 HP',
    '15 HP SeaPro',
    '15 HP SeaPro',
    '15 HP SeaPro (XD)',
    '15 HP Viking',
    '15 (2 Cylinder) (International)',
    '15 HP (4-Stroke)',
    '15 Carburetor (2 Cylinder) (4-Stroke)',
    '15 SeaPro (4-Stroke)',
    '18 HP',
    '18XD HP',
    '18 (2 Cylinder) (International)',
    '200',
    'Model 200 20 HP',
    'Model 200, 20 HP',
    '20 HP (2 Cylinder)',
    '20XD HP (2 Cylinder)',
    '20 Carburetor (2 Cylinder) (4-Stroke)',
    '20 HP Jet',
    '25 HP Jet (2 Cylinder) (2-Stroke) (International)',
    '25 HP',
    '25 HP (2 Cylinder)',
    '25 HP (2 Cylinder) (International)',
    '25 HP (2 Cylinder) (2-Stroke) (International)',
    '25 HP Lightning (3 Cylinder) (International Only)',
    '25 HP, 25 SeaPro, Super 15 (2 Cylinder)',
    '25XD HP',
    '25 HP (4-Stroke)',
    '25 SeaPro (4-Stroke)',
    '25 HP EFI (3 Cylinder) (4-Stroke)',
    '25 HP Jet EFI (3 Cylinder) (4-Stroke)',
    '30 HP (2 Cylinder)',
    '30 HP (2 Cylinder) (International)',
    '30 HP (2 Cylinder) (2-Stroke) (International)',
    '30 HP (4-Stroke)',
    '30 HP Carburetor (3 Cylinder) (4-Stroke)',
    '30 HP EFI (3 Cylinder) (4-Stroke)',
    '30 EFI (3 Cylinder) (4-Stroke)',
    '30 HP Jet',
    '30 HP Jet (3 Cylinder)',
    '300 350',
    '350',
    '35 HP (2 Cylinder)',
    '35 HP',
    '400',
    'Model 400 40 HP (2 Cylinder)',
    'Model 402 40 HP',
    'Model 402, 40 HP (2 Cylinder)',
    '40 (International)',
    '40 Lightning (International)',
    '40 Lightning XR (International)',
    '40 HP (2 Cylinder Product of USA)',
    '40 HP (2 Cylinder)',
    '40 HP (3 Cylinder)',
    '40 HP (4 Cylinder)',
    '40 HP (4-Stroke)',
    '40 HP Carburetor (3 Cylinder) (4-Stroke)',
    '40 HP (4-Stroke) (4 Cylinder)',
    '40 HP EFI (3 Cylinder) (4-Stroke)',
    '40 EFI (3 Cylinder) (4-Stroke)',
    '40 HP Italy (4-Stroke)',
    '40 HP EFI (4 Cylinder) (4-Stroke)',
    '40 HP EFI (4 Cylinder) (4-Stroke) (Jet)',
    '40 HP Jet',
    '40 MXL SeaPro',
    '450 (4 Cylinder)',
    '45 HP (4 Cylinder)',
    '45 (4 Cylinder)',
    '45 HP Jet',
    '45 HP Bodensee (4-Stroke)',
    '500',
    'Model 500 50 HP',
    'Model 500, 50 HP',
    '50 HP (3 Cylinder)',
    '50 HP (4 Cylinder)',
    '50 (4 Cylinder)',
    '50 HP (4-Stroke)',
    '50 HP Bigfoot (4-Stroke)',
    '50 HP (4-Stroke) (4 Cylinder)',
    '50 HP EFI (4 Cylinder) (4-Stroke)',
    '55 HP (3 Cylinder)',
    '60 HP (3 Cylinder)',
    '60 HP Bigfoot (3 Cylinder)',
    '60 HP (4-Stroke) (4 Cylinder)',
    '60 HP EFI (4 Cylinder) (4-Stroke)',
    '650 (4 Cylinder)',
    '650 (3 Cylinder)',
    'Model 650 65 HP (3 Cylinder)',
    '65 HP Jet',
    '65 HP Jet (3 Cylinder)',
    'Model 700 70 HP (6 Cylinder)',
    '700 (6 Cylinder)',
    '70 HP (3 Cylinder)',
    '70 (3 Cylinder)',
    '75 HP (3 Cylinder)',
    '75 HP (4 Cylinder)',
    '75 HP DFI (3 Cylinder) (1.5L)',
    '75 HP (4-Stroke)',
    '75 HP (4-Stroke) (Bodensee)',
    '75 HP EFI (4-Stroke)',
    'Model 800 80 HP (6 Cylinder)',
    '800 (4 Cylinder) , 80 (4 Cylinder)',
    'Model 800 (4 Cylinder) , 80 HP',
    '80 HP (3 Cylinder)',
    '80 HP EFI (4-Stroke)',
    '80 HP Jet',
    '80 HP Jet (3 Cylinder) (1.5L)',
    'Model 850 85 HP (6 Cylinder)',
    'Model 850 85 HP (4 Cylinder)',
    '850 (4 Cylinder)',
    '900 (6 Cylinder)',
    'Model 900, 90 HP',
    '90 HP (6 Cylinder)',
    '90 HP (3 Cylinder)',
    '90 HP DFI (3 Cylinder) (1.5L)',
    '90 HP (4-Stroke)',
    '90 HP EFI (4-Stroke)',
    '950 (6 Cylinder)',
    '1000',
    '1000SS',
    '1000BP',
    '100 HP (4 Cylinder)',
    '100 HP EFI (4-Stroke)',
    '105 HP Jet',
    '110 HP Jet (2.5L)',
    '1100',
    '1150',
    'Model 1150 115 HP',
    'Model 1150 115 HP, 115',
    '115 HP (4 Cylinder)',
    '115 HP (6 Cylinder)',
    '115 HP DFI (3 Cylinder) (1.5L)',
    'V-115 HP DFI (2.5L)',
    '115 HP Pro XS (3 Cylinder) (1.5L)',
    '115 HP EFI (4-Stroke)',
    '1250',
    '1250BP',
    '125 HP (4 Cylinder)',
    '125 HP DFI (3 Cylinder) (1.5L)',
    '1350',
    'V-135 HP',
    'V-135 HP DFI (2.5L)',
    '135 HP Verado (4-Stroke) (4 Cylinder)',
    '140 HP',
    '1400',
    'Model 1400 140 HP, 140',
    'V-140 HP (International)',
    '140 HP Jet',
    'Model 1500 150 HP',
    'Model 1500XS 150 HP',
    'V-1500',
    'V-150',
    'V-150 HP',
    'V-150 Work',
    'V-150-XR-2',
    'V-150 HP XRI (EFI)',
    'V-150 HP (EFI)',
    'V-150 HP EFI (2.5L)',
    'V-150 HP DFI (2.5L)',
    '150 HP Pro XS (2.5L)',
    '150 HP Verado (4-Stroke) (4 Cylinder)',
    'XR-4',
    'XR-6',
    'V-175 HP',
    'V-175 HP XRI (EFI)',
    'V-175 HP (EFI)',
    'V-175 HP EFI (2.5L)',
    'V-175 HP DFI (2.5L)',
    '175 Pro XS (2.5L)',
    '175 HP Verado (4-Stroke) (4 Cylinder)',
    'V-200',
    'V-200 HP',
    'V-200 HP (2.5L) 1991 ONLY',
    'V-200 HP (EFI)',
    'V-200 HP XRI (EFI)',
    'V-200 HP EFI (2.5L)',
    '200 HP (3.0L EFI)',
    '200 HP (DFI)',
    '200 HP (DFI) 3.0L',
    '200 HP (3.0L DFI) (DTS)',
    '200 HP Pro XS (DFI) 3.0L',
    '200 HP Verado (4-Stroke) (4 Cylinder)',
    '200 HP Verado (4-Stroke) (6 Cylinder)',
    'V-220 HP',
    'V-225 HP',
    '225 HP (3.0L Carburetor)',
    '225 HP SeaPro (3.0L Carburetor)',
    '225 HP (3.0L EFI)',
    '225 HP (3.0L EFI) SeaPro',
    '225 HP (DFI)',
    '225 HP (DFI) 3.0L',
    '225 HP (3.0L-DFI) (DTS)',
    'JP 3.0L DFI',
    '225 HP Pro XS (3.0L DFI)',
    '225 Pro XS (3.0L DFI)',
    '225 HP EFI (4-Stroke)',
    '225 HP Verado (4-Stroke) (6 Cylinder)',
    '250 HP (3.0L EFI)',
    '250 HP Long (3.0L) (EFI)',
    '250XB HP (3.0L EFI)',
    '250 HP (DFI) 3.0L',
    '250 HP Pro XS (3.0L DFI)',
    '250 HP Verado (4-Stroke) (6 Cylinder)',
    '250 HP / 275 HP',
    '275 HP Verado (4-Stroke) (6 Cylinder)',
    '3.0L EFI SeaPro',
    '300 HP Verado (4-Stroke) (6 Cylinder)',
    '350SCi Verado',
    'V-3.4 Liter '
]
