from price_updater import DBHandler, updater
import django.test as test
from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product, ProductClass, ProductAttribute
from decimal import Decimal as D
from django.db.models import ObjectDoesNotExist

# Fakes

class StubDB(DBHandler):
    created = False
    def update_by_part_number(self, p):
        return (None, self.created)


# Test data

test_data = \
    [
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4721',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : '27.13',
            'Dealer': '23.26',
            'Your Price' : '23.26'
        },
        {
            'IMMFGC': 'A/P',
            'IMITMC': '4723',
            'IMDESC': 'PACKING-TEFLON 5/16X	',
            'IMSUOM': 'EA',
            'List': '12.43',
            'Dealer': '10.66',
            'Your Price': '10.66'
        },
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4725',
            'IMDESC' : 'PACKING-TEFLON 1/2X3',
            'IMSUOM' :'EA',
            'List' : '79.43',
            'Dealer': '68.12',
            'Your Price' : '68.12'
        },
        {
            'IMMFGC': 'ABA',
            'IMITMC': '13302',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': '1.8',
            'Dealer': '0.83',
            'Your Price': '0.68'
        }
    ]


class TestUpdater(test.TestCase):

    def test_createAllProducts_returns6(self):
        st = StubDB()
        st.created = True
        stats = updater(test_data, st)
        self.assertEqual(stats['created'], 4)

    def test_updateAllProducts_return6(self):
        stats = updater(test_data, StubDB())
        self.assertEqual(stats['updated'], 4)


class TestIntegrationUpdatePartNumber(test.TestCase):
    # Auxiliar method
    def create_prod(self, title, hasStock, part_number):
        p = Product.objects.create(product_class=self.pc, title=title)
        self.part_number.save_value(p, part_number)
        if hasStock:
            StockRecord.objects.create(product=p, partner=self.partner
                                       , partner_sku=title, price_excl_tax=D('0.00'), num_in_stock=1)

    @classmethod
    def setUpTestData(cls):
        cls.pc = ProductClass.objects.create(name='Subcomponent')
        cls.partner = Partner.objects.create(name='Acme')
        cls.part_number = ProductAttribute.objects.create(
            product_class=cls.pc, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)

        cls.p3_invalid = {
            'IMMFGC': 'ABA',
            'IMITMC': 'not found',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'wrong_key_List': '1.8',
            'wrong_key_Dealer': '0.83',
            'wrong_key_Price': '0.68'
        }

    def setUp(self):
        self.create_prod('PACKING-TEFLON 3/16X', True, '4721')
        self.create_prod('RUBBER LINED CLAMP', False, '13302')

        self.p1 = {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4721',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : '27.13',
            'Dealer': '23.26',
            'Your Price' : '23.26'
        }

        self.p2 =      {
            'IMMFGC': 'ABA',
            'IMITMC': '13302',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': '1.8',
            'Dealer': '0.83',
            'Your Price': '0.68'
        }

        self.p3_invalid = {
            'IMMFGC': 'ABA',
            'Not Found': '13302',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': '1.8',
            'Dealer': '0.83',
            'Your Price': '0.68'
        }



        self.db = DBHandler()

    def test_updateProductWithStock_returnsFalse(self):
        sr1, _ = self.db.update_by_part_number(self.p1)
        self.assertEqual(sr1.price_excl_tax, D('23.26'))

    def test_updateProductWithoutStock_returnsTrue(self):
        sr2, _ = self.db.update_by_part_number(self.p2)
        self.assertEqual(sr2.price_excl_tax, D('0.68'))

    def test_productDoesntFound_raiseException(self):
        self.assertRaises(Product.DoesNotExist,self.db.update_by_part_number, self.p3_invalid)



class IntegrationTestUpdater(test.TestCase):
    pass