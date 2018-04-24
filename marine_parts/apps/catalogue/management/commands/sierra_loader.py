import csv

from django.core.management.base import BaseCommand
from oscar.apps.catalogue.models import ProductAttributeValue
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


def copy_attributes(original_part_upc, new_part, manufacturer=""):
    """
    Clone original part attributes and assign them to new part.
    """
    attribute_values = ProductAttributeValue.objects.filter(
        product__upc=original_part_upc
    )

    for attribute_value in attribute_values:
        # Assign None to pk and save will create a new instance.
        attribute_value.pk = None
        attribute_value.product = new_part

        if attribute_value.attribute.name == "Manufacturer":
            attribute_value.value = manufacturer
        if attribute_value.attribute.name == "Origin":
            attribute_value.value = "Aftermarket"

        attribute_value.save()


def search_original_part(original_part_number):
    """
    Looks for original part in database.
    """
    try:
        return Product.objects.get(upc=original_part_number)
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
            # Clonning product.
            # Assign None to pk and save will create a new instance.
            original_part.pk = None
            original_part.upc = data[0]
            new_part = original_part.save()

            # Clonning categories and attributes.
            copy_categories(original_part_upc, new_part)
            copy_attributes(original_part_upc, new_part, manufacturer)

            return True
        return False
    except Exception as e:
        # print(e)
        return False


def load_sierra_products(file, manufacturer):
    """
    Load manufacturer product from a csv file.
    With format UPC, OEM, OE#.
    """
    count = 0
    with open(file, 'rb') as csvfile:
        products = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in products:
            # Clone original part, if it exists.
            if clone_original_part(row, manufacturer):
                count += 1

    return count


class Command(BaseCommand):
    help = 'Load csv files (generic_upc, oem, oe#): python manage.py manufacturer_name file'

    def add_arguments(self, parser):
        parser.add_argument('manufacturer', nargs='+', type=str)
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        count = load_sierra_products(
            options['file'][0],
            options['manufacturer'][0]
        )

        print("Added: %d new products." % (count))
