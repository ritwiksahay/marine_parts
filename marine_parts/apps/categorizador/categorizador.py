#
#   Creador: Daniel Leones
#   Descripcion: Extrae las categorias  y los productos de los archivos JSON
#                usando un version simplificada de DFS. Se imprime por
#                salida estandar los resultados en la notacion jerarquica de Oscar.
#   Fecha: 7/12/2017
#   Modificado: 27/04/2018
#   Ejecucion: dentro del shell de Django. Usar extraer_prods. Este devuelve el
#              numero de productos que encuentra. Por otra parte, crea las
#              categorias, atributos, la clase de producto, y los valores de
#              los atributos.
#   - Capacidad de log ad-hoc incluida
#
from file_handler import FileHandler
from django.db import transaction
from db_handler import DBAccess
from decimal import Decimal as D


###############################################################################

def nav_prods(json_products, bre_cat, db_oscar):
    """
    Crea los productos que se encuentre en el JSON en la BD del proyecto.

    Devuelve el numero de productos procesados.
    """
    def obt_sucesores(hijo):
        products = hijo.get('products')
        if products:
            return products

        products = hijo.get('replacements')
        if products:
            return products

        return None

    comp_img = json_products.get('image')
    cat = db_oscar.crear_categoria(bre_cat, comp_img)

    pila = list()
    pila.append((json_products, None))
    nro_products = 0

    while pila:
        prod_json, padr = pila.pop()
        sucesores = obt_sucesores(prod_json)

        pro = None
        prod_name = prod_json.get('product')
        if prod_name:
            is_available = prod_json.get('is_available')
            part_number_v = prod_json.get('part_number')
            manufacturer_v = prod_json.get('manufacturer')
            diagram_number_v = prod_json.get('diagram_number')
            price_excl_tax = prod_json.get('price', '0.00')
            cost_price = prod_json.get('cost_price', '0.00')
            price_retail = prod_json.get('price_retail', '0.00')
            origin_v = prod_json.get('origin')

            prod, exists = db_oscar.check_partnumber(part_number_v)
            if exists:
                db_oscar.add_product_to_category(prod, cat, diagram_number_v)
                if padr:
                    db_oscar.asign_prod_replacement(padr, prod)
            else:
                pro = db_oscar.crear_prods(cat, is_available, prod_name,
                                           part_number_v, manufacturer_v,
                                           origin_v, diagram_number_v,
                                           price_excl_tax, price_retail,
                                           cost_price)
                db_oscar.add_part_number(part_number_v)
                nro_products += 1

                if padr:
                    db_oscar.asign_prod_replacement(padr, pro)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, pro))

    return nro_products

########################################################################################################################


def obt_sucesores(hijo):
    suc_cat = hijo.get('categories')
    if suc_cat:
        return suc_cat

    suc_sub_cat = hijo.get('sub_category')
    if suc_sub_cat:
        return suc_sub_cat

    return None


def obt_nombres(hijo):
    sucs_nom = hijo.get('category')
    if sucs_nom:
        return sucs_nom
    else:
        return ''


@transaction.atomic
def extraer_prods(json_categorias, db):
    pila = list()
    pila.append((json_categorias, ''))
    camino = list()
    nro_products = 0

    while pila:
        hijo, _ = pila.pop()
        sucesores = obt_sucesores(hijo)
        nom_hijo = obt_nombres(hijo).strip()
        camino.append(nom_hijo)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nom_hijo))
        else:
            nro_products += nav_prods(hijo, list(camino), db)

            if pila:
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()

    return nro_products


def extraer_cats(json_categorias):
    pila = list()
    pila.append((json_categorias, ''))
    categorias = list()
    camino = list()

    while pila:
        hijo, _ = pila.pop()
        sucesores = obt_sucesores(hijo)
        nom_hijo = obt_nombres(hijo).strip()
        camino.append(nom_hijo)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nom_hijo))
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
    total = 0
    for cat in categorias:
        print(cat)
        total += 1
    print('Categories found: %s' % total)

def ejec_extraer_cats(caminoArch):
    fh = FileHandler()
    ejec_extraer_cats_con(caminoArch, fh)

def ejec_extraer_cats_con(caminoArch, ioh):
    imprimirCate(aNotJerarquica(extraer_cats(ioh.leer(caminoArch))))

def ejec_cargador(caminoArch, cat_base, verbosity):
    if verbosity:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)
    fh = FileHandler()
    return extraer_prods(fh.leer(caminoArch), DBAccess(cat_base))
