"""."""
#
#   Creator: Ubicutus
#   Description: Delete all products and non-canonical categories
#                from DB.
#   Date: 02/20/2018
#   Execution: In project root. > python manage.py drop_catalogue
#

from .models import Product


def execute():
    """Remove all products from DB."""
    # Return the number of deleted products
    return Product.objects.all().delete()[0]
