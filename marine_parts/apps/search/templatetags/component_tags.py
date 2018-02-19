"""Template tags for component view."""

from django import template
from django.template.loader import select_template

from marine_parts.apps.catalogue.models import ReplacementProduct

register = template.Library()


@register.filter
def to_replacement_tree(products):
    """Retrieve all the parts to show in the component view."""
    # get a list of the products's ids
    products_ids = [p.pk for p in products]

    replacements = ReplacementProduct.objects \
        .values_list('replacement', flat=True)

    # get replaced products
    replacement_products = ReplacementProduct.objects \
        .select_related('primary') \
        .filter(primary__pk__in=products_ids) \
        .exclude(primary__pk__in=replacements) \
        .distinct()

    result_products = [rp.primary for rp in replacement_products]

    # get and append those products that neither replace or get replaced by
    # any other product
    result_products = result_products + \
        [p.object for p in products if
         p.object.replacements.count() == 0 and
         p.object.replacement_products.count() == 0]

    # sort the result list by diagram number
    result_products = sorted(result_products, key=get_key)

    return result_products


def get_key(p):
    """Key to sort products by diagram number."""
    try:
        if p.attr.DN[0] == "#":
            dn = int((p.attr.DN)[1:])
        else:
            dn = int(p.attr.DN)

    except (ValueError, IndexError):
        dn = 100000

    return dn


@register.simple_tag(takes_context=True)
def render_component_part(context, product, session):
    """Render a component part."""
    if not product:
        # Search index is returning products that don't exist in the
        # database...
        return ''

    names = ['catalogue/partials/component_part.html']
    template_ = select_template(names)
    context = context.flatten()

    # Ensure the passed product is in the context as 'product'
    context['product'] = product
    context['session'] = session
    return template_.render(context)


@register.simple_tag(takes_context=True)
def render_component_part_header(context, product, session):
    """Render a component part header."""
    if not product:
        # Search index is returning products that don't exist in the
        # database...
        return ''

    names = ['catalogue/partials/component_part_header.html']
    template_ = select_template(names)
    context = context.flatten()

    # Ensure the passed product is in the context as 'product'
    context['product'] = product
    context['session'] = session
    return template_.render(context)
