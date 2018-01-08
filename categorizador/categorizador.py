import json
import sys

class IOHandler:
    def leer(self, nomArch):
        pass

class FileHandler(IOHandler):
    def leer(self, nomArch):
        return open(nomArch, 'r')


def obtSucesores(hijo):
    if 'categories' in hijo:
        return hijo['categories']
    elif 'years' in hijo:
        return hijo['years']
    elif 'horse_powers' in hijo:
        return hijo['horse_powers']
    elif 'models' in hijo:
        return hijo['models']
    elif 'serial_ranges' in hijo:
        return hijo['serial_ranges']
    elif 'components' in hijo:
        return hijo['components']

    return None


def obtNombres(hijo):
    if 'category' in hijo :
        return hijo['category']
    elif 'year' in hijo:
        return hijo['year']
    elif 'horse_power'in hijo:
        return hijo['horse_power']
    elif 'model' in hijo:
        return hijo['model']
    elif 'serial_range'in hijo:
        return hijo['serial_range']
    elif 'component' in hijo:
        return hijo['component']
    else:
        return ''


def extCat(json_categorias):
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

def aNotJerarquia(list):
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
    categorias = extCat(arbolCategorias)
    imprimirCate(aNotJerarquia(categorias))

