from price_updater import DBHandler, updater, config_logger_prod
import django.test as test
from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product, ProductClass, ProductAttribute
from decimal import Decimal as D
from marine_parts.apps.users.models import User
from django.urls import reverse
from views import ReviewUpdater, UploadFileView
from forms import UploadFileForm, ExtFileField
from django.core.files.uploadedfile import SimpleUploadedFile

# Fakes

class StubDB(DBHandler):
    created = False
    throw_does_not_exists = False
    throw_mult_objs = False

    def update_by_part_number(self, part_number, price_excl_tax, price_retail, cost_price):
        if self.throw_does_not_exists:
            raise Product.DoesNotExist
        if self.throw_mult_objs:
            raise Product.MultipleObjectsReturned
        return (None, self.created)


# Test data
test_data = \
    [
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '1',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : '27.13',
            'Dealer': '23.26',
            'Your Price' : '23.26'
        },
        {
            'IMMFGC': 'A/P',
            'IMITMC': '2',
            'IMDESC': 'PACKING-TEFLON 5/16X	',
            'IMSUOM': 'EA',
            'List': '12.43',
            'Dealer': '10.66',
            'Your Price': '10.66'
        },
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '3',
            'IMDESC' : 'PACKING-TEFLON 1/2X3',
            'IMSUOM' :'EA',
            'List' : '79.43',
            'Dealer': '68.12',
            'Your Price' : '68.12'
        },
        {
            'IMMFGC': 'ABA',
            'IMITMC': '4',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': '1.8',
            'Dealer': '0.83',
            'Your Price': '0.68'
        }
    ]

test_data_Wrong_keys = \
    [
        {
            'IMMFGC' : 'A/P',
            'error' : '1',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : '27.13',
            'Dealer': '23.26',
            'Your Price' : '23.26'
        },
    ]


test_data_bad_prices = \
    [
        {
            'IMMFGC': 'ABA',
            'IMITMC': '1',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': None,
        },
        {
            'IMMFGC': 'ABA',
            'IMITMC': '2',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': 'dasd'
        }
    ]


class TestUpdater(test.TestCase):

    def setUp(self):
        self.st = StubDB('Test', D('30.00'))
        self.log_buf, self.handler = config_logger_prod(False)

    def test_productListEmpty_return0(self):
        stats = updater([], self.st)
        self.assertEqual(stats['total'], 0)
        self.assertEqual(self.log_buf.getvalue(),'')

    def test_createAllProducts_created4(self):
        self.st.created = True
        stats = updater(test_data, self.st)
        self.assertEqual(stats['created'], 4)
        self.assertEqual(stats['total'], 4)

    def test_updateAllProducts_updated4(self):
        stats = updater(test_data, self.st)
        self.assertEqual(stats['updated'], 4)
        self.assertEqual(stats['total'], 4)

    def test_NotFoundProduct_notfound4(self):
        self.st.throw_does_not_exists = True
        stats = updater(test_data, self.st)
        self.assertEqual(stats['not_found'], 4)
        self.assertEqual(stats['total'], 4)

    def test_MultiplesProductNotFound_returns4(self):
        self.st.throw_mult_objs = True
        stats = updater(test_data, self.st)
        self.assertEqual(stats['not_found'], 4)
        self.assertEqual(stats['total'], 4)

    def test_LogReportProductNotFound_returnLog(self):
        self.st.throw_does_not_exists = True
        updater(test_data, self.st)
        #self.handler.flush()
        self.assertEqual(self.log_buf.getvalue(),
            "WARNING - Product with part number 1 does not exists. Skipping update.\n"
            "WARNING - Product with part number 2 does not exists. Skipping update.\n"
            "WARNING - Product with part number 3 does not exists. Skipping update.\n"
            "WARNING - Product with part number 4 does not exists. Skipping update.\n"
                         )

    def test_LogReportMultiplesProductFound_returnLog(self):
        self.st.throw_mult_objs = True
        updater(test_data, self.st)
        #self.handler.flush()
        self.assertEqual(self.log_buf.getvalue(),
             'WARNING - Multiple Products with part number 1. Skipping update for those ones.\n'
             'WARNING - Multiple Products with part number 2. Skipping update for those ones.\n'
             'WARNING - Multiple Products with part number 3. Skipping update for those ones.\n'
             'WARNING - Multiple Products with part number 4. Skipping update for those ones.\n'
                         )

    def test_WrongHeadersWithLogReport_raiseKeyError(self):
        self.assertRaises(KeyError, updater, test_data_Wrong_keys, self.st)
        # self.assertEqual(self.log_buf.getvalue(),
        #                  'Wrong header: error. Unable to continue.'
        #                  'Use the following headers: IMITMC, List, Dealer and Your Price\n'
        #                  )

    def test_WrongValuePrices_return2(self):
        stats = updater(test_data_bad_prices, self.st)
        self.assertEqual(stats['not_found'], 2)
        self.assertEqual(stats['total'], 2)

    def test_WrongValuePrices_returnLog(self):
        stats = updater(test_data_bad_prices, self.st)
        self.assertEqual(self.log_buf.getvalue(),
                         'WARNING - Wrong value. Skipping product with part number 1\n'
                         'WARNING - Wrong value. Skipping product with part number 2\n'
                         )


class TestUAdjustPercent(test.TestCase):

    def test_increase_amount_returnsTrue(self):
        db = DBHandler('test', D(30.00))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(71.50))

    def test_zero_amount_returnsTrue(self):
        db = DBHandler('test', D(0))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(55))

    def test_decrease_amount_returnsTrue(self):
        db = DBHandler('test', D(-30))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(38.50))


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
        cls.partner = Partner.objects.create(name='NewPrice')
        cls.part_number = ProductAttribute.objects.create(
            product_class=cls.pc, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)

    def setUp(self):
        self.create_prod('PACKING-TEFLON 3/16X', True, '4721')
        self.create_prod('RUBBER LINED CLAMP', False, '13302')

        self.p1 = {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4721',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : D('27.13'),
            'Dealer': D('23.26'),
            'Your Price' : D('25.00')
        }

        self.p2 =      {
            'IMMFGC': 'ABA',
            'IMITMC': '13302',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': D('1.8'),
            'Dealer': D('0.83'),
            'Your Price': D('55.00')
        }

        self.db = DBHandler(self.partner, D(0))

    def test_updateProductWithStock_returnsTrue(self):
        sr1, _ = self.db.update_by_part_number(self.p1['IMITMC'], self.p1['Your Price'], self.p1['List'], self.p1['Dealer'])
        self.assertEqual(sr1.price_excl_tax, D(25.00))

    def test_updateProductWithoutStock_returnsTrue(self):
        sr2, _ = self.db.update_by_part_number(self.p2['IMITMC'], self.p2['Your Price'], self.p2['List'], self.p2['Dealer'])
        self.assertEqual(sr2.price_excl_tax, D(55.00))

    def test_updateProductWithoutStockWithIncrease_returnsTrue(self):
        db = DBHandler(self.partner, D(30))
        sr2, _ = db.update_by_part_number(self.p2['IMITMC'], self.p2['Your Price'], self.p2['List'], self.p2['Dealer'])
        self.assertEqual(sr2.price_excl_tax, D(71.50))

    def test_updateProductWithStockWithIncrease_returnsTrue(self):
        db = DBHandler(self.partner, D(30))
        sr1, _ = db.update_by_part_number(self.p1['IMITMC'], self.p1['Your Price'], self.p1['List'],
                                               self.p1['Dealer'])
        self.assertEqual(sr1.price_excl_tax, D(32.50))



class TestUploadFileForm(test.TestCase):
    def setUp(self):
        self.form = UploadFileForm()

    def test_ExtFileFieldFileExtension_returnsTrue(self):
        self.assertFieldOutput(ExtFileField,
               { 'file' : SimpleUploadedFile('a.csv','test')
                 #'b.xls' : SimpleUploadedFile('b.xls','test'),
                 #'c.xlsx': SimpleUploadedFile('c.xlsx', 'test')
                },
               {
                   'file': ["Not allowed filetype!"],
                   #'b.pdf': ["Not allowed filetype!"]
               },
               field_kwargs={ 'ext_whitelist' :  (".xls", ".csv", '.xlsx') })
    #def test_


class ReviewUpdaterClientTests(test.TestCase):
    fixtures = ['metadata.json']

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('dleones@ubicutus.com', '12qw')
        cls.session_review_file_empty = {'stats' : {'not_found' : 0, 'updated' : 0, 'created' : 0, 'total' : 0}, 'log' : ''}
        cls.session_review_sucessful = {'stats': {'not_found': 0, 'updated': 4, 'created': 4, 'total' : 8}, 'log': ''}
        cls.session_review_key_error = { 'stats' : {}, 'log': 'ERROR - Wrong header: bad_key. Unable to continue.'
             'Use the following headers: IMITMC, List, Dealer and Your Price'}
        cls.user_login =  {'username': 'dleones@ubicutus.com', 'password': '12qw'}

    def setUp(self):
        self.factory = test.RequestFactory()

    def test_GETBulkPriceUpdaterIndex_returns200(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-index'))
        request.user = self.user

        response = UploadFileView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_GETBulkPriceUpdaterReviewFileEmpty_returnStats0(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_file_empty
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            """<tr>
                <td>Not found</td>
                <td>0</td>
            </tr>
            <tr>
                <td>Updated</td>
                <td>0</td>
            </tr>
            <tr>
                <td>Created</td>
                <td>0</td>
            </tr>
            <tr>
                <td>Total</td>
                <td>0</td>
            </tr>""")
        self.assertContains(response,
            '<caption><i class="icon-reorder icon-large"></i>(0) Operational messages</caption>')

    def test_GETBulkPriceUpdaterReviewBadFileFormat_returnsLogError(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_key_error
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            'ERROR - Wrong header: bad_key. Unable to continue.Use the following headers: IMITMC, List, Dealer and Your Price')
        self.assertContains(response,
            '<table class="table table-striped table-bordered">'
            '<caption><i class="icon-reorder icon-large"></i> Stock records summary </caption>\n\n</table>',
            html=True, status_code=response.status_code)
        self.assertContains(response,
                            '<caption><i class="icon-reorder icon-large"></i>(1) Operational message</caption>')

    def test_GETBulkPriceUpdaterReviewSucessful_returns(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_sucessful
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            """<tr>
                <td>Not found</td>
                <td>0</td>
            </tr>
            <tr>
                <td>Updated</td>
                <td>4</td>
            </tr>
            <tr>
                <td>Created</td>
                <td>4</td>
            </tr>
            <tr>
                <td>Total</td>
                <td>8</td>
            </tr>""", html=True, status_code=response.status_code)
        self.assertContains(response,
            '<caption><i class="icon-reorder icon-large"></i>(0) Operational messages</caption>\n        \n    </table>',
                status_code=response.status_code,
                html=True)

    def test_GETUploadFileView_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)
        page = self.client.get(reverse('dashboard:bulk-price-updater-index'))

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-index.html')