"""Template tags for component view."""

from django import template
from django.template.loader import select_template

from marine_parts.apps.catalogue.models import ProductCategory

register = template.Library()


@register.filter
def build_results(result_page, comp_id):
    """Return searched parts with their Diagram number."""
    parts_pks = [part.object.pk for part in result_page]
    results = []

    # We don't want the replacements to appear twice
    # in the result page, so, if a replacement is already
    # in the results list then we remove it from there.
    def remove_duplicates(l_parts):
        for part in l_parts:
            if part.pk in parts_pks:
                parts_pks.remove(part.pk)
            else:
                if part.replacement_products.count() != 0:
                    remove_duplicates(part.replacement_products.all())

    for rs in result_page:
        remove_duplicates(rs.object.replacement_products.all())

    for rs in result_page:
        if rs.object.pk in parts_pks:
            # add Diagram Number attributes to the results
            rs.object.DN = \
                ProductCategory.objects \
                .get(product=rs.object, category=comp_id) \
                .diagram_number
            results.append(rs)

    results.sort(key=get_key)
    return results


def get_key(sr):
    """Key to sort products by diagram number."""
    try:
        if sr.object.DN[0] == "#":
            dn = int((sr.object.DN)[1:])
        else:
            dn = int(sr.object.DN)

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
def render_category_search_field(context, tree, parent=None):
    """Render the categories in the refined search widget."""
    if tree == []:
        return ""

    names = ['search/partials/category_search_field.html']
    template_ = select_template(names)
    context = context.flatten()

    context['category_tree'] = tree
    context['parent'] = parent

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
