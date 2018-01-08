from oscar.apps.catalogue.categories import create_from_breadcrumbs

categories = (
    'Johnson Evinrude Outboard(1955 - present) > 2011 > 300 hp > Model DE300CXIIC > Air Silencer',
    'Johnson Evinrude Outboard(1955 - present) > 2011 > 300 hp > Model DE300CXIIC > Cooling Hoses'
)

def crear_categorias():
    for breadcrumbs in categories:
        create_from_breadcrumbs(breadcrumbs)