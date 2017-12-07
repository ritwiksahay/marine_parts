#import sys
import unittest
#sys.path.insert(0,"./categorizador")
#print(sys.path)
import categorizador
import casos_prueba as casos

class TestHandler(categorizador.IOHandler):
    entrada = None

    def leer(self, nomArch):
        return self.entrada

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

if __name__ == '__main__':
    unittest.main()
