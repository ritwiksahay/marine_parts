import django.test as unittest
import casos_prueba as casos
import categorizador


class TestHandler(categorizador.IOHandler):
    entrada = None

    def leer(self, nomArch):
        return self.entrada

class FakeObjectOscar:
    pass

class StubDBHandler(categorizador.DBHandler):
    def crear_categoria(self, breadcrumb, comp_img=None):
        return FakeObjectOscar()

    def obt_subcomponent_class(self):
        return FakeObjectOscar()

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, p):
        return (FakeObjectOscar(), FakeObjectOscar(), FakeObjectOscar())

    def crear_prods(self, cat, is_aval, prod_name, part_num_v, manufac_v, diag_num_v):
        pass

class MockDB(categorizador.DBHandler):

    def __init__(self):
        self.ls = list()
        self.cnt = 0
        self.padres = list()

    def crear_categoria(self, breadcrumb, comp_img=None):
        pass

    def asign_prod_replacement(self, p_origin, p_asign):
        self.padres.append((p_origin, p_asign))

    def obt_crea_atributos_prods(self, product_class):
        pass

    def obt_subcomponent_class(self):
        pass

    def crear_prods(self, cat, is_aval, prod_name, part_num_v, manufac_v, diag_num_v):
        self.ls.append((self.cnt, prod_name))
        self.cnt += 1
        return prod_name

    @property
    def get_ls(self):
        return self.ls

    @property
    def get_num(self):
        return (self.cnt + 1)

    @property
    def get_padres(self):
        return self.padres

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

# class TestIntegrationIO_extraerProds(unittest.TestCase):
#     def setUp(self):
#         self.entrada = categorizador.FileHandler().leer('marine_parts/apps/categorizador/'
#                                                         'marine_engine_johnson_evinrude-2018-01-12.json')
#         self.contador = MockDB()
#
#     def test_contarProductosCategorias_regresaIgual(self):
#         categorizador.extraerProds_aux( self.entrada, self.contador )
#         self.assertEqual(self.contador.nro_prod, 101)
#
#

class TestIntegrationDB_NavProds(unittest.TestCase):
    def setUp(self):
        self.realDB = categorizador.DBAccess()

    def test_crear_productos_anidados_regresa5(self):
        nro_recom = categorizador.nav_prods(
            casos.varios_productos_anidados,
            "Prueba", self.realDB)
        self.assertEqual(5, nro_recom)


