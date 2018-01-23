#import unittest
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
    def crear_categoria(self, breadcrumb):
        return FakeObjectOscar()

    def obt_subcomponent_class(self):
        return FakeObjectOscar()

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, p):
        return (FakeObjectOscar(), FakeObjectOscar(), FakeObjectOscar())

    def crearProds(self, p, cat, product_class, part_number, manufacturer, diag_number):
        pass


class MockDB(categorizador.DBHandler):
    nro_prod = 0
    ls_nro_lists = list()
    cats = list()

    def crear_categoria(self, breadcrumb):
        self.cats.append( ' > '.join(breadcrumb[1:]) )

    def obt_subcomponent_class(self):
        return FakeObjectOscar()

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, p):
        return (FakeObjectOscar(), FakeObjectOscar(), FakeObjectOscar())

    def crearProds(self, p, cat, product_class, part_number, manufacturer, diag_number):
        self.nro_prod += 1

class TestUnitExtraerCats(unittest.TestCase):
    def setUp(self):
        self.handler = TestHandler()
        self.maxDiff = None

    def test_unElementoTodosNiveles_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_UnElemento
        resul = categorizador.extraerCats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_UnElemento)

    def test_variosElementosComponentes_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variosElemComponentes
        resul = categorizador.extraerCats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variosElementosCom)

    def test_variosElementosCate_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variasCateg_UnElemComp
        resul = categorizador.extraerCats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variasCateg_UnElemComp)

    def test_variosElementosCateSerialComp_Cierto(self):
        self.handler.entrada = casos.caso_nivelesCompletos_variasCateg_variasSerial_variosComp
        resul = categorizador.extraerCats(self.handler.leer('prueba.json'))
        self.assertEqual(resul, casos.casoR_nivelesCompletos_variasCateg_variasSerial_variosComp)

class TestCreaRecomemd(unittest.TestCase):
    def test_unProductoSinRecomendados_return0(self):
        recom = set()
        nro_recom = categorizador.creaRecomemd(
            casos.caso_unProductoRecomendNulo,
            casos.caso_unProductoRecomendNulo,
            recom, 0, None, None, None, None, None,
            StubDBHandler())
        self.assertEqual(0, nro_recom)

    def test_unProductoRecomendadosString_return0(self):
        recom = set()
        nro_recom = categorizador.creaRecomemd(
            casos.caso_unProductoRecomendString,
            casos.caso_unProductoRecomendString,
            recom, 0, None, None, None, None, None,
            StubDBHandler())
        self.assertEqual(0, nro_recom)

    def test_unProductoConUnRecomendados_return1(self):
        recom = set()
        nro_recom = categorizador.creaRecomemd(
            casos.caso_unProductosConRecomendadoUnNivel,
            casos.caso_unProductosConRecomendadoUnNivel,
            recom, 0, None, None, None, None, None,
            StubDBHandler())
        self.assertEqual(1, nro_recom)

    def test_unProductoConVariosRecomendados_return3(self):
        recom = set()
        nro_recom = categorizador.creaRecomemd(
            casos.caso_unProductoConRecomVariosNiveles,
            casos.caso_unProductoConRecomVariosNiveles,
            recom, 0, None, None, None, None, None,
            StubDBHandler())
        self.assertEqual(3, nro_recom)


class TestNavProds(unittest.TestCase):
    #def test_ArgumentosInvalidosBreadcrumbString_Excepcion(self):
        # nro_recom = categorizador.navProds(
        #     casos.caso_ProductosRepetidoConRecomendadoRepetidoUnNivel,
        #     None, TestDBHandler())
        # self.assertRaises(TypeError,)
        # self.assertEqual(2, nro_recom)


    def test_ProductosRepetidosRecomendados_return2(self):
        nro_recom = categorizador.navProds(
            casos.caso_ProductosRepetidoConRecomendadoRepetidoUnNivel['products'],
            "Prueba", StubDBHandler())
        self.assertEqual(2, nro_recom)

    def test_ProductosRepetidosRecomendadosRepetidosAnidados_return3(self):
        nro_recom = categorizador.navProds(
            casos.caso_ProductosRepetidoConRecomendadosAnidadosRepetidos['products'],
            "Prueba", StubDBHandler())
        self.assertEqual(3, nro_recom)

    def test_variosProductosDosRecomendadosRepetidosAnidados_return6(self):
            nro_recom = categorizador.navProds(
                casos.caso_variosProductosDosConRecomendadosAnidados['products'],
                "Prueba", StubDBHandler())
            self.assertEqual(6, nro_recom)


class TestIntegrationIO_navProds(unittest.TestCase):
    def setUp(self):
        self.entrada = categorizador.FileHandler().leer('marine_parts/apps/categorizador/'
                                                        'marine_engine_johnson_evinrude-2018-01-12.json')
        self.contador = MockDB()

    def test_contarProductosCategorias_regresaIgual(self):
        categorizador.extraerProds_aux( self.entrada, self.contador )
        self.assertEqual(self.contador.nro_prod, 101)


class TestIntegrationDB_NavProds(unittest.TestCase):
    def setUp(self):
        self.realDB = categorizador.DBAccess()

    def test_crearProductos_regresa6(self):
        nro_recom = categorizador.navProds(
            casos.caso_variosProductosDosConRecomendadosAnidados['products'],
            "Prueba", self.realDB)
        self.assertEqual(6, nro_recom)


if __name__ == '__main__':
    unittest.main()
