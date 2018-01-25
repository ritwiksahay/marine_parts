"""Override of Oscar's Shipping Repository."""

from oscar.apps.shipping import repository, methods


class Repository(repository.Repository):
    """Override Shipping Methods."""

    methods = (methods.Free(), methods.FixedPrice(200, 50))
