#
#   Creador: Daniel Leones
#   Descripcion: Extrae las categorias  y los productos de los archivos JSON usando un version simplificada de DFS. Se imprime por
#   salida estandar los resultados en la notacion jerarquica de Oscar.
#   Fecha: 7/12/2017
#   Ejecucion: dentro del shell de Django. Usar extraerProds. Este devuelve el numero de productos que encuentra. Por otra parte,
#   crea las categorias, atributos, la clase de producto, y los valores de los atributos.
#
import json, sys, types
from oscar.apps.catalogue.models import ProductClass, ProductCategory, ProductAttribute
from marine_parts.apps.catalogue.models import Product, ReplacementProduct
from oscar.apps.catalogue.categories import create_from_breadcrumbs
# Necesario para controlar que se introduce en la BD
#from django.db.transaction import atomic

class IOHandler:
    def leer(self, nomArch):
        pass

class FileHandler(IOHandler):
    def leer(self, nomArch):
        return json.load(open(nomArch, 'r'))


class DBHandler:
    def crear_categoria(self, breadcrumb):
        pass

    def obt_subcomponent_class(self):
        pass

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, product_class):
        pass

    def crearProds(self, p, cat, product_class, part_number, manufacturer, diag_number):
        pass

class DBAccess(DBHandler):
    def crear_categoria(self, breadcrumb):
        return create_from_breadcrumbs(' > '.join(breadcrumb[1:]))

    def obt_subcomponent_class(self):
        return self.obt_crea_prod_class('Subcomponent')

    def obt_crea_prod_class(self, nom):
        product_class, _ = ProductClass.objects.get_or_create(name=nom)
        return product_class

    def asign_prod_replacement(self, p_origin, p_asign):
        ReplacementProduct.objects.create(primary=p_origin, replacement=p_asign)

    def obt_crea_atributos_prods(self, product_class):
        manufacturer, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class, name='Manufacturer', code='M', required=True, type=ProductAttribute.TEXT)
        part_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class, name='Part number', code='PN', required=True, type=ProductAttribute.TEXT)
        diag_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class, name='Diagram number', code='DN', required=True, type=ProductAttribute.TEXT)

        return (manufacturer, part_number, diag_number)

    def crearProds(self, p, cat, product_class, part_number, manufacturer, diag_number):
        item = Product()
        item.product_class = product_class
        item.title = p['product']
        item.save()

        part_number.save_value(item, p['part_number'])
        manufacturer.save_value(item, p['manufacturer'])
        diag_number.save_value(item, p['diagram_number'])

        ProductCategory.objects.get_or_create(product=item, category=cat)
        item.save()
        return item


########################################################################################################################

# Crea los productos que se encuentre en el JSON en la BD del proyecto. Devuelve el numero de productos procesados
def navProds(json_products, bre_cat, db_oscar):
    cat = db_oscar.crear_categoria(bre_cat)
    product_class = db_oscar.obt_subcomponent_class()
    part_number, manufacturer, diag_number = db_oscar.obt_crea_atributos_prods(product_class)

    nro_products = 0
    recomendados = set()
    for p in json_products:
        nom_prod = p.get('product')
        if nom_prod not in recomendados:
            prod_saved = db_oscar.crearProds(p, cat, product_class, part_number, manufacturer, diag_number)
            nro_products += creaRecomemd(prod_saved, p, recomendados, 0,
                 cat, product_class, part_number, manufacturer, diag_number, db_oscar)
            nro_products += 1

    return nro_products


def creaRecomemd(pro_root_saved, prod, recom, nro, cat, product_class, part_number, manufacturer, diag_number, db_oscar):
    while True:
        prod = prod.get('recomended')
        if prod and (not isinstance(prod, types.StringTypes)):
            nom_prod = prod.get('product')
            if nom_prod:
                recom.add( nom_prod )
                prod_saved = db_oscar.crearProds(prod, cat, product_class, part_number, manufacturer, diag_number)
                db_oscar.asign_prod_replacement(pro_root_saved, prod_saved )
                nro += 1
        else:
            return nro
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
    return extraerProds_aux(json_categorias, DBHandler())

def extraerProds_aux(json_categorias, db):
    pila = list()
    pila.append((json_categorias, ''))
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
            nro_products += navProds(hijo['products'], list(camino), db)

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
            categorias.append(list(camino))

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

