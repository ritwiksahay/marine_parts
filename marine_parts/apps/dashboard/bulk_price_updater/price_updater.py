from django.core.exceptions import ObjectDoesNotExist
from oscar.apps.partner.models import StockRecord
from marine_parts.apps.catalogue.models import Product
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging
import StringIO


logger = logging.getLogger(__name__)


def config_logger_prod(with_dates=True):

    st = StringIO.StringIO()
    ch = logging.StreamHandler(st)
    # create formatter
    if with_dates:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter('%(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    logger.raiseExceptions = False
    logger.setLevel(logging.INFO)
    logger.addHandler(ch)
    return st, ch


class DBHandler:
    def __init__(self, partner, percent):
        self.partner = partner
        self.percent = percent / Decimal(100)

    def update_by_part_number(
        self,
        part_number,
        price_excl_tax,
        price_retail,
        cost_price
    ):
        # Search by part_number
        num_in_stock = 0
        pro = Product.objects.get(attribute_values__value_text=part_number)

        try:
            stock_record = StockRecord.objects.get(
                product=pro,
                partner=self.partner
            )
            num_in_stock = stock_record.num_in_stock
        except ObjectDoesNotExist:
            pass

        if num_in_stock is None or num_in_stock == 0:
            num_in_stock = 1000

        return StockRecord.objects.update_or_create(
            product=pro,
            partner=self.partner,
            defaults={
                'partner_sku': part_number + str(datetime.now()),
                'price_excl_tax': self.adjust_by_percent(price_excl_tax),
                'price_retail': price_retail,
                'cost_price': cost_price,
                'num_in_stock': num_in_stock
            })

    def adjust_by_percent(self, price):
        return (price * self.percent) + price


# This function must use Atomic Transactions for avoiding to damage
# DB when an exception raises
def updater(ls_st_rec, db):
    stats = {
        'created': 0,
        'updated': 0,
        'not_found': 0,
        'total': 0
    }

    for p in ls_st_rec:
        part_number = p['Part Number']
        try:
            price_retail = Decimal(p['List'])
            cost_price = Decimal(p['Dealer'])
            price_excl_tax = Decimal(p['Your Price'])
        except (TypeError, InvalidOperation):
            logger.warning(
                'Wrong value. Skipping product with part number %s' % part_number
            )
            stats['not_found'] += 1
            continue

        try:
            _, created = db.update_by_part_number(
                part_number, price_excl_tax, price_retail, cost_price
            )
        except Product.DoesNotExist:
            logger.warning(
                'Product with part number %s does not exists. Skipping update.' % part_number
            )
            stats['not_found'] += 1
            continue
        except Product.MultipleObjectsReturned:
            logger.warning(
                'Multiple Products with part number %s. Skipping update for those ones.' % part_number
            )
            stats['not_found'] += 1
            continue
        # except Partner.DoesNotExist:
        #     logger.error('Partner does not exists. )

        if created:
            stats['created'] += 1
        else:
            stats['updated'] += 1

    stats['total'] = stats['created'] + stats['updated'] + stats['not_found']
    return stats


def execUpdater(ls, partner, percent):
    st, h = config_logger_prod()
    stats = dict()

    try:
        stats = updater(ls, DBHandler(partner, percent))
    except KeyError as ke:
        logger.error('Missing header: %s. Unable to continue.'
            'Use the following headers: Part Number, List, Dealer and Your Price' % ke.message
        )

    h.flush()
    st.flush()

    return (stats, st.getvalue())
