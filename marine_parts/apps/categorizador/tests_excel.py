import django.test as test
from test_utils import create_test_file
from file_handler import ExcelHandler
from db_handler import DBAccess, DBHandler
from prods_excel import excel_load
from pyexcel import get_records


class TestExcelHandler(ExcelHandler):

    data = [
        ['ProductID','VariantID', 'KitItemID', 'Name', 'KitGroup',
            'SKU', 'ManufacturerPartNumber', 'SKUSuffix', 'Cost', 'MSRP', 'Price', 'SalePrice', 'Inventory'],

        ['79992', '80000', 'Extension Kit for Yamaha T8 & T9.9 4 stroke', '',
            'T8100811A', '811A', '', '0.00', '0.00', '0.00', '0.00', '0'],
        ['79993', '80001', 'Extension Kit for Yamaha T9.9', '',
         'T9100811', '811', '', '0.00', '0.00', '0.00', '0.00', '0'],
    ]

    def get_records_from_xls(self, nom_arch):
        return get_records(file_type='xls', file_content=create_test_file(self.data, 'xls').getvalue())

    def get_records_from_xlsx(self, nom_arch):
        return get_records(file_type='xlsx', file_content=create_test_file(self.data, 'xlsx').getvalue())


########################################################################################################################

class UnitTestsExcelHandler(test.SimpleTestCase):

    def setUp(self):
        self.excel = TestExcelHandler()

    def testleer_pathWithFileExtensionXLS_returnsRecords(self):
        records = self.excel.leer('/p/arch.xls')
        self.assertIsNotNone(records)

    def testleer_pathWithFileExtensionXLSX_returnsRecords(self):
        records = self.excel.leer('/p/arch.xlsx')
        self.assertIsNotNone(records)

    def testleer_pathWithNotSupportFileExtension_raisesRuntimeException(self):
        self.assertRaises(RuntimeError, self.excel.leer, '/p/arch.xxx')

    def testleer_pathWithoutFileExtension_raisesRuntimeException(self):
        self.assertRaises(RuntimeError, self.excel.leer, '/p/arch')

    def testleer_pathEmpty_raisesRuntimeException(self):
        self.assertRaises(RuntimeError, self.excel.leer, '')


class IntegrationTestsExcelLoad(test.TestCase):

    def setUp(self):
        self.excel_stub = TestExcelHandler()
        self.db = DBAccess("Base")

    def test_excel_load__complete_headers__returns2(self):
        nro = excel_load(["", "Ext"], self.db, self.excel_stub.leer('a.xls'), 'A', 'Original', None)
        self.assertEqual(2, nro)

    def test_excel_load__name_header_does_not_exists__returns2(self):
        self.excel_stub.data[0][3] = ''
        self.assertRaises(KeyError, excel_load, ["", "Ext"], self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original', None)

    def test_excel_load__sku_header_does_not_exists__returns2(self):
        self.excel_stub.data[0][5] = ''
        self.assertRaises(KeyError, excel_load, ["", "Ext"], self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original', None)