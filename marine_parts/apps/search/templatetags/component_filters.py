"""Handy filters to use in component view."""

from django import template

register = template.Library()


@register.filter
def strip_part_number(title):
    """Remove the part number from the part's title."""
    try:
        return title.split('-')[-1]
    except IndexError:
        return title
