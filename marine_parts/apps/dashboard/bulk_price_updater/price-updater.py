from oscar.apps.partner.models import StockRecord
from decimal import Decimal as D


def get_sr_part_numbers():
    return StockRecord.objects.filter(product__upc='')

def get_sr_partner_sku(stats, sku):
    return StockRecord.objects.filter(partner__sku=sku)


def updater(stats, ls_st_rec, change_func):
    for p in ls_st_rec:
        stats['updated'] += 1
        change_func(p)
        p.save()


def update_by_percent(percent):
    def apply(p):
        p.price_excl_tax += (p.price_excl_tax * percent)
    return apply


def update_by_fixed_price(new_price):
    def apply(p):
        p.price_excl_tax = new_price
    return apply

def execUpdater(sku,fun_updater):
    stats = {
                'not_found' : 0,
                'updated' : 0,
                'total' : 0
            }

    updater(stats, get_sr_partner_sku(stats, sku), fun_updater)

