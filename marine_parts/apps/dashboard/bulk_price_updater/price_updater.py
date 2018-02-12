from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product
from decimal import Decimal as D

class DBHandler:

    # Crear dos o una nueva exceptions to show the user errors.
    def update_by_part_number(self, p):
        # Search by part_number
        part_number_v = p.get('IMITMC')
        # if part_number_v:
        #     raise
        # Idea: When is None, it raises an exception and log the error.
        pp = Partner.objects.get(name='Acme')
        pro = Product.objects.get(attribute_values__value_text=part_number_v)

        # Manejo de excepciones en caso:
        # - KeyError: Esto puede mitigarse con get
        # - Product and Partner doesn't exists. Check API for get function
        # - Update_or_Create
        return StockRecord.objects.update_or_create(product=pro, partner=pp,
             defaults={
                        'price_excl_tax' : D(p['Your Price'])
                        , 'price_retail': D(p['List'])
                        , 'cost_price' : D(p['Dealer'])
                       })


# This function must use Atomic Transactions for avoiding to damage DB when an exception raises
def updater(ls_st_rec, db):
    stats = {
        'created': 0,
        'updated': 0,
        'total': 0
    }

    # Error handling when a Product and Partner doesn't exists. Report this error to user.
    for p in ls_st_rec:
        #try:
            _, created = db.update_by_part_number(p)
            if created:
                stats['created'] += 1
            else:
                stats['updated'] += 1
        #except
    stats['total'] = stats['created'] + stats['updated']
    return stats


def update_by_percent(percent):
    def apply(p):
        p.price_excl_tax += (p.price_excl_tax * percent)
    return apply


def update_by_fixed_price(new_price):
    def apply(p):
        p.price_excl_tax = new_price
    return apply

def execUpdater(ls):
    return updater(ls, DBHandler())
