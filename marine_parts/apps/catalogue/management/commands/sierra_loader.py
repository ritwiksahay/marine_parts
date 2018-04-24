import csv

from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import ProductAttribute
from marine_parts.apps.catalogue.models import Product, ProductCategory


def copy_categories(original_part_upc, new_part):
    """
    Clone original part categories and assign them to new part.
    """
    categories = ProductCategory.objects.filter(
        product__upc=original_part_upc
    )

    for category in categories:
        # Assign None to pk and save will create a new instance.
        category.pk = None
        category.product = new_part
        category.save()


def copy_attributes(original_part_upc, new_part):
    """
    Clone original part attributes and assign them to new part.
    """
    attributes = ProductAttribute.objects.filter(
        product__upc=original_part_upc
    )

    for attribute in attributes:
        # Assign None to pk and save will create a new instance.
        attribute.pk = None
        attribute.product = new_part
        attribute.save()


def search_original_part(original_part_number):
    """
    Looks for original part in database.
    """
    try:
        return Product.objects.get(original_part_number)
    except Exception:
        return None


def clone_original_part(data, manufacturer):
    """
    Data is an array with UPC, OEM and OE#.
    """
    original_part = None

    try:
        original_part = search_original_part(data[2])
        original_part_upc = original_part.upc

        if original_part is not None:
            print("Found")

            # Clonning product.
            # Assign None to pk and save will create a new instance.
            original_part.pk = None
            original_part.upc = data[0]
            original_part.title = manufacturer + original_part.title
            new_part = original_part.save()

            # Clonning categories and attributes.
            copy_categories(original_part_upc, new_part)
            copy_attributes(original_part_upc, new_part)

            return True
        return False
    except Exception:
        print("Not found")
        return False


def load_sierra_products(file, manufacturer):
    """
    Load manufacturer product from a csv file.
    With format UPC, OEM, OE#.
    """
    with open(file, 'rb') as csvfile:
        products = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in products:
            data = row[0].split(',')

            # Clone original part, if it exists.
            clone_original_part(data, manufacturer)


class Command(BaseCommand):
    help = 'Load csv files (generic_upc, oem, oe#): python manage.py manufacturer_name file'

    def add_arguments(self, parser):
        parser.add_argument('manufacturer', nargs='+', type=str)
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        load_sierra_products(options['file'], options['manufacturer'])
