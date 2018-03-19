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
from io import BytesIO
import pyexcel as pe

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

test_file = [
    ['IMMFGC','IMITMC',	'IMDESC', 'IMSUOM', 'List', 'Dealer', 'Your Price'],
    ['A/C', 'GF-626', 'MEMO - REFERENCE ONL', 'EA', '0', '0', '0'],
    ['A/C', '1', 'MEMO - REFERENCE ONL', 'EA', '0', '0', '55'],
    ['A/C', '2', 'MEMO - REFERENCE ONL', 'EA', '0', '0', '100']
]

def create_test_file(data, file_type, fake_name=False):
    io = BytesIO()
    sheet = pe.Sheet(data)
    if fake_name:
        io = sheet.save_to_memory('csv', io)
    else:
        io = sheet.save_to_memory(file_type, io)
    io.name = 'test.' + file_type
    return io


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
        db = DBHandler(None, D(30.00))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(71.50))

    def test_zero_amount_returnsTrue(self):
        db = DBHandler(None, D(0))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(55))

    def test_decrease_amount_returnsTrue(self):
        db = DBHandler(None, D(-30))
        new_value = db.adjust_by_percent(D(55.00))
        self.assertEqual(new_value, D(38.50))


class TestIntegrationUpdatePartNumber(test.TestCase):
    # Auxiliar method
    def create_prod(self, title, hasStock, part_number):
        p = Product.objects.create(product_class=self.pc, title=title)
        self.part_number.save_value(p, part_number)
        if hasStock:
            StockRecord.objects.create(product=p, partner=self.partner
                                       , partner_sku=part_number, price_excl_tax=D('0.00'), num_in_stock=1)

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

    def test_createNewStockRecordNewPartnerProductWithStock_NotRaiseIntegrityError(self):
        partner = Partner.objects.create(name='AnotherPartner')
        db = DBHandler(partner, D(0))
        sr1, created = db.update_by_part_number(self.p1['IMITMC'], self.p1['Your Price'], self.p1['List'], self.p1['Dealer'])
        self.assertTrue(created)
        self.assertEqual(sr1.partner.name, 'AnotherPartner')

    def test_updateProductWithStockWithIncrease_returnsTrue(self):
        db = DBHandler(self.partner, D(30))
        sr1, _ = db.update_by_part_number(self.p1['IMITMC'], self.p1['Your Price'], self.p1['List'],
                                               self.p1['Dealer'])
        self.assertEqual(sr1.price_excl_tax, D(32.50))


class TestUploadFileForm(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.partner = Partner.objects.create(name='NewPrice')

    def setUp(self):
        self.csv = SimpleUploadedFile('a.csv', 'contenido')
        self.xls = SimpleUploadedFile('a.xls', 'contenido')
        self.xlsx = SimpleUploadedFile('a.xlsx', 'contenido')
        self.data = { 'partner' : '1', 'percent' : '0'}
        self.file_data = {'file': ''}

    def test_FileExtensionCSV_returnTrue(self):
        self.file_data['file'] = self.csv
        form = UploadFileForm(self.data, self.file_data)
        self.assertTrue(form.is_valid())

    def test_FileExtensionXLS_returnTrue(self):
        self.file_data['file'] = self.xls
        form = UploadFileForm(self.data, self.file_data)
        self.assertTrue(form.is_valid())

    def test_FileExtensionXLSX_returnTrue(self):
        self.file_data['file'] = self.xlsx
        form = UploadFileForm(self.data, self.file_data)
        self.assertTrue(form.is_valid())

    def test_FileExtensionInValid_returnFalse(self):
        self.file_data['file'] = SimpleUploadedFile('as.xsx', 'error')
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())

    def test_FileFieldEmpty_returnFalse(self):
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())

    def test_PercentEmpty_returnFalse(self):
        self.file_data['file'] = self.csv
        self.data['percent'] = ''
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())

    def test_PercentNone_returnFalse(self):
        self.file_data['file'] = self.csv
        self.data['percent'] = None
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())

    def test_PartnerEmpty_returnFalse(self):
        self.file_data['file'] = self.csv
        self.data['partner'] = ''
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())

    def test_PartnerWrong_returnFalse(self):
        self.file_data['file'] = self.csv
        self.data['partner'] = '2'
        form = UploadFileForm(self.data, self.file_data)
        self.assertFalse(form.is_valid())


class IndexViewTestIntegration(test.TestCase):
    fixtures = ['metadata.json']

    @classmethod
    def setUpTestData(cls):
        Partner.objects.create(name='NewPrice')
        cls.user = User.objects.create_superuser('dleones@ubicutus.com', '12qw')
        cls.user_login = {'username': 'dleones@ubicutus.com', 'password': '12qw'}

        cls.xlsx = create_test_file(test_file, 'xlsx')
        cls.xls = create_test_file(test_file, 'xls')
        cls.csv = create_test_file(test_file, 'csv')
        cls.invalid_file = create_test_file(test_file, 'pdf', True)

    def setUp(self):
        self.post_data = {
            'file' : None,
            'partner' : '1',
            'percent' : '0.0'
        }

    def test_POSTUploadFileViewValidForm_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login,
                         follow=True)

        self.post_data['file'] = self.xls
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data)
        self.assertRedirects(page, '/en-us/dashboard/bulk_price_update/review/')


    def test_POSTUploadFileViewInvalidFormFileEmpty_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = ''
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-index.html')
        self.assertFormError(page, 'form', 'file', 'This field is required.')

    def test_POSTUploadFileViewInvalidFormBadFile_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = self.invalid_file
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-index.html')
        self.assertFormError(page, 'form', 'file', 'Not allowed filetype')


    def test_POSTUploadFileViewInvalidFormPartner_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = self.xlsx
        self.post_data['partner'] = ''
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-index.html')
        self.assertFormError(page, 'form','partner', [u'This field is required.'])


class ReviewUpdaterClientTests(test.TestCase):
    fixtures = ['metadata.json']

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('dleones@ubicutus.com', '12qw')
        cls.session_review_file_empty = {'stats' : {'not_found' : 0, 'updated' : 0, 'created' : 0, 'total' : 0}, 'log' : ''}
        cls.session_review_sucessful = {'stats': {'not_found': 0, 'updated': 4, 'created': 4, 'total' : 8}, 'log': ''}
        cls.session_review_key_error = { 'stats' : {}, 'log': 'ERROR - Missing header: bad_key. Unable to continue.'
             'Use the following headers: IMITMC, List, Dealer and Your Price'}

    def setUp(self):
        self.factory = test.RequestFactory()

    def test_GETBulkPriceUpdaterReviewFileEmpty_returnStats0(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_file_empty
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            """
            <table class="table table-striped table-bordered">
                <caption><i class="icon-bar-chart icon-large"></i> Stock records summary </caption>
                <tr>
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
                </tr>
            </table>""", html=True)
        self.assertContains(response,
            '<caption><i class="icon-info-sign icon-large"></i>(0) Operational messages</caption>')

    def test_GETBulkPriceUpdaterReviewBadFileFormat_returnsLogError(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_key_error
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            'ERROR - Missing header: bad_key. Unable to continue.Use the following headers: IMITMC, List, Dealer and Your Price')
        self.assertContains(response,
            '''
            <table class="table table-striped table-bordered">
                <caption><i class="icon-bar-chart icon-large"></i> Stock records summary </caption>
            </table>
            ''',
            html=True, status_code=response.status_code)

    def test_GETBulkPriceUpdaterReviewSucessful_returns(self):
        request = self.factory.get(reverse('dashboard:bulk-price-updater-review'))
        request.session = self.session_review_sucessful
        request.user = self.user

        response = ReviewUpdater.as_view()(request)
        self.assertEqual(response.template_name[0], 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertContains(response,
            """
            <table class="table table-striped table-bordered">
                <caption><i class="icon-bar-chart icon-large"></i> Stock records summary</caption>
                    <tr>
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
                    </tr>
            </table>
            """, status_code=response.status_code, html=True)
        self.assertContains(response,
            """
            <table class="table table-striped table-bordered">
                <caption><i class="icon-info-sign icon-large"></i>(0) Operational messages</caption>
            </table>
            """, status_code=response.status_code, html=True)

class SystemTestingIntegration(test.TestCase):
    fixtures = ['metadata.json']

    def create_prod(self, title, hasStock, part_number):
        p = Product.objects.create(product_class=self.pc, title=title)
        self.part_number.save_value(p, part_number)
        if hasStock:
            StockRecord.objects.create(product=p, partner=self.partner
                                       , partner_sku=title, price_excl_tax=D('0.00'), num_in_stock=1)

    def setUp(self):
        self.create_prod('PACKING-TEFLON 3/16X', True, '1')
        self.create_prod('RUBBER LINED CLAMP', False, '2')

    @classmethod
    def setUpTestData(cls):
        cls.pc = ProductClass.objects.create(name='Subcomponent')
        cls.partner = Partner.objects.create(name='NewPrice')
        cls.part_number = ProductAttribute.objects.create(
            product_class=cls.pc, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)

        Partner.objects.create(name='NewPrice')
        cls.user = User.objects.create_superuser('dleones@ubicutus.com', '12qw')
        cls.user_login = {'username': 'dleones@ubicutus.com', 'password': '12qw'}
        cls.post_data = {
            'file' : None,
            'partner' : '1',
            'percent' : '0.0'
        }

        cls.xlsx = create_test_file(test_file, 'xlsx')
        cls.xls = create_test_file(test_file, 'xls')
        cls.csv = create_test_file(test_file, 'csv')
        cls.invalid_file = create_test_file(test_file, 'pdf', True)

    def test_POSTFileXlsx_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = self.xlsx
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data, follow=True)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertDictEqual(page.context_data['stats'], {'not_found' : 1, 'updated' : 1, 'created' : 1, 'total' : 3})

    def test_POSTFileXls_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = self.xls
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data, follow=True)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertDictEqual(page.context_data['stats'], {'not_found' : 1, 'updated' : 1, 'created' : 1, 'total' : 3})

    def test_POSTFileCsv_returnsTrue(self):
        # Autheticate user first
        self.client.post('/en-us/dashboard/login/', data=self.user_login, follow=True)

        self.post_data['file'] = self.csv
        page = self.client.post(reverse('dashboard:bulk-price-updater-index'), data=self.post_data, follow=True)

        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'dashboard/bulk_price_updater/update-price-review.html')
        self.assertDictEqual(page.context_data['stats'], {'not_found' : 1, 'updated' : 1, 'created' : 1, 'total' : 3})
