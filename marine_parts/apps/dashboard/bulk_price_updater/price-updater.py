from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product
from decimal import Decimal as D

class DBHandler:

    def update_by_part_number(self, pn, partner_name, price_excl_tax, retail_price, cost_price):
        p = Product.objects.get(attribute_values__value_text=pn)
        pp = Partner.objects.get(name=partner_name)
        _, created = StockRecord.objects.get_or_create(product=p, partner=pp,
                 defaults={'price_excl_tax' : price_excl_tax
                            , 'retail_price': retail_price
                            , 'cost_price' : cost_price
                           })
        return created


def updater(ls_st_rec, db):
    stats = {
        'created': 0,
        'updated': 0,
        'total': 0
    }

    for p in ls_st_rec:
        if db.update_by_part_number(p[''],):
            stats['updated'] += 1
        else:
            stats['created'] += 1

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
