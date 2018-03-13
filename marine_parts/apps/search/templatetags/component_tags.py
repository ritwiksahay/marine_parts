"""Template tags for component view."""

from django import template
from django.template.loader import select_template

register = template.Library()


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
