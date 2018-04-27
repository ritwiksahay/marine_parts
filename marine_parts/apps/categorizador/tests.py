import django.test as unittest
from django.core.management import call_command, CommandError
import casos_prueba as casos
from django.utils.six import StringIO
from marine_parts.apps.catalogue.models import Product, ProductClass, ProductAttribute, ProductCategory
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from decimal import Decimal as D
from decimal import InvalidOperation
import categorizador
from db_handler import DBHandler, DBAccess
from file_handler import FSHandler
from django.db import DatabaseError


class TestHandler(FSHandler):
    entrada = None

    def leer(self, nomArch):
        return self.entrada


class FakeObjectOscar:
    pass


class StubDBHandler(DBHandler):
    def add_part_number(self, part_number_v):
        pass

    def check_partnumber(self, part_number_v):
        return (None, False)

    def crear_categoria(self, breadcrumb, comp_img=None):
        return FakeObjectOscar()

    def obt_subcomponent_class(self):
        return FakeObjectOscar()

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, p):
        return (FakeObjectOscar(), FakeObjectOscar(), FakeObjectOscar())

    def crear_prods(self, cat, is_aval, prod_name,
                    part_num_v, manufac_v, orig_v,
                    diag_num_v, price_excl_tax, price_retail, cost_price):
        return FakeObjectOscar, True

class MockDB(DBHandler):

    def __init__(self):
        self.ls = list()
        self.cnt = 0
        self.padres = list()
        self.lsCatsProd = list()
        self.part_number_set = set()

    def add_part_number(self, part_number_v):
        self.part_number_set.add(part_number_v)

    def check_partnumber(self, part_number_v):
        if part_number_v in self.part_number_set:
            return part_number_v, True
        else:
            return None, False

    def crear_categoria(self, breadcrumb, comp_img=None):
        return ' > '.join(breadcrumb)

    def asign_prod_replacement(self, p_origin, p_asign):
        self.padres.append((p_origin, p_asign))

    def obt_crea_atributos_prods(self, product_class):
        pass

    def obt_subcomponent_class(self):
        pass

    def crear_prods(self, cat, is_aval, prod_name,
                    part_num_v, manufac_v, orig_v,
                    diag_num_v, price_excl_tax, price_retail, cost_price):
        self.ls.append((self.cnt, prod_name))
        self.cnt += 1
        return prod_name

    def add_product_to_category(self, part_number_v, cat, diag_num):
        self.lsCatsProd.append((part_number_v, cat, diag_num))

    @property
    def get_ls(self):
        return self.ls

    @property
    def get_num(self):
        return (self.cnt + 1)

    @property
    def get_padres(self):
        return self.padres

    @property
    def get_cats_prods(self):
        return self.lsCatsProd


class TestUnitExtraerCats(unittest.TestCase):
    def setUp(self):
        self.handler = TestHandler()
        self.maxDiff = None

    def test_unElementoTodosNiveles_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_UnElemento
        resul = categorizador.extraer_cats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_UnElemento)

    def test_variosElementosComponentes_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variosElemComponentes
        resul = categorizador.extraer_cats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variosElementosCom)

    def test_variosElementosCate_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variasCateg_UnElemComp
        resul = categorizador.extraer_cats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variasCateg_UnElemComp)

    def test_variosElementosCateSerialComp_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variasCateg_variasSerial_variosComp
        resul = categorizador.extraer_cats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variasCateg_variasSerial_variosComp)


class CreaProdsTest(unittest.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = create_from_breadcrumbs('Prueba')
        cls.pc = ProductClass.objects.create(name='Subcomponent')
        cls.partner = Partner.objects.create(name='Loaded')
        cls.part_number = ProductAttribute.objects.create(
            product_class=cls.pc, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)

    def setUp(self):
        self.realDB = DBAccess('Prueba')

    def test_productos_sin_partnumber__regresaRunTimeError(self):
        self.assertRaises(RuntimeError, self.realDB.crear_prods, self.cat, True, 'Hey', None, 'Man', 'ori',
                          '1', '0.00', '0.00', '0.00')

    def test_productos_partnumber_string_empty__regresaRunTimeError(self):
        self.assertRaises(RuntimeError, self.realDB.crear_prods, self.cat, True, 'Hey', '', 'Man', 'ori',
                          '1', '0.00', '0.00', '0.00')

    def test_agregarDiagNumMayor5Caracteres_LevantaDatabaseError(self):
        self.assertRaises(DatabaseError, self.realDB.crear_prods, self.cat, True, 'Prod', '1', 'Man', 'Origin'
                          , 'pppppp', '0.00', '0.00', '0.00')

    def test_incluirPreciosPriceExclTaxComa_OK(self):
        prod = self.realDB.crear_prods(self.cat, True, 'Prod', '1', 'Man', 'Origin'
                          , 'pppppp', '1,002.00', '0.00', '0.00')
        self.assertEqual(prod.title, 'Prod')

    def test_incluirPreciosPriceExclTax_OK(self):
        prod = self.realDB.crear_prods(self.cat, True, 'Prod', '1', 'Man', 'Origin'
                          , 'pppppp', '2.00', '0.00', '0.00')
        self.assertEqual(prod.title, 'Prod')

    def test_incluirPreciosPriceExclTaxComa_regresaInvalidOperation(self):
        self.assertRaises(InvalidOperation, self.realDB.crear_prods, self.cat, True, 'Prod', '1', 'Man', 'Origin'
                          , 'pppppp', '', '0.00', '0.00')

class TestNavProds(unittest.TestCase):

    def setUp(self):
        self.mock = MockDB()

    def test_varios_prods_no_anidados_return3(self):
        nro_recom = categorizador.nav_prods(
            casos.varios_productos_no_anidados,
            "Prueba", StubDBHandler())
        self.assertEqual(3, nro_recom)

    def test_sin_prods_return0(self):
        nro_recom = categorizador.nav_prods(
            casos.sin_productos,
            "Prueba", MockDB())
        self.assertEqual(0, nro_recom)

    def test_varios_prods_con_anidado_returns3(self):
        categorizador.nav_prods(
            casos.varios_productos_con_un_anidado,
            "Prueba", self.mock)
        self.assertEqual(4, self.mock.cnt)
        self.assertEqual(
            [
                (0, "32-812940 4 - Hose"),
                (1, "12-809931044 - Washer"),
                (2, "878-9151 2 - Cylinder Block"),
                (3, "228M0064617 - Nipple Fitting")
            ]
            , self.mock.ls)

    def test_varios_prods_anidados_returns5(self):
        categorizador.nav_prods(
            casos.varios_productos_anidados,
            "Prueba", self.mock)
        self.assertEqual(5, self.mock.cnt)
        self.assertEqual(
            [
                (0, "34-95304 - Reed Stop, NLA"),
                (1, "878-9151 2 - Cylinder Block"),
                (2, "228M0064617 - Nipple Fitting"),
                (3, "32-812940 4 - Hose"),
                (4, "12-809931044 - Washer")
            ]
            , self.mock.ls)
        self.assertEqual(self.mock.padres,
            [
                ("878-9151 2 - Cylinder Block", "228M0064617 - Nipple Fitting"),
                ("228M0064617 - Nipple Fitting", "32-812940 4 - Hose"),
                ("32-812940 4 - Hose", "12-809931044 - Washer")
            ])



class TestExtraerProds(unittest.TestCase):

    def setUp(self):
        self.mockDB = MockDB()

    def test_variasPartesRepetidas(self,):
        nro_prod = categorizador.extraer_prods(casos.productos_repetidos_categorias, self.mockDB)
        self.assertEqual(self.mockDB.lsCatsProd,
             [
                 ('34-95304', '0T894577 & Up (USA) > Cylinder Block','12'),
                 ('878-9151 2', '0T894577 & Up (USA) > Cylinder Block','1'),
             ]
        )

        self.assertEqual(nro_prod, 6)


class TestIntegrationExtraerProds(unittest.TestCase):
    def setUp(self):
        self.realDB = DBAccess("catBase")

    def test_crear_productos_regresa6(self):
        nro_prod = categorizador.extraer_prods(casos.productos_repetidos_categorias, self.realDB)
        self.assertEqual(nro_prod, 6)



class TestIntegrationDB_NavProds(unittest.TestCase):
    def create_prod(self, title, has_stock, part_number, cat=None):
        p = Product.objects.create(product_class=self.pc, title=title)
        if cat:
            ProductCategory.objects.create(product=p, category=cat)

        self.part_number.save_value(p, part_number)
        if has_stock:
            StockRecord.objects.create(product=p, partner=self.partner
                                       , partner_sku=title, price_excl_tax=D('0.00'), num_in_stock=1)

    @classmethod
    def setUpTestData(cls):
        cls.pc = ProductClass.objects.create(name='Subcomponent')
        cls.partner = Partner.objects.create(name='Loaded')
        cls.part_number = ProductAttribute.objects.create(
            product_class=cls.pc, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)


    def setUp(self):
        self.realDB = DBAccess("catBase")

    def test_crear_productos_anidados_regresa5(self):
        nro_recom = categorizador.nav_prods(
            casos.varios_productos_anidados, ["", "Prueba"], self.realDB)
        self.assertEqual(5, nro_recom)

    def test_ProductoYCategoriaRepetidoBajoTransaccion_regresa2(self):
        cat = create_from_breadcrumbs("catBase > Prueba")
        self.create_prod("878-9151 2 - Cylinder Block", False, "878-9151  2", cat)
        nro_recom = categorizador.nav_prods(
            casos.varios_productos_no_anidados, ["", "Prueba"], self.realDB)
        self.assertEqual(2, nro_recom)

    def test_varios_prods_cruzados_returnsTrue(self):
        nro_recom = categorizador.nav_prods(casos.varios_productos_con_reemplazado_cruzado, ["Hola", "Prueba"], self.realDB)
        self.assertEqual(nro_recom, 3)


########################################################################################################################

class LoadProductsManageTest(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        self.out.flush()
        self.derr = StringIO()
        self.derr.flush()

    def test_executeFilepathsEmpty_regresaException(self):
        call_command('load_products', '', stdout=self.out, stderr=self.derr)
        self.assertIn('No products were created', self.out.getvalue())

    def test_executeInvalidSeveralFilePaths_regresaLog(self):
        call_command('load_products', 'file1', stderr=self.out, stdout=self.derr)
        self.assertIn('An error occurred while processing this file: file1', self.out.getvalue())

    def test_execWithCatBase_regresaStringCatBase(self):
        call_command('load_products', 'file1', 'file2', stdout=self.out, cat_base='Prueba', stderr=self.derr)
        self.assertIn('Using base category: Prueba.', self.out.getvalue())

    def test_execWithCatBase_regresaStringLog(self):
        call_command('load_products', 'file1', 'file2', stdout=self.out, cat_base='Prueba', log=True, stderr=self.derr)
        self.assertIn('Log mode on.', self.out.getvalue())

########################################################################################################################

class RetrieveCategoriesTest(unittest.TestCase):
    def setUp(self):
        self.out = StringIO()
        self.out.flush()
        self.derr = StringIO()
        self.derr.flush()

    def test_executeFilepathsEmpty_regresaException(self):
        self.assertRaises(CommandError, call_command, 'retrieve_categories', stdout=self.out, stderr=self.derr)

    def test_executeInvalidFilePath_regresaLog(self):
        call_command('retrieve_categories', 'file1', stderr=self.out, stdio=self.derr)
        self.assertIn('An error occurred while processing this file: file1', self.out.getvalue())