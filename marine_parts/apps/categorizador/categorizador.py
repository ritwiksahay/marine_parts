#
#   Creador: Daniel Leones
#   Descripción: Extrae las categorías  y los productos de los archivos JSON usando un versión simplificada de DFS. Se imprime por
#   salida estándar los resultados en la notación jerarquica de Oscar.
#   Fecha: 7/12/2017
#   Ejecución: dentro del shell de Django. Usar extraerProds. Este devuelve el numero de productos que encuentra. Por otra parte,
#   crea las categorias, atributos, la clase de producto, y los valores de los atributos.
#
import json, os, sys, django
from oscar.apps.catalogue.models import ProductClass, Product, Category, ProductCategory, ProductAttribute, ProductAttributeValue
from oscar.apps.catalogue.categories import create_from_breadcrumbs
# Necesario para controlar que se introduce en la BD
#from django.db.transaction import atomic

class IOHandler:
    def leer(self, nomArch):
        pass

class FileHandler(IOHandler):
    def leer(self, nomArch):
        return open(nomArch, 'r')


#class AccesoDB:
    #def crear_producto(self,nom_prod, ls_pro):

########################################################################################################################

# Crea los productos que se encuentre en el JSON en la BD del proyecto. Devuelve el número de productos procesados
def crearProds(json_products, bre_cat):
    cat = create_from_breadcrumbs(' > '.join(bre_cat[1:]))
    product_class, _ = ProductClass.objects.get_or_create(name='Subcomponent')

    nro_products = 0
    for p in json_products['products']:
        item = Product()
        item.product_class = product_class
        item.title = p['product']
        item.save()

        manufacturer, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class, name='Manufacturer', code='M', required=True, type=ProductAttribute.TEXT)
        part_number, _ = ProductAttribute.objects.get_or_create(
           product_class=product_class, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)
        diag_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class, name='Diagram number', code='DN', required=True, type=ProductAttribute.TEXT)

        part_number.save_value(item, p['part_number'])
        manufacturer.save_value(item, p['manufacturer'])
        diag_number.save_value(item, p['diagram_number'])

        ProductCategory.objects.get_or_create(product=item, category=cat)
        item.save()
        nro_products += 1
    return nro_products

########################################################################################################################

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


def extraerProds(json_categorias):
    pila = list()
    pila.append((json_categorias,''))
    camino = list()
    nro_products = 0

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
            # Agregar o crear categorias
            nro_products += crearProds(hijo,camino.copy())

            if pila:
                #print('camino antes' , camino)
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()
                #print('camino despues', camino)

    return nro_products

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

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nomHijo))
        else:
            # Agregar o crear categorias
            categorias.append(camino.copy())

            if pila:
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()

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
    nro = extraerProds(arbolCategorias)
    print('Nro de registros nuevos: ', nro)
    #imprimirCate(aNotJerarquica(categorias))

