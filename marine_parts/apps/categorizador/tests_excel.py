import django.test as test
from django.core.management import call_command, CommandError
from marine_parts.apps.catalogue.management.commands import load_prods_excel
from test_utils import create_test_file
from file_handler import ExcelHandler
from db_handler import DBAccess
from prods_excel import excel_load
from pyexcel import get_records
from django.utils.six import StringIO

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

class TestCommand(load_prods_excel.Command):
    nro = 0
    raise_exp = False

    def ejec(self, filepath, cat, cat_base, nom_man, nom_ori):
        if self.raise_exp:
            raise CommandError('An error occurred while processing this file: %s.' % filepath)

        return self.nro


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
        nro = excel_load("Ext", self.db, self.excel_stub.leer('a.xls'), 'A', 'Original')
        self.assertEqual(2, nro)

    def test_excel_load__name_header_does_not_exists__returnsKeyError(self):
        self.excel_stub.data[0][3] = ''
        self.assertRaises(KeyError, excel_load, "Ext", self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original')

    def test_excel_load__sku_header_does_not_exists__returnsKeyError(self):
        self.excel_stub.data[0][5] = ''
        self.assertRaises(KeyError, excel_load, "Ext", self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original')

    def test_excel_load__cost_header_does_not_exists__returnsKeyError(self):
        self.excel_stub.data[0][8] = ''
        self.assertRaises(KeyError, excel_load, "Ext", self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original')

    def test_excel_load__price_header_does_not_exists__returnsKeyError(self):
        self.excel_stub.data[0][10] = ''
        self.assertRaises(KeyError, excel_load, "Ext", self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original')

    def test_excel_load__saleprice_header_does_not_exists__returnsKeyError(self):
        self.excel_stub.data[0][11] = ''
        self.assertRaises(KeyError, excel_load, "Ext", self.db, self.excel_stub.leer('a.xls')
                          , 'A', 'Original')

########################################################################################################################

# Write required named parameters into *args
class UnitTestLoadProdsExcel(test.TestCase):

    def setUp(self):
        self.out = StringIO()
        self.out.flush()
        self.derr = StringIO()
        self.derr.flush()
        self.command = TestCommand()

    def test_executeCatArgNoPresent_regresaException(self):
        self.assertRaises(CommandError, call_command, 'self.command', '', 'stdout=self.out', 'stderr=self.derr')

    def test_executeManufacturerArgNoPresent_regresaException(self):
        self.assertRaises(CommandError, call_command, 'self.command', 'cat=Prueba', 'stdout=self.out', 'stderr=self.derr')

    def test_executeOriginArgNoPresent_regresaException(self):
        self.assertRaises(CommandError, call_command, 'self.command', 'cat=Prueba','manufacturer=Manu'
                          , 'stdout=self.out', 'stderr=self.derr')

    def test_executeFilepathsEmptyWithDefaultCatbase_regresaException(self):
        call_command(self.command, '', '--cat=Prueba', '--manufacturer=Manu', '--origin=Origin', stdout=self.out, stderr=self.derr)
        self.assertIn('No products were created', self.out.getvalue())
        self.assertIn('Using base category: Best Sellers > Extension Kits.', self.out.getvalue())

    def test_executeWithDefaultCatbase_returns1(self):
        self.command.nro = 1
        call_command(self.command, 'file', '--cat=Prueba', '--manufacturer=Manu', '--origin=Origin'
                     , stdout=self.out, stderr=self.derr)
        self.assertIn('%s products were created in DB from %s' % (self.command.nro, 'file'), self.out.getvalue())
        self.assertIn('Using base category: Best Sellers > Extension Kits.', self.out.getvalue())

    def test_executeInvalidSeveralFilePaths_regresaLog(self):
        self.command.raise_exp = True
        call_command(self.command, 'file1', '--cat=Prueba', '--manufacturer=Manu', '--origin=Origin',
                     stderr=self.derr, stdout=self.out)
        self.assertIn('An error occurred while processing this file: file1. Skipping...', self.derr.getvalue())

    def test_execWithCatBase_regresaLog(self):
        call_command(self.command, 'file1', '--cat_base=Prueba', '--cat=Ext', '--manufacturer=Manu', '--origin=Origin'
            , stdout=self.out, stderr=self.derr)
        self.assertIn('Using base category: Prueba.', self.out.getvalue())
    #
    def test_execWithCatManuOrig_regresaLog(self):
        call_command(self.command, 'file1', '--cat_base=Prueba', '--cat=Ext', '--manufacturer=Manu', '--origin=Origin',
                     stdout=self.out, stderr=self.derr)
        self.assertIn('Using base category: Prueba.', self.out.getvalue())
        self.assertIn('Category name: Ext.', self.out.getvalue())
        self.assertIn('Manufacturer name: Manu.', self.out.getvalue())
        self.assertIn('Origin name: Origin.', self.out.getvalue())
