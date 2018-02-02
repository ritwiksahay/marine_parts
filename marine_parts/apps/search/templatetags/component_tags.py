"""."""

from django import template
from django.template.loader import select_template

from marine_parts.apps.catalogue.models import ReplacementProduct

register = template.Library()


@register.filter
def to_replacement_tree(products):
    """."""
    # get a list of the products's ids
    products_ids = [p.pk for p in products]

    replacements = [rp.replacement.pk for rp in
                    ReplacementProduct.objects.all()]

    # get
    replacement_products = ReplacementProduct.objects \
        .filter(primary__pk__in=products_ids) \
        .exclude(primary__pk__in=replacements) \
        .distinct()

    result_products = [rp.primary for rp in replacement_products]

    # get and append those products that neither replace or get replaced by
    # any other product
    result_products = result_products + \
        [p.object for p in products if
         len(p.object.replacements.all()) == 0 and
         len(p.object.replacement_products.all()) == 0]

    result_products = sorted(result_products, key=get_key)

    return result_products


def get_key(p):
    """Key to sort products by diagram number."""
    dn = (p.attr.DN)[1:]
    return int(dn)


@register.simple_tag(takes_context=True)
def render_component_part(context, product, session):
    """
    Render a product snippet as you would see in a browsing display.

    This templatetag looks for different templates depending on the
    """
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
    """
    Render a product snippet as you would see in a browsing display.

    This templatetag looks for different templates depending on the UPC and
    product class of the passed product.  This allows alternative templates to
    be used for different product classes.
    """
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
