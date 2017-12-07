#
#   Creador: Daniel Leones
#   Descripción: Extrae las categorías de los archivos JSON usando un versión simplificada de DFS. Se imprime por
#   salida estándar los resultados en la notación jerarquica de Oscar.
#   Fecha: 7/12/2017
#
import json
import sys


class IOHandler:
    def leer(self, nomArch):
        pass

class FileHandler(IOHandler):
    def leer(self, nomArch):
        return open(nomArch, 'r')


def obtSucesores(hijo):
    sucCat = hijo.get('categories')
    if sucCat:
        return sucCat

    sucSub_cat = hijo.get('sub_category')
    if sucSub_cat:
        return sucSub_cat

    return None

def obtNombres(hijo):
    sucsNom = hijo.get('category')
    if sucsNom:
        return sucsNom
    else:
        return ''


def extraerCats(json_categorias):
    pila = list()
    pila.append((json_categorias,''))
    categorias = list()
    camino = list()

    while pila:
        hijo, _ = pila.pop()
        sucesores = obtSucesores(hijo)
        nomHijo = obtNombres(hijo).strip()
        camino.append(nomHijo)
        #print('\nHijo: ', nomHijo)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nomHijo))
        else:
            categorias.append(camino.copy())

            if pila:
                #print('camino antes' , camino)
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()
                #print('camino despues', camino)

    categorias.reverse()
    return categorias

def aNotJerarquica(list):
    xs = []
    for li in (list):
        lit = ' > '.join(li[1:])
        xs.append(lit)

    return xs

def imprimirCate(categorias):
    print('Categorias encontradas')
    for cat in categorias:
        print(cat)

if __name__ == '__main__':
    fh = FileHandler()
    arbolCategorias = json.load(fh.leer(sys.argv[1]))
    categorias = extraerCats(arbolCategorias)
    imprimirCate(aNotJerarquica(categorias))

