from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product
from decimal import Decimal as D
import logging
import StringIO



logger = logging.getLogger(__name__)




def config_logger_prod():
    logging.raiseExceptions = False
    logger.setLevel(logging.ERROR)

    st = StringIO.StringIO()
    ch = logging.StreamHandler(st)
    ch.setLevel(logging.ERROR)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return st

class DBHandler:

    # Manejo de excepciones en caso:
    # - KeyError: Esto puede mitigarse con get
    # - Product and Partner doesn't exists. Check API for get function
    # - Update_or_Create

    def update_by_part_number(self, part_number, price_excl_tax, price_retail, cost_price):
        #import pdb; pdb.set_trace()
        # Idea: When is None, it raises an exception and log the error.
        # Search by part_number
        pp = Partner.objects.get(name='Acme')
        pro = Product.objects.get(attribute_values__value_text=part_number)
        return StockRecord.objects.update_or_create(product=pro, partner=pp,
             defaults={
                        'price_excl_tax' : price_excl_tax
                        , 'price_retail': price_retail
                        , 'cost_price' : cost_price
                       })


# This function must use Atomic Transactions for avoiding to damage DB when an exception raises
def updater(ls_st_rec, db):
    stats = {
        'created': 0,
        'updated': 0,
        'not_found' : 0,
        'total': 0
    }

    for p in ls_st_rec:
        part_number = p['IMITMC']
        price_retail = D(p['List'])
        cost_price = D(p['Dealer'])
        price_excl_tax = D(p['Your Price'])

        # try:
        # except KeyError as ke:
        #     logger.error('Wrong header: %s. Unable to continue.'
        #          'Use the following headers: IMITMC, List, Dealer and Your Price' % ke.message)
        #     return stats
        # except TypeError:
        #     logger.warning('Wrong value. Using default value')

        try:
            _ , created = db.update_by_part_number(part_number, price_excl_tax, price_retail, cost_price)
        except Product.DoesNotExist:
            logger.warning('Product with part number %s does not exists. Skipping update.' % part_number)
            stats['not_found'] += 1
            continue

        if created:
            stats['created'] += 1
        else:
            stats['updated'] += 1

    stats['total'] = stats['created'] + stats['updated'] + stats['not_found']
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
    st = config_logger_prod()
    return (updater(ls, DBHandler()), st.getvalue())
